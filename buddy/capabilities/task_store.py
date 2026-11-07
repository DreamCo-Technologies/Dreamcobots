"""SQLite-backed, user-scoped task state and append-only audit events.

The authenticated host supplies the user ID. Never trust an HTTP payload to
choose an owner. This module does not execute external actions.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

STATUSES = {"proposed", "approved", "running", "verified", "needs_review", "rejected"}

class TaskStore:
    def __init__(self, path: str):
        self.path = str(Path(path))
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                owner TEXT NOT NULL, id TEXT NOT NULL, payload TEXT NOT NULL,
                status TEXT NOT NULL, PRIMARY KEY(owner,id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL, task_id TEXT NOT NULL, status TEXT NOT NULL,
                recorded_at TEXT NOT NULL)""")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    @staticmethod
    def _validate(owner, task_id):
        if not isinstance(owner, str) or not 1 <= len(owner) <= 128:
            raise ValueError("authenticated owner required")
        if not isinstance(task_id, str) or not 1 <= len(task_id) <= 128:
            raise ValueError("task ID required")

    def put(self, owner: str, packet: dict):
        task_id = packet.get("task_id")
        self._validate(owner, task_id)
        if packet.get("status", "proposed") != "proposed":
            raise ValueError("new tasks must be proposed")
        serialized = json.dumps(packet, allow_nan=False, sort_keys=True)
        if len(serialized) > 50000:
            raise ValueError("task too large")
        with self._connect() as db:
            db.execute("INSERT INTO tasks(owner,id,payload,status) VALUES(?,?,?,?)",
                       (owner, task_id, serialized, "proposed"))
            self._event(db, owner, task_id, "proposed")

    def get(self, owner: str, task_id: str):
        self._validate(owner, task_id)
        with self._connect() as db:
            row = db.execute("SELECT payload,status FROM tasks WHERE owner=? AND id=?",
                             (owner, task_id)).fetchone()
        return None if row is None else {**json.loads(row[0]), "status": row[1]}

    def list(self, owner: str):
        self._validate(owner, "_")
        with self._connect() as db:
            rows = db.execute("SELECT id FROM tasks WHERE owner=? ORDER BY id", (owner,)).fetchall()
        return [self.get(owner, row[0]) for row in rows]

    def transition(self, owner: str, task_id: str, *, expected: str, target: str):
        self._validate(owner, task_id)
        allowed = {
            "proposed": {"approved", "rejected"},
            "approved": {"running", "rejected"},
            "running": {"verified", "needs_review"},
            "needs_review": {"approved", "rejected"},
        }
        if target not in STATUSES or target not in allowed.get(expected, set()):
            raise ValueError("invalid state transition")
        with self._connect() as db:
            changed = db.execute(
                "UPDATE tasks SET status=? WHERE owner=? AND id=? AND status=?",
                (target, owner, task_id, expected)).rowcount
            if changed != 1:
                raise ValueError("task not found or state changed")
            self._event(db, owner, task_id, target)

    @staticmethod
    def _event(db, owner, task_id, status):
        db.execute("INSERT INTO events(owner,task_id,status,recorded_at) VALUES(?,?,?,?)",
                   (owner, task_id, status, datetime.now(timezone.utc).isoformat()))

    def history(self, owner: str, task_id: str):
        self._validate(owner, task_id)
        with self._connect() as db:
            rows = db.execute(
                "SELECT status,recorded_at FROM events WHERE owner=? AND task_id=? ORDER BY sequence",
                (owner, task_id)).fetchall()
        return [{"status": status, "recorded_at": timestamp} for status, timestamp in rows]
