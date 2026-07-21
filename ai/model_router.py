"""
DreamCo Model Router — AI Brain Switchboard.

Routes tasks to the optimal AI model/provider based on task type.
This is the core routing engine used across all DreamCo bots.

Routing map
-----------
  coding     → anthropic  (Claude — top-tier coding + long context)
  general    → openai     (GPT — best overall balance)
  vision     → google     (Gemini — best multimodal)
  cheap      → mistral    (Mistral/LLaMA — fast + cost-effective)
  search     → cohere     (Cohere — enterprise search + RAG)
  real_time  → xai        (Grok — real-time data + social)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------

DEFAULT_ROUTES: dict[str, str] = {
    "coding":    "anthropic",
    "general":   "openai",
    "vision":    "google",
    "cheap":     "mistral",
    "search":    "cohere",
    "real_time": "xai",
}

# Human-readable descriptions for each provider
PROVIDER_INFO: dict[str, dict] = {
    "anthropic": {
        "strengths": ["coding", "long_context", "reasoning", "safety"],
        "best_for": "Coding agents, system builders, compliance",
    },
    "openai": {
        "strengths": ["reasoning", "coding", "multimodal", "ecosystem"],
        "best_for": "General systems, orchestration, agents",
    },
    "google": {
        "strengths": ["multimodal", "video", "audio", "large_context", "research"],
        "best_for": "Vision agents, data-heavy systems, research",
    },
    "mistral": {
        "strengths": ["speed", "efficiency", "open_weight", "cost"],
        "best_for": "High-speed automation, cheap agents",
    },
    "cohere": {
        "strengths": ["enterprise_search", "rag", "multilingual"],
        "best_for": "Knowledge base agents",
    },
    "xai": {
        "strengths": ["real_time_data", "social", "live_info"],
        "best_for": "Trend detection, real-time bots",
    },
    "meta": {
        "strengths": ["open_source", "customizable", "cost"],
        "best_for": "Self-hosted scale, DreamCo bots at scale",
    },
}


# ---------------------------------------------------------------------------
# ModelRouter
# ---------------------------------------------------------------------------

class ModelRouter:
    """Routes tasks to the best AI model/provider.

    Parameters
    ----------
    routes : dict[str, str] | None
        Custom task-type → provider mapping.  Defaults to ``DEFAULT_ROUTES``.
    default_provider : str
        Fallback provider when a task type has no explicit route.
    """

    def __init__(
        self,
        routes: dict[str, str] | None = None,
        default_provider: str = "openai",
    ) -> None:
        self.routes: dict[str, str] = routes if routes is not None else dict(DEFAULT_ROUTES)
        self.default_provider: str = default_provider

    # ------------------------------------------------------------------
    # Core routing
    # ------------------------------------------------------------------

    def route(self, task_type: str) -> str:
        """Return the provider name for *task_type*.

        Parameters
        ----------
        task_type : str
            One of the recognised task-type keys (e.g. ``"coding"``).

        Returns
        -------
        str
            Provider identifier (e.g. ``"anthropic"``).
        """
        return self.routes.get(task_type, self.default_provider)

    def execute(self, task_type: str, prompt: str) -> dict:
        """Route *prompt* to the best model and return a simulated response.

        In production this method delegates to real provider API clients.
        The stub response here lets the system function end-to-end without
        live API keys.

        Parameters
        ----------
        task_type : str
            Classified task type.
        prompt : str
            The raw task or prompt string.

        Returns
        -------
        dict
            ``{"model": str, "task_type": str, "response": str}``
        """
        provider = self.route(task_type)
        return {
            "model": provider,
            "task_type": task_type,
            "response": f"[{provider.upper()}] Processed: {prompt}",
        }

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def list_routes(self) -> dict[str, str]:
        """Return a copy of the current routing table."""
        return dict(self.routes)

    def get_provider_info(self, provider: str) -> dict:
        """Return capability metadata for *provider*.

        Parameters
        ----------
        provider : str
            Provider identifier.

        Returns
        -------
        dict
            Info dict with 'strengths' and 'best_for' keys, or ``{}`` if
            unknown.
        """
        return PROVIDER_INFO.get(provider, {})

    def add_route(self, task_type: str, provider: str) -> None:
        """Register a new or override an existing task-type route.

        Parameters
        ----------
        task_type : str
            Task type key.
        provider : str
            Provider identifier to route to.
        """
        self.routes[task_type] = provider

    def get_summary(self) -> dict:
        """Return a summary of the router's configuration."""
        return {
            "total_routes": len(self.routes),
            "routes": self.list_routes(),
            "default_provider": self.default_provider,
            "supported_providers": list(PROVIDER_INFO.keys()),
        }
