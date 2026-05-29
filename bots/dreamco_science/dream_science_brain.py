# GLOBAL AI SOURCES FLOW
"""Shared DreamCo science knowledge store backed by SQLite."""
import sys
import os
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
import sqlite3
from datetime import datetime, timezone

from bots.dreamco_science.evidence_grading import EVIDENCE_RANK, grade_evidence


class DreamScienceBrain:
    """Persist discoveries, updates, and cross-field links for DreamCo science bots."""

    def __init__(self, db_path: str = ":memory:"):
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                evidence_level TEXT NOT NULL,
                source TEXT DEFAULT '',
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_id INTEGER,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(discovery_id) REFERENCES discoveries(id)
            );
            CREATE TABLE IF NOT EXISTS invention_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cross_field_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_id_a INTEGER NOT NULL,
                discovery_id_b INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(discovery_id_a) REFERENCES discoveries(id),
                FOREIGN KEY(discovery_id_b) REFERENCES discoveries(id)
            );
            CREATE TABLE IF NOT EXISTS discovery_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                headline TEXT NOT NULL,
                details TEXT,
                posted_at TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def record_discovery(self, domain, title, summary, evidence_level, source="") -> int:
        level = grade_evidence(evidence_level).value
        cur = self._db.execute(
            "INSERT INTO discoveries (domain, title, summary, evidence_level, source, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (domain, title, summary, level, source, self._now()),
        )
        self._db.execute(
            "INSERT INTO findings (discovery_id, note, created_at) VALUES (?, ?, ?)",
            (cur.lastrowid, summary or title, self._now()),
        )
        self._db.commit()
        return cur.lastrowid

    def get_discoveries(self, domain=None, min_evidence_level=None) -> list[dict]:
        rows = [dict(r) for r in self._db.execute(
            "SELECT * FROM discoveries ORDER BY id DESC"
        ).fetchall()]
        if domain:
            rows = [row for row in rows if row['domain'] == domain]
        if min_evidence_level:
            min_level = grade_evidence(min_evidence_level)
            rows = [
                row for row in rows
                if EVIDENCE_RANK[grade_evidence(row['evidence_level'])] <= EVIDENCE_RANK[min_level]
            ]
        return rows

    def link_discoveries(self, discovery_id_a, discovery_id_b, relationship_type) -> int:
        cur = self._db.execute(
            "INSERT INTO cross_field_links (discovery_id_a, discovery_id_b, relationship_type, created_at) VALUES (?, ?, ?, ?)",
            (discovery_id_a, discovery_id_b, relationship_type, self._now()),
        )
        self._db.commit()
        return cur.lastrowid

    def get_related_discoveries(self, discovery_id) -> list[dict]:
        rows = self._db.execute(
            """
            SELECT l.id AS link_id, l.relationship_type, d.*
            FROM cross_field_links l
            JOIN discoveries d
              ON d.id = CASE
                  WHEN l.discovery_id_a = ? THEN l.discovery_id_b
                  ELSE l.discovery_id_a
              END
            WHERE l.discovery_id_a = ? OR l.discovery_id_b = ?
            ORDER BY l.id DESC
            """,
            (discovery_id, discovery_id, discovery_id),
        ).fetchall()
        return [dict(r) for r in rows]

    def post_update(self, domain, headline, details) -> int:
        cur = self._db.execute(
            "INSERT INTO discovery_updates (domain, headline, details, posted_at) VALUES (?, ?, ?, ?)",
            (domain, headline, details, self._now()),
        )
        self._db.commit()
        return cur.lastrowid

    def get_updates(self, domain=None, limit=10) -> list[dict]:
        query = "SELECT * FROM discovery_updates"
        params = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self._db.execute(query, params).fetchall()]
