# GLOBAL AI SOURCES FLOW
"""DreamCo invention voting and credit marketplace."""
import sys
import os
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
import sqlite3
from datetime import datetime, timezone


class DreamCredits:
    """Track user balances for DreamCo invention participation."""

    def __init__(self, db_path: str = ':memory:', connection: sqlite3.Connection | None = None):
        self._db = connection or sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS dream_credits (
                user_id TEXT PRIMARY KEY,
                balance REAL NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dream_credit_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def award(self, user_id, amount, reason) -> float:
        current = self.get_balance(user_id)
        new_balance = current + float(amount)
        self._db.execute(
            "INSERT INTO dream_credits (user_id, balance, updated_at) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET balance=excluded.balance, updated_at=excluded.updated_at",
            (user_id, new_balance, self._now()),
        )
        self._db.execute(
            "INSERT INTO dream_credit_ledger (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
            (user_id, float(amount), reason, self._now()),
        )
        self._db.commit()
        return new_balance

    def get_balance(self, user_id) -> float:
        row = self._db.execute("SELECT balance FROM dream_credits WHERE user_id = ?", (user_id,)).fetchone()
        return float(row[0]) if row else 0.0

    def get_leaderboard(self, limit=10) -> list[dict]:
        rows = self._db.execute(
            "SELECT user_id, balance FROM dream_credits ORDER BY balance DESC, user_id ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


class InventionVoting:
    """Marketplace for submitting, voting on, and simulating invention ideas."""

    def __init__(self, db_path: str = ':memory:'):
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init_db()
        self.credits = DreamCredits(connection=self._db)

    def _init_db(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                domain TEXT NOT NULL,
                vote_count INTEGER NOT NULL DEFAULT 0,
                marked_for_simulation INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                invention_id INTEGER NOT NULL,
                vote_value INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, invention_id),
                FOREIGN KEY(invention_id) REFERENCES inventions(id)
            );
            CREATE TABLE IF NOT EXISTS dream_credits (
                user_id TEXT PRIMARY KEY,
                balance REAL NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def submit_idea(self, user_id, title, description, domain) -> int:
        cur = self._db.execute(
            "INSERT INTO inventions (user_id, title, description, domain, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, description, domain, self._now()),
        )
        self._db.commit()
        self.credits.award(user_id, 2.0, f"Submitted invention idea #{cur.lastrowid}")
        return cur.lastrowid

    def vote(self, user_id, invention_id, vote_value=1) -> int:
        if vote_value not in (1, -1):
            raise ValueError('vote_value must be 1 or -1')
        existing = self._db.execute(
            "SELECT vote_value FROM votes WHERE user_id = ? AND invention_id = ?",
            (user_id, invention_id),
        ).fetchone()
        if existing:
            delta = vote_value - int(existing['vote_value'])
            self._db.execute(
                "UPDATE votes SET vote_value = ?, created_at = ? WHERE user_id = ? AND invention_id = ?",
                (vote_value, self._now(), user_id, invention_id),
            )
        else:
            delta = vote_value
            self._db.execute(
                "INSERT INTO votes (user_id, invention_id, vote_value, created_at) VALUES (?, ?, ?, ?)",
                (user_id, invention_id, vote_value, self._now()),
            )
        self._db.execute(
            "UPDATE inventions SET vote_count = vote_count + ? WHERE id = ?",
            (delta, invention_id),
        )
        self._db.commit()
        self.credits.award(user_id, 0.5 if vote_value > 0 else 0.1, f"Voted on invention #{invention_id}")
        return int(self._db.execute("SELECT vote_count FROM inventions WHERE id = ?", (invention_id,)).fetchone()[0])

    def get_top_inventions(self, limit=10, domain=None) -> list[dict]:
        query = "SELECT * FROM inventions"
        params = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
        query += " ORDER BY vote_count DESC, id ASC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self._db.execute(query, params).fetchall()]

    def get_invention(self, invention_id) -> dict:
        row = self._db.execute("SELECT * FROM inventions WHERE id = ?", (invention_id,)).fetchone()
        return dict(row) if row else {}

    def mark_for_simulation(self, invention_id) -> bool:
        cur = self._db.execute(
            "UPDATE inventions SET marked_for_simulation = 1 WHERE id = ?",
            (invention_id,),
        )
        self._db.commit()
        return cur.rowcount > 0
