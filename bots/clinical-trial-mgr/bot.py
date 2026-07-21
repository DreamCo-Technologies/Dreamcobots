"""
Clinical Trial Manager — Manages clinical trials with participant tracking and regulatory documentation.
"""
# GLOBAL AI SOURCES FLOW
from __future__ import annotations

import sqlite3
import sys
import os
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
from bots.clinical_trial_mgr.tiers import BOT_FEATURES, get_bot_tier_info


class ClinicalTrialMgrBotError(Exception):
    pass


class ClinicalTrialMgrBotTierError(ClinicalTrialMgrBotError):
    pass


class ClinicalTrialMgrBot:
    """Clinical Trial Manager: Manages clinical trials with participant tracking and regulatory documentation.

    Division  : DreamScience
    Category  : clinical-trials
    Revenue   : Enterprise license
    Users     : Clinical research coordinators, sponsors
    """

    def __init__(self, tier: Tier = Tier.ENTERPRISE, db_path: str = ':memory:'):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._flow = GlobalAISourcesFlow(bot_name="ClinicalTrialMgrBot")
        self._db = self._init_db(db_path)

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def _init_db(self, db_path: str):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS records (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                category   TEXT    NOT NULL,
                title      TEXT    NOT NULL,
                data       TEXT,
                status     TEXT    DEFAULT 'active',
                created_at TEXT    NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type  TEXT    NOT NULL,
                payload     TEXT,
                occurred_at TEXT    NOT NULL
            );
            """
        )
        conn.commit()
        return conn

    # ------------------------------------------------------------------
    # Core capabilities
    # ------------------------------------------------------------------


    def track(self, item: str, value: Any, context: dict | None = None) -> dict:
        """Record a tracking event for *item* with *value*."""
        ts = datetime.now(timezone.utc).isoformat()
        record = {"item": item, "value": value, "context": context or {}, "tracked_at": ts}
        self._db.execute(
            "INSERT INTO records (category, title, data, status, created_at) VALUES (?,?,?,?,?)",
            ("tracking", item, str(record), "active", ts),
        )
        self._db.commit()
        return record

    def get_tracked_items(self, item: str | None = None) -> list:
        """Return tracked records, optionally filtered by *item* name."""
        if item:
            rows = self._db.execute(
                "SELECT * FROM records WHERE category='tracking' AND title=? ORDER BY id DESC",
                (item,),
            ).fetchall()
        else:
            rows = self._db.execute(
                "SELECT * FROM records WHERE category='tracking' ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def analyze(self, subject: str, data: dict | None = None) -> dict:
        """Run an analysis on *subject* with optional *data* context."""
        ts = datetime.now(timezone.utc).isoformat()
        payload = data or {}
        result = {
            "subject": subject,
            "metrics": {k: (float(v) if str(v).replace(".", "", 1).lstrip("-").isdigit() else v)
                        for k, v in payload.items()},
            "insights": [f"Key metric '{k}' noted for {subject}" for k in list(payload)[:3]],
            "analyzed_at": ts,
            "tier_used": self.tier.value,
        }
        self._db.execute(
            "INSERT INTO records (category, title, data, status, created_at) VALUES (?,?,?,?,?)",
            ("analysis", subject, str(result), "active", ts),
        )
        self._db.commit()
        return result

    def run_workflow(self, workflow_name: str, payload: dict | None = None) -> dict:
        """Execute a named workflow with optional *payload*."""
        ts = datetime.now(timezone.utc).isoformat()
        steps_completed = []
        for step in ["initialize", "validate", "execute", "finalize"]:
            steps_completed.append({"step": step, "status": "ok", "at": ts})
        result = {
            "workflow": workflow_name,
            "steps": steps_completed,
            "payload": payload or {},
            "completed_at": ts,
            "tier_used": self.tier.value,
        }
        self._db.execute(
            "INSERT INTO events (event_type, payload, occurred_at) VALUES (?,?,?)",
            (f"workflow:{workflow_name}", str(result), ts),
        )
        self._db.commit()
        return result

    def create_record(self, category: str, title: str, data: dict | None = None) -> dict:
        """Create a new managed record."""
        ts = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "INSERT INTO records (category, title, data, status, created_at) VALUES (?,?,?,?,?)",
            (category, title, str(data or {}), "active", ts),
        )
        self._db.commit()
        row_id = self._db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": row_id, "category": category, "title": title, "created_at": ts}

    def list_records(self, category: str | None = None, status: str | None = None) -> list:
        """Return managed records filtered by *category* and/or *status*."""
        sql = "SELECT * FROM records WHERE 1=1"
        params: list = []
        if category:
            sql += " AND category=?"
            params.append(category)
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY id DESC"
        return [dict(r) for r in self._db.execute(sql, params).fetchall()]

    def update_record_status(self, record_id: int, status: str) -> dict:
        """Update the status of an existing record."""
        ts = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "UPDATE records SET status=?, updated_at=? WHERE id=?",
            (status, ts, record_id),
        )
        self._db.commit()
        return {"id": record_id, "status": status, "updated_at": ts}

    def send_notification(self, recipient: str, message: str,
                          channel: str = "email", priority: str = "normal") -> dict:
        """Send a notification to *recipient* via *channel*."""
        ts = datetime.now(timezone.utc).isoformat()
        notification = {
            "recipient": recipient,
            "message": message,
            "channel": channel,
            "priority": priority,
            "status": "sent",
            "sent_at": ts,
        }
        self._db.execute(
            "INSERT INTO events (event_type, payload, occurred_at) VALUES (?,?,?)",
            (f"notification:{channel}", str(notification), ts),
        )
        self._db.commit()
        return notification

    def schedule_event(self, title: str, scheduled_for: str, details: dict | None = None) -> dict:
        """Schedule an event or appointment."""
        ts = datetime.now(timezone.utc).isoformat()
        payload = {"scheduled_for": scheduled_for, "details": details or {}}
        self._db.execute(
            "INSERT INTO records (category, title, data, status, created_at) VALUES (?,?,?,?,?)",
            ("event", title, str(payload), "scheduled", ts),
        )
        self._db.commit()
        row = self._db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": row, "title": title, "scheduled_for": scheduled_for, "created_at": ts}

    def get_schedule(self, status: str | None = None) -> list:
        """Return scheduled events, optionally filtered by *status*."""
        query = "SELECT * FROM records WHERE category='event'"
        params: list = []
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY id DESC"
        return [dict(r) for r in self._db.execute(query, params).fetchall()]

    def score_item(self, item_id: str, criteria: dict) -> dict:
        """Score *item_id* against the provided *criteria* dict."""
        if not criteria:
            raise ClinicalTrialMgrBotError("criteria must not be empty")
        score = sum(
            min(max(int(v), 0), 10) for v in criteria.values()
            if str(v).lstrip("-").isdigit()
        )
        ts = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "INSERT INTO records (category, title, data, status, created_at) VALUES (?,?,?,?,?)",
            ("score", item_id, str({"criteria": criteria, "score": score}), "active", ts),
        )
        self._db.commit()
        return {"item_id": item_id, "score": score, "criteria_count": len(criteria), "scored_at": ts}

    # ------------------------------------------------------------------
    # Tier & Pipeline
    # ------------------------------------------------------------------

    def describe_tier(self) -> dict:
        """Return tier information for this bot."""
        return get_bot_tier_info(self.tier)

    def run(self) -> dict:
        """Execute the bot's default pipeline via GlobalAISourcesFlow."""
        return self._flow.run_pipeline(
            raw_data={"bot": "ClinicalTrialMgrBot", "tier": self.tier.value},
        )

    def get_summary(self) -> dict:
        """Return an operational summary."""
        total = self._db.execute('SELECT COUNT(*) FROM records').fetchone()[0]
        active = self._db.execute(
            "SELECT COUNT(*) FROM records WHERE status='active'"
        ).fetchone()[0]
        return {
            "bot": "ClinicalTrialMgrBot",
            "division": "DreamScience",
            "tier": self.tier.value,
            "total_records": total,
            "active_records": active,
            "price_range": "$999/mo",
        }
