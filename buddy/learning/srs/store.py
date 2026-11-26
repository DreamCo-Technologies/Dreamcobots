"""Append-only local SRS event store with idempotent offline synchronization.

SQLite is the local/offline store. PostgreSQL production table definitions live
in the repository migration and shared Drizzle schema.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class IdempotencyConflictError(ValueError):
    """An event ID was reused with a different immutable payload."""


@dataclass(frozen=True)
class RecordReviewResult:
    status: str
    state_updated: bool
    replay_required: bool


class SRSStore:
    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("SRSStore requires a file-backed database for durable offline sync")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _migrate(self) -> None:
        with self._connect() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version > self.SCHEMA_VERSION:
                raise RuntimeError(f"database schema {version} is newer than supported {self.SCHEMA_VERSION}")
            if version == 0:
                conn.executescript("""
                    CREATE TABLE srs_review_events (
                        event_id TEXT PRIMARY KEY,
                        learner_id TEXT NOT NULL,
                        deck_id TEXT NOT NULL,
                        item_id TEXT NOT NULL,
                        division_ids_json TEXT NOT NULL,
                        scheduler_name TEXT NOT NULL,
                        scheduler_version TEXT NOT NULL,
                        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4),
                        reviewed_at_utc TEXT NOT NULL,
                        due_at_utc TEXT NOT NULL,
                        prior_state_json TEXT NOT NULL,
                        resulting_state_json TEXT NOT NULL,
                        predicted_retrievability REAL,
                        actual_recall INTEGER NOT NULL CHECK (actual_recall IN (0, 1)),
                        parameter_set_id TEXT,
                        provenance_json TEXT NOT NULL,
                        payload_hash TEXT NOT NULL,
                        created_at_utc TEXT NOT NULL
                    );
                    CREATE INDEX srs_review_events_card_idx
                        ON srs_review_events(learner_id, deck_id, item_id, reviewed_at_utc, event_id);
                    CREATE TABLE srs_card_states (
                        learner_id TEXT NOT NULL,
                        deck_id TEXT NOT NULL,
                        item_id TEXT NOT NULL,
                        division_ids_json TEXT NOT NULL,
                        scheduler_name TEXT NOT NULL,
                        scheduler_version TEXT NOT NULL,
                        state_json TEXT NOT NULL,
                        due_at_utc TEXT NOT NULL,
                        last_reviewed_at_utc TEXT NOT NULL,
                        desired_retention REAL,
                        parameter_set_id TEXT,
                        latest_event_id TEXT NOT NULL,
                        replay_required INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (learner_id, deck_id, item_id)
                    );
                    CREATE INDEX srs_card_states_due_idx
                        ON srs_card_states(learner_id, due_at_utc);
                    CREATE TABLE srs_mastery_evidence (
                        evidence_id TEXT PRIMARY KEY,
                        learner_id TEXT NOT NULL,
                        deck_id TEXT NOT NULL,
                        item_id TEXT NOT NULL,
                        division_ids_json TEXT NOT NULL,
                        benchmark_id TEXT NOT NULL,
                        passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
                        score REAL,
                        verified_at_utc TEXT NOT NULL,
                        evidence_json TEXT NOT NULL,
                        payload_hash TEXT NOT NULL
                    );
                    CREATE TRIGGER srs_review_events_no_update
                    BEFORE UPDATE ON srs_review_events
                    BEGIN SELECT RAISE(ABORT, 'review history is append-only'); END;
                    CREATE TRIGGER srs_review_events_no_delete
                    BEFORE DELETE ON srs_review_events
                    BEGIN SELECT RAISE(ABORT, 'review history is append-only'); END;
                    CREATE TRIGGER srs_mastery_evidence_no_update
                    BEFORE UPDATE ON srs_mastery_evidence
                    BEGIN SELECT RAISE(ABORT, 'mastery evidence is append-only'); END;
                    CREATE TRIGGER srs_mastery_evidence_no_delete
                    BEFORE DELETE ON srs_mastery_evidence
                    BEGIN SELECT RAISE(ABORT, 'mastery evidence is append-only'); END;
                    PRAGMA user_version=1;
                """)
            elif version != self.SCHEMA_VERSION:
                raise RuntimeError(f"no migration path from database schema {version}")

    @staticmethod
    def _canonical(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _utc_string(value: str) -> str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timestamps must include a UTC offset")
        return parsed.astimezone(timezone.utc).isoformat()

    def record_review(self, event: dict[str, Any]) -> RecordReviewResult:
        required = (
            "event_id", "learner_id", "deck_id", "item_id", "division_ids",
            "scheduler_name", "scheduler_version", "rating", "reviewed_at_utc",
            "due_at_utc", "prior_state", "resulting_state", "actual_recall",
        )
        missing = [key for key in required if key not in event]
        if missing:
            raise ValueError(f"missing review event fields: {', '.join(missing)}")
        for key in ("event_id", "learner_id", "deck_id", "item_id", "scheduler_name", "scheduler_version"):
            if not isinstance(event[key], str) or not event[key].strip():
                raise ValueError(f"{key} is required")
        if isinstance(event["rating"], bool) or not isinstance(event["rating"], int) or event["rating"] not in (1, 2, 3, 4):
            raise ValueError("rating must be 1..4")
        if not isinstance(event["division_ids"], list) or any(not isinstance(x, str) or not x for x in event["division_ids"]):
            raise ValueError("division_ids must be a list of non-empty strings")
        if not isinstance(event["actual_recall"], bool):
            raise ValueError("actual_recall must be boolean")

        reviewed = self._utc_string(event["reviewed_at_utc"])
        due = self._utc_string(event["due_at_utc"])
        if due < reviewed:
            raise ValueError("due_at_utc cannot be earlier than reviewed_at_utc")
        retention = event.get("desired_retention")
        if retention is not None and not 0.7 < float(retention) < 0.97:
            raise ValueError("desired_retention must be between 0.70 and 0.97")
        payload = dict(event)
        payload["reviewed_at_utc"] = reviewed
        payload["due_at_utc"] = due
        payload_json = self._canonical(payload)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        division_json = self._canonical(sorted(set(event["division_ids"])))
        state_json = self._canonical(event["resulting_state"])
        prior_json = self._canonical(event["prior_state"])
        provenance_json = self._canonical(event.get("provenance") or {})
        predicted = event.get("predicted_retrievability")
        if predicted is not None and not 0 <= float(predicted) <= 1:
            raise ValueError("predicted_retrievability must be between 0 and 1")

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT payload_hash FROM srs_review_events WHERE event_id=?", (event["event_id"],)
            ).fetchone()
            if existing:
                if existing["payload_hash"] != payload_hash:
                    raise IdempotencyConflictError("event_id already exists with a different payload")
                conn.rollback()
                return RecordReviewResult("duplicate", False, False)

            current = conn.execute(
                "SELECT last_reviewed_at_utc, latest_event_id FROM srs_card_states WHERE learner_id=? AND deck_id=? AND item_id=?",
                (event["learner_id"], event["deck_id"], event["item_id"]),
            ).fetchone()
            replay_required = bool(current and (reviewed, event["event_id"]) < (current["last_reviewed_at_utc"], current["latest_event_id"]))
            conn.execute("""
                INSERT INTO srs_review_events (
                    event_id, learner_id, deck_id, item_id, division_ids_json,
                    scheduler_name, scheduler_version, rating, reviewed_at_utc, due_at_utc,
                    prior_state_json, resulting_state_json, predicted_retrievability,
                    actual_recall, parameter_set_id, provenance_json, payload_hash, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event["event_id"], event["learner_id"], event["deck_id"], event["item_id"],
                division_json, event["scheduler_name"], event["scheduler_version"], event["rating"],
                reviewed, due, prior_json, state_json, predicted, int(event["actual_recall"]),
                event.get("parameter_set_id"), provenance_json, payload_hash, now,
            ))
            if replay_required:
                conn.execute("""
                    UPDATE srs_card_states SET replay_required=1
                    WHERE learner_id=? AND deck_id=? AND item_id=?
                """, (event["learner_id"], event["deck_id"], event["item_id"]))
            else:
                conn.execute("""
                    INSERT INTO srs_card_states (
                        learner_id, deck_id, item_id, division_ids_json, scheduler_name,
                        scheduler_version, state_json, due_at_utc, last_reviewed_at_utc,
                        desired_retention, parameter_set_id, latest_event_id, replay_required
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    ON CONFLICT(learner_id, deck_id, item_id) DO UPDATE SET
                        division_ids_json=excluded.division_ids_json,
                        scheduler_name=excluded.scheduler_name,
                        scheduler_version=excluded.scheduler_version,
                        state_json=excluded.state_json,
                        due_at_utc=excluded.due_at_utc,
                        last_reviewed_at_utc=excluded.last_reviewed_at_utc,
                        desired_retention=excluded.desired_retention,
                        parameter_set_id=excluded.parameter_set_id,
                        latest_event_id=excluded.latest_event_id,
                        replay_required=0
                """, (
                    event["learner_id"], event["deck_id"], event["item_id"], division_json,
                    event["scheduler_name"], event["scheduler_version"], state_json, due,
                    reviewed, event.get("desired_retention"), event.get("parameter_set_id"), event["event_id"],
                ))
            conn.commit()
        return RecordReviewResult("inserted", not replay_required, replay_required)

    def get_card_state(self, learner_id: str, deck_id: str, item_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM srs_card_states WHERE learner_id=? AND deck_id=? AND item_id=?",
                (learner_id, deck_id, item_id),
            ).fetchone()
        if not row:
            return None
        result = dict(row)
        result["division_ids"] = json.loads(result.pop("division_ids_json"))
        result["state"] = json.loads(result.pop("state_json"))
        return result

    def list_review_events(self, learner_id: str, deck_id: str, item_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM srs_review_events
                WHERE learner_id=? AND deck_id=? AND item_id=?
                ORDER BY reviewed_at_utc, event_id
            """, (learner_id, deck_id, item_id)).fetchall()
        return [dict(row) for row in rows]

    def due_items(self, learner_id: str, now_utc: str, division_id: str | None = None) -> list[dict[str, Any]]:
        now = self._utc_string(now_utc)
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM srs_card_states
                WHERE learner_id=? AND due_at_utc<=? AND replay_required=0
                ORDER BY due_at_utc, deck_id, item_id
            """, (learner_id, now)).fetchall()
        items = []
        for row in rows:
            divisions = json.loads(row["division_ids_json"])
            if division_id is not None and division_id not in divisions:
                continue
            item = dict(row)
            item["division_ids"] = divisions
            item["state"] = json.loads(item.pop("state_json"))
            item.pop("division_ids_json", None)
            items.append(item)
        return items

    def record_mastery_evidence(self, evidence: dict[str, Any]) -> str:
        required = ("evidence_id", "learner_id", "deck_id", "item_id", "division_ids",
                    "benchmark_id", "passed", "verified_at_utc")
        missing = [key for key in required if key not in evidence]
        if missing:
            raise ValueError(f"missing mastery evidence fields: {', '.join(missing)}")
        for key in ("evidence_id", "learner_id", "deck_id", "item_id", "benchmark_id"):
            if not isinstance(evidence[key], str) or not evidence[key].strip():
                raise ValueError(f"{key} is required")
        if not isinstance(evidence["division_ids"], list) or any(not isinstance(x, str) or not x for x in evidence["division_ids"]):
            raise ValueError("division_ids must be a list of non-empty strings")
        if not isinstance(evidence["passed"], bool):
            raise ValueError("passed must be boolean")
        verified = self._utc_string(evidence["verified_at_utc"])
        payload = dict(evidence)
        payload["verified_at_utc"] = verified
        payload_json = self._canonical(payload)
        digest = hashlib.sha256(payload_json.encode()).hexdigest()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            prior = conn.execute(
                "SELECT payload_hash FROM srs_mastery_evidence WHERE evidence_id=?",
                (evidence["evidence_id"],),
            ).fetchone()
            if prior:
                if prior["payload_hash"] != digest:
                    raise IdempotencyConflictError("evidence_id already exists with a different payload")
                conn.rollback()
                return "duplicate"
            conn.execute("""
                INSERT INTO srs_mastery_evidence (
                    evidence_id, learner_id, deck_id, item_id, division_ids_json,
                    benchmark_id, passed, score, verified_at_utc, evidence_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence["evidence_id"], evidence["learner_id"], evidence["deck_id"], evidence["item_id"],
                self._canonical(sorted(set(evidence["division_ids"]))), evidence["benchmark_id"],
                int(evidence["passed"]), evidence.get("score"), verified,
                self._canonical(evidence.get("evidence") or {}), digest,
            ))
            conn.commit()
        return "inserted"

    def list_mastery_evidence(self, learner_id: str, deck_id: str, item_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM srs_mastery_evidence
                WHERE learner_id=? AND deck_id=? AND item_id=?
                ORDER BY verified_at_utc, evidence_id
            """, (learner_id, deck_id, item_id)).fetchall()
        return [dict(row) for row in rows]
