"""
DreamCo Router Agent — Combines TaskClassifier and ModelRouter.

RouterAgent is the plug-in component for all DreamCo bots.  It receives a
raw task string, classifies it, routes it to the best provider, and returns
a structured result.

Usage
-----
    from ai.router_agent import RouterAgent

    agent = RouterAgent()
    result = agent.run("build a lead generation system")
    print(result)
    # {"task": "...", "task_type": "coding", "model": "anthropic", "response": "..."}

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401
from ai.model_router import ModelRouter
from ai.task_classifier import TaskClassifier


# ---------------------------------------------------------------------------
# RouterAgent
# ---------------------------------------------------------------------------

class RouterAgent:
    """Plug-in AI routing agent for DreamCo bots.

    Combines :class:`TaskClassifier` and :class:`ModelRouter` into a single
    ``run()`` interface.

    Parameters
    ----------
    router : ModelRouter | None
        Custom router instance.  Defaults to a fresh :class:`ModelRouter`.
    classifier : TaskClassifier | None
        Custom classifier instance.  Defaults to a fresh :class:`TaskClassifier`.
    """

    def __init__(
        self,
        router: ModelRouter | None = None,
        classifier: TaskClassifier | None = None,
    ) -> None:
        self.router: ModelRouter = router if router is not None else ModelRouter()
        self.classifier: TaskClassifier = (
            classifier if classifier is not None else TaskClassifier()
        )

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    def run(self, task: str) -> dict:
        """Classify *task* and route it to the best AI provider.

        Parameters
        ----------
        task : str
            Raw task or prompt text.

        Returns
        -------
        dict
            ``{"task": str, "task_type": str, "model": str, "response": str}``
        """
        task_type = self.classifier.classify(task)
        result = self.router.execute(task_type, task)
        return {
            "task": task,
            "task_type": task_type,
            "model": result["model"],
            "response": result["response"],
        }

    def explain(self, task: str) -> dict:
        """Return a full diagnostic breakdown for *task*.

        Includes the classification explanation and routing decision.

        Parameters
        ----------
        task : str
            Raw task or prompt text.

        Returns
        -------
        dict
            Extended result with classification and routing metadata.
        """
        classification = self.classifier.explain(task)
        task_type = classification["task_type"]
        provider = self.router.route(task_type)
        provider_info = self.router.get_provider_info(provider)
        return {
            "task": task,
            "task_type": task_type,
            "matched_keyword": classification.get("matched_keyword"),
            "model": provider,
            "provider_best_for": provider_info.get("best_for", ""),
            "provider_strengths": provider_info.get("strengths", []),
        }

    def get_summary(self) -> dict:
        """Return router and classifier configuration summary."""
        return {
            "router": self.router.get_summary(),
            "classifier_task_types": self.classifier.list_task_types(),
        }
