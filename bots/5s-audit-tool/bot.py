"""
5S Workplace Audit Tool — Conducts 5S workplace audits with photo documentation and scoring.
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
    "_5s_audit_tiers",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiers.py"),
)
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
BOT_FEATURES = _tiers_mod.BOT_FEATURES
get_bot_tier_info = _tiers_mod.get_bot_tier_info

# The five S pillars
FIVE_S = ["Sort", "Set_in_Order", "Shine", "Standardize", "Sustain"]


class FiveSAuditBotError(Exception):
    pass


class FiveSAuditBotTierError(FiveSAuditBotError):
    pass


class FiveSAuditBot:
    """5S Workplace Audit Tool: Conducts 5S audits with photo documentation and scoring.

    Division  : DreamProduction
    Category  : workplace-org
    Revenue   : SaaS subscription
    Users     : CI coordinators, production supervisors
    """

    def __init__(self, tier: Tier = Tier.FREE, db_path: str = ':memory:'):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._flow = GlobalAISourcesFlow(bot_name="FiveSAuditBot")
        self._db = self._init_db(db_path)

    def _init_db(self, db_path: str):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS audits (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                location     TEXT    NOT NULL,
                auditor      TEXT    NOT NULL,
                sort_score   INTEGER DEFAULT 0,
                set_score    INTEGER DEFAULT 0,
                shine_score  INTEGER DEFAULT 0,
                std_score    INTEGER DEFAULT 0,
                sustain_score INTEGER DEFAULT 0,
                total_score  INTEGER DEFAULT 0,
                notes        TEXT,
                status       TEXT    DEFAULT 'open',
                created_at   TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS actions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id   INTEGER NOT NULL,
                pillar     TEXT    NOT NULL,
                description TEXT   NOT NULL,
                assignee   TEXT,
                due_date   TEXT,
                status     TEXT    DEFAULT 'open',
                created_at TEXT    NOT NULL
            );
        """)
        conn.commit()
        return conn

    def run_audit(self, location: str, auditor: str, scores: dict | None = None) -> dict:
        """Run a 5S audit for *location*.

        *scores* should be a dict with keys sort, set, shine, standardize, sustain
        each valued 0-10.
        """
        s = scores or {}
        sort_s = min(max(int(s.get("sort", 5)), 0), 10)
        set_s = min(max(int(s.get("set", 5)), 0), 10)
        shine_s = min(max(int(s.get("shine", 5)), 0), 10)
        std_s = min(max(int(s.get("standardize", 5)), 0), 10)
        sustain_s = min(max(int(s.get("sustain", 5)), 0), 10)
        total = sort_s + set_s + shine_s + std_s + sustain_s
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            """INSERT INTO audits
               (location, auditor, sort_score, set_score, shine_score, std_score,
                sustain_score, total_score, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (location, auditor, sort_s, set_s, shine_s, std_s, sustain_s, total, ts),
        )
        self._db.commit()
        return {
            "audit_id": cur.lastrowid,
            "location": location,
            "auditor": auditor,
            "scores": {"sort": sort_s, "set": set_s, "shine": shine_s,
                       "standardize": std_s, "sustain": sustain_s},
            "total_score": total,
            "max_score": 50,
            "grade": "A" if total >= 45 else "B" if total >= 35 else "C" if total >= 25 else "D",
            "conducted_at": ts,
        }

    def get_audits(self, location: str | None = None) -> list:
        """Return audit history, optionally filtered by *location*."""
        if location:
            rows = self._db.execute(
                "SELECT * FROM audits WHERE location=? ORDER BY id DESC", (location,)
            ).fetchall()
        else:
            rows = self._db.execute("SELECT * FROM audits ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def assign_action(self, audit_id: int, pillar: str, description: str,
                      assignee: str = "", due_date: str = "") -> dict:
        """Create a corrective action item for an audit."""
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            "INSERT INTO actions (audit_id, pillar, description, assignee, due_date, created_at) VALUES (?,?,?,?,?,?)",
            (audit_id, pillar, description, assignee, due_date, ts),
        )
        self._db.commit()
        return {"action_id": cur.lastrowid, "audit_id": audit_id, "pillar": pillar,
                "description": description, "assignee": assignee, "due_date": due_date}

    def get_actions(self, audit_id: int | None = None, status: str | None = None) -> list:
        """Return corrective actions, optionally filtered."""
        sql = "SELECT * FROM actions WHERE 1=1"
        params: list = []
        if audit_id is not None:
            sql += " AND audit_id=?"
            params.append(audit_id)
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY id DESC"
        return [dict(r) for r in self._db.execute(sql, params).fetchall()]

    def get_trend(self, location: str) -> dict:
        """Return score trend for *location* across all audits."""
        rows = self._db.execute(
            "SELECT * FROM audits WHERE location=? ORDER BY id ASC", (location,)
        ).fetchall()
        totals = [r["total_score"] for r in rows]
        return {
            "location": location,
            "audit_count": len(totals),
            "scores": totals,
            "avg_score": round(sum(totals) / len(totals), 2) if totals else 0,
            "trend": "improving" if len(totals) >= 2 and totals[-1] > totals[0] else
                     "declining" if len(totals) >= 2 and totals[-1] < totals[0] else "stable",
        }

    def describe_tier(self) -> dict:
        return get_bot_tier_info(self.tier)

    def run(self) -> dict:
        return self._flow.run_pipeline(
            raw_data={"bot": "FiveSAuditBot", "tier": self.tier.value},
        )

    def get_summary(self) -> dict:
        total = self._db.execute("SELECT COUNT(*) FROM audits").fetchone()[0]
        actions_open = self._db.execute(
            "SELECT COUNT(*) FROM actions WHERE status='open'"
        ).fetchone()[0]
        return {
            "bot": "FiveSAuditBot",
            "division": "DreamProduction",
            "tier": self.tier.value,
            "total_audits": total,
            "open_actions": actions_open,
        }
