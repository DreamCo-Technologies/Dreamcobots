"""
DreamCo Platform — Capability Execution Engine
===============================================

``ExecutionEngine`` runs a ``WorkflowGraph`` end-to-end, producing a
structured execution report.  It builds on ``WorkflowGraph.execute()`` and
adds:

* Per-node timing and cost accounting
* Event emission via the ``EventBus`` (capability.invoked / completed / failed)
* Retry orchestration with configurable back-off
* Execution hooks for observability integration

Usage::

    from dreamco_platform.capabilities.execution_engine import ExecutionEngine
    from dreamco_platform.events.emitter import get_default_bus

    engine = ExecutionEngine(bus=get_default_bus())
    report = engine.run(workflow_graph, initial_inputs={"query": "leads"})
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.capabilities.models import (
    CapabilityNode,
    WorkflowGraph,
)
from dreamco_platform.events.emitter import EventBus
from dreamco_platform.events.schema import EventFamily, make_event


# ---------------------------------------------------------------------------
# Report types
# ---------------------------------------------------------------------------

@dataclass
class NodeExecutionRecord:
    capability_id: str
    success: bool
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    error: str | None
    duration_ms: float
    cost_usd: float
    attempt: int


@dataclass
class ExecutionReport:
    graph_id: str
    success: bool
    records: list[NodeExecutionRecord] = field(default_factory=list)
    total_duration_ms: float = 0.0
    total_cost_usd: float = 0.0
    failed_node: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "success": self.success,
            "total_duration_ms": self.total_duration_ms,
            "total_cost_usd": self.total_cost_usd,
            "failed_node": self.failed_node,
            "records": [
                {
                    "capability_id": r.capability_id,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "cost_usd": r.cost_usd,
                    "attempt": r.attempt,
                    "error": r.error,
                }
                for r in self.records
            ],
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class ExecutionEngine:
    """Runs a ``WorkflowGraph`` with event emission and cost tracking.

    Parameters
    ----------
    bus:
        ``EventBus`` instance.  Pass ``None`` to disable event emission.
    source_id:
        Identifies this engine in emitted events (e.g. ``"execution_engine"``).
    """

    def __init__(
        self,
        bus: EventBus | None = None,
        source_id: str = "execution_engine",
    ) -> None:
        self._bus = bus
        self._source_id = source_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        graph: WorkflowGraph,
        initial_inputs: dict[str, Any] | None = None,
    ) -> ExecutionReport:
        """Execute *graph* and return an ``ExecutionReport``."""
        start = time.perf_counter()
        report = ExecutionReport(graph_id=graph.graph_id, success=False)
        accumulated: dict[str, Any] = dict(initial_inputs or {})

        try:
            node_ids = graph.topological_sort()
        except ValueError as exc:
            report.success = False
            report.failed_node = "<topology>"
            report.total_duration_ms = (time.perf_counter() - start) * 1000
            return report

        for node_id in node_ids:
            node = graph.nodes[node_id]
            record = self._execute_node(node, accumulated, graph.graph_id)
            report.records.append(record)
            report.total_cost_usd += record.cost_usd

            if not record.success:
                report.success = False
                report.failed_node = node.capability_id
                report.total_duration_ms = (time.perf_counter() - start) * 1000
                return report

            accumulated.update(record.outputs)

        report.success = True
        report.total_duration_ms = (time.perf_counter() - start) * 1000
        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_node(
        self,
        node: CapabilityNode,
        inputs: dict[str, Any],
        graph_id: str,
    ) -> NodeExecutionRecord:
        max_attempts = node.retry_policy.get("max_attempts", 1)
        backoff = node.retry_policy.get("backoff_seconds", 0)
        per_call_cost = node.cost_profile.get("per_call_usd", 0.0)

        self._emit_capability_event("invoked", node.capability_id, graph_id)

        last_error: str | None = None
        for attempt in range(1, max_attempts + 1):
            t0 = time.perf_counter()
            try:
                if node.executor is not None:
                    raw_result = node.executor(inputs)
                    outputs = raw_result if isinstance(raw_result, dict) else {"result": raw_result}
                else:
                    outputs = {}
                duration_ms = (time.perf_counter() - t0) * 1000
                self._emit_capability_event("completed", node.capability_id, graph_id)
                return NodeExecutionRecord(
                    capability_id=node.capability_id,
                    success=True,
                    inputs=inputs,
                    outputs=outputs,
                    error=None,
                    duration_ms=duration_ms,
                    cost_usd=per_call_cost,
                    attempt=attempt,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                duration_ms = (time.perf_counter() - t0) * 1000
                if attempt < max_attempts and backoff > 0:
                    time.sleep(backoff)

        self._emit_capability_event("failed", node.capability_id, graph_id, {"error": last_error})
        return NodeExecutionRecord(
            capability_id=node.capability_id,
            success=False,
            inputs=inputs,
            outputs={},
            error=last_error,
            duration_ms=0.0,
            cost_usd=per_call_cost,
            attempt=max_attempts,
        )

    def _emit_capability_event(
        self,
        action: str,
        capability_id: str,
        graph_id: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        if self._bus is None:
            return
        payload = {"capability_id": capability_id, "graph_id": graph_id}
        if extra:
            payload.update(extra)
        try:
            event = make_event(
                EventFamily.CAPABILITY,
                action,
                self._source_id,
                payload=payload,
            )
            self._bus.emit(event)
        except Exception:  # noqa: BLE001
            pass
