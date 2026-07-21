"""
Bot Performance Database — SQLite-backed tracking for DreamCo bots.

Stores bot activity, KPI scores, and historical performance data so the
AI Learning System and Control Center can make smarter, data-driven
decisions instead of relying on random scoring.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.ai_learning_system.database import BotPerformanceDB

    db = BotPerformanceDB()          # in-memory (default)
    db = BotPerformanceDB("bots.db") # persistent file

    db.record_run("affiliate_bot", {"revenue_usd": 42.5, "leads_converted": 3})
    print(db.get_kpi_summary("affiliate_bot"))
    print(db.get_leaderboard())
"""

from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS bot_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_name    TEXT    NOT NULL,
    run_at      TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'ok',
    kpis        TEXT    NOT NULL DEFAULT '{}',
    notes       TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS bot_scores (
    bot_name        TEXT PRIMARY KEY,
    efficiency_score REAL DEFAULT 0.0,
    roi_score        REAL DEFAULT 0.0,
    reliability_score REAL DEFAULT 100.0,
    composite_score  REAL DEFAULT 0.0,
    total_runs       INTEGER DEFAULT 0,
    failed_runs      INTEGER DEFAULT 0,
    last_updated     TEXT
);
"""


class BotPerformanceDB:
    """
    Lightweight SQLite database for tracking bot performance metrics.

    Parameters
    ----------
    db_path : str
        Path to SQLite database file.  Use ``":memory:"`` (the default) for
        an in-process, non-persistent store useful for testing.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_run(
        self,
        bot_name: str,
        kpis: Optional[dict] = None,
        status: str = "ok",
        notes: str = "",
    ) -> dict:
        """Record a single bot run with associated KPIs.

        Parameters
        ----------
        bot_name : str
            Unique name of the bot (e.g. ``"affiliate_bot"``).
        kpis : dict, optional
            Key-performance indicators for this run.  Supported keys:

            - ``revenue_usd`` — revenue generated (float)
            - ``leads_converted`` — number of leads converted (int)
            - ``tasks_completed`` — tasks finished this run (int)
            - ``error_count`` — errors encountered (int)
            - ``response_time_ms`` — average response time in ms (float)
        status : str
            ``"ok"`` or ``"error"``.
        notes : str
            Free-form notes about the run.

        Returns
        -------
        dict
            The recorded run entry.
        """
        kpis = kpis or {}
        run_at = datetime.now(timezone.utc).isoformat()
        kpis_json = json.dumps(kpis)

        self._conn.execute(
            "INSERT INTO bot_runs (bot_name, run_at, status, kpis, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (bot_name, run_at, status, kpis_json, notes),
        )
        self._conn.commit()
        self._update_scores(bot_name, kpis, status)

        return {
            "bot_name": bot_name,
            "run_at": run_at,
            "status": status,
            "kpis": kpis,
            "notes": notes,
        }

    def _update_scores(self, bot_name: str, kpis: dict, status: str) -> None:
        """Recompute composite KPI scores for a bot after a new run."""
        row = self._conn.execute(
            "SELECT * FROM bot_scores WHERE bot_name = ?", (bot_name,)
        ).fetchone()

        if row:
            total_runs = row["total_runs"] + 1
            failed_runs = row["failed_runs"] + (1 if status == "error" else 0)
            # Weighted rolling average for efficiency and ROI
            n = total_runs
            revenue = kpis.get("revenue_usd", 0.0)
            tasks = kpis.get("tasks_completed", 0)
            errors = kpis.get("error_count", 0)
            resp_ms = kpis.get("response_time_ms", 0.0)

            old_efficiency = row["efficiency_score"]
            old_roi = row["roi_score"]

            # Efficiency: tasks completed vs errors, normalised 0–100
            run_efficiency = max(0.0, min(100.0, (tasks * 10) - (errors * 5)))
            efficiency_score = round(
                (old_efficiency * (n - 1) + run_efficiency) / n, 2
            )

            # ROI: revenue contribution, normalised 0–100 (cap at $500/run = 100)
            run_roi = min(100.0, (revenue / 500.0) * 100.0)
            roi_score = round((old_roi * (n - 1) + run_roi) / n, 2)

            # Reliability: % of successful runs
            reliability_score = round((1 - failed_runs / total_runs) * 100, 2)

            # Response speed contribution (lower is better; 0 ms = 100, 5000 ms = 0)
            speed_score = max(0.0, min(100.0, 100.0 - (resp_ms / 50.0)))

            composite_score = round(
                0.30 * efficiency_score
                + 0.30 * roi_score
                + 0.25 * reliability_score
                + 0.15 * speed_score,
                2,
            )

            self._conn.execute(
                """UPDATE bot_scores SET
                    efficiency_score  = ?,
                    roi_score         = ?,
                    reliability_score = ?,
                    composite_score   = ?,
                    total_runs        = ?,
                    failed_runs       = ?,
                    last_updated      = ?
                WHERE bot_name = ?""",
                (
                    efficiency_score,
                    roi_score,
                    reliability_score,
                    composite_score,
                    total_runs,
                    failed_runs,
                    datetime.now(timezone.utc).isoformat(),
                    bot_name,
                ),
            )
        else:
            tasks = kpis.get("tasks_completed", 0)
            errors = kpis.get("error_count", 0)
            revenue = kpis.get("revenue_usd", 0.0)
            resp_ms = kpis.get("response_time_ms", 0.0)
            failed = 1 if status == "error" else 0

            efficiency_score = round(max(0.0, min(100.0, (tasks * 10) - (errors * 5))), 2)
            roi_score = round(min(100.0, (revenue / 500.0) * 100.0), 2)
            reliability_score = 0.0 if status == "error" else 100.0
            speed_score = max(0.0, min(100.0, 100.0 - (resp_ms / 50.0)))
            composite_score = round(
                0.30 * efficiency_score
                + 0.30 * roi_score
                + 0.25 * reliability_score
                + 0.15 * speed_score,
                2,
            )

            self._conn.execute(
                """INSERT INTO bot_scores
                    (bot_name, efficiency_score, roi_score, reliability_score,
                     composite_score, total_runs, failed_runs, last_updated)
                   VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
                (
                    bot_name,
                    efficiency_score,
                    roi_score,
                    reliability_score,
                    composite_score,
                    failed,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

        self._conn.commit()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_kpi_summary(self, bot_name: str) -> dict:
        """Return the current KPI scores for a single bot.

        Returns
        -------
        dict
            Keys: ``bot_name``, ``efficiency_score``, ``roi_score``,
            ``reliability_score``, ``composite_score``, ``total_runs``,
            ``failed_runs``, ``last_updated``.
        """
        row = self._conn.execute(
            "SELECT * FROM bot_scores WHERE bot_name = ?", (bot_name,)
        ).fetchone()
        if not row:
            return {
                "bot_name": bot_name,
                "efficiency_score": 0.0,
                "roi_score": 0.0,
                "reliability_score": 0.0,
                "composite_score": 0.0,
                "total_runs": 0,
                "failed_runs": 0,
                "last_updated": None,
            }
        return dict(row)

    def get_run_history(
        self,
        bot_name: str,
        limit: int = 50,
    ) -> list:
        """Return recent run history for a bot.

        Parameters
        ----------
        bot_name : str
        limit : int
            Maximum number of rows to return (most recent first).

        Returns
        -------
        list of dict
        """
        rows = self._conn.execute(
            "SELECT * FROM bot_runs WHERE bot_name = ? "
            "ORDER BY id DESC LIMIT ?",
            (bot_name, limit),
        ).fetchall()
        result = []
        for row in rows:
            entry = dict(row)
            entry["kpis"] = json.loads(entry["kpis"])
            result.append(entry)
        return result

    def get_leaderboard(self, top_n: int = 10) -> list:
        """Return the top-N bots ranked by composite score.

        Returns
        -------
        list of dict, sorted by ``composite_score`` descending.
        """
        rows = self._conn.execute(
            "SELECT * FROM bot_scores ORDER BY composite_score DESC LIMIT ?",
            (top_n,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_underperformers(self, threshold: float = 30.0) -> list:
        """Return bots whose composite score is below *threshold*.

        Parameters
        ----------
        threshold : float
            Composite score cutoff (0–100).  Default is 30.

        Returns
        -------
        list of dict
        """
        rows = self._conn.execute(
            "SELECT * FROM bot_scores WHERE composite_score < ? "
            "ORDER BY composite_score ASC",
            (threshold,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all_scores(self) -> list:
        """Return KPI scores for every tracked bot."""
        rows = self._conn.execute(
            "SELECT * FROM bot_scores ORDER BY composite_score DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        """Return aggregate statistics across all tracked bots."""
        total_bots = self._conn.execute(
            "SELECT COUNT(*) FROM bot_scores"
        ).fetchone()[0]
        total_runs = self._conn.execute(
            "SELECT SUM(total_runs) FROM bot_scores"
        ).fetchone()[0] or 0
        avg_composite = self._conn.execute(
            "SELECT AVG(composite_score) FROM bot_scores"
        ).fetchone()[0] or 0.0
        underperformers = self._conn.execute(
            "SELECT COUNT(*) FROM bot_scores WHERE composite_score < 30"
        ).fetchone()[0]
        return {
            "tracked_bots": total_bots,
            "total_runs": total_runs,
            "avg_composite_score": round(avg_composite, 2),
            "underperformers_below_30": underperformers,
        }

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
