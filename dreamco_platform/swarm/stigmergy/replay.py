from __future__ import annotations

from dataclasses import dataclass, field
import time
import uuid
from typing import Any

from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace


@dataclass(frozen=True)
class StigmergyEvent:
    event_type: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: list[StigmergyEvent] = []

    def append(self, event: StigmergyEvent) -> None:
        self._events.append(event)

    def query_since(self, timestamp: float, *, event_type_prefix: str = "stigmergy.") -> list[StigmergyEvent]:
        return [
            event
            for event in self._events
            if event.timestamp >= timestamp and event.event_type.startswith(event_type_prefix)
        ]

    def all(self) -> list[StigmergyEvent]:
        return list(self._events)


class StigmergyReplayer:
    def __init__(self, event_store: InMemoryEventStore) -> None:
        self.event_store = event_store

    def replay_from(self, timestamp: float, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        filters = filters or {}
        traces: list[PheromoneTrace] = []
        for event in self.event_store.query_since(timestamp):
            if filters and any(event.payload.get(k) != v for k, v in filters.items()):
                continue
            if event.event_type == "stigmergy.deposit":
                traces.append(PheromoneTrace(**event.payload))
        return {
            "events_replayed": len(self.event_store.query_since(timestamp)),
            "active_traces": traces,
            "total_strength": sum(t.strength for t in traces),
        }
