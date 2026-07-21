"""
Kill Switch — Emergency stop for all DreamCobots systems.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


# GLOBAL AI SOURCES FLOW

@dataclass
class KillSwitchEvent:
    event_id: str
    action: str         # "activate" | "deactivate"
    reason: str
    timestamp: datetime


class KillSwitch:
    """Global emergency stop for all registered bots and services."""

    def __init__(self) -> None:
        self._active: bool = False
        self._log: List[KillSwitchEvent] = []
        self._registered_bots: Dict[str, Callable] = {}   # bot_id -> stop_callback
        self._notifications: List[str] = []

    # ------------------------------------------------------------------
    # Core control
    # ------------------------------------------------------------------

    def activate(self, reason: str = "") -> KillSwitchEvent:
        """Activate the kill switch — stops all bots and logs the event."""
        self._active = True
        event = KillSwitchEvent(
            event_id=str(uuid.uuid4()),
            action="activate",
            reason=reason or "Manual activation.",
            timestamp=datetime.utcnow(),
        )
        self._log.append(event)
        self.halt_all_bots()
        self._send_notifications(f"KILL SWITCH ACTIVATED: {reason}")
        return event

    def deactivate(self) -> KillSwitchEvent:
        """Deactivate the kill switch and restore normal operations."""
        self._active = False
        event = KillSwitchEvent(
            event_id=str(uuid.uuid4()),
            action="deactivate",
            reason="Manual deactivation — operations restored.",
            timestamp=datetime.utcnow(),
        )
        self._log.append(event)
        self._send_notifications("Kill switch deactivated. Operations restored.")
        return event

    @property
    def is_active(self) -> bool:
        """Return True if the kill switch is currently active."""
        return self._active

    def get_log(self) -> List[KillSwitchEvent]:
        """Return a copy of all activation events."""
        return list(self._log)

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str, stop_callback: Callable) -> None:
        """Register a bot with a callable that stops it."""
        self._registered_bots[bot_id] = stop_callback

    def unregister_bot(self, bot_id: str) -> None:
        """Unregister a previously registered bot."""
        self._registered_bots.pop(bot_id, None)

    def halt_all_bots(self) -> dict:
        """Invoke the stop callback on every registered bot."""
        results = {}
        for bot_id, callback in self._registered_bots.items():
            try:
                callback()
                results[bot_id] = "stopped"
            except Exception as exc:  # noqa: BLE001
                results[bot_id] = f"error: {exc}"
        return results

    def list_registered_bots(self) -> List[str]:
        """Return a list of registered bot IDs."""
        return list(self._registered_bots.keys())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _send_notifications(self, message: str) -> None:
        """Record a notification (mock implementation)."""
        entry = f"[{datetime.utcnow().isoformat()}] {message}"
        self._notifications.append(entry)

    def get_notifications(self) -> List[str]:
        """Return all notification messages sent."""
        return list(self._notifications)
