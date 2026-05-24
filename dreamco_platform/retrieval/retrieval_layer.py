"""
DreamCo Platform — Unified Retrieval Layer
============================================

``RetrievalLayer`` is the single entry-point for all retrieval operations.
It aggregates multiple ``RetrievalBackend`` instances and dispatches:

* **Write** → all registered backends that accept the record's type
* **Read (by key)** → first backend that returns a result
* **Search** → all backends, results merged + deduplicated by key,
  re-ranked by score

This architecture ensures:
* Hot data lands in Redis (fast)
* Semantic search goes through Pinecone (vectors)
* Full-text search goes through Elasticsearch (BM25)
* Persistent structured facts live in SQL

Usage::

    layer = RetrievalLayer()
    layer.add_backend(RedisStore(), write=True, search=False)
    layer.add_backend(PineconeStore(), write=True, search=True)
    layer.add_backend(ElasticStore(), write=True, search=True)
    layer.add_backend(SQLStore(), write=True, search=True)

    layer.upsert(RetrievalRecord(key="doc:1", content="DreamCo AI platform"))
    results = layer.search("AI platform", limit=5)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord


@dataclass
class BackendRegistration:
    """Metadata binding a backend to its dispatch role."""
    backend: RetrievalBackend
    write: bool = True    # Participate in upsert / delete
    search: bool = True   # Participate in search


class RetrievalLayer:
    """
    Aggregates multiple retrieval backends into a unified interface.

    Parameters
    ----------
    merge_limit : int
        Maximum total results returned after merging all backends.
    """

    def __init__(self, merge_limit: int = 50) -> None:
        self._registrations: list[BackendRegistration] = []
        self._merge_limit = merge_limit

    # ------------------------------------------------------------------
    # Backend management
    # ------------------------------------------------------------------

    def add_backend(
        self,
        backend: RetrievalBackend,
        *,
        write: bool = True,
        search: bool = True,
    ) -> None:
        """Register *backend* with the given dispatch roles."""
        self._registrations.append(BackendRegistration(backend=backend, write=write, search=search))

    def remove_backend(self, backend_name: str) -> bool:
        """Remove a backend by its ``backend_name``.  Return ``True`` if found."""
        before = len(self._registrations)
        self._registrations = [
            r for r in self._registrations
            if r.backend.backend_name != backend_name
        ]
        return len(self._registrations) < before

    def list_backends(self) -> list[str]:
        """Return the names of all registered backends."""
        return [r.backend.backend_name for r in self._registrations]

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def upsert(self, record: RetrievalRecord) -> None:
        """Write *record* to all write-enabled backends."""
        for reg in self._registrations:
            if reg.write:
                try:
                    reg.backend.upsert(record)
                except Exception:  # noqa: BLE001
                    pass

    def delete(self, key: str) -> int:
        """Delete the record with *key* from all write-enabled backends.

        Returns the count of backends that confirmed deletion.
        """
        count = 0
        for reg in self._registrations:
            if reg.write:
                try:
                    if reg.backend.delete(key):
                        count += 1
                except Exception:  # noqa: BLE001
                    pass
        return count

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def get(self, key: str) -> RetrievalRecord | None:
        """Return the first record found for *key* across all backends."""
        for reg in self._registrations:
            try:
                record = reg.backend.get(key)
                if record is not None:
                    return record
            except Exception:  # noqa: BLE001
                pass
        return None

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        """
        Search across all search-enabled backends, merge + deduplicate.

        Results are sorted by score descending.  When the same key appears
        in multiple backends the highest score is kept.
        """
        seen: dict[str, RetrievalRecord] = {}
        for reg in self._registrations:
            if not reg.search:
                continue
            try:
                results = reg.backend.search(
                    query,
                    limit=limit,
                    filters=filters,
                    embedding=embedding,
                )
                for record in results:
                    if record.key not in seen or record.score > seen[record.key].score:
                        seen[record.key] = record
            except Exception:  # noqa: BLE001
                pass

        merged = sorted(seen.values(), key=lambda r: r.score, reverse=True)
        return merged[: min(limit, self._merge_limit)]

    # ------------------------------------------------------------------
    # Aggregated stats
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return a per-backend record count summary."""
        result: dict[str, Any] = {}
        for reg in self._registrations:
            try:
                result[reg.backend.backend_name] = reg.backend.count()
            except Exception:  # noqa: BLE001
                result[reg.backend.backend_name] = "error"
        return result

    def __repr__(self) -> str:
        backends = ", ".join(self.list_backends())
        return f"RetrievalLayer(backends=[{backends}])"
