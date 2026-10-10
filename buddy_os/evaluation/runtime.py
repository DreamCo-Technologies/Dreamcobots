"""Trusted-adapter execution and checkpoint recovery for the existing scheduler.

Adapters must enforce their own isolation, network scopes, deadlines and actual
spend ceilings. The evaluator does not execute untrusted code in the host process.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Callable

from .review import ReviewStore, digest, finite


@dataclass(frozen=True)
class GovernedAdapter:
    name: str
    action_class: str
    execute: Callable
    verify: Callable


def execute_reviewed(store, action_id, expected_hash, adapter, budget_usd=0):
    action = store.consume(action_id, expected_hash, action_class=adapter.action_class, budget_usd=budget_usd)
    try:
        result = adapter.execute(action["parameters"])
        if not isinstance(result, dict) or not finite(result.get("actual_cost_usd")):
            raise ValueError("Adapter must report actual cost")
        verified = adapter.verify(result) is True
        store.finish(action_id, passed=verified, evidence_hash=digest(result), actual_cost_usd=result["actual_cost_usd"])
        return result
    except Exception:
        # Unknown effects or spend must not be invented as zero or auto-retried.
        with store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            store._audit(db, "execution_uncertain", action_id, {"reconciliation_required": True})
        raise


class EvaluationTaskAdapter:
    """Inject into BuddyTaskRunner; each scheduled execution consumes fresh scope."""
    name = "human-reviewed-evaluation"

    def __init__(self, store: ReviewStore, adapter: GovernedAdapter, bindings: dict):
        self.store, self.adapter, self.bindings = store, adapter, bindings

    def execute(self, task):
        binding = self.bindings.get(task.task_id)
        if not binding:
            raise ValueError("Scheduled evaluation has no action binding")
        if task.approval_id != binding["action_id"]:
            raise ValueError("Scheduler approval does not match action")
        return execute_reviewed(self.store, binding["action_id"], binding["hash"], self.adapter, binding["budget_usd"])


class LongHorizon:
    """Checkpoints store references/hashes, never private task content or secrets."""

    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS horizons(id TEXT PRIMARY KEY, body TEXT NOT NULL)")

    def start(self, objective_hash, max_steps, budget_usd, deadline, rollback_ref):
        import re
        if (not re.fullmatch(r"[a-f0-9]{64}", objective_hash) or type(max_steps) is not int
                or not 1 <= max_steps <= 10000 or not finite(budget_usd) or not finite(deadline, time.time())
                or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{3,200}", rollback_ref)):
            raise ValueError("Bounded objective, budget, deadline and rollback reference required")
        task_id = "horizon-" + uuid.uuid4().hex
        state = {"id": task_id, "objective_hash": objective_hash, "max_steps": max_steps, "budget_usd": budget_usd,
                 "deadline": deadline, "rollback_ref": rollback_ref, "status": "running", "checkpoints": [], "interventions": 0, "cost_usd": 0}
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self.store._assert_audit(db)
            db.execute("INSERT INTO horizons VALUES(?,?)", (task_id, json.dumps(state)))
            self.store._audit(db, "horizon_started", task_id, {"objective_hash": objective_hash})
        return state

    def preflight(self, task_id, *, additional_cost_usd=0):
        with self.store.connect() as db:
            self.store._assert_audit(db)
            row = db.execute("SELECT body FROM horizons WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise ValueError("Unknown long-horizon task")
        state = json.loads(row[0])
        if (state["status"] != "running" or time.time() >= state["deadline"]
                or len(state["checkpoints"]) >= state["max_steps"] or not finite(additional_cost_usd)
                or state["cost_usd"] + additional_cost_usd > state["budget_usd"]):
            raise ValueError("Checkpoint, runtime or budget requires human intervention")
        return state

    def checkpoint(self, task_id, action_id, *, expected_step, event="checkpoint"):
        if event not in {"checkpoint", "failure", "recover", "rollback", "complete"}:
            raise ValueError("Unknown checkpoint event")
        action = self.store.get(action_id)
        if action["status"] not in {"verified", "failed"} or not action["receipt"]:
            raise ValueError("Checkpoint requires post-action verification")
        if event in {"recover", "rollback"} and (not action["reviewer"] or action["action"]["action_class"] != "rollback"):
            raise ValueError("Recovery and rollback require a reviewed rollback action")
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self.store._assert_audit(db)
            row = db.execute("SELECT body FROM horizons WHERE id=?", (task_id,)).fetchone()
            if not row:
                raise ValueError("Unknown long-horizon task")
            state = json.loads(row[0])
            if state["status"] in {"completed", "rolled_back"} or expected_step != len(state["checkpoints"]):
                raise ValueError("Terminal task or stale checkpoint")
            if any(c["action_id"] == action_id for c in state["checkpoints"]):
                raise ValueError("Action already checkpointed")
            if state["status"] == "paused" and event not in {"recover", "rollback"}:
                raise ValueError("Human recovery required before continuing")
            if event in {"recover", "rollback", "complete"} and action["status"] != "verified":
                raise ValueError("Recovery, rollback and completion must pass verification")
            state["checkpoints"].append({"action_id": action_id, "event": event, "hash": action["receipt"]["evidence_hash"]})
            state["cost_usd"] += action["receipt"]["actual_cost_usd"]
            state["interventions"] += int(bool(action["reviewer"]))
            exceeded = len(state["checkpoints"]) > state["max_steps"] or state["cost_usd"] > state["budget_usd"] or time.time() > state["deadline"]
            if event == "rollback":
                state["status"] = "rolled_back"
            elif exceeded or action["status"] == "failed" or event == "failure":
                state["status"] = "paused"
            else:
                state["status"] = "completed" if event == "complete" else "running"
            db.execute("UPDATE horizons SET body=? WHERE id=?", (json.dumps(state), task_id))
            self.store._audit(db, "horizon_" + event, task_id, {"action_id": action_id, "state_hash": digest(state), "status": state["status"]})
        return state

    def execute_step(self, task_id, action_id, expected_hash, adapter, *, budget_usd=0, event="checkpoint"):
        """Canonical step entry point: check caps before executing, then checkpoint."""
        if event not in {"checkpoint", "complete"}:
            raise ValueError("Recovery requires a separately reviewed rollback action and checkpoint")
        action = self.store.get(action_id)
        state = self.preflight(task_id, additional_cost_usd=action["action"]["expected_cost_usd"])
        result = execute_reviewed(self.store, action_id, expected_hash, adapter, budget_usd)
        updated = self.checkpoint(task_id, action_id, expected_step=len(state["checkpoints"]), event=event)
        return {"result": result, "task": updated}


class ComponentRegistry:
    """Atomic local model+policy+router+retrieval pointer, with reviewed rollback.

