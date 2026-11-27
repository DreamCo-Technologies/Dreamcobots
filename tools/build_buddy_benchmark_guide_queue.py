#!/usr/bin/env python3
"""Build a benchmark guide/evidence work queue from DreamCo's canonical registries.

This indexes required authoring and validation work. It never claims a benchmark
has run, that a score is measured, or that a benchmark suite is certified.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "config/buddy-benchmark-index.json"
TASKS = ROOT / "config/buddy-benchmark-task-registry.json"

GUIDE_SECTIONS = (
    "benchmark_purpose", "target_capability", "task_and_dataset_provenance",
    "workload_and_environment", "baseline_and_comparator", "metrics_and_scoring",
    "acceptance_thresholds", "reproducibility_and_seeds", "holdout_and_contamination_controls",
    "safety_and_permission_boundaries", "artifact_and_evidence_schema",
    "failure_analysis_and_remediation", "known_limitations", "review_and_version_history",
)

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"

def build_queue(index: dict[str, Any], task_registry: dict[str, Any]) -> dict[str, Any]:
    if index.get("schema") != "dreamco.benchmark_index_source.v1":
        raise ValueError("unsupported benchmark index schema")
    if task_registry.get("schema") != "dreamco.buddy_benchmark_registry.v1":
        raise ValueError("unsupported benchmark task registry schema")
    programs = index.get("programs")
    tasks = task_registry.get("tasks")
    if not isinstance(programs, list) or not programs:
        raise ValueError("benchmark programs must be a non-empty list")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("benchmark tasks must be a non-empty list")

    seen_programs: set[str] = set()
    queue: list[dict[str, Any]] = []
    for program in programs:
        if not isinstance(program, dict):
            raise ValueError("benchmark program rows must be objects")
        item_id = str(program.get("id", "")).strip()
        name = str(program.get("name", "")).strip()
        if not item_id or item_id in seen_programs or not name:
            raise ValueError("benchmark program IDs must be unique and names non-empty")
        seen_programs.add(item_id)
        queue.append({
            "work_item_id": f"BENCH-PROGRAM-{slug(item_id)}",
            "work_item_type": "program_guide",
            "benchmark_id": item_id,
            "title": name,
            "scope": program.get("scope", ""),
            "generator": program.get("generator"),
            "check_command": program.get("check_command"),
            "guide_status": "not_authored_or_not_linked",
            "test_status": "execution_evidence_required",
            "measured": False,
            "required_sections": list(GUIDE_SECTIONS),
            "acceptance": [
                "guide is linked to the canonical benchmark ID",
                "test command is executable in a safe isolated environment",
                "evidence records exact code/model/dataset versions",
                "holdout and contamination controls are documented",
                "scores are not populated until a real run completes",
            ],
        })

    seen_tasks: set[str] = set()
    for task in tasks:
        if not isinstance(task, str) or not task.strip():
            raise ValueError("benchmark task names must be non-empty strings")
        normalized = task.strip()
        if normalized.casefold() in seen_tasks:
            raise ValueError(f"duplicate benchmark task {normalized!r}")
        seen_tasks.add(normalized.casefold())
        queue.append({
            "work_item_id": f"BENCH-TASK-{slug(normalized)}",
            "work_item_type": "task_guide",
            "benchmark_id": f"task-{slug(normalized)}",
            "title": f"{normalized} benchmark task guide",
            "scope": f"Define representative, adversarial and unseen-transfer tasks for {normalized}.",
            "guide_status": "not_authored_or_not_linked",
            "test_status": "execution_evidence_required",
            "measured": False,
            "required_sections": list(GUIDE_SECTIONS),
            "acceptance": [
                "task has deterministic input/output contract",
                "expected behavior and failure rubric are explicit",
                "at least one held-out transfer case is defined",
                "safety and permission checks are included",
                "results are tied to an immutable run record",
            ],
        })

    ids = [row["work_item_id"] for row in queue]
    if len(ids) != len(set(ids)):
        raise ValueError("generated benchmark work item IDs are not unique")
    return {
        "schema": "dreamco.buddy_benchmark_guide_queue.v1",
        "source_index": "config/buddy-benchmark-index.json",
        "source_task_registry": "config/buddy-benchmark-task-registry.json",
        "program_count": len(programs),
        "task_count": len(tasks),
        "work_item_count": len(queue),
        "measured_count": 0,
        "status": "guide_and_evidence_backlog",
        "work_items": queue,
        "truth_boundary": "An indexed benchmark or queued guide is not an executed benchmark, measured score, certified capability, or model mastery claim.",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--tasks", type=Path, default=TASKS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_queue(
        json.loads(args.index.read_text(encoding="utf-8")),
        json.loads(args.tasks.read_text(encoding="utf-8")),
    )
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
