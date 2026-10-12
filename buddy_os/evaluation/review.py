"""Transactional one-action review gates. The caller authenticates human reviewers.

No provider execution, shell evaluation, or permission elevation is implemented here.
The local bridge keeps reviewer credentials separate from the agent session token.
SQLite is a local trust boundary, not a cryptographic identity provider. Protect it
with OS permissions and back up audit heads outside the host for tamper detection.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT / "config/general-intelligence/framework.json").read_text())
SECRET = re.compile(r"(?:github_pat_|gh[pso]_|sk[-_](?:live|proj)[-_]|-----BEGIN .*PRIVATE KEY|Bearer\s+\S+)", re.I)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def finite(value, minimum=0, maximum=float("inf")):
    return type(value) in (int, float) and math.isfinite(value) and minimum <= value <= maximum


def validate_action(action):
    required = {"action_class", "title", "rationale", "evidence", "risk", "reversible", "expected_cost_usd", "tools", "data", "preview", "verification", "rollback", "parameters"}
    if not isinstance(action, dict) or set(action) != required:
        raise ValueError("Action must contain exactly the review contract fields")
    known = set(POLICY["approval_actions"] + POLICY["forbidden_actions"] + ["read", "draft", "sandbox"])
    if action["action_class"] not in known or action["risk"] not in {"low", "medium", "high", "critical"}:
        raise ValueError("Unknown action class or risk")
    if type(action["reversible"]) is not bool or not finite(action["expected_cost_usd"]):
        raise ValueError("Invalid reversibility or cost")
    for field in ("title", "rationale", "preview", "verification", "rollback"):
        if not isinstance(action[field], str) or not 1 <= len(action[field]) <= 8000:
            raise ValueError(f"Missing or oversized {field}")
    for field in ("evidence", "tools", "data"):
        if not isinstance(action[field], list) or len(action[field]) > 100 or any(not isinstance(v, str) or not v or len(v) > 1000 for v in action[field]):
            raise ValueError(f"Invalid {field}")
    if not isinstance(action["parameters"], dict):
        raise ValueError("Parameters must be an object")
    encoded = json.dumps(action, allow_nan=False)
    if len(encoded) > 32000 or SECRET.search(encoded):
        raise ValueError("Oversized action or credential-like content; use opaque secret references")
    return action


def boundary(action, autonomy):
    validate_action(action)
    if autonomy not in POLICY["autonomy"]:
        raise ValueError("Unknown autonomy level")
    if action["action_class"] in POLICY["forbidden_actions"]:
        return "forbidden"
    if (action["action_class"] in POLICY["autonomy"][autonomy] and action["risk"] == "low"
            and action["reversible"] and action["expected_cost_usd"] == 0):
        return "allowed"
    return "approval_required"


class ReviewStore:
    """Durable queue with optimistic revisions and atomic approval consumption."""

    def __init__(self, path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS actions (
                    id TEXT PRIMARY KEY, revision INTEGER NOT NULL, body TEXT NOT NULL,
                    hash TEXT NOT NULL, autonomy TEXT NOT NULL, status TEXT NOT NULL,
                    expires REAL, reviewer TEXT, receipt TEXT);
                CREATE TABLE IF NOT EXISTS audit (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL,
                    previous TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
                    BEGIN SELECT RAISE(ABORT, 'append-only audit'); END;
                CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
                    BEGIN SELECT RAISE(ABORT, 'append-only audit'); END;
            """)
        if self.path != ":memory:":
            Path(path).chmod(0o600)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def _audit(self, db, kind, action_id, details):
        last = db.execute("SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        previous = last[0] if last else "genesis"
        body = {"at": time.time(), "kind": kind, "action_id": action_id, "details": details}
        db.execute("INSERT INTO audit(body,previous,hash) VALUES(?,?,?)", (json.dumps(body), previous, digest([previous, body])))

    def _assert_audit(self, db):
        previous = "genesis"
        for row in db.execute("SELECT * FROM audit ORDER BY seq"):
            if row["previous"] != previous or row["hash"] != digest([previous, json.loads(row["body"])]):
                raise ValueError("Audit chain is invalid; execution blocked")
            previous = row["hash"]

    def propose(self, action, autonomy="Guided"):
        status = boundary(action, autonomy)
        action_id = "approval-" + uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._assert_audit(db)
            db.execute("INSERT INTO actions VALUES(?,?,?,?,?,?,NULL,NULL,NULL)",
                       (action_id, 1, json.dumps(action), digest(action), autonomy, "forbidden" if status == "forbidden" else "pending"))
            self._audit(db, "proposed", action_id, {"hash": digest(action), "boundary": status})
        return action_id

    def get(self, action_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        if not row:
            raise ValueError("Unknown review request")
        result = dict(row)
        result["action"] = json.loads(result.pop("body"))
        if result["hash"] != digest(result["action"]):
            raise ValueError("Action integrity mismatch")
        result["receipt"] = json.loads(result["receipt"]) if result["receipt"] else None
        result["boundary"] = boundary(result["action"], result["autonomy"])
        if result["status"] == "approved" and (result["expires"] or 0) <= time.time():
            result["status"] = "expired"
        return result

    def queue(self):
        with self.connect() as db:
            self._assert_audit(db)
            ids = [r[0] for r in db.execute("SELECT id FROM actions ORDER BY rowid DESC LIMIT 1000")]
        return [self.get(i) for i in ids]

    def decide(self, action_id, revision, decision, reviewer, *, edited=None, note="", ttl=900):
        if decision not in {"approve", "reject", "edit", "escalate"}:
            raise ValueError("Unknown decision")
        if not isinstance(reviewer, str) or not re.fullmatch(r"[a-zA-Z0-9_.:-]{2,80}", reviewer):
            raise ValueError("Authenticated reviewer identity required")
        if not finite(ttl, 1, 3600) or not isinstance(note, str) or len(note) > 2000 or SECRET.search(note):
            raise ValueError("Invalid review lifetime or note")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._assert_audit(db)
            row = db.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
            if not row or row["revision"] != revision or row["status"] not in {"pending", "escalated", "approved"}:
                raise ValueError("Stale revision or terminal review")
            action = json.loads(row["body"])
            if digest(action) != row["hash"]:
                raise ValueError("Action integrity mismatch")
            if decision == "edit":
                action = validate_action(edited)
                status = "forbidden" if boundary(action, row["autonomy"]) == "forbidden" else "pending"
            else:
                status = {"approve": "approved", "reject": "rejected", "escalate": "escalated"}[decision]
            if status == "approved" and boundary(action, row["autonomy"]) == "forbidden":
                raise ValueError("Forbidden actions cannot be approved")
            db.execute("UPDATE actions SET revision=revision+1,body=?,hash=?,status=?,expires=?,reviewer=? WHERE id=?",
                       (json.dumps(action), digest(action), status, time.time() + ttl if status == "approved" else None, reviewer, action_id))
            self._audit(db, decision, action_id, {"revision": revision + 1, "hash": digest(action), "reviewer": reviewer, "note": note})
        return self.get(action_id)

    def consume(self, action_id, expected_hash, *, action_class, budget_usd=0):
        """Trusted adapter supplies its own class; never accept the caller's class."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._assert_audit(db)
            row = db.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
            if not row:
                raise ValueError("Missing approval")
            action = json.loads(row["body"])
            if digest(action) != row["hash"] or expected_hash != row["hash"] or action["action_class"] != action_class:
                raise ValueError("Approval scope mismatch")
            gate = boundary(action, row["autonomy"])
            automatic = gate == "allowed" and row["status"] == "pending"
            reviewed = row["status"] == "approved" and (row["expires"] or 0) > time.time()
            if gate == "forbidden" or not (automatic or reviewed):
                raise ValueError("Fresh one-action approval required")
            if not finite(budget_usd) or action["expected_cost_usd"] > budget_usd:
                raise ValueError("Approved budget exceeded")
            db.execute("UPDATE actions SET status='executing',revision=revision+1 WHERE id=?", (action_id,))
            self._audit(db, "consumed", action_id, {"hash": expected_hash, "human_reviewed": bool(reviewed)})
        return action

    def finish(self, action_id, *, passed, evidence_hash, actual_cost_usd, error=None):
        if type(passed) is not bool or not re.fullmatch(r"[0-9a-f]{64}", evidence_hash) or not finite(actual_cost_usd):
            raise ValueError("Post-action verification requires measured cost and evidence hash")
        if error is not None and (not isinstance(error, str) or len(error) > 2000 or SECRET.search(error)):
            raise ValueError("Unsafe error detail")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._assert_audit(db)
            row = db.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
            if not row or row["status"] != "executing":
                raise ValueError("Action is not executing")
            overrun = actual_cost_usd > json.loads(row["body"])["expected_cost_usd"]
            receipt = {"passed": passed and not overrun, "evidence_hash": evidence_hash, "actual_cost_usd": actual_cost_usd, "budget_overrun": overrun, "error": error}
            db.execute("UPDATE actions SET status=?,receipt=?,revision=revision+1 WHERE id=?",
                       ("verified" if receipt["passed"] else "failed", json.dumps(receipt), action_id))
            self._audit(db, "verification", action_id, receipt)
        return receipt

    def audit(self):
        with self.connect() as db:
            self._assert_audit(db)
            return [{**json.loads(r["body"]), "hash": r["hash"]} for r in db.execute("SELECT * FROM audit ORDER BY seq")]
