"""
3D Asset Manager — Manages 3D assets with texture library and model versioning.
"""
# GLOBAL AI SOURCES FLOW
from __future__ import annotations

import sqlite3
import sys
import os
import importlib.util
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'ai-models-integration'))
from framework import GlobalAISourcesFlow  # noqa: F401
from tiers import Tier, get_tier_config, get_upgrade_path

_tiers_spec = importlib.util.spec_from_file_location(
    "_3d_asset_mgr_tiers",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiers.py"),
)
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
BOT_FEATURES = _tiers_mod.BOT_FEATURES
get_bot_tier_info = _tiers_mod.get_bot_tier_info


class AssetManagerBotError(Exception):
    pass


class AssetManagerBotTierError(AssetManagerBotError):
    pass


class ThreeDAssetManagerBot:
    """3D Asset Manager: Manages 3D assets with texture library and model versioning.

    Division  : DreamArts
    Category  : 3d-design
    Revenue   : Enterprise license
    Users     : 3D artists, game studios, VFX houses
    """

    def __init__(self, tier: Tier = Tier.ENTERPRISE, db_path: str = ':memory:'):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._flow = GlobalAISourcesFlow(bot_name="ThreeDAssetManagerBot")
        self._db = self._init_db(db_path)

    def _init_db(self, db_path: str):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS assets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                asset_type TEXT    NOT NULL,
                format     TEXT,
                version    INTEGER DEFAULT 1,
                lod_level  TEXT,
                tags       TEXT,
                file_path  TEXT,
                created_at TEXT    NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS textures (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                resolution TEXT,
                format     TEXT,
                asset_id   INTEGER,
                created_at TEXT    NOT NULL
            );
        """)
        conn.commit()
        return conn

    def add_asset(self, name: str, asset_type: str, format: str = "fbx",
                  file_path: str = "", tags: list | None = None) -> dict:
        """Add a 3D asset to the catalog."""
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            "INSERT INTO assets (name, asset_type, format, file_path, tags, created_at) VALUES (?,?,?,?,?,?)",
            (name, asset_type, format, file_path, str(tags or []), ts),
        )
        self._db.commit()
        return {"id": cur.lastrowid, "name": name, "asset_type": asset_type,
                "format": format, "version": 1, "created_at": ts}

    def get_assets(self, asset_type: str | None = None) -> list:
        """Return all assets, optionally filtered by *asset_type*."""
        if asset_type:
            rows = self._db.execute(
                "SELECT * FROM assets WHERE asset_type=? ORDER BY id DESC", (asset_type,)
            ).fetchall()
        else:
            rows = self._db.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def add_texture(self, name: str, resolution: str = "2K",
                    format: str = "png", asset_id: int | None = None) -> dict:
        """Add a texture to the library."""
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            "INSERT INTO textures (name, resolution, format, asset_id, created_at) VALUES (?,?,?,?,?)",
            (name, resolution, format, asset_id, ts),
        )
        self._db.commit()
        return {"id": cur.lastrowid, "name": name, "resolution": resolution,
                "format": format, "asset_id": asset_id, "created_at": ts}

    def version_asset(self, asset_id: int) -> dict:
        """Increment the version number of an asset."""
        ts = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "UPDATE assets SET version=version+1, updated_at=? WHERE id=?", (ts, asset_id)
        )
        self._db.commit()
        row = self._db.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
        return dict(row) if row else {"error": "asset not found"}

    def optimize_lod(self, asset_id: int, lod_level: str = "medium") -> dict:
        """Set LOD optimization level for a model."""
        ts = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "UPDATE assets SET lod_level=?, updated_at=? WHERE id=?", (lod_level, ts, asset_id)
        )
        self._db.commit()
        return {"asset_id": asset_id, "lod_level": lod_level, "optimized_at": ts}

    def describe_tier(self) -> dict:
        return get_bot_tier_info(self.tier)

    def run(self) -> dict:
        return self._flow.run_pipeline(
            raw_data={"bot": "ThreeDAssetManagerBot", "tier": self.tier.value},
        )

    def get_summary(self) -> dict:
        assets = self._db.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        textures = self._db.execute("SELECT COUNT(*) FROM textures").fetchone()[0]
        return {
            "bot": "ThreeDAssetManagerBot",
            "division": "DreamArts",
            "tier": self.tier.value,
            "total_assets": assets,
            "total_textures": textures,
        }
