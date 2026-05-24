"""
DreamCo BaseEventBus — In-memory pub/sub for testing / offline environments.

Provides the same interface as RedisEventBus so code can switch between
implementations without change.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, List


class BaseEventBus:
    """
    In-memory base event bus with publish/subscribe behavior.

    Concrete subclasses can override methods (e.g., to add Redis transport),
    while this class remains directly usable in offline/test contexts.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Pub/Sub API
    # ------------------------------------------------------------------

    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish *data* to every subscriber registered for *event_type*."""
        entry = {"event_type": event_type, "data": data}
        self._event_log.append(entry)
        for handler in list(self._subscribers.get(event_type, [])):
            handler(data)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be called when *event_type* is published."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove *handler* from *event_type* subscriptions."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h is not handler
            ]

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_events(self, event_type: str = None) -> List:
        """Return published events, optionally filtered by event_type."""
        if event_type is not None:
            return [e["data"] for e in self._event_log if e["event_type"] == event_type]
        return list(self._event_log)

    def clear(self) -> None:
        """Clear subscriber list and event log."""
        self._subscribers.clear()
        self._event_log.clear()

    def subscriber_count(self, event_type: str) -> int:
        """Return the number of subscribers for *event_type*."""
        return len(self._subscribers.get(event_type, []))
