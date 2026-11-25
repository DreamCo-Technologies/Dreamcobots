"""Runtime adapter that routes approved DreamCo summary packages into Buddy's study scheduler.

The adapter consumes the organizer artifact; it never infers rights, creates summaries,
changes model weights, or awards mastery merely because a package exists.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

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
                          score: float | None = None, training_permission: bool = False) -> dict:
    if event_type == "mastery_awarded":
        raise PermissionError("mastery is computed only by the evidence verifier, never self-reported")
    if event_type not in EVENTS:
        raise ValueError(f"unsupported progress event: {event_type}")
    if event_type.startswith("training_run_") and training_permission is not True:
        raise PermissionError("training progress requires explicit asset training permission")
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
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\\n")
    return event
