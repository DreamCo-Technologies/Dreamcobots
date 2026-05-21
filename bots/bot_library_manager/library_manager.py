"""
Bot Library Manager
===================

Persistent tracker for per-bot library knowledge and mastery scores.
Each bot can register libraries it depends on, update its mastery level,
store free-form learning notes, and retrieve a human-readable summary.

Data is stored in a SQLite database so that knowledge persists across runs
and can be shared across multiple bot processes on the same machine.

Usage
-----
    from bots.bot_library_manager import BotLibraryManager

    mgr = BotLibraryManager("bot_libraries.db")
    mgr.register_library("scraper_bot", "requests", category="http")
    mgr.update_mastery("scraper_bot", "requests", 85.0)
    mgr.store_learning("scraper_bot", "github_workflow",
                       "Use matrix strategy for parallel scraping",
                       source="github", relevance_score=90.0)
    print(mgr.get_library_summary("scraper_bot"))
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from framework import GlobalAISourcesFlow

class BotLibraryManager:
    """Manages per-bot library registrations, mastery levels, and learning notes.

    Parameters
    ----------
    db_path : str
        Filesystem path to the SQLite database file.  Defaults to
        ``"bot_libraries.db"`` in the current working directory.
    """

    def __init__(self, db_path: str = "bot_libraries.db") -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self.flow = GlobalAISourcesFlow(bot_name="BotLibraryManager")
        self._init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        cursor = self._conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS bot_libraries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id      TEXT    NOT NULL,
                library     TEXT    NOT NULL,
                category    TEXT,
                mastery     REAL    DEFAULT 0.0,
                registered  TEXT    NOT NULL,
                UNIQUE(bot_id, library)
            );

            CREATE TABLE IF NOT EXISTS bot_learnings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id          TEXT    NOT NULL,
                topic           TEXT    NOT NULL,
                content         TEXT    NOT NULL,
                source          TEXT,
                relevance_score REAL    DEFAULT 0.0,
                recorded_at     TEXT    NOT NULL
            );
            """
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_library(
        self,
        bot_id: str,
        library: str,
        *,
        category: Optional[str] = None,
    ) -> None:
        """Register a library dependency for *bot_id*.

        If the ``(bot_id, library)`` pair already exists the record is left
        unchanged (idempotent).

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.
        library : str
            Python package / library name.
        category : str, optional
            Informal grouping tag (e.g. ``"http"``, ``"ml"``, ``"db"``).
        """
        now = datetime.now(tz=timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT OR IGNORE INTO bot_libraries (bot_id, library, category, registered)
            VALUES (?, ?, ?, ?)
            """,
            (bot_id, library, category, now),
        )
        self._conn.commit()
        self._run_framework_validation(
            action="register_library",
            payload={"bot_id": bot_id, "library": library, "category": category},
        )

    def update_mastery(self, bot_id: str, library: str, mastery: float) -> None:
        """Update the mastery score for a ``(bot_id, library)`` pair.

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.
        library : str
            Python package / library name (must have been registered first).
        mastery : float
            New mastery score in the range ``[0.0, 100.0]``.
        """
        self._conn.execute(
            """
            UPDATE bot_libraries SET mastery = ?
            WHERE bot_id = ? AND library = ?
            """,
            (mastery, bot_id, library),
        )
        self._conn.commit()
        self._run_framework_validation(
            action="update_mastery",
            payload={"bot_id": bot_id, "library": library, "mastery": mastery},
        )

    def store_learning(
        self,
        bot_id: str,
        topic: str,
        content: str,
        *,
        source: Optional[str] = None,
        relevance_score: float = 0.0,
    ) -> None:
        """Persist a free-form learning note for *bot_id*.

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.
        topic : str
            Short label for the learning (e.g. ``"github_workflow"``).
        content : str
            The learning content / insight text.
        source : str, optional
            Where the knowledge came from (e.g. ``"github"``, ``"docs"``).
        relevance_score : float
            Importance weight in the range ``[0.0, 100.0]``.
        """
        now = datetime.now(tz=timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO bot_learnings
                (bot_id, topic, content, source, relevance_score, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (bot_id, topic, content, source, relevance_score, now),
        )
        self._conn.commit()
        self._run_framework_validation(
            action="store_learning",
            payload={
                "bot_id": bot_id,
                "topic": topic,
                "source": source,
                "relevance_score": relevance_score,
            },
        )

    def get_library_summary(self, bot_id: str) -> Dict[str, Any]:
        """Return a summary dict for all libraries registered to *bot_id*.

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.

        Returns
        -------
        dict
            Keys:
            - ``bot_id`` – the queried bot.
            - ``libraries`` – list of ``{"library", "category", "mastery"}`` dicts.
            - ``learnings`` – list of ``{"topic", "content", "source",
              "relevance_score", "recorded_at"}`` dicts.
        """
        cursor = self._conn.cursor()

        cursor.execute(
            """
            SELECT library, category, mastery
            FROM bot_libraries
            WHERE bot_id = ?
            ORDER BY library
            """,
            (bot_id,),
        )
        libraries: List[Dict[str, Any]] = [
            {"library": row["library"], "category": row["category"], "mastery": row["mastery"]}
            for row in cursor.fetchall()
        ]

        cursor.execute(
            """
            SELECT topic, content, source, relevance_score, recorded_at
            FROM bot_learnings
            WHERE bot_id = ?
            ORDER BY recorded_at DESC
            """,
            (bot_id,),
        )
        learnings: List[Dict[str, Any]] = [
            {
                "topic": row["topic"],
                "content": row["content"],
                "source": row["source"],
                "relevance_score": row["relevance_score"],
                "recorded_at": row["recorded_at"],
            }
            for row in cursor.fetchall()
        ]

        summary = {"bot_id": bot_id, "libraries": libraries, "learnings": learnings}
        self._run_framework_validation(
            action="get_library_summary",
            payload={"bot_id": bot_id, "library_count": len(libraries), "learning_count": len(learnings)},
        )
        return summary

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def _run_framework_validation(self, *, action: str, payload: Dict[str, Any]) -> None:
        """Run the mandatory GlobalAISourcesFlow pipeline after each public operation."""
        self.flow.run_pipeline(
            raw_data={
                "domain": "bot_library_management",
                "action": action,
                "payload": payload,
            },
            learning_method="supervised",
        )
