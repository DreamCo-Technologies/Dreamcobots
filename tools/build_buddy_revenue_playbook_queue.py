#!/usr/bin/env python3
"""Build a transparent task-by-task playbook authoring queue from the canonical career/business curriculum.

The queue creates work items only. It does not claim the playbooks are authored,
validated, profitable, legally sufficient, or ready for autonomous execution.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/buddy-workforce-entrepreneurship-bootcamp.json"

REQUIRED_SECTIONS = (
    "task_definition", "inputs_and_outputs", "workflow_steps", "decision_points",
    "tools_and_software", "tool_selection_rationale", "integrations_and_APIs",
    "data_and_permission_requirements", "automation_opportunities",
    "human_approval_points", "quality_and_acceptance_tests",
    "failure_modes_and_recovery", "security_privacy_and_compliance",
    "cost_and_time_estimates", "credentials_and_licensing",
    "customer_or_employer_value", "portfolio_project", "sales_or_employment_pathway",
)

REVIEW_GATES = (
    "source_and_fact_verification",
    "jurisdiction_and_eligibility_check_when_relevant",
    "privacy_and_permission_review",
    "cost_and_unit_economics_review",
    "human_approval_for_external_commitments",
    "independent_acceptance_test",
)

def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "unnamed"

def build_queue(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("schema") != "dreamco.buddy_workforce_entrepreneurship_bootcamp.v1":
        raise ValueError("unsupported workforce/entrepreneurship bootcamp schema")
    paths = config.get("training_paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("training_paths must be a non-empty list")
    required = config.get("task_capability_catalog", {}).get("task_playbook_requirements")
    if not isinstance(required, list) or not required:
        raise ValueError("canonical task_playbook_requirements are missing")

    seen_tracks: set[str] = set()
    queue: list[dict[str, Any]] = []
    for track in paths:
        if not isinstance(track, dict):
            raise ValueError("training path rows must be objects")
        track_id = str(track.get("id", "")).strip()
        title = str(track.get("title", "")).strip()
        subjects = track.get("subjects")
        capstone = str(track.get("capstone", "")).strip()
        if not track_id or track_id in seen_tracks or not title:
            raise ValueError("training path IDs must be unique and titles non-empty")
        seen_tracks.add(track_id)
        if not isinstance(subjects, list) or not subjects or any(not isinstance(x, str) or not x.strip() for x in subjects):
            raise ValueError(f"{track_id}: subjects must be a non-empty list of non-empty strings")
        if not capstone:
            raise ValueError(f"{track_id}: a capstone outcome is required")
        seen_subjects: set[str] = set()
        for index, subject in enumerate(subjects, start=1):
            normalized = subject.strip()
            if normalized.casefold() in seen_subjects:
                raise ValueError(f"{track_id}: duplicate subject {normalized!r}")
            seen_subjects.add(normalized.casefold())
            queue.append({
                "playbook_id": f"REV-{slug(track_id)}-{index:03d}",
                "track_id": track_id,
                "track_title": title,
                "sequence": index,
                "subject": normalized,
                "capstone_outcome": capstone,
                "status": "not_authored",
                "authored_lesson_ref": None,
                "reviewed_playbook_ref": None,
                "required_sections": list(required),
                "review_gates": list(REVIEW_GATES),
                "authoring_brief": {
                    "objective": f"Teach and assess the real-world workflow for {normalized}.",
                    "must_identify": [
                        "beginner prerequisites",
                        "legitimate user/employer/customer outcome",
                        "current tools and verified alternatives",
                        "required data, access, permissions and credentials",
                        "costs, pricing and operational constraints",
                        "human decisions and approval boundaries",
                        "measurable acceptance criteria",
                    ],
                    "must_not_assume": [
                        "guaranteed employment, income, funding or business success",
                        "professional licensing or legal/tax authority",
                        "current vendor pricing or integrations without verification",
                        "permission to access accounts, contact third parties or spend money",
                    ],
                },
            })
    return {
        "schema": "dreamco.buddy_revenue_playbook_queue.v1",
        "source_manifest": "config/buddy-workforce-entrepreneurship-bootcamp.json",
        "track_count": len(seen_tracks),
        "playbook_work_item_count": len(queue),
        "authored_count": 0,
        "reviewed_count": 0,
        "status": "authoring_queue_only",
        "tracks": sorted(seen_tracks),
        "playbooks": queue,
        "truth_boundary": "Queue entries are authoring tasks, not completed playbooks, verified advice, guaranteed outcomes, or permission to execute external actions.",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = json.loads(args.source.read_text(encoding="utf-8"))
    result = build_queue(config)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
