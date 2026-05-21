"""
DreamCo Platform — Event Bus Emitter
=====================================

The ``EventBus`` is the central nervous system of the DreamCo platform.

CORE RULE:
    No direct bot-to-bot or workflow-to-workflow communication is allowed.
    All cross-system communication MUST go through the event bus:

        Bot → EventBus → subscribers → Analytics/Learning/Orchestrator

Architecture
------------
* In-process pub/sub with typed handlers.
* Supports synchronous and deferred (callback) handler modes.
* Each emission is appended to a bounded in-memory event log for replay/debug.
* A ``DreamCoEvent`` is validated against the canonical schema before dispatch.
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from typing import Any, Callable, Deque

from dreamco_platform.events.schema import DreamCoEvent, make_event, EventFamily
from dreamco_platform.events.validator import EventValidator


# ---------------------------------------------------------------------------
# Handler type alias
# ---------------------------------------------------------------------------

Handler = Callable[[DreamCoEvent], None]


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------

class EventBus:
    """Thread-safe in-process event bus.

    Usage::

        bus = EventBus()
        bus.subscribe("workflow.*", my_handler)
        bus.emit(make_event(EventFamily.WORKFLOW, "started", "my_bot"))
    """

    def __init__(self, max_log_size: int = 10_000) -> None:
        self._lock = threading.Lock()
        # Exact-type handlers and wildcard (family.*) handlers
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        # Rolling event log (bounded FIFO)
        self._log: Deque[DreamCoEvent] = deque(maxlen=max_log_size)
        self._emit_count: int = 0
        self._error_count: int = 0

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Register *handler* for *event_type*.

        *event_type* may be an exact type string (``"workflow.started"``) or a
        wildcard family pattern (``"workflow.*"``).
        """
        with self._lock:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> bool:
        """Remove *handler* from *event_type*.  Returns True if found."""
        with self._lock:
            handlers = self._handlers.get(event_type, [])
            try:
                handlers.remove(handler)
                return True
            except ValueError:
                return False

    def subscriber_count(self, event_type: str) -> int:
        with self._lock:
            return len(self._handlers.get(event_type, []))

    # ------------------------------------------------------------------
    # Emission
    # ------------------------------------------------------------------

    def emit(self, event: DreamCoEvent) -> int:
        """Publish *event* to all matching subscribers.

        Returns the number of handlers that were called.
        """
        EventValidator.validate(event)

        # Collect matching handlers under the lock to avoid holding it during
        # handler execution (which could cause deadlocks).
        family_wildcard = event.event_type.split(".")[0] + ".*"
        with self._lock:
            exact = list(self._handlers.get(event.event_type, []))
            wildcard = list(self._handlers.get(family_wildcard, []))
            global_wildcard = list(self._handlers.get("*", []))
            self._log.append(event)
            self._emit_count += 1

        handlers = exact + wildcard + global_wildcard
        dispatched = 0
        for handler in handlers:
            try:
                handler(event)
                dispatched += 1
            except Exception:  # noqa: BLE001
                with self._lock:
                    self._error_count += 1

        return dispatched

    def emit_raw(
        self,
        family: EventFamily,
        action: str,
        source_id: str,
        payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> int:
        """Convenience wrapper: build a ``DreamCoEvent`` and emit it."""
        event = make_event(family, action, source_id, payload=payload or {}, **kwargs)
        return self.emit(event)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def recent_events(self, n: int = 100) -> list[DreamCoEvent]:
        """Return the last *n* events from the rolling log."""
        with self._lock:
            log = list(self._log)
        return log[-n:]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "emit_count": self._emit_count,
                "error_count": self._error_count,
                "log_size": len(self._log),
                "subscriber_keys": list(self._handlers.keys()),
            }

    def clear_log(self) -> None:
        with self._lock:
            self._log.clear()


# ---------------------------------------------------------------------------
# Module-level singleton bus (optional convenience)
# ---------------------------------------------------------------------------

_default_bus: EventBus | None = None
_bus_lock = threading.Lock()


def get_default_bus() -> EventBus:
    """Return (and lazily create) the module-level default ``EventBus``."""
    global _default_bus
    with _bus_lock:
        if _default_bus is None:
            _default_bus = EventBus()
    return _default_bus


def reset_default_bus() -> None:
    """Replace the default bus with a fresh instance (useful in tests)."""
    global _default_bus
    with _bus_lock:
        _default_bus = EventBus()
