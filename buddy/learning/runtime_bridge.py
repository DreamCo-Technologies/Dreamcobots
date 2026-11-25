"""Host-mediated bridge between existing Buddy task runner, capability adapters and learning.

No automatic observation, background worker, model training, or external action.
Authenticated callers supply tenant ID and explicit consent. Private SQLite
data must live outside public Pages and the repository.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

from buddy.learning.library_knowledge_router import route_library_question
from buddy.learning.course_track_registry import load_course_lessons, resources_for_division, resources_for_masterbot
from buddy.learning.evidence_acquisition import (
    Capability, CapabilityRegistry, LearningEvent, LearningLedger, benchmark_gate,
)
from dreamco_platform.automation.task_runner import BuddyTaskRunner


class PrivateLearningStore:
    """Persist validated, redacted evidence by tenant; do not store raw task packets."""
    def __init__(self, filename: str):
        self.filename = str(Path(filename).expanduser())
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS learning_evidence (
                tenant TEXT NOT NULL, event_id TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY (tenant, event_id))""")
        os.chmod(self.filename, 0o600)

    def _connect(self):
        db = sqlite3.connect(self.filename, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def save(self, event: LearningEvent) -> str:
        event.validate()
        if event.split != "train":
            raise ValueError("holdout and validation data belong in separate evaluation storage")
        ledger = LearningLedger()
        key = ledger.record(event)
        payload = json.dumps(asdict(event), sort_keys=True, allow_nan=False)
        with self._connect() as db:
            existing = db.execute(
                "SELECT payload FROM learning_evidence WHERE tenant=? AND event_id=?",
                (event.tenant_id, key)).fetchone()
            if existing and existing[0] != payload:
                raise ValueError("conflicting event")
            db.execute("INSERT OR IGNORE INTO learning_evidence VALUES (?,?,?)",
                       (event.tenant_id, key, payload))
        return key

    def load(self, tenant_id: str) -> LearningLedger:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("authenticated tenant ID required")
        ledger = LearningLedger()
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM learning_evidence WHERE tenant=?",
                              (tenant_id,)).fetchall()
        for (payload,) in rows:
            row = json.loads(payload)
            if row["tenant_id"] != tenant_id:
                raise ValueError("tenant isolation violation")
            ledger.record(LearningEvent(**row))
        return ledger

    def forget(self, tenant_id: str) -> int:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("authenticated tenant ID required")
        with self._connect() as db:
            result = db.execute("DELETE FROM learning_evidence WHERE tenant=?", (tenant_id,))
            return result.rowcount


