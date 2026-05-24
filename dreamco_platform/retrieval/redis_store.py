"""
DreamCo Platform — Redis Store Adapter
=======================================

``RedisStore`` provides hot-cache and session-memory semantics backed by
Redis.  Uses Redis ``HSET`` for record storage and prefix-based key scanning
for search.

**Stub mode** — when no Redis connection is configured the store operates
entirely in-process using a plain dict, making it safe for CI and local
development without a running Redis instance.
"""

from __future__ import annotations

import fnmatch
from typing import Any

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord


class RedisStore(RetrievalBackend):
    """
    Redis-backed retrieval adapter.

    Parameters
    ----------
    host : str
        Redis hostname.
    port : int
        Redis port.
    db : int
        Redis DB index.
    password : str | None
        Redis AUTH password.
    prefix : str
        Key prefix to namespace this store's records (e.g. ``"dreamco:mem:"``).
    stub : bool
        Force stub mode regardless of connection settings.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        prefix: str = "dreamco:retrieval:",
        stub: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._prefix = prefix
        self._stub = stub
        self._client: Any = None
        self._local: dict[str, RetrievalRecord] = {}  # in-process fallback
        if not stub:
            self._connect()

    # ------------------------------------------------------------------
    # RetrievalBackend interface
    # ------------------------------------------------------------------

    @property
    def backend_name(self) -> str:
        return "redis"

    def upsert(self, record: RetrievalRecord) -> None:
        if self._client is None:
            self._local[record.key] = record
            return
        import json
        full_key = self._prefix + record.key
        self._client.hset(full_key, mapping={
            "record_id": record.record_id,
            "content": record.content,
            "score": str(record.score),
            "metadata": json.dumps(record.metadata),
            "created_at": str(record.created_at),
        })

    def get(self, key: str) -> RetrievalRecord | None:
        if self._client is None:
            return self._local.get(key)
        import json
        full_key = self._prefix + key
        data = self._client.hgetall(full_key)
        if not data:
            return None
        return RetrievalRecord(
            key=key,
            content=data.get(b"content", b"").decode(),
            score=float(data.get(b"score", b"1.0")),
            metadata=json.loads(data.get(b"metadata", b"{}")),
            created_at=float(data.get(b"created_at", b"0")),
            record_id=data.get(b"record_id", b"").decode(),
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        if self._client is None:
            results = [
                r for r in self._local.values()
                if query.lower() in r.content.lower()
            ]
            results.sort(key=lambda r: r.score, reverse=True)
            return results[:limit]

        # Live Redis: scan keys and filter by content substring
        pattern = self._prefix + "*"
        matched: list[RetrievalRecord] = []
        for raw_key in self._client.scan_iter(pattern):
            key = raw_key.decode().removeprefix(self._prefix)
            record = self.get(key)
            if record and query.lower() in record.content.lower():
                matched.append(record)
        matched.sort(key=lambda r: r.score, reverse=True)
        return matched[:limit]

    def delete(self, key: str) -> bool:
        if self._client is None:
            return self._local.pop(key, None) is not None
        full_key = self._prefix + key
        return bool(self._client.delete(full_key))

    def count(self) -> int:
        if self._client is None:
            return len(self._local)
        pattern = self._prefix + "*"
        return sum(1 for _ in self._client.scan_iter(pattern))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        """Attempt to connect to Redis; fall back to in-process stub on failure."""
        try:
            import redis  # type: ignore[import]
            kwargs: dict[str, Any] = {"host": self._host, "port": self._port, "db": self._db}
            if self._password:
                kwargs["password"] = self._password
            client = redis.Redis(**kwargs)
            client.ping()
            self._client = client
        except Exception:  # noqa: BLE001
            # Redis not available — operate in stub mode
            self._client = None

    def __repr__(self) -> str:
        mode = "live" if self._client else "stub"
        return f"RedisStore(mode={mode!r}, records={len(self._local)})"
