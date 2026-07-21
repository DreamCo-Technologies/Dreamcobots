"""
DreamCo BaseEventBus — In-memory pub/sub for testing / offline environments.

Provides the same interface as RedisEventBus so code can switch between
implementations without change.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Dict, List


class BaseEventBus(ABC):
    """
    Abstract base event bus.

    Concrete subclasses must implement ``publish`` and ``subscribe``.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Pub/Sub API (abstract)
    # ------------------------------------------------------------------

    @abstractmethod
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish *data* to every subscriber registered for *event_type*."""
        ...

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be called when *event_type* is published."""
        ...

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
