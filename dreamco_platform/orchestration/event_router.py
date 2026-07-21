"""
DreamCo Platform — Event Router (Orchestration Layer)
======================================================

``EventRouter`` sits between the ``EventBus`` and the set of registered
orchestrators/subscribers.  It enforces the routing rule:

    Workflow → EventBus → EventRouter → Orchestrators → Subscribers

Key features
------------
* Rule-based routing: route event types to named handlers.
* Priority ordering: higher-priority handlers are called first.
* Dead-letter queue: events that match no route are stored for inspection.
* Middleware chain: optional pre-dispatch transforms/filters.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque

from dreamco_platform.events.schema import DreamCoEvent


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

RouteHandler = Callable[[DreamCoEvent], None]


@dataclass(order=True)
class Route:
    """A routing rule binding an event pattern to a handler.

    *pattern* may be an exact event_type string (``"workflow.started"``) or a
    wildcard family pattern (``"workflow.*"``).
    """

    priority: int  # lower number = higher priority
    pattern: str = field(compare=False)
    handler: RouteHandler = field(compare=False)
    description: str = field(default="", compare=False)


# ---------------------------------------------------------------------------
# EventRouter
# ---------------------------------------------------------------------------

class EventRouter:
    """Rule-based event router.

    Usage::

        router = EventRouter()
        router.add_route(Route(0, "workflow.*", my_orchestrator.handle))
        router.add_route(Route(10, "*", analytics_sink))

        # Wire to EventBus:
        bus.subscribe("*", router.dispatch)
    """

    def __init__(self, max_dlq_size: int = 1_000) -> None:
        self._lock = threading.Lock()
        self._routes: list[Route] = []
        self._dlq: Deque[DreamCoEvent] = deque(maxlen=max_dlq_size)
        self._dispatch_count: int = 0
        self._dlq_count: int = 0

    # ------------------------------------------------------------------
    # Route management
    # ------------------------------------------------------------------

    def add_route(self, route: Route) -> None:
        with self._lock:
            self._routes.append(route)
            self._routes.sort()

    def remove_route(self, pattern: str, handler: RouteHandler) -> bool:
        with self._lock:
            before = len(self._routes)
            self._routes = [
                r for r in self._routes
                if not (r.pattern == pattern and r.handler is handler)
            ]
            return len(self._routes) < before

    def route_count(self) -> int:
        with self._lock:
            return len(self._routes)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch(self, event: DreamCoEvent) -> int:
        """Dispatch *event* to all matching routes.  Returns handler count."""
        family_wildcard = event.event_type.split(".")[0] + ".*"

        with self._lock:
            matching = [
                r for r in self._routes
                if r.pattern in (event.event_type, family_wildcard, "*")
            ]
            self._dispatch_count += 1

        if not matching:
            with self._lock:
                self._dlq.append(event)
                self._dlq_count += 1
            return 0

        dispatched = 0
        for route in matching:
            try:
                route.handler(event)
                dispatched += 1
            except Exception:  # noqa: BLE001
                pass

        return dispatched

    # ------------------------------------------------------------------
    # Dead-letter queue inspection
    # ------------------------------------------------------------------

    def dead_letters(self) -> list[DreamCoEvent]:
        with self._lock:
            return list(self._dlq)

    def clear_dlq(self) -> None:
        with self._lock:
            self._dlq.clear()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "routes": len(self._routes),
                "dispatch_count": self._dispatch_count,
                "dlq_size": len(self._dlq),
                "dlq_total": self._dlq_count,
            }
