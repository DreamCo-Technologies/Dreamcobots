"""
DreamCo Platform — Embedding Store
=====================================

``EmbeddingStore`` stores and queries dense vector embeddings associated with
platform entities (bot descriptions, capability summaries, workflow outcomes).

In production, replace the linear scan with an ANN index (FAISS, Pinecone,
pgvector).  The interface is designed for that swap to be trivial.

Usage::

    store = EmbeddingStore()
    store.upsert("cap:lead.scrape", [0.1, 0.2, 0.9], metadata={"tags": ["lead"]})
    neighbours = store.nearest([0.1, 0.2, 0.8], top_k=5)
"""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

@dataclass
class EmbeddingEntry:
    key: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def dimension(self) -> int:
        return len(self.vector)


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"Vector dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# EmbeddingStore
# ---------------------------------------------------------------------------

@dataclass
class ScoredEntry:
    key: str
    score: float
    metadata: dict[str, Any]


class EmbeddingStore:
    """In-memory embedding store with cosine similarity search."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, EmbeddingEntry] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert(
        self,
        key: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or replace the embedding for *key*."""
        with self._lock:
            self._store[key] = EmbeddingEntry(key=key, vector=list(vector), metadata=metadata or {})

    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self._store:
                return False
            del self._store[key]
            return True

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, key: str) -> EmbeddingEntry | None:
        with self._lock:
            return self._store.get(key)

    def nearest(
        self,
        query_vector: list[float],
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[ScoredEntry]:
        """Return the *top_k* nearest entries by cosine similarity."""
        with self._lock:
            entries = list(self._store.values())

        scored = []
        for entry in entries:
            try:
                score = _cosine_similarity(query_vector, entry.vector)
            except ValueError:
                continue
            if score >= min_score:
                scored.append(ScoredEntry(key=entry.key, score=score, metadata=entry.metadata))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:top_k]

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._store.keys())

    def count(self) -> int:
        with self._lock:
            return len(self._store)
