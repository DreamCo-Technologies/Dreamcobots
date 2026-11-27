#!/usr/bin/env python3
"""Build a compact, attributed O*NET task index for Buddy's internal study queue.

The index stores public task metadata and provenance only. It does not certify
occupational competence, grant professional authority, or mark tasks mastered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from tools.build_onet_task_curricula import pick, read_rows
except ModuleNotFoundError:
    from build_onet_task_curricula import pick, read_rows

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/buddy-onet-content-model-curriculum.json"


def build_task_index(
    rows: list[dict[str, str]],
    *,
    version: str,
    source_url: str,
    source_bytes: bytes,
    curriculum: dict[str, Any],
    minimum_task_count: int = 10000,
) -> dict[str, Any]:
    """Normalize task statements, preserving stable O*NET IDs and release evidence."""
    tasks: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    missing_identity_count = 0
    duplicate_count = 0

    for row in rows:
        occupation_code = pick(row, "O*NET-SOC Code", "O*NET SOC Code", "onetsoc_code", "occupation code")
        task_id = pick(row, "Task ID", "task id", "id")
        statement = pick(row, "Task", "Task Statement", "task statement", "title")
        if not occupation_code or not task_id or not statement:
            missing_identity_count += 1
            continue
        identity = (occupation_code, task_id)
        if identity in seen:
            duplicate_count += 1
            continue
        seen.add(identity)
        tasks.append({
            "onet_release": version,
            "occupation_code": occupation_code,
            "occupation_title": pick(row, "Occupation Title", "Title"),
            "task_id": task_id,
            "task_statement": statement,
            "task_type": pick(row, "Task Type", "task type", "category") or "unspecified",
            "date": pick(row, "Date", "date") or None,
            "domain_source": pick(row, "Domain Source", "domain source") or None,
            "importance": pick(row, "Importance", "importance") or None,
        })

    tasks.sort(key=lambda item: (item["occupation_code"], item["task_id"]))
    source_config = curriculum.get("source", {})
    reference_release = str(source_config.get("current_reference_release", ""))
    expected_task_count = next(
        (int(item["rows"]) for item in curriculum.get("source_files", [])
         if item.get("name") == "Task Statements" and isinstance(item.get("rows"), int)),
        None,
    )
    release_matches_reference = bool(reference_release and version == reference_release)
    expected_count_matches = expected_task_count is not None and len(tasks) == expected_task_count
    minimum_count_passed = len(tasks) >= minimum_task_count
    identity_integrity_passed = missing_identity_count == 0 and duplicate_count == 0
    complete = (
        minimum_count_passed
        and identity_integrity_passed
        and release_matches_reference
        and expected_count_matches
    )
    occupations = {item["occupation_code"] for item in tasks}
    return {
        "schema": "dreamco.buddy_onet_task_index.v1",
        "title": "Buddy O*NET Task-Level Study Index",
        "status": "verified_complete_release_snapshot" if complete else "release_review_required",
        "source": {
            "name": "O*NET Database",
            "release_version": version,
            "official_release_page": "https://www.onetcenter.org/database.html",
            "official_download_url": source_url,
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "download_bytes": len(source_bytes),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "license": "Creative Commons Attribution 4.0 International (CC BY 4.0), subject to the current O*NET license notice.",
            "attribution": "Credit the O*NET Database and the U.S. Department of Labor, Employment and Training Administration; link to CC BY 4.0 and indicate changes.",
            "guide_standard": "docs/BUDDY_ONET_FULL_CONTENT_MODEL_AND_TASK_PLAYBOOKS.md",
        },
        "inventory": {
            "occupation_count": len(occupations),
            "task_statement_count": len(tasks),
            "expected_task_count_for_reference_release": expected_task_count,
            "minimum_task_count": minimum_task_count,
            "minimum_count_passed": minimum_count_passed,
            "release_matches_reference": release_matches_reference,
            "expected_count_matches": expected_count_matches,
            "missing_identity_count": missing_identity_count,
            "duplicate_identity_count": duplicate_count,
            "identity_integrity_passed": identity_integrity_passed,
            "complete": complete,
        },
        "task_guide_policy": {
            "task_metadata_is_not_a_detailed_guide": True,
            "each_task_requires_original_workflow_and_practice": True,
            "each_task_requires_ai_human_suitability_review": True,
            "professional_license_or_authority_is_never_inferred": True,
            "mastery_requires_unseen_assessment_and_reviewer_evidence": True,
        },
        "tasks": tasks,
        "truth_boundary": (
            "This is a task-level study index, not 18,000 completed study guides, "
            "occupational certifications, licenses, job placement, or proof Buddy can "
            "perform the listed work. Task-specific guides and capability evidence remain pending."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Official O*NET task_statements JSON or CSV")
    parser.add_argument("--metadata", required=True, type=Path, help="JSON containing release_version and official_download_url")
    parser.add_argument("--out", type=Path, default=ROOT / "data/onet/onet-task-index.json")
    parser.add_argument("--minimum-task-count", type=int, default=10000)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    raw = args.input.read_bytes()
    rows = read_rows(args.input)
    curriculum = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    result = build_task_index(
        rows,
        version=str(metadata["release_version"]),
        source_url=str(metadata["official_download_url"]),
        source_bytes=raw,
        curriculum=curriculum,
        minimum_task_count=args.minimum_task_count,
    )
    if result["inventory"]["task_statement_count"] < args.minimum_task_count:
        raise SystemExit("O*NET task inventory is below the minimum completeness threshold")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["inventory"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
