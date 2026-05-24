"""
DreamCo Platform — DreamCoModelRouter
======================================

``DreamCoModelRouter`` is the top-level Model Router for the DreamCobots
reference architecture (Layer 4):

    Agent Runtime + Workflow Graph
            ↓
    DreamCoModelRouter  ← this module
    ├── ArbitrationEngine  (internal provider selection + fallback)
    └── OpenRouterAdapter  (HTTP gateway to 200+ models)
            ↓
    Reasoning Providers (OpenAI, Anthropic, Mistral, …)

How it works
------------
1. Caller submits a ``RouteRequest`` (task type + prompt + options).
2. ``ArbitrationEngine`` selects the best provider for the task type.
3. ``OpenRouterAdapter.complete()`` dispatches the request via OpenRouter
   (or returns a stub response in CI / no-key environments).
4. On provider error the router retries down the ``fallback_chain``.
5. Every call is recorded in the latency feedback loop so subsequent
   selections benefit from real performance data.
6. A ``RouteResponse`` is returned, carrying the content, chosen model,
   cost estimate, latency, and stub flag.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.model_router.openrouter import (
    OpenRouterAdapter,
    OpenRouterRequest,
    OpenRouterResponse,
)
from dreamco_platform.model_router.arbitration import (
    ArbitrationEngine,
    ArbitrationPolicy,
    ProviderSpec,
)


# ---------------------------------------------------------------------------
# Request / Response
# ---------------------------------------------------------------------------

@dataclass
class RouteRequest:
    """
    A routing request submitted to the ``DreamCoModelRouter``.

    Attributes
    ----------
    task_type : str
        Semantic task category (e.g. ``"coding"``, ``"vision"``).
    prompt : str
        The user / system prompt to send to the model.
    system_prompt : str
        Optional system-level instruction to prepend.
    temperature : float
    max_tokens : int
    policy : ArbitrationPolicy | None
        Override the engine's default arbitration policy for this call.
    metadata : dict
        Arbitrary key-value pairs forwarded to OpenRouter.
    """

    task_type: str
    prompt: str
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    policy: ArbitrationPolicy | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteResponse:
    """
    The result of a routing + completion call.

    Attributes
    ----------
    model_id : str
        The model that produced the response.
    content : str
        The generated text.
    task_type : str
        Task type used for routing.
    finish_reason : str
    prompt_tokens : int
    completion_tokens : int
    total_tokens : int
    cost_usd : float
    latency_ms : float
    fallback_used : bool
        ``True`` if the primary provider failed and a fallback was used.
    stub : bool
        ``True`` if no live API key was configured.
    metadata : dict
        Arbitrary extra data.
    """

    model_id: str
    content: str
    task_type: str
    finish_reason: str = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    fallback_used: bool = False
    stub: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "content": self.content,
            "task_type": self.task_type,
            "finish_reason": self.finish_reason,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "fallback_used": self.fallback_used,
            "stub": self.stub,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# DreamCoModelRouter
# ---------------------------------------------------------------------------

class DreamCoModelRouter:
    """
    Top-level model router combining OpenRouter + internal arbitration.

    Parameters
    ----------
    adapter : OpenRouterAdapter | None
        Custom adapter instance.  Defaults to a new ``OpenRouterAdapter``
        (which runs in stub mode when no API key is set).
    engine : ArbitrationEngine | None
        Custom arbitration engine.  Defaults to a new engine with the
        built-in DEFAULT_PROVIDERS catalogue.
    max_fallback_attempts : int
        Number of fallback providers to try before giving up.
    """

    def __init__(
        self,
        adapter: OpenRouterAdapter | None = None,
        engine: ArbitrationEngine | None = None,
        max_fallback_attempts: int = 3,
    ) -> None:
        self._adapter = adapter or OpenRouterAdapter()
        self._engine = engine or ArbitrationEngine()
        self._max_fallbacks = max_fallback_attempts

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, request: RouteRequest) -> RouteResponse:
        """
        Route *request* to the best provider and return the completion.

        Retries down the fallback chain on error.

        Parameters
        ----------
        request : RouteRequest

        Returns
        -------
        RouteResponse

        Raises
        ------
        RuntimeError
            If all providers in the fallback chain fail.
        """
        chain = self._engine.fallback_chain(
            request.task_type, policy=request.policy
        )
        if not chain:
            # No matching provider — fall back to a generic model
            chain = ["openai/gpt-4o"]

        last_error: str | None = None
        fallback_used = False

        for attempt, model_id in enumerate(chain[: self._max_fallbacks]):
            is_fallback = attempt > 0
            try:
                or_request = self._build_or_request(request, model_id)
                t0 = time.monotonic()
                or_response = self._adapter.complete(or_request)
                latency_ms = (time.monotonic() - t0) * 1000

                # Feed latency back to the arbitration engine
                self._engine.record_latency(model_id, latency_ms)

                return self._build_route_response(
                    request,
                    or_response,
                    model_id,
                    fallback_used=is_fallback or fallback_used,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                fallback_used = True
                continue

        raise RuntimeError(
            f"All providers failed for task_type={request.task_type!r}. "
            f"Last error: {last_error}"
        )

    def select_provider(self, task_type: str) -> ProviderSpec | None:
        """Return the top-ranked provider for *task_type* without executing."""
        return self._engine.select(task_type)

    def fallback_chain(self, task_type: str) -> list[str]:
        """Return the ordered fallback chain for *task_type*."""
        return self._engine.fallback_chain(task_type)

    def register_provider(self, spec: ProviderSpec) -> None:
        """Register or replace a provider spec in the arbitration engine."""
        self._engine.register(spec)

    @property
    def stub_mode(self) -> bool:
        """``True`` when the adapter has no live API key."""
        return self._adapter.stub_mode

    def get_summary(self) -> dict[str, Any]:
        """Return a diagnostic summary of the router."""
        return {
            "stub_mode": self.stub_mode,
            "providers": len(self._engine.list_providers()),
            "max_fallback_attempts": self._max_fallbacks,
            "arbitration_policy": self._engine._policy.value,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_or_request(
        self, req: RouteRequest, model_id: str
    ) -> OpenRouterRequest:
        messages: list[dict[str, str]] = []
        if req.system_prompt:
            messages.append({"role": "system", "content": req.system_prompt})
        messages.append({"role": "user", "content": req.prompt})
        return OpenRouterRequest(
            model=model_id,
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            metadata=dict(req.metadata),
        )

    @staticmethod
    def _build_route_response(
        req: RouteRequest,
        resp: OpenRouterResponse,
        model_id: str,
        *,
        fallback_used: bool,
    ) -> RouteResponse:
        return RouteResponse(
            model_id=model_id,
            content=resp.content,
            task_type=req.task_type,
            finish_reason=resp.finish_reason,
            prompt_tokens=resp.prompt_tokens,
            completion_tokens=resp.completion_tokens,
            total_tokens=resp.total_tokens,
            cost_usd=resp.cost_usd,
            latency_ms=resp.latency_ms,
            fallback_used=fallback_used,
            stub=resp.stub,
        )
