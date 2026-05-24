"""
DreamCo Platform — SQL Store Adapter
======================================

``SQLStore`` persists structured retrieval records in a SQL database.
Defaults to an in-process SQLite database so the full pipeline runs
without any external dependency in CI and local development.

In production, swap the *connection_string* for PostgreSQL or MySQL:

    store = SQLStore("postgresql+psycopg2://user:pass@host/dreamco")
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord


# ---------------------------------------------------------------------------
# SQLite-backed implementation (no external dependencies)
# ---------------------------------------------------------------------------

class SQLStore(RetrievalBackend):
    """
    SQL-backed retrieval adapter.

    Parameters
    ----------
    connection_string : str
        SQLAlchemy-style connection string.  ``"sqlite://"`` uses an
        in-memory SQLite database (default; safe for CI).
        ``"sqlite:///path/to/db.sqlite"`` uses a file-backed database.
        PostgreSQL: ``"postgresql+psycopg2://user:pass@host/db"``
    table : str
        Table name for retrieval records.
    """

    def __init__(
        self,
        connection_string: str = "sqlite://",
        table: str = "dreamco_retrieval",
    ) -> None:
        self._connection_string = connection_string
        self._table = table
        self._lock = threading.Lock()
        self._engine: Any = None
        self._conn: sqlite3.Connection | None = None
        self._connect()

    # ------------------------------------------------------------------
    # RetrievalBackend interface
    # ------------------------------------------------------------------

    @property
    def backend_name(self) -> str:
        return "sql"

    def upsert(self, record: RetrievalRecord) -> None:
        with self._lock:
            if self._conn:
                self._conn.execute(
                    f"""
                    INSERT OR REPLACE INTO {self._table}
                        (key, record_id, content, score, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.key,
                        record.record_id,
                        record.content,
                        record.score,
                        json.dumps(record.metadata),
                        record.created_at,
                    ),
                )
                self._conn.commit()
            else:
                self._sqlalchemy_upsert(record)

    def get(self, key: str) -> RetrievalRecord | None:
        with self._lock:
            if self._conn:
                cur = self._conn.execute(
                    f"SELECT key, record_id, content, score, metadata, created_at "
                    f"FROM {self._table} WHERE key = ?",
                    (key,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return self._row_to_record(row)
            return self._sqlalchemy_get(key)

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        with self._lock:
            if self._conn:
                pattern = f"%{query}%"
                cur = self._conn.execute(
                    f"SELECT key, record_id, content, score, metadata, created_at "
                    f"FROM {self._table} WHERE content LIKE ? ORDER BY score DESC LIMIT ?",
                    (pattern, limit),
                )
                return [self._row_to_record(row) for row in cur.fetchall()]
            return self._sqlalchemy_search(query, limit=limit)

    def delete(self, key: str) -> bool:
        with self._lock:
            if self._conn:
                cur = self._conn.execute(
                    f"DELETE FROM {self._table} WHERE key = ?",
                    (key,),
                )
                self._conn.commit()
                return cur.rowcount > 0
            return self._sqlalchemy_delete(key)

    def count(self) -> int:
        with self._lock:
            if self._conn:
                cur = self._conn.execute(f"SELECT COUNT(*) FROM {self._table}")
                return cur.fetchone()[0]
            return self._sqlalchemy_count()

    # ------------------------------------------------------------------
    # Internal — SQLite path
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        """Connect to SQLite (always) or try SQLAlchemy for other dialects."""
        cs = self._connection_string
        if cs.startswith("sqlite"):
            # Use the stdlib sqlite3 driver directly
            db_path = cs.removeprefix("sqlite:///").removeprefix("sqlite://")
            self._conn = sqlite3.connect(
                db_path or ":memory:", check_same_thread=False
            )
            self._init_sqlite_schema()
        else:
            self._conn = None
            self._init_sqlalchemy()

    def _init_sqlite_schema(self) -> None:
        assert self._conn is not None
        self._conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._table} (
                key        TEXT PRIMARY KEY,
                record_id  TEXT,
                content    TEXT,
                score      REAL,
                metadata   TEXT,
                created_at REAL
            )
            """
        )
        self._conn.commit()

    @staticmethod
    def _row_to_record(row: tuple) -> RetrievalRecord:
        key, record_id, content, score, metadata_json, created_at = row
        return RetrievalRecord(
            key=key,
            record_id=record_id,
            content=content,
            score=score,
            metadata=json.loads(metadata_json or "{}"),
            created_at=created_at,
        )

    # ------------------------------------------------------------------
    # Internal — SQLAlchemy path (PostgreSQL, MySQL, etc.)
    # ------------------------------------------------------------------

    def _init_sqlalchemy(self) -> None:
        try:
            from sqlalchemy import (  # type: ignore[import]
                Column, Float, MetaData, String, Table, Text, create_engine
            )
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            self._engine = create_engine(self._connection_string)
            meta = MetaData()
            self._sa_table = Table(
                self._table,
                meta,
                Column("key", String(512), primary_key=True),
                Column("record_id", String(64)),
                Column("content", Text),
                Column("score", Float, default=1.0),
                Column("metadata", Text),
                Column("created_at", Float, default=time.time),
            )
            meta.create_all(self._engine)
        except Exception:  # noqa: BLE001
            self._engine = None

    def _sqlalchemy_upsert(self, record: RetrievalRecord) -> None:
        if self._engine is None:
            return
        with self._engine.connect() as conn:
            conn.execute(
                self._sa_table.insert().prefix_with("OR REPLACE"),
                {
                    "key": record.key,
                    "record_id": record.record_id,
                    "content": record.content,
                    "score": record.score,
                    "metadata": json.dumps(record.metadata),
                    "created_at": record.created_at,
                },
            )
            conn.commit()

    def _sqlalchemy_get(self, key: str) -> RetrievalRecord | None:
        if self._engine is None:
            return None
        with self._engine.connect() as conn:
            row = conn.execute(
                self._sa_table.select().where(self._sa_table.c.key == key)
            ).fetchone()
        if row is None:
            return None
        return RetrievalRecord(
            key=row.key,
            record_id=row.record_id,
            content=row.content,
            score=row.score,
            metadata=json.loads(row.metadata or "{}"),
            created_at=row.created_at,
        )

    def _sqlalchemy_search(self, query: str, *, limit: int) -> list[RetrievalRecord]:
        if self._engine is None:
            return []
        with self._engine.connect() as conn:
            rows = conn.execute(
                self._sa_table.select()
                .where(self._sa_table.c.content.like(f"%{query}%"))
                .order_by(self._sa_table.c.score.desc())
                .limit(limit)
            ).fetchall()
        return [
            RetrievalRecord(
                key=r.key,
                record_id=r.record_id,
                content=r.content,
                score=r.score,
                metadata=json.loads(r.metadata or "{}"),
                created_at=r.created_at,
            )
            for r in rows
        ]

    def _sqlalchemy_delete(self, key: str) -> bool:
        if self._engine is None:
            return False
        with self._engine.connect() as conn:
            result = conn.execute(
                self._sa_table.delete().where(self._sa_table.c.key == key)
            )
            conn.commit()
        return result.rowcount > 0

    def _sqlalchemy_count(self) -> int:
        if self._engine is None:
            return 0
        from sqlalchemy import func  # type: ignore[import]
        with self._engine.connect() as conn:
            return conn.execute(
                self._sa_table.select().with_only_columns(func.count())
            ).scalar() or 0

    def __repr__(self) -> str:
        return f"SQLStore(connection={self._connection_string!r}, table={self._table!r})"
