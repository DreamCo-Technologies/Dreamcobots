"""
DreamCo Platform — DreamcoPipeline
=====================================

``DreamcoPipeline`` is the single class that wires all eight layers of the
DreamCobots reference architecture together:

    User / API / Events
            ↓  (1) EventBus intake
    Command Center / Policy Engine
            ↓  (2) PolicyEngine gate
    Agent Runtime + Workflow Graph
            ↓  (3) ExecutionRuntime + WorkflowGraph
    Model Router (OpenRouter / internal arbitration)
            ↓  (4) DreamCoModelRouter
    Reasoning Providers (OpenAI, Anthropic, Mistral, …)
            ↓  (5) OpenRouterAdapter dispatch
    Memory + Retrieval Layer
            ↓  (6) RetrievalLayer read/write
    Execution Layer
            ↓  (7) capability execution + tool dispatch
    Observability + Governance
            ↓  (8) TelemetryCollector + AuditLog

Usage::

    pipeline = DreamcoPipeline()
    result = pipeline.run(PipelineRequest(
        task_type="coding",
        prompt="Write a Python function that sorts a list",
        user_id="user:alice",
    ))
    print(result.content)

Design notes
------------
* Every layer is independently injectable so you can swap a real Redis
  adapter for a stub without changing the pipeline code.
* When no external credentials are present every layer operates in stub /
  in-process mode, meaning the full pipeline runs in CI without any
  external dependencies.
* ``run()`` is synchronous.  Wrap in ``asyncio.to_thread`` or a thread
  pool for concurrent execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.events.emitter import EventBus
from dreamco_platform.events.schema import EventFamily, make_event
from dreamco_platform.governance.policy_engine import PolicyEngine
from dreamco_platform.model_router.router import DreamCoModelRouter, RouteRequest
from dreamco_platform.model_router.openrouter import OpenRouterAdapter
from dreamco_platform.model_router.arbitration import ArbitrationEngine
from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime, RuntimeContext
from dreamco_platform.retrieval.retrieval_layer import RetrievalLayer
from dreamco_platform.retrieval.sql_store import SQLStore
from dreamco_platform.retrieval.base import RetrievalRecord
from dreamco_platform.observability.telemetry import TelemetryCollector
from dreamco_platform.observability.audit_log import AuditLog


# ---------------------------------------------------------------------------
# Request / Response
# ---------------------------------------------------------------------------

@dataclass
class PipelineRequest:
    """
    A request submitted to the DreamcoPipeline.

    Attributes
    ----------
    task_type : str
        Semantic task category (e.g. ``"coding"``, ``"vision"``).
    prompt : str
        User prompt / task description.
    user_id : str
        Identifier of the requesting user or bot.
    system_prompt : str
        Optional system instruction.
    temperature : float
    max_tokens : int
    workflow_id : str
        Optional workflow identifier for tracing.
    correlation_id : str
        End-to-end trace ID.  Auto-generated if not supplied.
    context : dict
        Arbitrary context forwarded to the policy engine.
    retrieve_memory : bool
        Whether to retrieve relevant memories and inject them into the prompt.
    store_result : bool
        Whether to persist the result in the retrieval layer.
    metadata : dict
        Arbitrary extra metadata.
    """

    task_type: str
    prompt: str
    user_id: str = "anonymous"
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    workflow_id: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: dict[str, Any] = field(default_factory=dict)
    retrieve_memory: bool = True
    store_result: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """
    The output of a full pipeline execution.

    Attributes
    ----------
    content : str
        Generated text content.
    model_id : str
        Model that produced the response.
    task_type : str
    correlation_id : str
    policy_blocked : bool
        ``True`` if the request was blocked by a policy rule.
    policy_messages : list[str]
        Human-readable policy evaluation messages.
    retrieved_context : list[str]
        Memory snippets injected as context (if ``retrieve_memory=True``).
    latency_ms : float
        Total pipeline wall-clock latency.
    cost_usd : float
    stub : bool
    metadata : dict
    """

    content: str
    model_id: str
    task_type: str
    correlation_id: str
    policy_blocked: bool = False
    policy_messages: list[str] = field(default_factory=list)
    retrieved_context: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    stub: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model_id": self.model_id,
            "task_type": self.task_type,
            "correlation_id": self.correlation_id,
            "policy_blocked": self.policy_blocked,
            "policy_messages": self.policy_messages,
            "retrieved_context": self.retrieved_context,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "stub": self.stub,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# DreamcoPipeline
# ---------------------------------------------------------------------------

class DreamcoPipeline:
    """
    End-to-end DreamCobots inference + execution pipeline.

    All constructor parameters are optional — defaults create a fully
    in-process stub pipeline with no external dependencies.

    Parameters
    ----------
    event_bus : EventBus | None
    policy_engine : PolicyEngine | None
    execution_runtime : ExecutionRuntime | None
    model_router : DreamCoModelRouter | None
    retrieval_layer : RetrievalLayer | None
    telemetry : TelemetryCollector | None
    audit_log : AuditLog | None
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        policy_engine: PolicyEngine | None = None,
        execution_runtime: ExecutionRuntime | None = None,
        model_router: DreamCoModelRouter | None = None,
        retrieval_layer: RetrievalLayer | None = None,
        telemetry: TelemetryCollector | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        # Layer 1 — Events
        self._bus = event_bus or EventBus()

        # Layer 2 — Policy Engine
        self._policy = policy_engine or PolicyEngine()

        # Layer 3 — Agent Runtime
        self._runtime = execution_runtime or ExecutionRuntime(
            default_max_attempts=3, default_backoff_seconds=0.0
        )

        # Layer 4 + 5 — Model Router + Reasoning Providers
        self._router = model_router or DreamCoModelRouter(
            adapter=OpenRouterAdapter(),
            engine=ArbitrationEngine(load_defaults=True),
        )

        # Layer 6 — Memory + Retrieval
        if retrieval_layer is not None:
            self._retrieval = retrieval_layer
        else:
            self._retrieval = RetrievalLayer()
            self._retrieval.add_backend(SQLStore(), write=True, search=True)

        # Layer 8 — Observability + Governance
        self._telemetry = telemetry or TelemetryCollector()
        self._audit = audit_log or AuditLog()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self, request: PipelineRequest) -> PipelineResult:
        """
        Execute the full 8-layer pipeline for *request*.

        Parameters
        ----------
        request : PipelineRequest

        Returns
        -------
        PipelineResult
        """
        t0 = time.monotonic()

        # ── Layer 1: Event intake ────────────────────────────────────
        self._emit("workflow.started", request, payload={
            "task_type": request.task_type,
            "user_id": request.user_id,
        })

        # ── Layer 2: Policy gate ─────────────────────────────────────
        policy_ctx = {
            "task_type": request.task_type,
            "user_id": request.user_id,
            **request.context,
        }
        policy_results = self._policy.evaluate_all(policy_ctx)
        triggered = [r for r in policy_results if r.triggered]
        blocked = self._policy.has_blocking_violation(policy_ctx)

        if blocked:
            latency_ms = (time.monotonic() - t0) * 1000
            self._telemetry.record_latency(
                "pipeline", "dreamco_pipeline", latency_ms, success=False,
                correlation_id=request.correlation_id,
            )
            self._emit("governance.policy_violated", request, payload={
                "triggered_rules": [r.rule_id for r in triggered]
            })
            return PipelineResult(
                content="",
                model_id="",
                task_type=request.task_type,
                correlation_id=request.correlation_id,
                policy_blocked=True,
                policy_messages=[r.message for r in triggered],
                latency_ms=latency_ms,
            )

        # ── Layer 3: Agent Runtime / Workflow Graph ──────────────────
        retrieved_context: list[str] = []

        def _step(ctx: RuntimeContext) -> dict[str, Any]:
            # ── Layer 6: Memory retrieval ────────────────────────────
            nonlocal retrieved_context
            if request.retrieve_memory:
                records = self._retrieval.search(
                    request.prompt, limit=5
                )
                retrieved_context = [r.content for r in records]

            # Build enriched prompt
            enriched_prompt = request.prompt
            if retrieved_context:
                context_block = "\n".join(f"- {c}" for c in retrieved_context)
                enriched_prompt = (
                    f"Relevant context:\n{context_block}\n\n{request.prompt}"
                )

            # ── Layers 4 + 5: Model Router + Provider dispatch ───────
            route_req = RouteRequest(
                task_type=request.task_type,
                prompt=enriched_prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            route_resp = self._router.route(route_req)

            # ── Layer 6: Store result ────────────────────────────────
            if request.store_result:
                result_key = f"result:{request.correlation_id}"
                self._retrieval.upsert(RetrievalRecord(
                    key=result_key,
                    content=route_resp.content,
                    metadata={
                        "task_type": request.task_type,
                        "user_id": request.user_id,
                        "model_id": route_resp.model_id,
                        "correlation_id": request.correlation_id,
                    },
                ))

            ctx.checkpoint({"model_id": route_resp.model_id})
            return {
                "content": route_resp.content,
                "model_id": route_resp.model_id,
                "cost_usd": route_resp.cost_usd,
                "latency_ms": route_resp.latency_ms,
                "stub": route_resp.stub,
            }

        record = self._runtime.run(
            job_id=request.correlation_id,
            step=_step,
            max_attempts=3,
            backoff_seconds=0.0,
        )

        latency_ms = (time.monotonic() - t0) * 1000

        # ── Layer 8: Telemetry + Observability ───────────────────────
        self._telemetry.record_latency(
            "pipeline",
            "dreamco_pipeline",
            latency_ms,
            success=record.status.value == "succeeded",
            correlation_id=request.correlation_id,
        )

        if record.result:
            self._telemetry.record_cost(
                "pipeline",
                "dreamco_pipeline",
                record.result.get("cost_usd", 0.0),
                correlation_id=request.correlation_id,
            )

        event_type = (
            "workflow.completed" if record.status.value == "succeeded"
            else "workflow.failed"
        )
        self._emit(event_type, request, payload={
            "latency_ms": latency_ms,
            "status": record.status.value,
        })

        if record.status.value != "succeeded":
            return PipelineResult(
                content=f"Pipeline execution failed: {record.error}",
                model_id="",
                task_type=request.task_type,
                correlation_id=request.correlation_id,
                policy_blocked=False,
                policy_messages=[r.message for r in triggered],
                latency_ms=latency_ms,
            )

        result_data = record.result or {}
        return PipelineResult(
            content=result_data.get("content", ""),
            model_id=result_data.get("model_id", ""),
            task_type=request.task_type,
            correlation_id=request.correlation_id,
            policy_blocked=False,
            policy_messages=[r.message for r in triggered if r.triggered],
            retrieved_context=retrieved_context,
            latency_ms=latency_ms,
            cost_usd=result_data.get("cost_usd", 0.0),
            stub=result_data.get("stub", True),
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_summary(self) -> dict[str, Any]:
        """Return a health summary across all pipeline layers."""
        return {
            "model_router": self._router.get_summary(),
            "retrieval_backends": self._retrieval.list_backends(),
            "retrieval_stats": self._retrieval.stats(),
            "runtime_stats": self._runtime.stats(),
            "telemetry_summary": self._telemetry.summarize(),
            "policy_rules": len(self._policy),
        }

    @property
    def policy_engine(self) -> PolicyEngine:
        return self._policy

    @property
    def retrieval_layer(self) -> RetrievalLayer:
        return self._retrieval

    @property
    def telemetry(self) -> TelemetryCollector:
        return self._telemetry

    @property
    def model_router(self) -> DreamCoModelRouter:
        return self._router

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _emit(
        self,
        event_type: str,
        request: PipelineRequest,
        payload: dict[str, Any] | None = None,
    ) -> None:
        try:
            family, subtype = event_type.split(".", 1)
            event = make_event(
                family=family,
                subtype=subtype,
                source="dreamco_pipeline",
                payload=payload or {},
                correlation_id=request.correlation_id,
            )
            self._bus.emit(event)
        except Exception:  # noqa: BLE001
            pass
