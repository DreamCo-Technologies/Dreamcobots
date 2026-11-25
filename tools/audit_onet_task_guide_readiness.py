#!/usr/bin/env python3
"""Audit O*NET occupation/task guide readiness without inventing guide content.

Consumes the generated onet-task-curricula.v1 document. A task is not ready
until its authored guide, practice, assessment, citations and review evidence
are explicitly recorded. This audit never marks a task complete or mastered.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def audit(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("schema") != "dreamco.onet_task_curricula.v1":
        raise ValueError("unsupported O*NET task curriculum schema")
    occupations = document.get("occupations")
    if not isinstance(occupations, list):
        raise ValueError("occupations must be an array")

    tasks_seen: set[tuple[str, str]] = set()
    task_count = 0
    duplicate_count = 0
    gaps = {
        "guide_not_authored": 0,
        "practice_missing": 0,
        "assessment_missing": 0,
        "citations_missing": 0,
        "rights_review_missing": 0,
        "human_review_missing": 0,
    }
    occupation_rows = []
    for occupation in occupations:
        if not isinstance(occupation, dict):
            raise ValueError("each occupation must be an object")
        code = str(occupation.get("occupation_code", "")).strip()
        if not code:
            raise ValueError("occupation record is missing occupation_code")
        tasks = occupation.get("task_playbooks")
        if not isinstance(tasks, list):
            raise ValueError(f"{code}: task_playbooks must be an array")
        occupation_task_count = 0
        ready_count = 0
        for task in tasks:
            if not isinstance(task, dict):
                raise ValueError(f"{code}: task playbook must be an object")
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                raise ValueError(f"{code}: task playbook is missing task_id")
            identity = (code, task_id)
            if identity in tasks_seen:
                duplicate_count += 1
                continue
            tasks_seen.add(identity)
            task_count += 1
            occupation_task_count += 1

            guide = task.get("authored_guide")
            guide_ok = (
                isinstance(guide, dict)
                and bool(str(guide.get("content_path", "")).strip())
                and guide.get("status") == "authored"
                and bool(guide.get("version"))
            )
            practice_ok = bool(task.get("practice_exercises"))
            assessment_ok = bool(task.get("assessment"))
            citations_ok = bool(task.get("citations")) and all(
                isinstance(c, dict) and c.get("url") and c.get("accessed_at")
                for c in task.get("citations", [])
            )
            rights_ok = task.get("rights_review") == "approved"
            human_review_ok = task.get("human_review") == "approved"

            if not guide_ok:
                gaps["guide_not_authored"] += 1
            if not practice_ok:
                gaps["practice_missing"] += 1
            if not assessment_ok:
                gaps["assessment_missing"] += 1
            if not citations_ok:
                gaps["citations_missing"] += 1
            if not rights_ok:
                gaps["rights_review_missing"] += 1
            if not human_review_ok:
                gaps["human_review_missing"] += 1
            if all((guide_ok, practice_ok, assessment_ok, citations_ok, rights_ok, human_review_ok)):
                ready_count += 1

        occupation_rows.append({
            "occupation_code": code,
            "occupation_title": occupation.get("occupation_title", ""),
            "task_count": occupation_task_count,
            "ready_for_study_review": ready_count,
        })

    ready_total = sum(row["ready_for_study_review"] for row in occupation_rows)
    return {
        "schema": "dreamco.onet_task_guide_readiness_audit.v1",
        "status": "structural_errors" if duplicate_count else ("all_tasks_ready_for_review" if task_count and ready_total == task_count else "guide_coverage_gaps"),
        "source_version": document.get("source", {}).get("version"),
        "occupation_count": len(occupation_rows),
        "task_count": task_count,
        "duplicate_task_count": duplicate_count,
        "ready_for_study_review": ready_total,
        "not_ready_for_study_review": task_count - ready_total,
        "gap_counts": gaps,
        "occupations": occupation_rows,
        "completion_claim": False,
        "mastery_claim": False,
        "truth_boundary": "Readiness means required guide artifacts and reviews are recorded; it is not evidence of learning, competence, occupational qualification, certification, or mastery.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Generated onet-task-curricula.json")
    parser.add_argument("--output", type=Path, help="Optional JSON report destination")
    args = parser.parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8"))
    report = audit(document)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if report["duplicate_task_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
