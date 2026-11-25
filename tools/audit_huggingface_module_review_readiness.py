#!/usr/bin/env python3
"""Audit authored/reviewed Hugging Face Bootcamp module artifacts separately from catalog drafts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "config/buddy-huggingface-18-ecosystem-module-guides.json"
REVIEWS = ROOT / "config/buddy-huggingface-module-review-artifacts.json"
OUTPUT = ROOT / "config/generated/huggingface-module-review-readiness.json"
GUIDE_SCHEMA = "dreamco.huggingface_18_ecosystem_module_guides.v1"
REVIEW_SCHEMA = "dreamco.huggingface_module_review_artifacts.v1"


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(guides: dict[str, Any], reviews: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    if guides.get("schema") != GUIDE_SCHEMA:
        raise ValueError("unsupported Hugging Face guide schema")
    if reviews.get("schema") != REVIEW_SCHEMA:
        raise ValueError("unsupported Hugging Face review artifact schema")
    modules = guides.get("modules")
    courses = guides.get("official_courses")
    artifacts = reviews.get("modules", [])
    if not isinstance(modules, list) or len(modules) != 18:
        raise ValueError("exactly 18 Hugging Face ecosystem module drafts are required")
    if not isinstance(courses, list) or len(courses) != 12:
        raise ValueError("exactly 12 official course references are required")
    expected_ids = [f"HFEC-{i:02d}" for i in range(1, 19)]
    actual_ids = [row.get("module_id") for row in modules if isinstance(row, dict)]
    if actual_ids != expected_ids:
        raise ValueError("Hugging Face module IDs must be contiguous in prerequisite order")
    if any(row.get("transcript_permission") != "not_granted" or row.get("training_data_authorized") is not False for row in courses):
        raise ValueError("official course transcript/training permissions must remain ungranted")
    if not isinstance(artifacts, list):
        raise ValueError("review modules must be an array")

    by_id: dict[str, dict[str, Any]] = {}
    for row in artifacts:
        if not isinstance(row, dict) or not isinstance(row.get("module_id"), str):
            raise ValueError("each review artifact requires a module_id")
        module_id = row["module_id"]
        if module_id not in expected_ids:
            raise ValueError(f"non-canonical Hugging Face module: {module_id}")
        if module_id in by_id:
            raise ValueError(f"duplicate review artifact: {module_id}")
        by_id[module_id] = row

    result_rows = []
    gaps = {"guide_missing": 0, "lab_missing": 0, "assessment_missing": 0,
            "citations_missing_or_undated": 0, "rights_review_missing": 0,
            "human_review_missing": 0}
    for module in modules:
        module_id = module["module_id"]
        row = by_id.get(module_id, {})
        path_status = {}
        for field in ("guide_path", "lab_path", "assessment_path"):
            raw = row.get(field)
            exists = False
            if isinstance(raw, str) and raw.startswith("docs/bootcamp/huggingface/"):
                candidate = (root / raw).resolve()
                try:
                    candidate.relative_to(root.resolve())
                except ValueError:
                    pass
                else:
                    exists = candidate.is_file()
                    if exists and row.get(field.replace("_path", "_sha256")) != file_sha(candidate):
                        exists = False
            path_status[field] = exists
        citations = row.get("citations")
        citations_ok = isinstance(citations, list) and bool(citations) and all(
            isinstance(c, dict) and isinstance(c.get("url"), str) and c.get("url").startswith("https://")
            and c.get("accessed_at") and c.get("rights_evidence_ref")
            for c in citations
        )
        rights_ok = row.get("rights_review") == "approved"
        human_ok = (
            row.get("human_review") == "approved"
            and bool(row.get("reviewer"))
            and bool(row.get("reviewed_at"))
        )
        if not path_status["guide_path"]:
            gaps["guide_missing"] += 1
        if not path_status["lab_path"]:
            gaps["lab_missing"] += 1
        if not path_status["assessment_path"]:
            gaps["assessment_missing"] += 1
        if not citations_ok:
            gaps["citations_missing_or_undated"] += 1
        if not rights_ok:
            gaps["rights_review_missing"] += 1
        if not human_ok:
            gaps["human_review_missing"] += 1
        ready = all(path_status.values()) and citations_ok and rights_ok and human_ok
        result_rows.append({
            "module_id": module_id,
            "title": module.get("title", ""),
            "status": "ready_for_study" if ready else "draft_or_review_pending",
            "artifacts": path_status,
            "citation_count": len(citations) if isinstance(citations, list) else 0,
            "rights_review": row.get("rights_review", "pending"),
            "human_review": row.get("human_review", "pending"),
            "reviewer": row.get("reviewer"),
            "reviewed_at": row.get("reviewed_at"),
            "benchmark_evidence_status": "not_assessed",
        })
    ready_count = sum(row["status"] == "ready_for_study" for row in result_rows)
    return {
        "schema": "dreamco.huggingface_module_review_readiness.v1",
        "official_course_reference_count": len(courses),
        "module_count": len(modules),
        "ready_for_study_count": ready_count,
        "review_pending_count": len(modules) - ready_count,
        "gap_counts": gaps,
        "status": "ready_for_study" if ready_count == len(modules) else "human_review_and_artifact_gaps",
        "modules": result_rows,
        "transcripts_downloaded": False,
        "transcript_permission_granted": False,
        "training_data_authorized": False,
        "study_completed": False,
        "mastery_awarded": False,
        "truth_boundary": "A ready_for_study module has authored and reviewed materials; it does not mean Buddy studied it, passed an assessment, demonstrated mastery, or trained on official course content.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    guides = json.loads(GUIDES.read_text(encoding="utf-8"))
    reviews = json.loads(REVIEWS.read_text(encoding="utf-8"))
    report = audit(guides, reviews)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "official_course_reference_count", "module_count",
        "ready_for_study_count", "review_pending_count", "gap_counts",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
