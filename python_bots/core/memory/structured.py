"""
DreamCo OS — Structured Memory (Postgres / SQLite)
====================================================

Relational storage for bot state, run history, and agent metadata.
Uses SQLite by default (zero-config local dev) and Postgres in production
via the ``DATABASE_URL`` environment variable.

Usage::

    mem = StructuredMemory(bot_id="stock_bot")
    mem.upsert_state("portfolio", {"AAPL": 10, "TSLA": 5})
    state = mem.get_state("portfolio")
    mem.record_run(success=True, tokens_used=450, cost_usd=0.009)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

_CREATE_STATE = """
CREATE TABLE IF NOT EXISTS bot_state (
    bot_id      TEXT NOT NULL,
    key         TEXT NOT NULL,
    value       TEXT NOT NULL,
    updated_at  REAL NOT NULL,
    PRIMARY KEY (bot_id, key)
)
"""

_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS bot_runs (
    run_id      TEXT PRIMARY KEY,
    bot_id      TEXT NOT NULL,
    success     INTEGER NOT NULL,
    tokens_used INTEGER,
    cost_usd    REAL,
    duration_s  REAL,
    metadata    TEXT,
    created_at  REAL NOT NULL
)
"""


class StructuredMemory:
    """SQLite/Postgres-backed relational memory for a single bot.

    Parameters
    ----------
    bot_id:
        Owning bot identifier.
    db_url:
        SQLite path or Postgres URL.  Reads ``DATABASE_URL`` env-var; defaults
        to ``.dreamco_state.db`` (SQLite).
    """

    def __init__(self, bot_id: str, db_url: str | None = None) -> None:
        self.bot_id = bot_id
        self._lock = threading.Lock()
        url = db_url or os.getenv("DATABASE_URL", ".dreamco_state.db")

        # Use sqlite3 for file paths; psycopg2 for postgres:// URLs
        if url.startswith("postgres"):
            self._backend = "postgres"
            try:
                import psycopg2  # type: ignore
                self._conn = psycopg2.connect(url)
                logger.debug("StructuredMemory: connected to Postgres")
            except Exception as exc:  # noqa: BLE001
                logger.warning("StructuredMemory: Postgres unavailable (%s) — falling back to SQLite", exc)
                self._conn = sqlite3.connect(".dreamco_state.db", check_same_thread=False)
                self._backend = "sqlite"
        else:
            self._backend = "sqlite"
            self._conn = sqlite3.connect(url, check_same_thread=False)

        with self._lock:
            cur = self._conn.cursor()
            cur.execute(_CREATE_STATE)
            cur.execute(_CREATE_RUNS)
            self._conn.commit()

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def upsert_state(self, key: str, value: Any) -> None:
        """Persist *value* under *key* for this bot."""
        encoded = json.dumps(value)
        with self._lock:
            cur = self._conn.cursor()
            if self._backend == "postgres":
                cur.execute(
                    "INSERT INTO bot_state (bot_id,key,value,updated_at) VALUES (%s,%s,%s,%s) "
                    "ON CONFLICT (bot_id,key) DO UPDATE SET value=EXCLUDED.value, updated_at=EXCLUDED.updated_at",
                    (self.bot_id, key, encoded, time.time()),
                )
            else:
                cur.execute(
                    "INSERT OR REPLACE INTO bot_state (bot_id,key,value,updated_at) VALUES (?,?,?,?)",
                    (self.bot_id, key, encoded, time.time()),
                )
            self._conn.commit()

    def get_state(self, key: str) -> Any | None:
        """Return the stored value for *key*, or ``None``."""
        with self._lock:
            cur = self._conn.cursor()
            ph = "%s" if self._backend == "postgres" else "?"
            cur.execute(
                f"SELECT value FROM bot_state WHERE bot_id={ph} AND key={ph}",
                (self.bot_id, key),
            )
            row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def delete_state(self, key: str) -> None:
        """Remove *key* from state (GDPR-compliant)."""
        with self._lock:
            cur = self._conn.cursor()
            ph = "%s" if self._backend == "postgres" else "?"
            cur.execute(
                f"DELETE FROM bot_state WHERE bot_id={ph} AND key={ph}",
                (self.bot_id, key),
            )
            self._conn.commit()

    # ------------------------------------------------------------------
    # Run history
    # ------------------------------------------------------------------

    def record_run(
        self,
        success: bool,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        duration_s: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a bot run and return the generated run_id."""
        run_id = str(uuid.uuid4())
        with self._lock:
            cur = self._conn.cursor()
            ph = ("%s",) * 8 if self._backend == "postgres" else ("?",) * 8
            cur.execute(
                f"INSERT INTO bot_runs (run_id,bot_id,success,tokens_used,cost_usd,duration_s,metadata,created_at) "
                f"VALUES ({','.join(ph)})",
                (
                    run_id,
                    self.bot_id,
                    int(success),
                    tokens_used,
                    cost_usd,
                    duration_s,
                    json.dumps(metadata or {}),
                    time.time(),
                ),
            )
            self._conn.commit()
        return run_id

    def get_run_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the last *limit* run records for this bot, newest first."""
        with self._lock:
            cur = self._conn.cursor()
            ph = "%s" if self._backend == "postgres" else "?"
            cur.execute(
                f"SELECT run_id,success,tokens_used,cost_usd,duration_s,metadata,created_at "
                f"FROM bot_runs WHERE bot_id={ph} ORDER BY created_at DESC LIMIT {ph if self._backend == 'postgres' else '?'}",
                (self.bot_id, limit),
            )
            rows = cur.fetchall()
        return [
            {
                "run_id": r[0],
                "success": bool(r[1]),
                "tokens_used": r[2],
                "cost_usd": r[3],
                "duration_s": r[4],
                "metadata": json.loads(r[5]) if r[5] else {},
                "created_at": r[6],
            }
            for r in rows
        ]
