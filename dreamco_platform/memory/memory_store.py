"""
DreamCo Platform — Memory Store
=================================

``MemoryStore`` is the generic, append-and-query backbone for all Dream Memory
sub-systems (user memory, workflow memory, embedding store).

Each record is a ``MemoryRecord`` that carries:
* a subject key (e.g. ``user:alice``, ``workflow:lead_pipeline``)
* a ``MemoryType`` enum tag
* a numeric ``importance`` score (used for pruning)
* an arbitrary ``context`` dict
* an optional embedding vector

Usage::

    store = MemoryStore()
    store.write(MemoryRecord(
        subject="workflow:lead_pipeline",
        memory_type=MemoryType.OUTCOME,
        content="Pipeline succeeded with 143 leads",
        importance=0.8,
        context={"run_id": "r123", "cost_usd": 0.42},
    ))
    records = store.recall("workflow:lead_pipeline", memory_type=MemoryType.OUTCOME)
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# MemoryType
# ---------------------------------------------------------------------------

class MemoryType(str, Enum):
    DECISION = "decision"
    OUTCOME = "outcome"
    PROFITABILITY = "profitability"
    LEARNING_SIGNAL = "learning_signal"
    ANOMALY = "anomaly"
    CONTEXT = "context"
    EMBEDDING_REF = "embedding_ref"


# ---------------------------------------------------------------------------
# MemoryRecord
# ---------------------------------------------------------------------------

@dataclass
class MemoryRecord:
    subject: str
    memory_type: MemoryType
    content: str
    importance: float = 0.5          # 0.0 (low) → 1.0 (critical)
    context: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "subject": self.subject,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "importance": self.importance,
            "context": self.context,
            "embedding": self.embedding,
            "created_at": self.created_at,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------

class MemoryStore:
    """Generic append-and-query memory store.

    Parameters
    ----------
    max_records:
        Hard cap on stored records; lowest-importance records are pruned first
        when the cap is reached.
    """

    def __init__(self, max_records: int = 100_000) -> None:
        self._lock = threading.Lock()
        self._records: list[MemoryRecord] = []
        self._max = max_records

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write(self, record: MemoryRecord) -> None:
        with self._lock:
            self._records.append(record)
            if len(self._records) > self._max:
                # Prune the least-important record
                self._records.sort(key=lambda r: r.importance, reverse=True)
                self._records = self._records[: self._max]

    # ------------------------------------------------------------------
    # Recall
    # ------------------------------------------------------------------

    def recall(
        self,
        subject: str,
        memory_type: MemoryType | None = None,
        min_importance: float = 0.0,
        limit: int = 50,
        tag: str | None = None,
    ) -> list[MemoryRecord]:
        """Return records for *subject*, newest-first."""
        with self._lock:
            records = list(self._records)

        results = []
        for r in reversed(records):
            if r.subject != subject:
                continue
            if memory_type and r.memory_type != memory_type:
                continue
            if r.importance < min_importance:
                continue
            if tag and tag not in r.tags:
                continue
            results.append(r)
            if len(results) >= limit:
                break
        return results

    def recall_all(
        self,
        memory_type: MemoryType | None = None,
        min_importance: float = 0.0,
        limit: int = 100,
    ) -> list[MemoryRecord]:
        with self._lock:
            records = list(self._records)
        results = [
            r for r in reversed(records)
            if (not memory_type or r.memory_type == memory_type)
            and r.importance >= min_importance
        ]
        return results[:limit]

    def delete_by_subject(self, subject: str) -> int:
        with self._lock:
            before = len(self._records)
            self._records = [r for r in self._records if r.subject != subject]
            return before - len(self._records)

    def count(self) -> int:
        with self._lock:
            return len(self._records)

    def subjects(self) -> list[str]:
        with self._lock:
            return list({r.subject for r in self._records})
