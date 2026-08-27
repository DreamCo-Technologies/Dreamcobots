"""Lifecycle state tracking for Buddy-managed objects and workflows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


DEFAULT_STATES = (
    "discovered", "observed", "understood", "planned", "simulated", "verified",
    "authorized", "executing", "completed", "measured", "learned",
)


@dataclass(frozen=True)
class StateEvent:
    object_id: str
    previous: str
    current: str
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StateEngine:
    def __init__(self, allowed_states=DEFAULT_STATES) -> None:
        self.allowed_states = tuple(allowed_states)
        self._state: Dict[str, str] = {}
        self._history: Dict[str, List[StateEvent]] = {}

    def set_state(self, object_id: str, state: str, reason: str = "") -> StateEvent:
        if state not in self.allowed_states:
            raise ValueError(f"unsupported state: {state}")
        previous = self._state.get(object_id, state)
        event = StateEvent(object_id, previous, state, reason)
        self._state[object_id] = state
        self._history.setdefault(object_id, []).append(event)
        return event

    def get_state(self, object_id: str) -> str | None:
        return self._state.get(object_id)

    def history(self, object_id: str) -> List[StateEvent]:
        return list(self._history.get(object_id, ()))

    def snapshot(self) -> Dict[str, str]:
        return dict(self._state)
