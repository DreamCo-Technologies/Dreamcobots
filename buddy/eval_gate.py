"""Offline exact-match evaluation gate for small Buddy model candidates.

Inputs are external model outputs, not training weights. A receipt verifies arithmetic
and input integrity, NOT that the evaluator or model is independent or deployed.
"""
from __future__ import annotations

import hashlib
import json


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def evaluate(cases, baseline, candidate, *, division, task, model_id, min_accuracy=0.5, max_regression=0.0):
    """Compare candidate predictions with a pinned baseline on holdout-only cases.

    No network, database, weights, downloads, or paid compute are involved.
    Exact match is unsuitable for open-ended generation without a validated rubric.
    """
    if not all(isinstance(v, str) and v.strip() for v in (division, task, model_id)):
        raise ValueError("Division, task and model ID are required")
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one holdout case required")
    if not 0 <= min_accuracy <= 1 or not 0 <= max_regression <= 1:
        raise ValueError("Invalid thresholds")
    ids, sources = set(), set()
    for row in cases:
        if not isinstance(row, dict):
            raise ValueError("Invalid case")
        required = ("id", "source_id", "expected", "license", "provenance")
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in required):
            raise ValueError("Incomplete holdout provenance")
        if row.get("split") != "holdout" or row.get("consent") is not True or row.get("privacy_safe") is not True:
            raise ValueError("Holdout rights/privacy requirements not satisfied")
        if row["license"] not in {"owner_created", "CC0-1.0", "MIT"}:
            raise ValueError("Unreviewed license")
        if row["id"] in ids or row["source_id"] in sources:
            raise ValueError("Duplicate holdout ID or source")
        if row.get("division") != division or row.get("task") != task:
            raise ValueError("Cross-division/task holdout mix")
        ids.add(row["id"])
        sources.add(row["source_id"])
    if not isinstance(baseline, dict) or not isinstance(candidate, dict) or set(baseline) != ids or set(candidate) != ids:
        raise ValueError("Predictions must cover the exact holdout set")
    if any(not isinstance(v, str) for v in list(baseline.values()) + list(candidate.values())):
        raise ValueError("Predictions must be strings")
    n = len(cases)
    base_hits = sum(baseline[row["id"]] == row["expected"] for row in cases)
    cand_hits = sum(candidate[row["id"]] == row["expected"] for row in cases)
    base_accuracy, cand_accuracy = base_hits / n, cand_hits / n
    passed = cand_accuracy >= min_accuracy and cand_accuracy >= base_accuracy - max_regression
    return {
        "schema": "dreamco.buddy_offline_eval.v1", "division": division, "task": task,
        "model_id": model_id, "metric": "exact_match", "holdout_count": n,
        "baseline_accuracy": base_accuracy, "candidate_accuracy": cand_accuracy,
        "min_accuracy": min_accuracy, "max_regression": max_regression,
        "gate_passed": passed, "holdout_sha256": _digest(cases),
        "baseline_predictions_sha256": _digest(baseline),
        "candidate_predictions_sha256": _digest(candidate),
        "production_verified": False,
        "limitations": "Offline exact-match only; source rights and evaluator independence need external audit; no model inference performed here.",
    }
