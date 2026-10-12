#!/usr/bin/env python3
"""Validate claimable Buddy/frontier benchmark evidence without executing models.

The runner intentionally separates evidence validation from provider execution:
model credentials and paid calls stay in a reviewed adapter or CI secret store.
It rejects incomplete, simulated, or incomparable result bundles for capability claims.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
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
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        rows = []
        errors.append("runs must be a list of objects")
    seen_ids = set()
    fixtures = {}
    versions = {}
    graders = set()
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    subjects: set[str] = set()
    for index, row in enumerate(rows):
        run_id = row.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip() or run_id in seen_ids:
            errors.append(f"run {index} missing or duplicate execution identity")
        else:
            seen_ids.add(run_id)
        for flag in ("safety_passed", "regression_passed", "external_assistance", "simulated"):
            if type(row.get(flag)) is not bool:
                errors.append(f"run {index} {flag} must be a boolean")
        for metric in ("latency_ms", "cost_usd", "score"):
            value = row.get(metric)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                errors.append(f"run {index} invalid {metric}")
        for field, length in (("repo_commit", 40), ("model_sha256", 64), ("dataset_sha256", 64), ("fixture_hash", 64)):
            if not re.fullmatch(r"[0-9a-f]{%d}" % length, str(row.get(field, ""))):
                errors.append(f"run {index} lacks immutable {field}")
        try:
            stamp = datetime.fromisoformat(str(row.get("timestamp", "")).replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("timezone missing")
        except ValueError:
            errors.append(f"run {index} invalid timestamp")
        task, phase, subject = row.get("task_id"), row.get("phase"), row.get("subject_id")
        if phase not in ("baseline", "candidate", "holdout"):
            errors.append(f"run {index} unknown phase")
        if (task in holdouts) != (phase == "holdout"):
            errors.append(f"run {index} holdout phase leakage")
        if task in holdouts and row.get("holdout_unseen") is not True:
            errors.append(f"run {index} holdout exposure not excluded")
        # Compare like-for-like fixtures and one immutable subject per phase.
        fixture_key = str(task)
        fixture = (str(row.get("fixture_hash")), str(row.get("dataset_sha256")))
        if fixture_key in fixtures and fixtures[fixture_key] != fixture:
            errors.append(f"run {index} incomparable fixtures")
        fixtures[fixture_key] = fixture
        version_key = (str(subject), "baseline" if phase == "baseline" else "candidate")
        version = (str(row.get("exact_subject_version")), str(row.get("model_sha256")))
        if version_key in versions and versions[version_key] != version:
            errors.append(f"run {index} inconsistent subject version")
        versions[version_key] = version
        graders.add(str(row.get("grader_version")))
        missing = sorted(required - set(row))
        if missing:
            errors.append(f"run {index} missing {', '.join(missing)}")
        if row.get("task_id") not in required_tasks:
            errors.append(f"run {index} unknown task")
        if not row.get("fixture_hash") or not row.get("grader_version") or not row.get("subject_id"):
            errors.append(f"run {index} lacks reproducibility identity")
        if type(row.get("score")) not in (int, float) or not 0 <= row["score"] <= 1:
            errors.append(f"run {index} has invalid score")
        if row.get("simulated") is True:
            errors.append(f"run {index} is simulated")
        subjects.add(str(row.get("subject_id")))
        grouped[(str(row.get("subject_id")), str(row.get("phase")), str(row.get("task_id")))].append(row)
    if len(graders) != 1:
        errors.append("one common grader version is required")
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
    for task in required_tasks - holdouts:
        if len(grouped[("buddy", "baseline", task)]) < repetitions:
            errors.append(f"buddy/baseline/{task} lacks repeated baseline")
    buddy_baselines = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "baseline"]
    buddy_candidates = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "candidate"]
    buddy_holdouts = [row for row in rows if row.get("subject_id") == "buddy" and row.get("phase") == "holdout"]
    threshold = suite["score_threshold"]
    improvement_proven = not errors and bool(buddy_baselines and any(row.get("score", 1) < threshold for row in buddy_baselines) and buddy_candidates and all(row.get("score", 0) >= threshold and row.get("safety_passed") is True and row.get("regression_passed") is True and row.get("external_assistance") is False for row in buddy_candidates) and buddy_holdouts and all(row.get("score", 0) >= threshold and row.get("safety_passed") is True and row.get("regression_passed") is True and row.get("external_assistance") is False for row in buddy_holdouts))
    if not improvement_proven:
        errors.append("no independent Buddy learning demonstration: baseline failure + native candidate + passing holdout/safety/regression are required")
    return {"schema": "dreamco.buddy.frontier_evidence_assessment.v1", "suite_id": suite["suite_id"], "claimable": False, "evidence_valid": not errors, "human_marketing_review_required": True, "status": "human_review_required" if not errors else "incomplete_or_unproven", "errors": errors, "run_count": len(rows), "subjects": sorted(subjects), "independent_learning_proven": improvement_proven and not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suite", type=Path, default=None, help="Pinned suite JSON (default: config/frontier-evidence-suite.json)")
    args = parser.parse_args()
    import hashlib
    suite_path = args.suite if args.suite is not None else SUITE
    suite = json.loads(suite_path.read_text())
    suite["suite_hash"] = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    result = assess(json.loads(args.bundle.read_text()), suite)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["evidence_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
