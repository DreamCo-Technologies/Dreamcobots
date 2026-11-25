"""Runtime adapter that routes approved DreamCo summary packages into Buddy's study scheduler.

The adapter consumes the organizer artifact; it never infers rights, creates summaries,
changes model weights, or awards mastery merely because a package exists.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Callable, Any

from buddy.learning.permissioned_study_worker import StudyAuthorization, run_study_attempt
from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next, study_plan

SCHEMA = "dreamco.buddy_learning_organization.v1"
EVENTS = {
    "asset_assigned", "study_started", "lesson_completed",
    "knowledge_check_submitted", "exercise_passed", "capstone_submitted",
    "capstone_passed", "remediation_assigned",
    "training_run_started", "training_run_completed", "training_run_evaluated",
}


def stable_resource_id(asset_id: str) -> int:
    if not isinstance(asset_id, str) or not asset_id.strip():
        raise ValueError("asset_id must be a non-empty string")
    value = int.from_bytes(hashlib.sha256(asset_id.encode("utf-8")).digest()[:8], "big") & 0x7FFFFFFFFFFFFFFF
    return value or 1


def load_organization(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError("unsupported DreamCo learning organization schema")
    if not isinstance(payload.get("packages"), list) or not isinstance(payload.get("division_curricula"), list):
        raise ValueError("learning organization is missing packages or division curricula")
    return payload


def resources_for_division(division: str, path: Path) -> list[Resource]:
    if not isinstance(division, str) or not division.strip():
        raise ValueError("division must be a non-empty canonical division name")
    payload = load_organization(path)
    known = {row.get("division") for row in payload["division_curricula"]}
    if division not in known:
        raise ValueError(f"unknown division: {division}")
    resources = []
    seen: dict[int, str] = {}
    for package in payload["packages"]:
        if division not in package.get("division_ids", []):
            continue
        rights = package.get("rights") or {}
        if not all(rights.get(key) is True for key in ("study_permission", "summary_derivative_permission", "evaluation_permission")):
            continue
        asset_id = package.get("asset_id")
        resource_id = stable_resource_id(asset_id)
        if resource_id in seen and seen[resource_id] != asset_id:
            raise ValueError("stable learning asset ID collision")
        seen[resource_id] = asset_id
        source = package.get("source") or {}
        resources.append(Resource(
            id=resource_id,
            name=(package.get("summary") or {}).get("executive_overview", asset_id)[:120],
            category=" ".join(package.get("division_ids", [])),
            url=source.get("url", ""),
            methods=("read_original_summary", "deep_study_path", "worked_examples", "sandbox_exercises",
                     "knowledge_check", "independent_capstone", "record_progress_evidence"),
        ))
    return resources


def select_next_for_division(division: str, gaps: Iterable[Capability], path: Path, *, recent: set[int] | None = None) -> dict | None:
    payload = load_organization(path)
    resources = resources_for_division(division, path)
    gap_list = list(gaps)
    resource = choose_next(resources, gap_list, recent=recent)
    if resource is None:
        return None
    package = next((row for row in payload["packages"] if stable_resource_id(row.get("asset_id")) == resource.id), None)
    if package is None:
        raise ValueError("selected learning resource has no package")
    capability = gap_list[0] if gap_list else None
    if capability is None:
        capability = Capability(name=division, category=division)
    plan = study_plan(resource, capability)
    plan.update({
        "division": division,
        "asset_id": package["asset_id"],
        "source": package.get("source"),
        "source_revision": (package.get("source") or {}).get("revision"),
        "summary": package.get("summary"),
        "study_path": package.get("study_path"),
        "assessment": package.get("assessment"),
        "ownership": package.get("ownership"),
        "rights": package.get("rights"),
        "weight_training_eligible": package.get("training", {}).get("weight_training_eligible") is True,
        "completion_status": "queued_not_studied",
    })
    return plan


def append_progress_event(path: Path, *, asset_id: str, division: str, event_type: str,
                          evidence_ref: str, source_revision: str | None = None,
                          score: float | None = None, organization_path: Path) -> dict:
    if event_type == "mastery_awarded":
        raise PermissionError("mastery is computed only by the evidence verifier, never self-reported")
    if event_type not in EVENTS:
        raise ValueError(f"unsupported progress event: {event_type}")
    organization = load_organization(organization_path)
    package = next((row for row in organization["packages"] if row.get("asset_id") == asset_id), None)
    if package is None or division not in package.get("division_ids", []):
        raise ValueError("progress event must reference a known asset assigned to this division")
    package_revision = (package.get("source") or {}).get("revision")
    if source_revision is not None and source_revision != package_revision:
        raise ValueError("progress event source revision does not match the learning asset")
    if event_type.startswith("training_run_") and (
        package.get("training", {}).get("weight_training_eligible") is not True
        or (package.get("rights") or {}).get("training_permission") is not True
    ):
        raise PermissionError("this learning asset is not explicitly authorized for model-weight training")
    if not asset_id or not division or not evidence_ref:
        raise ValueError("asset_id, division and evidence_ref are required")
    if score is not None and not 0 <= score <= 1:
        raise ValueError("score must be between 0 and 1")
    event = {
        "event_id": hashlib.sha256(f"{asset_id}|{division}|{event_type}|{evidence_ref}".encode()).hexdigest(),
        "asset_id": asset_id,
        "division": division,
        "event_type": event_type,
        "evidence_ref": evidence_ref,
        "source_revision": source_revision,
        "score": score,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and json.loads(line).get("event_id") == event["event_id"]:
                return json.loads(line)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def execute_study_plan(plan: dict, authorization: StudyAuthorization, study: Callable[[Any], Any],
                       workspace_root: Path, progress_path: Path, organization_path: Path) -> dict:
    """Execute one approved summary study attempt through Buddy's cleanup boundary.

    The callback receives a read-only StudyContext and may use the in-memory plan.
    Only the official source page is authorized; this adapter never downloads media,
    ingests transcripts, or trains model weights.
    """
    if plan.get("completion_status") != "queued_not_studied":
        raise ValueError("only queued, not-yet-studied summary plans can be executed")
    source = plan.get("source") or {}
    rights = plan.get("rights") or {}
    if authorization.source_url != source.get("url"):
        raise ValueError("study authorization URL does not match the selected summary")
    if authorization.source_name != source.get("source_id"):
        raise ValueError("study authorization source ID does not match the selected summary")
    if authorization.review_status != "approved" or not authorization.evidence_ref:
        raise PermissionError("summary execution requires approved rights evidence")
    if rights.get("evidence_ref") != authorization.evidence_ref:
        raise PermissionError("study authorization evidence does not match the summary package")
    if set(authorization.allowed_operations) != {"open_official_page"}:
        raise PermissionError("summary study is read-only; media download and transcript ingestion are not authorized")
    result = run_study_attempt(authorization, lambda context: study(plan, context), workspace_root)
    evidence = result.get("result") if isinstance(result.get("result"), dict) else {}
    recorded_events = []
    def emit(event_type: str, evidence_ref: str, score: float | None = None) -> None:
        append_progress_event(
            progress_path, asset_id=plan["asset_id"], division=plan["division"],
            event_type=event_type, evidence_ref=evidence_ref, score=score,
            source_revision=plan.get("source_revision"), organization_path=organization_path
        )
        recorded_events.append(event_type)

    run_evidence = evidence.get("evidence_ref")
    if run_evidence:
        emit("study_started", run_evidence)
    independent = bool(evidence.get("independent_evaluator_id")) and evidence.get("independent_evaluator_id") != "buddy"
    completed = evidence.get("lesson_status") == "verified_pass" and bool(evidence.get("lesson_evidence_ref")) and independent
    if completed:
        emit("lesson_completed", evidence["lesson_evidence_ref"])
    if evidence.get("knowledge_check_evidence_ref"):
        emit("knowledge_check_submitted", evidence["knowledge_check_evidence_ref"], evidence.get("knowledge_check_score"))
    if evidence.get("exercise_status") == "verified_pass" and evidence.get("exercise_evidence_ref") and independent:
        emit("exercise_passed", evidence["exercise_evidence_ref"])
    if evidence.get("capstone_evidence_ref"):
        emit("capstone_submitted", evidence["capstone_evidence_ref"])
    if evidence.get("capstone_status") == "verified_pass" and evidence.get("capstone_pass_evidence_ref") and independent:
        emit("capstone_passed", evidence["capstone_pass_evidence_ref"])
    if evidence.get("remediation_evidence_ref"):
        emit("remediation_assigned", evidence["remediation_evidence_ref"])
    result["division"] = plan["division"]
    result["asset_id"] = plan["asset_id"]
    result["completion_status"] = "lesson_completed_with_evidence" if completed else "attempted_evidence_pending"
    result["lesson_completed"] = completed
    result["progress_events_recorded"] = recorded_events
    result["model_training_performed"] = False
    return result
