"""
DreamCo Platform — Arbitration Engine
======================================

``ArbitrationEngine`` implements **internal arbitration** between multiple
AI providers/models.  It wraps each call with:

* **Primary selection** — choose the best provider for the task type
* **Fallback chain** — on error, retry down the preference list
* **Cost guard** — skip providers whose estimated per-call cost exceeds a
  configurable cap
* **Latency circuit-breaker** — automatically deprioritise providers that
  have been slow in the rolling window
* **Audit record** — every arbitration decision is journalled so the
  Observability layer can ingest it

This sits between the WorkflowGraph/Agent Runtime and the actual provider
calls (OpenRouter or direct SDK).

Usage::

    engine = ArbitrationEngine()
    engine.register(ProviderSpec("openai/gpt-4o",  task_types=["general","coding"], priority=1))
    engine.register(ProviderSpec("anthropic/claude-3-5-sonnet", task_types=["coding"], priority=0))
    engine.register(ProviderSpec("mistral/mistral-small", task_types=["cheap"], priority=2))

    spec = engine.select("coding")   # → ProviderSpec for claude-3-5-sonnet
    fallbacks = engine.fallback_chain("coding")  # ordered list
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Arbitration policy
# ---------------------------------------------------------------------------

class ArbitrationPolicy(str, Enum):
    PRIORITY = "priority"         # Use provider with lowest priority number
    COST_FIRST = "cost_first"     # Use cheapest provider that covers the task
    LATENCY_FIRST = "latency_first"  # Use fastest (lowest avg latency) provider
    ROUND_ROBIN = "round_robin"   # Rotate across all eligible providers


# ---------------------------------------------------------------------------
# ProviderSpec
# ---------------------------------------------------------------------------

@dataclass
class ProviderSpec:
    """
    Metadata record for a single AI provider/model.

    Attributes
    ----------
    model_id : str
        Full model identifier, e.g. ``"openai/gpt-4o"`` or
        ``"anthropic/claude-3-5-sonnet"``.
    task_types : list[str]
        Task categories this provider covers
        (e.g. ``["coding", "general", "vision"]``).
    priority : int
        Arbitration priority; **lower = higher priority**.
    cost_per_1k_tokens_usd : float
        Approximate cost per 1 000 tokens (used by COST_FIRST policy and
        cost-guard logic).
    max_tokens : int
        Maximum context window this model supports.
    enabled : bool
        Whether this provider is available for routing.
    tags : list[str]
        Arbitrary labels (``"open_source"``, ``"vision"``, etc.).
    metadata : dict
        Arbitrary extra metadata.
    """

    model_id: str
    task_types: list[str] = field(default_factory=list)
    priority: int = 10
    cost_per_1k_tokens_usd: float = 0.002
    max_tokens: int = 4096
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def covers(self, task_type: str) -> bool:
        """Return ``True`` if this provider covers *task_type*."""
        return task_type in self.task_types or "*" in self.task_types

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "task_types": list(self.task_types),
            "priority": self.priority,
            "cost_per_1k_tokens_usd": self.cost_per_1k_tokens_usd,
            "max_tokens": self.max_tokens,
            "enabled": self.enabled,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# Arbitration decision record (audit)
# ---------------------------------------------------------------------------

@dataclass
class ArbitrationDecision:
    """Audit record for a single arbitration selection."""

    task_type: str
    selected_model: str
    policy: ArbitrationPolicy
    candidates_considered: int
    fallback_chain: list[str]
    reasoning: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "selected_model": self.selected_model,
            "policy": self.policy.value,
            "candidates_considered": self.candidates_considered,
            "fallback_chain": self.fallback_chain,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# ArbitrationEngine
# ---------------------------------------------------------------------------

# Built-in provider catalogue (OpenRouter model IDs)
DEFAULT_PROVIDERS: list[ProviderSpec] = [
    ProviderSpec(
        "anthropic/claude-3-5-sonnet",
        task_types=["coding", "reasoning", "general"],
        priority=1,
        cost_per_1k_tokens_usd=0.003,
        max_tokens=200_000,
        tags=["high_quality"],
    ),
    ProviderSpec(
        "openai/gpt-4o",
        task_types=["general", "coding", "vision", "multimodal"],
        priority=2,
        cost_per_1k_tokens_usd=0.005,
        max_tokens=128_000,
        tags=["multimodal"],
    ),
    ProviderSpec(
        "google/gemini-1.5-pro",
        task_types=["vision", "multimodal", "research", "general"],
        priority=3,
        cost_per_1k_tokens_usd=0.003,
        max_tokens=1_000_000,
        tags=["long_context", "multimodal"],
    ),
    ProviderSpec(
        "mistral/mistral-small",
        task_types=["cheap", "general", "coding"],
        priority=4,
        cost_per_1k_tokens_usd=0.0002,
        max_tokens=32_000,
        tags=["open_source", "cost_effective"],
    ),
    ProviderSpec(
        "cohere/command-r-plus",
        task_types=["search", "rag", "retrieval", "general"],
        priority=5,
        cost_per_1k_tokens_usd=0.003,
        max_tokens=128_000,
        tags=["enterprise_search"],
    ),
    ProviderSpec(
        "x-ai/grok-beta",
        task_types=["real_time", "social", "general"],
        priority=6,
        cost_per_1k_tokens_usd=0.005,
        max_tokens=131_072,
        tags=["real_time"],
    ),
    ProviderSpec(
        "meta-llama/llama-3.1-8b-instruct",
        task_types=["cheap", "general"],
        priority=10,
        cost_per_1k_tokens_usd=0.00006,
        max_tokens=128_000,
        tags=["open_source", "free_tier"],
    ),
]


class ArbitrationEngine:
    """
    Selects the best AI provider for a given task with fallback support.

    Parameters
    ----------
    policy : ArbitrationPolicy
        Default selection policy.  Can be overridden per ``select()`` call.
    max_cost_per_call_usd : float | None
        When set, providers whose estimated cost per call exceeds this limit
        are excluded.  Estimate = ``cost_per_1k_tokens * max_tokens / 1000``.
    load_defaults : bool
        Pre-register the built-in ``DEFAULT_PROVIDERS`` catalogue.
    """

    def __init__(
        self,
        policy: ArbitrationPolicy = ArbitrationPolicy.PRIORITY,
        max_cost_per_call_usd: float | None = None,
        load_defaults: bool = True,
    ) -> None:
        self._policy = policy
        self._max_cost = max_cost_per_call_usd
        self._lock = threading.Lock()
        self._providers: dict[str, ProviderSpec] = {}
        self._latency_window: dict[str, list[float]] = {}  # model_id → recent latencies
        self._rr_index: int = 0
        self._audit: list[ArbitrationDecision] = []

        if load_defaults:
            for spec in DEFAULT_PROVIDERS:
                self.register(spec)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, spec: ProviderSpec) -> None:
        """Register or replace a provider spec."""
        with self._lock:
            self._providers[spec.model_id] = spec

    def unregister(self, model_id: str) -> ProviderSpec | None:
        with self._lock:
            return self._providers.pop(model_id, None)

    def get(self, model_id: str) -> ProviderSpec | None:
        with self._lock:
            return self._providers.get(model_id)

    def list_providers(self, enabled_only: bool = True) -> list[ProviderSpec]:
        with self._lock:
            specs = list(self._providers.values())
        if enabled_only:
            specs = [s for s in specs if s.enabled]
        return sorted(specs, key=lambda s: s.priority)

    # ------------------------------------------------------------------
    # Latency feedback
    # ------------------------------------------------------------------

    def record_latency(self, model_id: str, latency_ms: float) -> None:
        """Feed observed latency back so LATENCY_FIRST policy can use it."""
        with self._lock:
            window = self._latency_window.setdefault(model_id, [])
            window.append(latency_ms)
            if len(window) > 20:
                window.pop(0)

    def avg_latency_ms(self, model_id: str) -> float:
        with self._lock:
            window = self._latency_window.get(model_id, [])
        return sum(window) / len(window) if window else float("inf")

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select(
        self,
        task_type: str,
        policy: ArbitrationPolicy | None = None,
    ) -> ProviderSpec | None:
        """
        Return the best available provider for *task_type*.

        Parameters
        ----------
        task_type : str
            Task category (e.g. ``"coding"``).
        policy : ArbitrationPolicy | None
            Override the instance-level policy for this call.

        Returns
        -------
        ProviderSpec | None
            The selected provider, or ``None`` if no eligible provider exists.
        """
        pol = policy or self._policy
        chain = self.fallback_chain(task_type, policy=pol)
        if not chain:
            return None
        selected = chain[0]
        with self._lock:
            spec = self._providers.get(selected)

        decision = ArbitrationDecision(
            task_type=task_type,
            selected_model=selected,
            policy=pol,
            candidates_considered=len(chain),
            fallback_chain=list(chain),
            reasoning=f"policy={pol.value}, eligible={len(chain)}",
        )
        with self._lock:
            self._audit.append(decision)

        return spec

    def fallback_chain(
        self,
        task_type: str,
        policy: ArbitrationPolicy | None = None,
    ) -> list[str]:
        """
        Return an ordered list of model IDs for *task_type*.

        The list is ordered by the active policy so callers can try them in
        sequence, falling back to the next on error.
        """
        pol = policy or self._policy
        candidates = [
            s for s in self.list_providers(enabled_only=True)
            if s.covers(task_type) and not self._exceeds_cost_guard(s)
        ]

        if pol == ArbitrationPolicy.PRIORITY:
            candidates.sort(key=lambda s: s.priority)
        elif pol == ArbitrationPolicy.COST_FIRST:
            candidates.sort(key=lambda s: s.cost_per_1k_tokens_usd)
        elif pol == ArbitrationPolicy.LATENCY_FIRST:
            candidates.sort(key=lambda s: self.avg_latency_ms(s.model_id))
        elif pol == ArbitrationPolicy.ROUND_ROBIN:
            with self._lock:
                offset = self._rr_index % max(len(candidates), 1)
                self._rr_index += 1
            candidates = candidates[offset:] + candidates[:offset]

        return [s.model_id for s in candidates]

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_log(self, limit: int | None = None) -> list[ArbitrationDecision]:
        with self._lock:
            log = list(self._audit)
        if limit is not None:
            log = log[-limit:]
        return log

    def clear_audit(self) -> None:
        with self._lock:
            self._audit.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _exceeds_cost_guard(self, spec: ProviderSpec) -> bool:
        if self._max_cost is None:
            return False
        estimate = spec.cost_per_1k_tokens_usd * spec.max_tokens / 1000
        return estimate > self._max_cost

    def __repr__(self) -> str:
        return (
            f"ArbitrationEngine(providers={len(self._providers)}, "
            f"policy={self._policy.value!r})"
        )
