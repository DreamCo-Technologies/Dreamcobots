"""
DreamCo Platform — Event Stream
================================

``EventStream`` is a persistent, subscribable stream of ``DreamCoEvent``
objects partitioned by event family.  It provides:

* **Fan-out** to multiple consumers (e.g. Dream Brain ingestion, analytics)
* **Position tracking** so consumers can replay from any offset
* **Filtering** by event family or type pattern

Architecture note
-----------------
This is an in-process ordered buffer.  In production, replace the internal
``deque`` with a Kafka / Kinesis / Pub-Sub partition.  The consumer API
(``consume()``, ``consume_from()``) is designed to mirror that of streaming
systems so the swap is low-friction.

Usage::

    stream = EventStream()
    stream.publish(event)

    # Consumer: read all new events since offset 5
    batch = stream.consume_from(offset=5, max_count=100)
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

from dreamco_platform.events.schema import DreamCoEvent


# ---------------------------------------------------------------------------
# Positioned event wrapper
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StreamRecord:
    offset: int
    event: DreamCoEvent

    def to_dict(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "event_id": self.event.event_id,
            "event_type": self.event.event_type,
            "source_id": self.event.source_id,
            "timestamp": self.event.timestamp,
        }


# ---------------------------------------------------------------------------
# EventStream
# ---------------------------------------------------------------------------

class EventStream:
    """Partitioned, offset-tracked event stream.

    Parameters
    ----------
    partition:
        Logical partition name (e.g. a workspace_id or family name).
    max_size:
        Maximum number of records retained in memory before FIFO eviction.
    """

    def __init__(self, partition: str = "default", max_size: int = 50_000) -> None:
        self._partition = partition
        self._max_size = max_size
        self._lock = threading.Lock()
        self._records: list[StreamRecord] = []
        self._next_offset: int = 0

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def publish(self, event: DreamCoEvent) -> int:
        """Append *event* to the stream.  Returns the assigned offset."""
        with self._lock:
            offset = self._next_offset
            self._next_offset += 1
            self._records.append(StreamRecord(offset=offset, event=event))
            # Evict oldest if over capacity
            if len(self._records) > self._max_size:
                self._records = self._records[-self._max_size :]
        return offset

    # ------------------------------------------------------------------
    # Consume
    # ------------------------------------------------------------------

    def consume_from(
        self,
        offset: int = 0,
        max_count: int = 100,
        event_type_filter: str | None = None,
    ) -> list[StreamRecord]:
        """Return up to *max_count* records starting at *offset*.

        Parameters
        ----------
        offset:
            Stream offset to start reading from (inclusive).
        max_count:
            Maximum number of records to return.
        event_type_filter:
            If set, only return records whose event_type matches this string
            exactly or whose family prefix matches a ``"family.*"`` wildcard.
        """
        with self._lock:
            records = [r for r in self._records if r.offset >= offset]

        if event_type_filter:
            family_wildcard = event_type_filter.endswith(".*")
            if family_wildcard:
                family = event_type_filter[:-2]
                records = [r for r in records if r.event.event_type.startswith(family + ".")]
            else:
                records = [r for r in records if r.event.event_type == event_type_filter]

        return records[:max_count]

    def latest_offset(self) -> int:
        with self._lock:
            return self._next_offset - 1 if self._next_offset > 0 else -1

    def size(self) -> int:
        with self._lock:
            return len(self._records)

    @property
    def partition(self) -> str:
        return self._partition

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "partition": self._partition,
                "stored": len(self._records),
                "next_offset": self._next_offset,
            }