class BuddyLearningBridge:
    """Read-only supervision and reporting around existing runtime objects."""
    def __init__(self, store: PrivateLearningStore, runner: BuddyTaskRunner):
        self.store = store
        self.runner = runner
        self.capabilities = CapabilityRegistry()

    def learn_from_result(self, *, tenant_id: str, task_id: str, domain: str,
                          workflow: str, source_revision: str, result: dict[str, Any],
                          capture_consent: bool, redacted: bool, outcome_verified: bool,
                          rating: int | None = None) -> str:
        """Accept only externally verified results for an existing tenant-owned task."""
        task = next((t for t in self.runner.dashboard()["tasks"]
                     if t["task_id"] == task_id and t["owner_user_id"] == tenant_id), None)
        if task is None:
            raise PermissionError("task not found for authenticated tenant")
        if task["status"] not in {"completed", "failed"} or result.get("status") != task["status"]:
            raise ValueError("task is not in a completed, verifiable state")
        event = LearningEvent(tenant_id=tenant_id, task_id=task_id, domain=domain,
                              goal=task["objective"], workflow=workflow,
                              outcome="success" if task["status"] == "completed" else "failure",
                              source="buddy-task-runner",
                              source_revision=source_revision, rating=rating,
                              consent=capture_consent, redacted=redacted,
                              verified=outcome_verified)
        return self.store.save(event)

    def coach(self, tenant_id: str, domain: str) -> dict[str, Any]:
        summary = self.store.load(tenant_id).recommendations(tenant_id, domain)
        return {"schema": "dreamco.coaching.v1", **summary,
                "teaching": {"mode": "guided", "next_step": summary["next_step"],
                             "check_understanding": "Would you like to review a verified example?"},
                "automated": False}

    def library_knowledge(self, query: str, *, external_discovery: bool = False,
                          persist_gap: bool = False, query_is_redacted: bool = False,
                          gap_root: Path | None = None) -> dict[str, Any]:
        """Internal-first library retrieval; network and gap persistence require explicit opt-in."""
        return route_library_question(
            query,
            external_discovery=external_discovery,
            persist_gap=persist_gap,
            query_is_redacted=query_is_redacted,
            requested_by="buddy-runtime",
            gap_root=gap_root,
        )

    def library_learning_queue(self, *, division: str | None = None,
                               masterbot: str | None = None, query: str = "",
                               limit: int = 50) -> dict[str, Any]:
        """Return queued library lessons for a canonical division or MasterBot lane."""
        if bool(division) == bool(masterbot):
            raise ValueError("provide exactly one canonical division or MasterBot lane")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 100:
            raise ValueError("limit must be an integer between 1 and 100")
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        if division:
            resources_for_division(division)
            owner = {"division": division}
        else:
            resources_for_masterbot(str(masterbot))
            owner = {"masterbot": masterbot}
        lessons = [
            lesson for lesson in load_course_lessons()
            if lesson.track_id == "universal-software-libraries"
        ]
        if query.strip():
            terms = {token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 1}
            lessons = [
                lesson for lesson in lessons
                if terms & set(__import__("re").findall(
                    r"[a-z0-9]+",
                    f"{lesson.title} {lesson.category} {lesson.objective}".lower()
                ))
            ]
        items = [{
            "resource_id": lesson.resource_id,
            "lesson_id": lesson.lesson_id,
            "track_id": lesson.track_id,
            "title": lesson.title,
            "category": lesson.category,
            "objective": lesson.objective,
            "practice": lesson.practice,
            "assessment": lesson.assessment,
            "benchmark": lesson.benchmark,
            "source_url": lesson.source_url,
            "guide_path": lesson.guide_path,
            "rights_mode": lesson.rights_mode,
            "completion_status": "queued_not_studied",
            "mastery_awarded": False,
            "model_weight_training_authorized": False,
            "paid_compute_authorized": False,
        } for lesson in lessons[:limit]]
        return {
            "schema": "dreamco.buddy_library_learning_queue.v1",
            **owner,
            "query": query,
            "available_count": len(lessons),
            "returned_count": len(items),
            "items": items,
            "external_model_call_performed": False,
        }

    def sop_candidates(self, tenant_id: str, domain: str, *, minimum_successes: int = 3) -> list[dict]:
        """Produce review-only SOP outlines, not inferred steps or executable automation."""
        if minimum_successes < 3:
            raise ValueError("at least three verified successes required")
        suggestions = self.coach(tenant_id, domain)["candidates"]
        return [{"workflow": row["workflow"], "purpose": "Draft from verified task outcomes",
                 "evidence_count": row["successes"], "status": "requires_human_step_review",
                 "steps": [], "approved": False}
                for row in suggestions if row["successes"] >= minimum_successes]

    def discover_adapter(self, adapter: Any, *, evidence_id: str, tested: bool,
                         approved: bool, risk: str = "read_only") -> None:
        """Adapter's discover() advertises actions; the host still enforces pairing/grants."""
        actions = adapter.discover()
        if not actions:
            raise ValueError("adapter has no advertised actions")
        self.capabilities.register(Capability(
            capability_id=str(adapter.id), adapter_id=str(adapter.id),
            revision=str(adapter.revision), actions=tuple(a.id for a in actions),
            evidence_id=evidence_id, tested=tested, approved=approved, risk=risk))

    def model_route_report(self, tenant_id: str, domain: str,
                           candidates: list[dict[str, Any]]) -> dict[str, Any]:
        """Evidence-only ranking; no provider calls and no invented measurements."""
        if not isinstance(candidates, list):
            raise ValueError("candidate list required")
        eligible = []
        for item in candidates:
            if not all(k in item for k in ("model", "baseline", "candidate", "holdout")):
                continue
            verdict = benchmark_gate(item["baseline"], item["candidate"], item["holdout"])
            eligible.append({"model": item["model"], "evidence": verdict})
        eligible.sort(key=lambda item: (not item["evidence"]["promote"],
                                         -item["evidence"]["holdout"], str(item["model"])))
        return {"schema": "dreamco.model_route_evidence.v1", "domain": domain,
                "tenant_scope": "private", "eligible": eligible,
                "selection": "human_review_required", "provider_called": False}

    def dashboard(self, tenant_id: str, domain: str) -> dict[str, Any]:
        """Private evidence view. Never publish tenant data to GitHub Pages."""
        tasks = [t for t in self.runner.dashboard()["tasks"] if t["owner_user_id"] == tenant_id]
        recommendations = self.coach(tenant_id, domain)
        return {"schema": "dreamco.private_learning_dashboard.v1",
                "task_counts": {status: sum(t["status"] == status for t in tasks)
                                for status in ("scheduled", "running", "completed", "failed", "paused", "cancelled")},
                "learning_observations": recommendations["observations"],
                "workflow_candidates": recommendations["candidates"],
                "verified_public_benchmarks": [],
                "scope": "authenticated_private_only",
                "long_running_execution": "existing_runner_only_no_background_worker"}

    def propose_supervised_project(self, tenant_id: str, bot_slug: str, objective: str,
                                   *, max_runs: int = 3, interval_seconds: int = 3600) -> dict:
        """Create a reviewable schedule proposal; do not enqueue without explicit approval."""
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant required")
        if not isinstance(objective, str) or len(objective.strip()) < 10:
            raise ValueError("objective too short")
        if not 1 <= max_runs <= 100 or interval_seconds < 60:
            raise ValueError("bounded schedule required")
        return {"owner_user_id": tenant_id, "bot_slug": bot_slug,
                "objective": objective, "recurrence": "interval",
                "interval_seconds": interval_seconds, "max_runs": max_runs,
                "live_external_action": False, "status": "awaiting_host_approval",
                "scheduled": False}
