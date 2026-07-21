"""
DreamCo Task Classifier — Maps raw task text to a task-type key.

The classifier examines the task description and returns a standardised
task-type string consumed by ModelRouter to select the optimal provider.

Task types
----------
  coding    — build, code, debug, fix, develop, script, function, class
  vision    — image, vision, photo, video, scan, ocr, visual, pixel
  cheap     — cheap, low-cost, fast, lite, quick
  search    — search, find, data, database, retrieve, rag, knowledge, fetch
  real_time — live, trend, real-time, breaking, news, social, feed, current
  general   — everything else (default)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Keyword maps
# ---------------------------------------------------------------------------

_TASK_KEYWORDS: dict[str, list[str]] = {
    "coding": [
        "code", "build", "debug", "fix", "develop", "script",
        "function", "class", "implement", "refactor", "api",
        "program", "software", "bug", "error",
    ],
    "vision": [
        "image", "vision", "photo", "video", "picture",
        "ocr", "scan", "visual", "camera", "frame", "pixel",
        "screenshot", "recognition",
    ],
    "cheap": [
        "cheap", "budget", "lite", "lightweight", "efficient", "affordable",
    ],
    "search": [
        "search", "find", "lookup", "data", "database",
        "retrieve", "query", "index", "rag", "knowledge", "fetch",
        "document",
    ],
    "real_time": [
        "live", "trend", "breaking", "news",
        "social", "feed", "stream", "latest", "current",
    ],
}

# Priority order — first match wins
_PRIORITY: list[str] = ["coding", "vision", "real_time", "search", "cheap"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _keyword_matches(keyword: str, text: str) -> bool:
    """Return True if *keyword* appears as a whole word in *text*.

    Uses ``\\b`` word-boundary anchors so that short keywords (e.g. ``"rag"``)
    do not false-match inside longer words (e.g. ``"paragraph"``).
    Hyphenated keywords such as ``"real-time"`` are also supported.
    """
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return bool(re.search(pattern, text))


# ---------------------------------------------------------------------------
# TaskClassifier
# ---------------------------------------------------------------------------

class TaskClassifier:
    """Classifies a free-text task description into a task-type key.

    Parameters
    ----------
    keywords : dict[str, list[str]] | None
        Custom keyword map.  Defaults to the built-in ``_TASK_KEYWORDS`` map.
    priority : list[str] | None
        Evaluation order.  Defaults to ``_PRIORITY``.
    default_task_type : str
        Task type returned when no keyword matches (default: ``"general"``).
    """

    def __init__(
        self,
        keywords: dict[str, list[str]] | None = None,
        priority: list[str] | None = None,
        default_task_type: str = "general",
    ) -> None:
        self.keywords: dict[str, list[str]] = (
            keywords if keywords is not None else {k: list(v) for k, v in _TASK_KEYWORDS.items()}
        )
        self.priority: list[str] = priority if priority is not None else list(_PRIORITY)
        self.default_task_type: str = default_task_type

    # ------------------------------------------------------------------
    # Core classification
    # ------------------------------------------------------------------

    def classify(self, task: str) -> str:
        """Return the task-type key for *task*.

        Parameters
        ----------
        task : str
            Raw task or prompt text.

        Returns
        -------
        str
            Task-type key (e.g. ``"coding"``).
        """
        normalised = task.lower()
        for task_type in self.priority:
            for kw in self.keywords.get(task_type, []):
                if _keyword_matches(kw, normalised):
                    return task_type
        return self.default_task_type

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def explain(self, task: str) -> dict:
        """Return classification result with matched keyword detail.

        Parameters
        ----------
        task : str
            Raw task or prompt text.

        Returns
        -------
        dict
            ``{"task_type": str, "matched_keyword": str | None, "task": str}``
        """
        normalised = task.lower()
        for task_type in self.priority:
            for kw in self.keywords.get(task_type, []):
                if _keyword_matches(kw, normalised):
                    return {
                        "task_type": task_type,
                        "matched_keyword": kw,
                        "task": task,
                    }
        return {
            "task_type": self.default_task_type,
            "matched_keyword": None,
            "task": task,
        }

    def list_task_types(self) -> list[str]:
        """Return all supported task-type keys."""
        return self.priority + [self.default_task_type]
