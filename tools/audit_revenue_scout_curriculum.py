#!/usr/bin/env python3
"""Audit task-by-task revenue scout curriculum coverage; never infer mastery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config/buddy-master-scout-opportunity-resource-library-program.json"
LANES = ROOT / "money_os/config/revenue_lanes_expanded.json"
SOURCES = ROOT / "money_os/data/opportunity_sources.json"
ARTIFACTS = ROOT / "config/buddy-revenue-scout-curriculum-artifacts.json"
OUTPUT = ROOT / "config/generated/revenue-scout-curriculum-readiness.json"

REQUIRED_MODULES = (
    "discover", "verify", "economics", "user_fit", "risk_and_rights",
    "prepare", "approval_and_execution", "outcome_and_learning",
)


def audit(program: dict[str, Any], lanes_doc: dict[str, Any],
          sources_doc: dict[str, Any], artifacts_doc: dict[str, Any]) -> dict[str, Any]:
    if program.get("schema") != "dreamco.buddy.master_scout_opportunity_resource_library.v1":
        raise ValueError("unsupported Master Scout program schema")
    if artifacts_doc.get("schema") != "dreamco.revenue_scout_curriculum_artifacts.v1":
        raise ValueError("unsupported revenue curriculum artifact schema")
    scouts = program.get("master_scout_team")
    lanes = lanes_doc.get("lanes")
    categories = sources_doc.get("categories")
    if not isinstance(scouts, list) or not scouts:
        raise ValueError("master_scout_team must be a non-empty array")
    if not isinstance(lanes, list) or not lanes:
        raise ValueError("revenue lanes must be a non-empty array")
    if not isinstance(categories, dict):
        raise ValueError("opportunity source categories must be an object")

    scout_ids = [s.get("id") for s in scouts if isinstance(s, dict)]
    if len(scout_ids) != len(scouts) or any(not isinstance(x, str) or not x for x in scout_ids):
        raise ValueError("every scout requires a non-empty id")
    if len(scout_ids) != len(set(scout_ids)):
        raise ValueError("duplicate scout ids")
    lane_ids = [x.get("id") for x in lanes if isinstance(x, dict)]
    if len(lane_ids) != len(lanes) or len(lane_ids) != len(set(lane_ids)):
        raise ValueError("revenue lanes must have unique ids")
    artifact_rows = artifacts_doc.get("artifacts", [])
    if not isinstance(artifact_rows, list):
        raise ValueError("artifacts must be an array")
    artifact_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in artifact_rows:
        if not isinstance(row, dict):
            raise ValueError("each curriculum artifact must be an object")
        key = (row.get("scout_id"), row.get("module_id"))
        if key in artifact_by_key:
            raise ValueError(f"duplicate artifact: {key}")
        artifact_by_key[key] = row

    rows = []
    gap_counts = {module: 0 for module in REQUIRED_MODULES}
    for scout in scouts:
        scout_id = scout["id"]
        modules = []
        for module_id in REQUIRED_MODULES:
            artifact = artifact_by_key.get((scout_id, module_id), {})
            guide_path = artifact.get("guide_path")
            guide_exists = False
            if isinstance(guide_path, str) and guide_path:
                candidate = (ROOT / guide_path).resolve()
                guide_exists = candidate.is_relative_to(ROOT.resolve()) and candidate.is_file()
            exercises = artifact.get("exercises")
            citations = artifact.get("citations")
            ready = all((
                guide_exists,
                isinstance(exercises, list) and len(exercises) > 0,
                isinstance(artifact.get("assessment"), dict),
                isinstance(citations, list) and len(citations) > 0,
                artifact.get("rights_review") == "approved",
                artifact.get("human_review") == "approved",
            ))
            if not ready:
                gap_counts[module_id] += 1
            modules.append({
                "module_id": module_id,
                "status": "ready_for_study_review" if ready else "not_ready",
                "guide_exists": guide_exists,
                "exercise_count": len(exercises) if isinstance(exercises, list) else 0,
                "assessment_recorded": isinstance(artifact.get("assessment"), dict),
                "citation_count": len(citations) if isinstance(citations, list) else 0,
                "rights_review": artifact.get("rights_review", "pending"),
                "human_review": artifact.get("human_review", "pending"),
            })
        rows.append({
            "scout_id": scout_id,
            "search_focus_count": len(scout.get("searches", [])),
            "modules": modules,
            "ready_module_count": sum(m["status"] == "ready_for_study_review" for m in modules),
        })

    ready_modules = sum(row["ready_module_count"] for row in rows)
    required_modules = len(rows) * len(REQUIRED_MODULES)
    source_counts = {key: len(value) if isinstance(value, list) else 0 for key, value in categories.items()}
    return {
        "schema": "dreamco.revenue_scout_curriculum_readiness.v1",
        "scout_count": len(rows),
        "revenue_lane_count": len(lane_ids),
        "opportunity_source_category_count": len(categories),
        "source_reference_count": sum(source_counts.values()),
        "required_module_count": required_modules,
        "ready_module_count": ready_modules,
        "not_ready_module_count": required_modules - ready_modules,
        "gap_counts": gap_counts,
        "status": "ready_for_study_review" if ready_modules == required_modules else "curriculum_gaps",
        "scouts": rows,
        "execution_claim": False,
        "mastery_claim": False,
        "truth_boundary": "A module is ready for study review only when its authored guide, exercises, assessment, citations, rights review and human review exist. This audit does not prove a learner studied, passed, earned revenue, obtained a grant/job/contract, or completed a transaction.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    docs = [json.loads(path.read_text(encoding="utf-8")) for path in (PROGRAM, LANES, SOURCES, ARTIFACTS)]
    report = audit(*docs)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "status", "scout_count", "revenue_lane_count", "opportunity_source_category_count",
        "required_module_count", "ready_module_count", "not_ready_module_count", "gap_counts"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
