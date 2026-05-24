"""
DreamCo OS — Behavioral Memory (Event Graph)
=============================================

Tracks agent decisions as a directed graph of events over time.
Provides decision-chain analysis, workflow replay, and behavioral
pattern recognition.

Usage::

    mem = BehavioralMemory(bot_id="sales_bot")
    mem.record_event("task_started", {"task": "lead_scrape", "priority": "high"})
    mem.record_event("tool_called", {"tool": "web_search", "query": "ACME Corp"})
    mem.record_event("task_completed", {"result": "found 12 leads"})

    history = mem.get_history(limit=10)
    graph = mem.to_task_graph()
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

_BEHAVIORAL_TTL_DAYS = 90  # events older than this are eligible for pruning


@dataclass
class BehavioralEvent:
    """A single recorded agent decision or action."""

    event_id: str
    bot_id: str
    event_type: str
    payload: dict[str, Any]
    timestamp: float
    parent_id: str | None = None  # links to the preceding event for graph traversal
    pinned: bool = False          # pinned events are exempt from TTL pruning

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "bot_id": self.bot_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "parent_id": self.parent_id,
            "pinned": self.pinned,
        }


class BehavioralMemory:
    """In-memory event graph tracking bot decisions over time.

    Parameters
    ----------
    bot_id:
        Owning bot identifier.
    ttl_days:
        How long to retain un-pinned events (default 90 days).
    """

    def __init__(self, bot_id: str, ttl_days: int = _BEHAVIORAL_TTL_DAYS) -> None:
        self.bot_id = bot_id
        self.ttl_seconds = ttl_days * 86_400
        self._events: list[BehavioralEvent] = []
        self._last_event_id: str | None = None

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record_event(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        *,
        pin: bool = False,
    ) -> BehavioralEvent:
        """Append an event and return it.  Automatically links to the previous event."""
        event = BehavioralEvent(
            event_id=str(uuid.uuid4()),
            bot_id=self.bot_id,
            event_type=event_type,
            payload=payload or {},
            timestamp=time.time(),
            parent_id=self._last_event_id,
            pinned=pin,
        )
        self._events.append(event)
        self._last_event_id = event.event_id
        return event

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the last *limit* events, most-recent first."""
        return [e.to_dict() for e in reversed(self._events[-limit:])]

    def get_chain(self, event_id: str) -> list[dict[str, Any]]:
        """Walk the parent-link chain back from *event_id* to the root."""
        index = {e.event_id: e for e in self._events}
        chain: list[dict[str, Any]] = []
        current = index.get(event_id)
        while current is not None:
            chain.append(current.to_dict())
            current = index.get(current.parent_id or "")  # type: ignore[arg-type]
        return chain

    def to_task_graph(self) -> dict[str, Any]:
        """Serialize the entire event graph as an adjacency list."""
        nodes = [e.to_dict() for e in self._events]
        edges = [
            {"from": e.parent_id, "to": e.event_id}
            for e in self._events
            if e.parent_id
        ]
        return {"nodes": nodes, "edges": edges}

    # ------------------------------------------------------------------
    # TTL / GDPR
    # ------------------------------------------------------------------

    def prune_expired(self) -> int:
        """Remove events older than TTL (unless pinned).  Returns count pruned."""
        cutoff = time.time() - self.ttl_seconds
        before = len(self._events)
        self._events = [
            e for e in self._events if e.pinned or e.timestamp >= cutoff
        ]
        return before - len(self._events)

    def forget(self, event_id: str) -> bool:
        """Delete a specific event by ID.  Returns True if found and deleted."""
        before = len(self._events)
        self._events = [e for e in self._events if e.event_id != event_id]
        return len(self._events) < before

    def pin(self, event_id: str) -> bool:
        """Mark an event as permanent (excluded from TTL pruning)."""
        for e in self._events:
            if e.event_id == event_id:
                e.pinned = True  # BehavioralEvent is a regular dataclass, not frozen
                return True
        return False

    def stats(self) -> dict[str, Any]:
        types: dict[str, int] = {}
        for e in self._events:
            types[e.event_type] = types.get(e.event_type, 0) + 1
        return {
            "total_events": len(self._events),
            "bot_id": self.bot_id,
            "by_type": types,
        }
