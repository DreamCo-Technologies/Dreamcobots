from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


EventListener = Callable[[dict[str, Any]], None]


@dataclass(slots=True)
class DashboardEventBridge:
    listeners: dict[str, list[EventListener]] = field(default_factory=dict)
    event_history: list[dict[str, Any]] = field(default_factory=list)

    def register_listener(self, topic: str, listener: EventListener) -> None:
        key = topic.strip().lower() or "default"
        self.listeners.setdefault(key, []).append(listener)

    def publish(self, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        key = topic.strip().lower() or "default"
        event = {
            "topic": key,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.event_history.append(event)
        for listener in self.listeners.get(key, []):
            listener(event)
        for listener in self.listeners.get("*", []):
            listener(event)
        return event

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        return self.event_history[-limit:]
