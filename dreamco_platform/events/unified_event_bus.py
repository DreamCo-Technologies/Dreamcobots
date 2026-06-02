"""Unified event bus using Redis Streams with in-memory fallback."""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover
    Redis = None


@dataclass
class EventEnvelope:
    event_type: str
    payload: dict[str, Any]
    timestamp: float


class UnifiedEventBus:
    """Publish, subscribe, and replay events through one DreamCo abstraction."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis = Redis.from_url(redis_url) if redis_url and Redis else None
        self._events: list[EventEnvelope] = []
        self._handlers: dict[str, list[Callable[[dict[str, Any]], Awaitable[None] | None]]] = defaultdict(list)
        self._dead_letter: list[EventEnvelope] = []

    async def publish(self, event_type: str, payload: dict[str, Any]) -> EventEnvelope:
        event = EventEnvelope(event_type=event_type, payload=payload, timestamp=time.time())
        self._events.append(event)
        if self.redis is not None:
            await self.redis.xadd("dreamco-events", {"event": json.dumps(event.__dict__)})
        for handler in self._handlers.get(event_type, []):
            try:
                result = handler(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                self._dead_letter.append(event)
        return event

    def subscribe(self, event_type: str, handler: Callable[[dict[str, Any]], Awaitable[None] | None]) -> None:
        self._handlers[event_type].append(handler)

    async def replay(self, since: float) -> list[EventEnvelope]:
        candidates = [event for event in self._events if event.timestamp >= since]
        for event in candidates:
            for handler in self._handlers.get(event.event_type, []):
                result = handler(event.payload)
                if asyncio.iscoroutine(result):
                    await result
        return candidates

    def dead_letter_queue(self) -> list[EventEnvelope]:
        return list(self._dead_letter)
