"""Host-mediated bridge between existing Buddy task runner, capability adapters and learning.

No automatic observation, background worker, model training, or external action.
Authenticated callers supply tenant ID and explicit consent. Private SQLite
data must live outside public Pages and the repository.
"""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

from buddy.learning.library_knowledge_router import route_library_question
from buddy.learning.universal_library_registry import library_coverage_report
from buddy.learning.course_track_registry import load_course_lessons, resources_for_division, resources_for_masterbot
from buddy.learning.evidence_acquisition import (
    Capability, CapabilityRegistry, LearningEvent, LearningLedger, benchmark_gate,
)
from dreamco_platform.automation.task_runner import BuddyTaskRunner


@lru_cache(maxsize=1)
def _freecodecamp_division_category_profiles() -> tuple[set[str], dict[str, set[str]]]:
    """Load the shared subject-category profiles used by the queue builder."""
    path = Path(__file__).resolve().parents[2] / "config/freecodecamp-division-category-profiles.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != "dreamco.freecodecamp_division_category_profiles.v1":
        raise ValueError("unsupported FreeCodeCamp division category profile schema")
    shared = set(document.get("shared_foundation_categories", []))
    profiles = {
        str(domain_id): set(categories)
        for domain_id, categories in document.get("domain_categories", {}).items()
    }
    if len(profiles) != 55 or not shared:
        raise ValueError("FreeCodeCamp category profiles must cover all 55 divisions and shared foundation")
    return shared, profiles


