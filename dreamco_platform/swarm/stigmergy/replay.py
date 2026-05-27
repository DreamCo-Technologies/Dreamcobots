from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import threading
import time
import uuid
from typing import Any
from typing import Protocol

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

    def prune_before(self, timestamp: float) -> int:
        before = len(self._events)
        self._events = [event for event in self._events if event.timestamp >= timestamp]
        return before - len(self._events)


class FileDurableEventStore:
    """Append-only JSONL event store with simple replay and retention support."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "a", encoding="utf-8"):
                pass

    def append(self, event: StigmergyEvent) -> None:
        payload = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "payload": event.payload,
        }
        with self._lock, open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def append_trace_event(self, event: StigmergyEvent) -> None:
        self.append(event)

    def _load_events(self) -> list[StigmergyEvent]:
        events: list[StigmergyEvent] = []
        if not os.path.exists(self.path):
            return events
        with self._lock, open(self.path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    events.append(
                        StigmergyEvent(
                            event_type=data["event_type"],
                            payload=data["payload"],
                            timestamp=float(data.get("timestamp", time.time())),
                            event_id=str(data.get("event_id", uuid.uuid4())),
                        )
                    )
                except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                    continue
        return events

    def query_since(self, timestamp: float, *, event_type_prefix: str = "stigmergy.") -> list[StigmergyEvent]:
        return [
            event
            for event in self._load_events()
            if event.timestamp >= timestamp and event.event_type.startswith(event_type_prefix)
        ]

    def all(self) -> list[StigmergyEvent]:
        return self._load_events()

    def load_active_traces(self) -> list[PheromoneTrace]:
        traces: list[PheromoneTrace] = []
        for event in self._load_events():
            if event.event_type != "stigmergy.deposit":
                continue
            try:
                payload = dict(event.payload)
                if isinstance(payload.get("position"), list):
                    payload["position"] = tuple(payload["position"])
                traces.append(PheromoneTrace(**payload))
            except TypeError:
                continue
        return traces

    def prune_before(self, timestamp: float) -> int:
        events = self._load_events()
        retained = [event for event in events if event.timestamp >= timestamp]
        removed = len(events) - len(retained)
        with self._lock, open(self.path, "w", encoding="utf-8") as handle:
            for event in retained:
                payload = {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "payload": event.payload,
                }
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
        return removed


class StigmergyReplayer:
    def __init__(self, event_store: "ReplayEventStore") -> None:
        self.event_store = event_store

    def replay_from(self, timestamp: float, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        filters = filters or {}
        traces: list[PheromoneTrace] = []
        rejected_events = 0
        seen_event_ids: set[str] = set()
        replayed_events = 0
        for event in self.event_store.query_since(timestamp):
            if event.event_id in seen_event_ids:
                continue
            seen_event_ids.add(event.event_id)
            replayed_events += 1
            if filters and any(event.payload.get(k) != v for k, v in filters.items()):
                continue
            if event.event_type == "stigmergy.deposit":
                traces.append(PheromoneTrace(**event.payload))
            if event.event_type in {"stigmergy.rejected", "stigmergy.persistence_failure"}:
                rejected_events += 1
        return {
            "events_replayed": replayed_events,
            "active_traces": traces,
            "total_strength": sum(t.strength for t in traces),
            "rejected_events": rejected_events,
        }


class ReplayEventStore(Protocol):
    def query_since(self, timestamp: float, *, event_type_prefix: str = "stigmergy.") -> list[StigmergyEvent]: ...
