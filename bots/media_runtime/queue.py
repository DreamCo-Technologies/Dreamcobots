from __future__ import annotations

import heapq
import threading
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from framework import GlobalAISourcesFlow  # noqa: F401


class QueuePriority(IntEnum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class QueueItem:
    job_id: str
    priority: QueuePriority = QueuePriority.NORMAL
    tier: str = "free"
    enqueued_at: float = field(default_factory=time.time)
    lease_until: float = 0.0
    leased_by: str | None = None
    canceled: bool = False
    retry_count: int = 0
    last_error: str | None = None


class DurableMediaQueue:
    """Priority queue with lease/retry/dead-letter semantics for runtime workers."""

    def __init__(self, *, max_depth: int = 500) -> None:
        self.max_depth = max_depth
        self._lock = threading.RLock()
        self._items: dict[str, QueueItem] = {}
        self._heap: list[tuple[int, float, str]] = []
        self._dead_letter: dict[str, dict[str, Any]] = {}
        self._canceled: dict[str, dict[str, Any]] = {}
        self._stats: dict[str, int] = {
            "enqueued": 0,
            "dequeued": 0,
            "acked": 0,
            "retried": 0,
            "dead_lettered": 0,
            "canceled": 0,
            "stalled_recovered": 0,
        }

    def enqueue(self, job_id: str, *, priority: QueuePriority = QueuePriority.NORMAL, tier: str = "free") -> None:
        with self._lock:
            if len(self._items) >= self.max_depth:
                raise RuntimeError("Queue saturation threshold reached")
            item = QueueItem(job_id=job_id, priority=priority, tier=tier)
            self._items[job_id] = item
            heapq.heappush(self._heap, (int(priority), item.enqueued_at, job_id))
            self._stats["enqueued"] += 1

    def dequeue(self, *, worker_id: str, lease_seconds: int = 60) -> str | None:
        with self._lock:
            now = time.time()
            while self._heap:
                _priority, _enqueued_at, job_id = heapq.heappop(self._heap)
                item = self._items.get(job_id)
                if item is None or item.canceled:
                    continue
                if item.lease_until > now:
                    heapq.heappush(self._heap, (int(item.priority), item.enqueued_at, job_id))
                    return None
                item.leased_by = worker_id
                item.lease_until = now + lease_seconds
                self._stats["dequeued"] += 1
                return job_id
            return None

    def ack(self, job_id: str) -> None:
        with self._lock:
            if job_id in self._items:
                del self._items[job_id]
                self._stats["acked"] += 1

    def retry(self, job_id: str, *, reason: str | None = None, delay_seconds: float = 0.0) -> None:
        with self._lock:
            item = self._items.get(job_id)
            if not item:
                return
            item.retry_count += 1
            item.last_error = reason
            item.leased_by = None
            item.lease_until = time.time() + max(0.0, delay_seconds)
            heapq.heappush(self._heap, (int(item.priority), item.enqueued_at, job_id))
            self._stats["retried"] += 1

    def dead_letter(self, job_id: str, *, reason: str | None = None) -> None:
        with self._lock:
            item = self._items.pop(job_id, None)
            if item is None:
                return
            self._dead_letter[job_id] = {
                "job_id": job_id,
                "reason": reason or item.last_error,
                "retry_count": item.retry_count,
                "tier": item.tier,
                "priority": int(item.priority),
                "dead_lettered_at": time.time(),
            }
            self._stats["dead_lettered"] += 1

    def cancel(self, job_id: str, *, reason: str = "user_cancelled") -> bool:
        with self._lock:
            item = self._items.get(job_id)
            if item is None:
                return False
            item.canceled = True
            self._canceled[job_id] = {
                "job_id": job_id,
                "reason": reason,
                "retry_count": item.retry_count,
                "canceled_at": time.time(),
            }
            self._stats["canceled"] += 1
            return True

    def recover_stalled(self, *, stall_after_seconds: int = 120) -> int:
        with self._lock:
            now = time.time()
            recovered = 0
            for job_id, item in list(self._items.items()):
                if item.canceled:
                    continue
                if item.leased_by and item.lease_until and (now - item.lease_until) > stall_after_seconds:
                    item.leased_by = None
                    item.lease_until = 0.0
                    heapq.heappush(self._heap, (int(item.priority), item.enqueued_at, job_id))
                    recovered += 1
            self._stats["stalled_recovered"] += recovered
            return recovered

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            leased = len([item for item in self._items.values() if item.leased_by and not item.canceled])
            depth = len([item for item in self._items.values() if not item.canceled and not item.leased_by])
            return {
                "depth": depth,
                "leased": leased,
                "active_jobs": len(self._items),
                "dead_letter_count": len(self._dead_letter),
                "canceled_count": len(self._canceled),
                "max_depth": self.max_depth,
                "stats": dict(self._stats),
            }

    def dead_letter_items(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._dead_letter.values())
