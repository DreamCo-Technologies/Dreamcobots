"""pgvector-backed embedding storage with cosine-scan fallback."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Iterable

import psycopg2
from psycopg2.extras import Json, RealDictCursor

try:
    from pgvector.psycopg2 import register_vector
except ImportError:  # pragma: no cover - optional at runtime
    register_vector = None


@dataclass
class VectorMatch:
    key: str
    score: float
    metadata: dict[str, Any]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions differ: {len(a)} != {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


class PgVectorEmbeddingStore:
    """Store dense vectors in PostgreSQL and query with pgvector ANN when available."""

    def __init__(self, dsn: str | None = None, *, dimension: int = 1536) -> None:
        self._dsn = dsn or os.getenv("DATABASE_URL", "")
        self.dimension = dimension
        self._pgvector_enabled: bool | None = None
        self._conn = psycopg2.connect(self._dsn) if self._dsn else None
        if self._conn is not None and register_vector is not None:
            register_vector(self._conn)
        if self._conn is not None:
            self._conn.autocommit = True
            self._ensure_schema()

    def _require_conn(self):
        if self._conn is None:
            raise RuntimeError("DATABASE_URL is required for PgVectorEmbeddingStore")
        return self._conn

    def _ensure_schema(self) -> None:
        conn = self._require_conn()
        with conn.cursor() as cur:
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                self._pgvector_enabled = True
            except Exception:
                conn.rollback()
                self._pgvector_enabled = False
            vector_type = f"vector({self.dimension})" if self._pgvector_enabled else "DOUBLE PRECISION[]"
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS embedding_store (
                    key TEXT PRIMARY KEY,
                    vector {vector_type} NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            if self._pgvector_enabled:
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_embedding_store_vector_ivfflat "
                    "ON embedding_store USING ivfflat (vector vector_cosine_ops) WITH (lists = 100)"
                )

    def upsert(self, key: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Insert or replace an embedding row."""
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO embedding_store (key, vector, metadata, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (key)
                DO UPDATE SET vector = EXCLUDED.vector, metadata = EXCLUDED.metadata, updated_at = NOW()
                """,
                (key, vector, Json(metadata or {})),
            )

    def nearest(self, query_vector: list[float], top_k: int = 10) -> list[VectorMatch]:
        """Return nearest neighbors using pgvector distance or in-process cosine scan."""
        conn = self._require_conn()
        if self._pgvector_enabled:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT key, metadata, 1 - (vector <=> %s::vector) AS score
                    FROM embedding_store
                    ORDER BY vector <=> %s::vector ASC
                    LIMIT %s
                    """,
                    (query_vector, query_vector, top_k),
                )
                rows = cur.fetchall()
            return [VectorMatch(key=row["key"], score=float(row["score"]), metadata=row["metadata"]) for row in rows]
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT key, vector, metadata FROM embedding_store")
            rows = cur.fetchall()
        scored = [
            VectorMatch(key=row["key"], score=_cosine_similarity(query_vector, list(row["vector"])), metadata=row["metadata"])
            for row in rows
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def delete(self, key: str) -> bool:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM embedding_store WHERE key = %s", (key,))
            return cur.rowcount > 0

    def count(self) -> int:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM embedding_store")
            return int(cur.fetchone()[0])

    def bulk_upsert(self, entries: Iterable[tuple[str, list[float], dict[str, Any]]]) -> None:
        """Persist a stream of embeddings."""
        for key, vector, metadata in entries:
            self.upsert(key, vector, metadata)

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
