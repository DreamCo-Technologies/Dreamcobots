"""
DreamCo Platform — Elasticsearch Store Adapter
===============================================

``ElasticStore`` provides full-text and hybrid search backed by
Elasticsearch / OpenSearch.

**Stub mode** — operates with an in-process list + token-based BM25-style
scoring when no Elasticsearch host is reachable.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Any

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord


def _bm25_score(query: str, content: str) -> float:
    """Minimal BM25-like overlap score for stub mode."""
    qtokens = set(query.lower().split())
    ctokens = content.lower().split()
    if not qtokens or not ctokens:
        return 0.0
    counts = Counter(ctokens)
    overlap = sum(min(counts[t], 1) for t in qtokens)
    return overlap / len(qtokens)


class ElasticStore(RetrievalBackend):
    """
    Elasticsearch / OpenSearch retrieval adapter.

    Parameters
    ----------
    hosts : list[str] | None
        Elasticsearch host(s).  Defaults to ``["localhost:9200"]``.
    api_key : str | None
        Elasticsearch API key.  Falls back to ``ELASTICSEARCH_API_KEY``.
    index : str
        Index name for DreamCo records.
    stub : bool
        Force stub mode.
    """

    def __init__(
        self,
        hosts: list[str] | None = None,
        api_key: str | None = None,
        index: str = "dreamco_retrieval",
        stub: bool = False,
    ) -> None:
        self._hosts = hosts or ["localhost:9200"]
        self._api_key = api_key or os.environ.get("ELASTICSEARCH_API_KEY", "")
        self._index = index
        self._client: Any = None
        self._local: dict[str, RetrievalRecord] = {}

        if not stub:
            self._connect()

    # ------------------------------------------------------------------
    # RetrievalBackend interface
    # ------------------------------------------------------------------

    @property
    def backend_name(self) -> str:
        return "elasticsearch"

    def upsert(self, record: RetrievalRecord) -> None:
        if self._client is None:
            self._local[record.key] = record
            return
        doc = {
            "content": record.content,
            "metadata": record.metadata,
            "created_at": record.created_at,
        }
        self._client.index(index=self._index, id=record.key, document=doc)

    def get(self, key: str) -> RetrievalRecord | None:
        if self._client is None:
            return self._local.get(key)
        try:
            result = self._client.get(index=self._index, id=key)
            src = result["_source"]
            return RetrievalRecord(
                key=key,
                content=src.get("content", ""),
                metadata=src.get("metadata", {}),
                created_at=src.get("created_at", 0.0),
            )
        except Exception:  # noqa: BLE001
            return None

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        if self._client is None:
            scored = [
                (r, _bm25_score(query, r.content))
                for r in self._local.values()
                if not query or query.lower() in r.content.lower() or _bm25_score(query, r.content) > 0
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            results = []
            for rec, score in scored[:limit]:
                import dataclasses
                results.append(dataclasses.replace(rec, score=score))
            return results

        es_query: dict[str, Any] = {
            "query": {
                "match": {"content": query}
            },
            "size": limit,
        }
        if filters:
            es_query["query"] = {
                "bool": {
                    "must": {"match": {"content": query}},
                    "filter": [{"term": {k: v}} for k, v in filters.items()],
                }
            }
        resp = self._client.search(index=self._index, body=es_query)
        records = []
        for hit in resp["hits"]["hits"]:
            src = hit["_source"]
            records.append(RetrievalRecord(
                key=hit["_id"],
                content=src.get("content", ""),
                score=hit["_score"],
                metadata=src.get("metadata", {}),
                created_at=src.get("created_at", 0.0),
            ))
        return records

    def delete(self, key: str) -> bool:
        if self._client is None:
            return self._local.pop(key, None) is not None
        try:
            self._client.delete(index=self._index, id=key)
            return True
        except Exception:  # noqa: BLE001
            return False

    def count(self) -> int:
        if self._client is None:
            return len(self._local)
        resp = self._client.count(index=self._index)
        return resp.get("count", 0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        try:
            from elasticsearch import Elasticsearch  # type: ignore[import]
            kwargs: dict[str, Any] = {"hosts": self._hosts}
            if self._api_key:
                kwargs["api_key"] = self._api_key
            client = Elasticsearch(**kwargs)
            client.info()
            self._client = client
            if not self._client.indices.exists(index=self._index):
                self._client.indices.create(
                    index=self._index,
                    mappings={"properties": {"content": {"type": "text"}}},
                )
        except Exception:  # noqa: BLE001
            self._client = None

    def __repr__(self) -> str:
        mode = "live" if self._client else "stub"
        return f"ElasticStore(mode={mode!r}, index={self._index!r})"
