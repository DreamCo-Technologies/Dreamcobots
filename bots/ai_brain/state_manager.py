"""
State Manager — provides persistent memory for DreamCo bots, storing and
loading system state (revenue, leads, bot count, decisions) to/from
data/system_state.json.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Default state path
# ---------------------------------------------------------------------------

_DEFAULT_STATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "system_state.json"
)


# ---------------------------------------------------------------------------
# Module-level helpers (as described in problem statement)
# ---------------------------------------------------------------------------

def save_state(data: dict, path: str = _DEFAULT_STATE_PATH) -> None:
    """
    Persist system state to a JSON file.

    Parameters
    ----------
    data : dict
        State data to save.
    path : str
        File path for the state file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_state(path: str = _DEFAULT_STATE_PATH) -> dict:
    """
    Load persisted system state from a JSON file.

    Returns an empty dict if the file does not exist or cannot be parsed.

    Parameters
    ----------
    path : str
        File path for the state file.
    """
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# StateManager class
# ---------------------------------------------------------------------------

class StateManager:
    """
    Manages persistent state for the DreamCo system across runs.

    Tracks: total_revenue, total_leads, bot_count, decisions, and
    any other key/value pairs via the generic state dict.

    Parameters
    ----------
    state_path : str, optional
        Path to the JSON state file. Defaults to data/system_state.json.
    auto_load : bool
        If True, load existing state on construction.
    """

    def __init__(
        self,
        state_path: Optional[str] = None,
        auto_load: bool = True,
    ) -> None:
        self._path = state_path or _DEFAULT_STATE_PATH
        self._state: dict[str, Any] = {
            "total_revenue": 0.0,
            "total_leads": 0,
            "bot_count": 0,
            "decisions": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if auto_load:
            loaded = load_state(self._path)
            if loaded:
                self._state.update(loaded)

    # ------------------------------------------------------------------
    # Generic get/set
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value by key."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a state value and persist."""
        self._state[key] = value
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._persist()

    def update(self, data: dict) -> None:
        """Update multiple keys and persist."""
        self._state.update(data)
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._persist()

    # ------------------------------------------------------------------
    # Domain-specific helpers
    # ------------------------------------------------------------------

    def add_revenue(self, amount: float) -> float:
        """Add revenue and return the new total."""
        current = float(self._state.get("total_revenue", 0.0))
        new_total = round(current + amount, 2)
        self.set("total_revenue", new_total)
        return new_total

    def add_leads(self, count: int) -> int:
        """Add leads and return the new total."""
        current = int(self._state.get("total_leads", 0))
        new_total = current + count
        self.set("total_leads", new_total)
        return new_total

    def increment_bot_count(self) -> int:
        """Increment bot count and return the new total."""
        current = int(self._state.get("bot_count", 0))
        new_total = current + 1
        self.set("bot_count", new_total)
        return new_total

    def record_decision(self, decision: str) -> None:
        """Append a decision to the decisions log."""
        decisions: list = list(self._state.get("decisions", []))
        decisions.append({
            "decision": decision,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._state["decisions"] = decisions
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._persist()

    # ------------------------------------------------------------------
    # State I/O
    # ------------------------------------------------------------------

    def load(self) -> dict:
        """Reload state from disk."""
        self._state = load_state(self._path)
        return dict(self._state)

    def save(self) -> None:
        """Persist current state to disk."""
        self._persist()

    def reset(self) -> None:
        """Reset state to defaults (does not delete file)."""
        self._state = {
            "total_revenue": 0.0,
            "total_leads": 0,
            "bot_count": 0,
            "decisions": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._persist()

    def get_full_state(self) -> dict:
        """Return a copy of the full state dict."""
        return dict(self._state)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        save_state(self._state, self._path)
