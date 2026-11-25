#!/usr/bin/env python3
"""Schedule approved DreamCo summary packages across all canonical divisions.

Five daily slots are created per division by default. A slot is actionable only
when an approved, rights-cleared original guide exists. Empty slots remain
explicitly blocked/pending; the planner never invents lessons or progress.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from buddy.learning.dreamco_summary_source import (
    load_organization,
    select_next_for_division,
    stable_resource_id,
)
from buddy.learning.study_resource_scheduler import Capability

MAP_SCHEMA = "dreamco.buddy_university_learning_map.v1"


def build_daily_plan(university_map: dict[str, Any], organization_path: Path,
                     day: str, lessons_per_division: int = 5) -> dict[str, Any]:
    date.fromisoformat(day)
    if not isinstance(lessons_per_division, int) or not 1 <= lessons_per_division <= 20:
        raise ValueError("lessons_per_division must be between 1 and 20")
    if university_map.get("schema") != MAP_SCHEMA:
        raise ValueError("unsupported Buddy University map schema")
    divisions = university_map.get("divisions")
    if not isinstance(divisions, list) or len(divisions) != 55:
        raise ValueError("exactly 55 canonical division curricula are required")
    names = [row.get("division") for row in divisions]
    if len(set(names)) != 55 or any(not isinstance(x, str) or not x for x in names):
        raise ValueError("division names must be unique and non-empty")
    organization = load_organization(organization_path)
    package_by_id = {row.get("asset_id"): row for row in organization["packages"]}
    if len(package_by_id) != len(organization["packages"]):
        raise ValueError("learning asset IDs must be unique")
    for package in organization["packages"]:
        if not package.get("asset_id") or not isinstance(package.get("division_ids"), list):
            raise ValueError("learning package identity and division assignments are required")
        if package.get("completion_status") == "mastered":
            raise ValueError("package must not self-assert mastery; progress comes from evidence ledger")
        rights = package.get("rights") or {}
        if not all(rights.get(key) is True for key in (
            "study_permission", "summary_derivative_permission", "evaluation_permission"
        )):
            raise ValueError("organization contains a package without required study/summary/evaluation permissions")

    division_plans = []
    all_asset_ids = set()
    for division_row in sorted(divisions, key=lambda row: row["division"]):
        division = division_row["division"]
        focus = division_row.get("focus_areas", [])
        gaps = [Capability(name=str(item), category=division, score=0.0) for item in focus] or [
            Capability(name=division, category=division, score=0.0)
        ]
        recent: set[int] = set()
        slots = []
        for ordinal in range(1, lessons_per_division + 1):
            plan = select_next_for_division(division, gaps, organization_path, recent=recent)
            if plan is None:
                slots.append({
                    "slot": ordinal,
                    "status": "awaiting_approved_original_summary",
                    "asset_id": None,
                    "reason": "No eligible, reviewed summary package is assigned to this division yet.",
                    "completion_status": "not_started",
                })
                continue
            asset_id = plan["asset_id"]
            recent.add(stable_resource_id(asset_id))
            all_asset_ids.add(asset_id)
            package = package_by_id[asset_id]
            slots.append({
                "slot": ordinal,
                "status": "ready_to_assign",
                "asset_id": asset_id,
                "source": plan.get("source"),
                "source_revision": plan.get("source_revision"),
                "summary": plan.get("summary"),
                "study_path": plan.get("study_path"),
                "assessment": plan.get("assessment"),
                "ownership": plan.get("ownership"),
                "rights": plan.get("rights"),
                "weight_training_eligible": plan.get("weight_training_eligible") is True,
                "completion_status": "queued_not_studied",
                "required_evidence": [
                    "study_started_event", "lesson_and_exercise_attempts",
                    "knowledge_check_score", "independent_capstone",
                    "unseen_transfer_assessment", "review_and_remediation_record"
                ],
                "package_progress": package.get("progress", {}),
            })
        weekly_assets = sorted({
            package["asset_id"] for package in organization["packages"]
            if division in package.get("division_ids", [])
        })
        division_plans.append({
            "division": division,
            "curriculum_sources": {
                "hugging_face_subjects": division_row.get("hugging_face_subjects", []),
                "freecodecamp_tracks": division_row.get("freecodecamp_tracks", []),
                "freecodecamp_video_ids": division_row.get("freecodecamp_video_ids", []),
                "college_domains": division_row.get("college_domains", []),
                "onet_task_refs": division_row.get("onet_task_refs", []),
                "venture_and_workforce_tracks": division_row.get("venture_and_workforce_tracks", []),
                "source_families": division_row.get("source_families", []),
            },
            "daily_target": lessons_per_division,
            "slots": slots,
            "weekly_review": {
                "required": True,
                "eligible_asset_ids": weekly_assets,
                "assess_each_eligible_asset_at_least_once": True,
                "mastery_requires_independent_capstone_and_unseen_transfer": True,
            },
            "progress": {
                "assigned": sum(slot["status"] == "ready_to_assign" for slot in slots),
                "awaiting_summary": sum(slot["status"] == "awaiting_approved_original_summary" for slot in slots),
                "studied": 0,
                "mastered": 0,
                "status": "planned_not_started",
            },
        })
    ready = sum(row["progress"]["assigned"] for row in division_plans)
    waiting = sum(row["progress"]["awaiting_summary"] for row in division_plans)
    return {
        "schema": "dreamco.buddy_university_daily_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "day": day,
        "teacher": university_map.get("instructional_model", {}).get("teacher", {}),
        "student": university_map.get("instructional_model", {}).get("student", {}),
        "parallel_execution": {
            "logical_division_lanes": len(division_plans),
            "eligible_for_parallel_study": len(division_plans),
            "policy": university_map.get("university_curriculum", {}).get("parallel_learning_policy", {}),
            "weight_training_jobs_started": 0,
            "truth_boundary": "Logical parallel study lanes do not imply available compute or model-weight training; runtime capacity and per-asset approvals control execution."
        },
        "division_count": len(division_plans),
        "lessons_per_division_target": lessons_per_division,
        "daily_target_slots": len(division_plans) * lessons_per_division,
        "ready_to_assign_slots": ready,
        "awaiting_approved_summary_slots": waiting,
        "unique_learning_assets_selected": len(all_asset_ids),
        "divisions": division_plans,
        "progress_policy": {
            "queued_is_not_studied": True,
            "summary_reading_is_not_mastery": True,
            "study_and_weight_training_are_separate": True,
            "weight_training_requires_explicit_per_asset_permission": True,
            "progress_events_require_evidence_references": True,
        },
        "truth_boundary": "This is a daily assignment plan. It does not execute a study session, update model weights, or prove Buddy learned anything. Slots without approved summaries remain waiting rather than being filled with fabricated lessons.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--university-map", required=True)
    parser.add_argument("--organization", required=True)
    parser.add_argument("--day", default=date.today().isoformat())
    parser.add_argument("--lessons-per-division", type=int, default=5)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    university_map = json.loads(Path(args.university_map).read_text(encoding="utf-8"))
    result = build_daily_plan(university_map, Path(args.organization), args.day, args.lessons_per_division)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "day", "division_count", "daily_target_slots", "ready_to_assign_slots",
        "awaiting_approved_summary_slots", "unique_learning_assets_selected"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
