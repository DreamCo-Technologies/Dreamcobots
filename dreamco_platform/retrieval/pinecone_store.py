"""
DreamCo Platform — Pinecone Store Adapter
==========================================

``PineconeStore`` provides vector similarity search backed by Pinecone.
It stores dense embeddings and retrieves records by cosine similarity.

**Stub mode** — when no Pinecone API key is configured, the store
operates with an in-process brute-force cosine similarity fallback so
the rest of the pipeline can run end-to-end without a Pinecone account.
"""

from __future__ import annotations

import math
import os
from typing import Any

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord


def _cosine(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class PineconeStore(RetrievalBackend):
    """
    Pinecone vector store adapter.

    Parameters
    ----------
    api_key : str | None
        Pinecone API key.  Falls back to ``PINECONE_API_KEY`` env var.
    index_name : str
        Name of the Pinecone index to use.
    environment : str
        Pinecone environment / region (e.g. ``"us-east1-gcp"``).
    namespace : str
        Pinecone namespace for partitioning.
    dimension : int
        Embedding dimension (must match the index).
    stub : bool
        Force stub mode.
    """

    def __init__(
        self,
        api_key: str | None = None,
        index_name: str = "dreamco",
        environment: str = "us-east1-gcp",
        namespace: str = "default",
        dimension: int = 1536,
        stub: bool = False,
    ) -> None:
        self._api_key = api_key or os.environ.get("PINECONE_API_KEY", "")
        self._index_name = index_name
        self._environment = environment
        self._namespace = namespace
        self._dimension = dimension
        self._index: Any = None
        self._local: dict[str, RetrievalRecord] = {}  # in-process fallback

        if not stub and self._api_key:
            self._connect()

    # ------------------------------------------------------------------
    # RetrievalBackend interface
    # ------------------------------------------------------------------

    @property
    def backend_name(self) -> str:
        return "pinecone"

    def upsert(self, record: RetrievalRecord) -> None:
        if self._index is None:
            self._local[record.key] = record
            return
        vector = record.embedding or [0.0] * self._dimension
        self._index.upsert(
            vectors=[(record.key, vector, {"content": record.content, **record.metadata})],
            namespace=self._namespace,
        )

    def get(self, key: str) -> RetrievalRecord | None:
        if self._index is None:
            return self._local.get(key)
        result = self._index.fetch(ids=[key], namespace=self._namespace)
        vectors = result.get("vectors", {})
        if key not in vectors:
            return None
        vec = vectors[key]
        meta = vec.get("metadata", {})
        content = meta.pop("content", "")
        return RetrievalRecord(
            key=key,
            content=content,
            embedding=vec.get("values"),
            metadata=meta,
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        if self._index is None:
            # Stub: keyword filter, then cosine if embeddings available
            candidates = list(self._local.values())
            if query:
                candidates = [r for r in candidates if query.lower() in r.content.lower()]
            if embedding:
                for r in candidates:
                    if r.embedding:
                        r.score = _cosine(embedding, r.embedding)
            candidates.sort(key=lambda r: r.score, reverse=True)
            return candidates[:limit]

        query_vec = embedding or [0.0] * self._dimension
        kwargs: dict[str, Any] = {
            "vector": query_vec,
            "top_k": limit,
            "include_metadata": True,
            "namespace": self._namespace,
        }
        if filters:
            kwargs["filter"] = filters
        results = self._index.query(**kwargs)
        records = []
        for match in results.get("matches", []):
            meta = dict(match.get("metadata", {}))
            content = meta.pop("content", "")
            records.append(RetrievalRecord(
                key=match["id"],
                content=content,
                embedding=match.get("values"),
                score=match.get("score", 0.0),
                metadata=meta,
            ))
        return records

    def delete(self, key: str) -> bool:
        if self._index is None:
            return self._local.pop(key, None) is not None
        self._index.delete(ids=[key], namespace=self._namespace)
        return True

    def count(self) -> int:
        if self._index is None:
            return len(self._local)
        stats = self._index.describe_index_stats()
        ns = stats.get("namespaces", {}).get(self._namespace, {})
        return ns.get("vector_count", 0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        try:
            import pinecone  # type: ignore[import]
            pinecone.init(api_key=self._api_key, environment=self._environment)
            self._index = pinecone.Index(self._index_name)
        except Exception:  # noqa: BLE001
            self._index = None

    def __repr__(self) -> str:
        mode = "live" if self._index else "stub"
        return f"PineconeStore(mode={mode!r}, index={self._index_name!r})"