This registry never installs models or changes proprietary weights. Deployment
adapters must still verify availability and enforce their existing release gates.
"""
    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS components(slot TEXT PRIMARY KEY, body TEXT NOT NULL)")

    def transition(self, action_id, expected_hash, *, expected_current, components, champion, challenger, evidence_root, suites, rollback=False):
        from .evidence import COMPONENTS, promotion, verify_artifacts
        from tools.general_intelligence import registered
        evidence_assessment = promotion(champion, challenger)
        if not rollback and (not verify_artifacts(champion, evidence_root) or not verify_artifacts(challenger, evidence_root)
                             or not registered(champion, suites) or not registered(challenger, suites)
                             or components != challenger.get("components")):
            raise ValueError("Verified comparable artifacts and preregistered suites required")
        if set(components) != COMPONENTS or any(not isinstance(v, str) or not v.strip() for v in components.values()):
            raise ValueError("Exact component revisions required")
        row = self.store.get(action_id)
        params = {"expected_current": expected_current, "components": components, "assessment_hash": digest(evidence_assessment)}
        if row["action"]["parameters"] != params:
            raise ValueError("Registry update differs from reviewed preview")
        if not rollback and evidence_assessment.get("status") != "human_review_required":
            raise ValueError("Candidate rejected by evaluation gates")
        self.store.consume(action_id, expected_hash, action_class="rollback" if rollback else "model_promotion")
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self.store._assert_audit(db)
            current = db.execute("SELECT body FROM components WHERE slot='active'").fetchone()
            value = json.loads(current[0]) if current else None
            if value != expected_current:
                raise ValueError("Active components changed; fresh review required")
            if rollback:
                previous = db.execute("SELECT body FROM components WHERE slot='previous'").fetchone()
                if not previous or json.loads(previous[0]) != components:
                    raise ValueError("Rollback must restore the recorded previous components")
            previous_value = value if value is not None else champion.get("components")
            if previous_value is not None:
                db.execute("INSERT OR REPLACE INTO components VALUES('previous',?)", (json.dumps(previous_value),))
            db.execute("INSERT OR REPLACE INTO components VALUES('active',?)", (json.dumps(components),))
            self.store._audit(db, "rollback" if rollback else "promotion", action_id, {"previous": value, "components": components})
        self.store.finish(action_id, passed=True, evidence_hash=digest(components), actual_cost_usd=0)
        return components
