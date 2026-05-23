"""
registry_db.py — Production-ready SQLite schema + auto-ingestion pipeline.

Provides:
  - RegistryDB  : initialize, upsert, query the local provider database
  - ingest_catalog() : bulk-load PROVIDER_CATALOG into the DB
  - export_json()     : write all 200 providers to a JSON file
"""

from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bots.ai_provider_registry.provider_schema import AIProviderObject
from bots.ai_provider_registry.provider_catalog import PROVIDER_CATALOG

# Default DB path — can be overridden via env var
_DEFAULT_DB = Path(__file__).parent.parent.parent / "data" / "ai_provider_registry.db"


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------
_DDL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS providers (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    pricing             TEXT NOT NULL,
    categories          TEXT NOT NULL,   -- JSON array
    core_skill          TEXT NOT NULL,
    best_at             TEXT NOT NULL,
    agent_role          TEXT NOT NULL,
    bundle_fit          TEXT NOT NULL,   -- JSON array
    tier                TEXT NOT NULL,
    api_access          INTEGER NOT NULL DEFAULT 1,
    embedding_ready     INTEGER NOT NULL DEFAULT 0,
    risk_level          TEXT NOT NULL DEFAULT 'low',
    competition_cluster TEXT NOT NULL DEFAULT 'general',
    is_open_source      INTEGER NOT NULL DEFAULT 0,
    notes               TEXT NOT NULL DEFAULT '',
    ingested_at         TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_clusters (
    cluster_id   TEXT NOT NULL,
    provider_id  TEXT NOT NULL,
    PRIMARY KEY (cluster_id, provider_id),
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);

CREATE TABLE IF NOT EXISTS ingest_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source     TEXT NOT NULL,
    count      INTEGER NOT NULL,
    status     TEXT NOT NULL,
    ran_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_providers_tier            ON providers(tier);
CREATE INDEX IF NOT EXISTS idx_providers_pricing         ON providers(pricing);
CREATE INDEX IF NOT EXISTS idx_providers_cluster         ON providers(competition_cluster);
CREATE INDEX IF NOT EXISTS idx_providers_embedding_ready ON providers(embedding_ready);
"""


class RegistryDB:
    """Thread-safe (per connection) SQLite registry for AI providers."""

    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        path = Path(db_path) if db_path else Path(
            os.environ.get("AI_REGISTRY_DB", str(_DEFAULT_DB))
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    def connect(self) -> "RegistryDB":
        self._conn = sqlite3.connect(str(self._path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)
        self._conn.commit()
        return self

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "RegistryDB":
        return self.connect()

    def __exit__(self, *_) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def upsert(self, provider: AIProviderObject) -> None:
        """Insert or replace a provider record."""
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO providers (
                id, name, pricing, categories, core_skill, best_at,
                agent_role, bundle_fit, tier, api_access, embedding_ready,
                risk_level, competition_cluster, is_open_source, notes,
                ingested_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                pricing=excluded.pricing,
                categories=excluded.categories,
                core_skill=excluded.core_skill,
                best_at=excluded.best_at,
                agent_role=excluded.agent_role,
                bundle_fit=excluded.bundle_fit,
                tier=excluded.tier,
                api_access=excluded.api_access,
                embedding_ready=excluded.embedding_ready,
                risk_level=excluded.risk_level,
                competition_cluster=excluded.competition_cluster,
                is_open_source=excluded.is_open_source,
                notes=excluded.notes,
                updated_at=excluded.updated_at
            """,
            (
                provider.id,
                provider.name,
                provider.pricing,
                json.dumps(provider.categories),
                provider.core_skill,
                provider.best_at,
                provider.agent_role,
                json.dumps(provider.bundle_fit),
                provider.tier,
                int(provider.api_access),
                int(provider.embedding_ready),
                provider.risk_level,
                provider.competition_cluster,
                int(provider.open_source),
                provider.notes,
                now,
                now,
            ),
        )
        # Refresh cluster index
        self._conn.execute(
            "DELETE FROM provider_clusters WHERE provider_id=?", (provider.id,)
        )
        if provider.competition_cluster:
            self._conn.execute(
                "INSERT OR IGNORE INTO provider_clusters VALUES (?,?)",
                (provider.competition_cluster, provider.id),
            )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get(self, provider_id: str) -> Optional[dict]:
        """Return a single provider row as a dict, or None."""
        row = self._conn.execute(
            "SELECT * FROM providers WHERE id=?", (provider_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_all(self) -> list[dict]:
        rows = self._conn.execute("SELECT * FROM providers ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def query(
        self,
        *,
        pricing: Optional[str] = None,
        tier: Optional[str] = None,
        cluster: Optional[str] = None,
        embedding_ready: Optional[bool] = None,
        is_open_source: Optional[bool] = None,
    ) -> list[dict]:
        """Flexible filter query; all parameters are optional."""
        conditions, params = [], []
        if pricing:
            conditions.append("pricing = ?")
            params.append(pricing)
        if tier:
            conditions.append("tier = ?")
            params.append(tier)
        if cluster:
            conditions.append("competition_cluster = ?")
            params.append(cluster)
        if embedding_ready is not None:
            conditions.append("embedding_ready = ?")
            params.append(int(embedding_ready))
        if is_open_source is not None:
            conditions.append("is_open_source = ?")
            params.append(int(is_open_source))
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = self._conn.execute(
            f"SELECT * FROM providers {where} ORDER BY name", params
        ).fetchall()
        return [dict(r) for r in rows]

    def cluster_members(self, cluster_id: str) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT p.* FROM providers p
            JOIN provider_clusters c ON p.id = c.provider_id
            WHERE c.cluster_id = ?
            ORDER BY p.name
            """,
            (cluster_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM providers").fetchone()[0]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def stats(self) -> dict:
        by_pricing = {
            r[0]: r[1]
            for r in self._conn.execute(
                "SELECT pricing, COUNT(*) FROM providers GROUP BY pricing"
            ).fetchall()
        }
        by_tier = {
            r[0]: r[1]
            for r in self._conn.execute(
                "SELECT tier, COUNT(*) FROM providers GROUP BY tier"
            ).fetchall()
        }
        by_cluster = {
            r[0]: r[1]
            for r in self._conn.execute(
                "SELECT competition_cluster, COUNT(*) FROM providers GROUP BY competition_cluster ORDER BY COUNT(*) DESC LIMIT 20"
            ).fetchall()
        }
        return {
            "total": self.count(),
            "by_pricing": by_pricing,
            "by_tier": by_tier,
            "top_clusters": by_cluster,
            "embedding_ready": self._conn.execute(
                "SELECT COUNT(*) FROM providers WHERE embedding_ready=1"
            ).fetchone()[0],
            "open_source": self._conn.execute(
                "SELECT COUNT(*) FROM providers WHERE is_open_source=1"
            ).fetchone()[0],
        }


# ---------------------------------------------------------------------------
# Ingestion pipeline
# ---------------------------------------------------------------------------
def ingest_catalog(
    providers: Optional[list[AIProviderObject]] = None,
    db_path: Optional[str | Path] = None,
) -> int:
    """Bulk-upsert all providers from the catalog into the DB. Returns count."""
    providers = providers or PROVIDER_CATALOG
    with RegistryDB(db_path) as db:
        for p in providers:
            db.upsert(p)
        count = db.count()
        db._conn.execute(
            "INSERT INTO ingest_log (source, count, status, ran_at) VALUES (?,?,?,?)",
            ("provider_catalog", len(providers), "ok",
             datetime.now(timezone.utc).isoformat()),
        )
        db._conn.commit()
    return count


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------
def export_json(
    out_path: Optional[str | Path] = None,
    db_path: Optional[str | Path] = None,
) -> Path:
    """Export all providers from DB to a JSON file. Returns the output path."""
    default_out = Path(__file__).parent.parent.parent / "data" / "ai_providers_export.json"
    out = Path(out_path) if out_path else default_out
    out.parent.mkdir(parents=True, exist_ok=True)

    # Use DB if an explicit path is given and exists, or if the default DB exists.
    # Otherwise fall back to the catalog directly (no DB required).
    resolved_db = Path(db_path) if db_path else Path(
        os.environ.get("AI_REGISTRY_DB", str(_DEFAULT_DB))
    )
    if resolved_db.exists():
        with RegistryDB(resolved_db) as db:
            rows = db.list_all()
        if not rows:
            rows = [p.to_dict() for p in PROVIDER_CATALOG]
    else:
        rows = [p.to_dict() for p in PROVIDER_CATALOG]

    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total": len(rows),
        "providers": rows,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


__all__ = ["RegistryDB", "ingest_catalog", "export_json"]
