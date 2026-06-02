"""Bot version history and rollback support using PostgreSQL snapshots."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor


@dataclass
class VersionSnapshot:
    bot_id: str
    version: str
    config_hash: str
    deployed_at: str
    deployed_by: str


class VersionHistory:
    """Persist up to 50 version snapshots per bot and roll back on demand."""

    def __init__(self, dsn: str | None = None) -> None:
        self.conn = psycopg2.connect(dsn or os.getenv("DATABASE_URL", "")) if (dsn or os.getenv("DATABASE_URL")) else None
        if self.conn is not None:
            self.conn.autocommit = True
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bot_version_history (
                        bot_id TEXT NOT NULL,
                        version TEXT NOT NULL,
                        config_hash TEXT NOT NULL,
                        deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        deployed_by TEXT NOT NULL,
                        payload JSONB NOT NULL,
                        PRIMARY KEY (bot_id, version)
                    )
                    """
                )

    def snapshot(self, bot_id: str, payload: dict[str, Any], deployed_by: str = "system") -> VersionSnapshot:
        if self.conn is None:
            raise RuntimeError("DATABASE_URL is required")
        version = payload.get("version", "1.0.0")
        config_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO bot_version_history (bot_id, version, config_hash, deployed_by, payload) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (bot_id, version) DO UPDATE SET payload = EXCLUDED.payload",
                (bot_id, version, config_hash, deployed_by, Json(payload)),
            )
            cur.execute(
                "DELETE FROM bot_version_history WHERE ctid IN (SELECT ctid FROM bot_version_history WHERE bot_id = %s ORDER BY deployed_at DESC OFFSET 50)",
                (bot_id,),
            )
            cur.execute("SELECT bot_id, version, config_hash, deployed_at::text, deployed_by FROM bot_version_history WHERE bot_id = %s AND version = %s", (bot_id, version))
            row = cur.fetchone()
        return VersionSnapshot(**row)

    def rollback(self, bot_id: str, version: str) -> dict[str, Any]:
        if self.conn is None:
            raise RuntimeError("DATABASE_URL is required")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT payload FROM bot_version_history WHERE bot_id = %s AND version = %s", (bot_id, version))
            row = cur.fetchone()
        if row is None:
            raise KeyError(f"No snapshot for {bot_id} version {version}")
        return row["payload"]
