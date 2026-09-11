#!/usr/bin/env python3
"""Validate claimable Buddy/frontier benchmark evidence without executing models.

The runner intentionally separates evidence validation from provider execution:
model credentials and paid calls stay in a reviewed adapter or CI secret store.
It rejects incomplete, simulated, or incomparable result bundles for capability claims.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "config" / "frontier-evidence-suite.json"


def assess(bundle: dict, suite: dict) -> dict:
    errors: list[str] = []
    if bundle.get("schema") != "dreamco.buddy.frontier_run_bundle.v1":
        errors.append("invalid schema")
    if bundle.get("claim_context") != "live_comparison":
        errors.append("bundle is not a live comparison")
    if bundle.get("suite_id") != suite["suite_id"]:
        errors.append("wrong suite id")
    if bundle.get("suite_hash") != suite.get("suite_hash"):
        errors.append("suite hash does not match pinned suite")
    required_tasks = {task for lane in suite["lanes"] for task in lane["training_tasks"] + lane["holdout_tasks"]}
    holdouts = {task for lane in suite["lanes"] for task in lane["holdout_tasks"]}
    required = set(suite["evidence_required"])
    rows = bundle.get("runs", [])
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    subjects: set[str] = set()
    for index, row in enumerate(rows):
        missing = sorted(required - set(row))
        if missing:
            errors.append(f"run {index} missing {', '.join(missing)}")
        if row.get("task_id") not in required_tasks:
            errors.append(f"run {index} unknown task")
        if not row.get("fixture_hash") or not row.get("grader_version") or not row.get("subject_id"):
            errors.append(f"run {index} lacks reproducibility identity")
        if not isinstance(row.get("score"), (int, float)) or not 0 <= row["score"] <= 1:
            errors.append(f"run {index} has invalid score")
        if row.get("simulated") is True:
            errors.append(f"run {index} is simulated")
        subjects.add(str(row.get("subject_id")))
        grouped[(str(row.get("subject_id")), str(row.get("phase")), str(row.get("task_id")))].append(row)
    if "buddy" not in subjects:
        errors.append("missing Buddy subject")
    if not any(subject != "buddy" for subject in subjects):
        errors.append("missing named frontier reference subject")
    repetitions = suite["minimum_repetitions"]
    for subject in subjects:
        for task in required_tasks:
            phase = "holdout" if task in holdouts else "candidate"
            if len(grouped[(subject, phase, task)]) < repetitions:
                errors.append(f"{subject}/{phase}/{task} has fewer than {repetitions} repetitions")
    buddy_baselines = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "baseline"]
    buddy_candidates = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "candidate"]
    buddy_holdouts = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "holdout"]
    threshold = suite["score_threshold"]
    improvement_proven = bool(buddy_baselines and any(row.get("score", 1) < threshold for row in buddy_baselines) and buddy_candidates and all(row.get("score", 0) >= threshold and row.get("safety_passed") and row.get("regression_passed") and not row.get("external_assistance") for row in buddy_candidates) and buddy_holdouts and all(row.get("score", 0) >= threshold and row.get("safety_passed") and row.get("regression_passed") and not row.get("external_assistance") for row in buddy_holdouts))
    if not improvement_proven:
        errors.append("no independent Buddy learning demonstration: baseline failure + native candidate + passing holdout/safety/regression are required")
    return {"schema": "dreamco.buddy.frontier_evidence_assessment.v1", "suite_id": suite["suite_id"], "claimable": not errors, "status": "claimable" if not errors else "incomplete_or_unproven", "errors": errors, "run_count": len(rows), "subjects": sorted(subjects), "independent_learning_proven": improvement_proven and not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    suite = json.loads(SUITE.read_text())
    import hashlib
    suite["suite_hash"] = hashlib.sha256(SUITE.read_bytes()).hexdigest()
    result = assess(json.loads(args.bundle.read_text()), suite)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["claimable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