class PrivateLearningStore:
    """Persist validated, redacted evidence by tenant; do not store raw task packets."""
    def __init__(self, filename: str):
        self.filename = str(Path(filename).expanduser())
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS learning_evidence (
                tenant TEXT NOT NULL, event_id TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY (tenant, event_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS library_study_progress (
                tenant TEXT NOT NULL, owner_type TEXT NOT NULL, owner_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL, guide_revision TEXT NOT NULL, status TEXT NOT NULL,
                attempts INTEGER NOT NULL, evidence_id TEXT NOT NULL,
                benchmark_passed INTEGER NOT NULL, holdout_passed INTEGER NOT NULL,
                regression_passed INTEGER NOT NULL, reviewer_approved INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (tenant, owner_type, owner_id, lesson_id))""")
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

    def record_library_progress(self, *, tenant_id: str, owner_type: str, owner_id: str,
                                 lesson_id: str, guide_revision: str, evidence_id: str,
                                 capture_consent: bool, redacted: bool, outcome_verified: bool,
                                 benchmark_passed: bool, holdout_passed: bool,
                                 regression_passed: bool, reviewer_approved: bool) -> dict[str, Any]:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("authenticated tenant ID required")
        if owner_type not in {"division", "masterbot"} or not owner_id.strip():
            raise ValueError("canonical division or MasterBot owner required")
        for label, value in (("lesson_id", lesson_id), ("guide_revision", guide_revision), ("evidence_id", evidence_id)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} is required")
        if not capture_consent or not redacted:
            raise PermissionError("explicit consent and redacted evidence are required")
        if not outcome_verified:
            raise ValueError("library lesson outcome must be verified")
        if any(type(value) is not bool for value in (benchmark_passed, holdout_passed, regression_passed, reviewer_approved)):
            raise ValueError("assessment and review outcomes must be booleans")
        all_assessments_passed = benchmark_passed and holdout_passed and regression_passed
        status = "mastered" if all_assessments_passed and reviewer_approved else (
            "assessment_passed" if all_assessments_passed else "in_progress"
        )
        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        with self._connect() as db:
            existing = db.execute(
                "SELECT guide_revision, attempts FROM library_study_progress "
                "WHERE tenant=? AND owner_type=? AND owner_id=? AND lesson_id=?",
                (tenant_id, owner_type, owner_id, lesson_id),
            ).fetchone()
            attempts = existing[1] + 1 if existing and existing[0] == guide_revision else 1
            db.execute(
                """INSERT OR REPLACE INTO library_study_progress
                (tenant, owner_type, owner_id, lesson_id, guide_revision, status, attempts,
                 evidence_id, benchmark_passed, holdout_passed, regression_passed,
                 reviewer_approved, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (tenant_id, owner_type, owner_id, lesson_id, guide_revision, status, attempts,
                 evidence_id, int(benchmark_passed), int(holdout_passed), int(regression_passed),
                 int(reviewer_approved), now),
            )
        return {"lesson_id": lesson_id, "status": status, "attempts": attempts,
                "evidence_id": evidence_id, "guide_revision": guide_revision,
                "mastery_awarded": status == "mastered",
                "model_weight_training_authorized": False}

    def load_library_progress(self, tenant_id: str, owner_type: str, owner_id: str) -> dict[str, dict[str, Any]]:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("authenticated tenant ID required")
        if owner_type not in {"division", "masterbot"} or not owner_id.strip():
            raise ValueError("canonical division or MasterBot owner required")
        with self._connect() as db:
            rows = db.execute(
                """SELECT lesson_id, guide_revision, status, attempts, evidence_id,
                benchmark_passed, holdout_passed, regression_passed, reviewer_approved, updated_at
                FROM library_study_progress WHERE tenant=? AND owner_type=? AND owner_id=?""",
                (tenant_id, owner_type, owner_id),
            ).fetchall()
        return {
            row[0]: {
                "guide_revision": row[1], "status": row[2], "attempts": row[3],
                "evidence_id": row[4], "benchmark_passed": bool(row[5]),
                "holdout_passed": bool(row[6]), "regression_passed": bool(row[7]),
                "reviewer_approved": bool(row[8]), "updated_at": row[9],
            } for row in rows
        }

    def forget(self, tenant_id: str) -> int:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("authenticated tenant ID required")
        with self._connect() as db:
            evidence = db.execute("DELETE FROM learning_evidence WHERE tenant=?", (tenant_id,))
            progress = db.execute("DELETE FROM library_study_progress WHERE tenant=?", (tenant_id,))
            return evidence.rowcount + progress.rowcount


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

    def library_coverage(self) -> dict[str, Any]:
        """Return transparent library catalog, guide, rights and freshness coverage."""
        return library_coverage_report()

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
            and (
                (not lesson.division_targets or division in lesson.division_targets)
                if division else
                (not lesson.masterbot_targets or masterbot in lesson.masterbot_targets)
            )
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
            "source_video_id": lesson.source_video_id,
            "guide_path": lesson.guide_path,
            "division_targets": list(lesson.division_targets),
            "masterbot_targets": list(lesson.masterbot_targets),
            "capability_tags": list(lesson.capability_tags),
            "tool_tags": list(lesson.tool_tags),
            "agent_tags": list(lesson.agent_tags),
            "learning_modes": list(lesson.learning_modes),
            "implementation_steps": list(lesson.implementation_steps),
            "buddy_demo": lesson.buddy_demo,
            "rights_mode": lesson.rights_mode,
            "content_status": lesson.content_status,
            "review_status": lesson.review_status,
            "training_eligibility": lesson.training_eligibility,
            "exercise_ids": list(lesson.exercise_ids),
            "project_ids": list(lesson.project_ids),
            "assessment_ids": list(lesson.assessment_ids),
            "retraining_policy_id": lesson.retraining_policy_id,
            "completion_status": (
                "queued_for_owner_review" if lesson.review_status != "approved"
                else "queued_not_studied" if lesson.content_status == "authored"
                else "authoring_backlog"
            ),
            "study_allowed": (
                lesson.content_status == "authored"
                and lesson.review_status == "approved"
                and lesson.training_eligibility in {"internal_sandbox_practice_only", "approved_for_training"}
                and lesson.learner_visible
                and not lesson.source_url
            ),
            "authoring_required": lesson.content_status in {"authoring_backlog", "metadata_only", "original_implementation_brief"},
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
            "track_ids": sorted({lesson.track_id for lesson in lessons}),
            "external_discovery_performed": False,
            "external_model_call_performed": False,
        }

    def bootcamp_learning_queue(self, *, division: str | None = None,
                                masterbot: str | None = None, query: str = "",
                                limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Return all shared Bootcamp course tracks for one canonical division or MasterBot lane."""
        if bool(division) == bool(masterbot):
            raise ValueError("provide exactly one canonical division or MasterBot lane")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 100:
            raise ValueError("limit must be an integer between 1 and 100")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ValueError("offset must be a non-negative integer")
        if not isinstance(query, str) or len(query) > 1000:
            raise ValueError("query must be a string of at most 1000 characters")
        if division:
            resources_for_division(division)
            owner = {"division": division}
        else:
            resources_for_masterbot(str(masterbot))
            owner = {"masterbot": masterbot}

        catalog_lessons = [
            lesson for lesson in load_course_lessons()
            if lesson.track_id == "dreamco-division-specialist"
            and lesson.learner_visible
            and not lesson.source_url
            and lesson.content_status == "authored"
        ]
        if division:
            shared_categories, domain_profiles = _freecodecamp_division_category_profiles()
            domain_categories = domain_profiles.get(division.casefold())
            if domain_categories is None:
                raise ValueError(f"no FreeCodeCamp category profile for canonical division: {division}")
            allowed_video_categories = shared_categories | domain_categories

            def belongs_to_division(lesson: CourseLesson) -> bool:
                # The general catalog is category-routed to every relevant
                # division; its explicit targets are discovery hints, not
                # exclusive ownership. Curated specialist briefs remain scoped
                # to their explicit division targets.
                if lesson.track_id == "freecodecamp-video-catalog" and lesson.video_categories:
                    return bool(set(lesson.video_categories) & allowed_video_categories)
                if lesson.track_id == "freecodecamp-specialist-learning-paths":
                    if lesson.division_targets:
                        return division in lesson.division_targets
                    if lesson.video_categories:
                        return bool(set(lesson.video_categories) & allowed_video_categories)
                if lesson.division_targets:
                    return division in lesson.division_targets
                return True

            lessons = [lesson for lesson in catalog_lessons if belongs_to_division(lesson)]
        else:
            lessons = [
                lesson for lesson in catalog_lessons
                if not lesson.masterbot_targets or masterbot in lesson.masterbot_targets
            ]
        if query.strip():
            terms = list(dict.fromkeys(
                token.replace("_", "-")
                for token in re.findall(r"[a-z0-9][a-z0-9_.+-]*", query.lower())
                if len(token) > 1
            ))
            query_phrase = " ".join(terms)

            def tokens_for(value: str) -> set[str]:
                return {
                    token.replace("_", "-")
                    for token in re.findall(r"[a-z0-9][a-z0-9_.+-]*", value.lower())
                }

            def token_matches(term: str, token: str) -> bool:
                return term == token or (
                    min(len(term), len(token)) >= 4
                    and (term.startswith(token) or token.startswith(term))
                )

            def relevance(lesson: CourseLesson) -> int:
                title = f"{lesson.title} {lesson.lesson_id}".lower()
                title_tokens = tokens_for(title)
                searchable = " ".join((
                    lesson.title, lesson.lesson_id, lesson.track_id, lesson.category,
                    lesson.objective, lesson.practice, lesson.assessment, lesson.benchmark,
                    lesson.source_url, lesson.source_video_id,
                    " ".join(lesson.division_targets), " ".join(lesson.masterbot_targets),
                    " ".join(lesson.video_categories), " ".join(lesson.capability_tags), " ".join(lesson.tool_tags),
                    " ".join(lesson.agent_tags), " ".join(lesson.implementation_steps),
                    lesson.buddy_demo,
                ))
                search_tokens = tokens_for(searchable)
                matched_terms = [
                    term for term in terms
                    if any(token_matches(term, token) for token in search_tokens)
                ]
                if not matched_terms:
                    return 0
                title_matches = [
                    term for term in terms
                    if any(token_matches(term, token) for token in title_tokens)
                ]
                tag_tokens = tokens_for(" ".join(lesson.capability_tags))
                tag_matches = [
                    term for term in terms
                    if any(token_matches(term, token) for token in tag_tokens)
                ]
                score = len(matched_terms) * 5 + len(title_matches) * 20 + len(tag_matches) * 15
                normalized_title = " ".join(
                    token.replace("_", "-")
                    for token in re.findall(r"[a-z0-9][a-z0-9_.+-]*", title.lower())
                )
                if query_phrase and query_phrase in normalized_title:
                    score += 100
                if terms and len(matched_terms) == len(terms):
                    score += 25
                if lesson.source_video_id and any(token_matches(term, lesson.source_video_id.lower()) for term in terms):
                    score += 50
                return score

            ranked = [
                (score, index, lesson)
                for index, lesson in enumerate(lessons)
                if (score := relevance(lesson)) > 0
            ]
            ranked.sort(key=lambda item: (-item[0], item[1]))
            lessons = [lesson for _, _, lesson in ranked]
        total_count = len(lessons)
        page_lessons = lessons[offset:offset + limit]
        next_offset = offset + len(page_lessons)
        if next_offset >= total_count:
            next_offset = None
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
            "source_video_id": lesson.source_video_id,
            "video_categories": list(lesson.video_categories),
            "guide_path": lesson.guide_path,
            "division_targets": list(lesson.division_targets),
            "masterbot_targets": list(lesson.masterbot_targets),
            "capability_tags": list(lesson.capability_tags),
            "tool_tags": list(lesson.tool_tags),
            "agent_tags": list(lesson.agent_tags),
            "learning_modes": list(lesson.learning_modes),
            "implementation_steps": list(lesson.implementation_steps),
            "buddy_demo": lesson.buddy_demo,
            "rights_mode": lesson.rights_mode,
            "content_status": lesson.content_status,
            "completion_status": (
                "queued_not_studied" if lesson.content_status == "authored"
                else "metadata_only" if lesson.content_status == "metadata_only"
                else "authoring_backlog"
            ),
            "study_allowed": lesson.content_status == "authored",
            "authoring_required": lesson.content_status in {"authoring_backlog", "metadata_only", "original_implementation_brief"},
            "mastery_awarded": False,
            "model_weight_training_authorized": False,
            "paid_compute_authorized": False,
        } for lesson in page_lessons]
        return {
            "schema": "dreamco.buddy_bootcamp_learning_queue.v1",
            **owner,
            "query": query,
            "scope": "shared_foundation_plus_specialist_division_and_masterbot_learning_routes",
            "catalog_lesson_count": len(catalog_lessons),
            "study_ready_count": sum(lesson.content_status == "authored" for lesson in lessons),
            "authoring_backlog_count": sum(lesson.content_status != "authored" for lesson in lessons),
            "available_count": total_count,
            "total_count": total_count,
            "offset": offset,
            "next_offset": next_offset,
            "has_more": next_offset is not None,
            "returned_count": len(items),
            "track_ids": sorted({lesson.track_id for lesson in lessons}),
            "items": items,
            "study_required": True,
            "mastery_awarded": False,
            "external_discovery_performed": False,
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
