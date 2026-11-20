#!/usr/bin/env python3
"""Deterministic failure fingerprinting and verified-lesson matching for Buddy.

This module does not execute repairs. It turns failure observations and prior
verified outcomes into a machine-readable triage recommendation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY = ROOT / "artifacts" / "failure-learning-memory.json"
SAFE_CLASSES = {"documentation", "formatting", "generated-index", "deterministic-test-fixture"}
GATED_CLASSES = {"security", "permissions", "secrets", "production", "data-migration", "dependency-major", "billing"}


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def fingerprint(observation: dict[str, Any]) -> str:
    """Stable across run IDs; intentionally excludes timestamps and commit SHA."""
    parts = [
        _clean(observation.get("repository")),
        _clean(observation.get("workflow")),
        _clean(observation.get("job")),
        _clean(observation.get("failed_step")),
        _clean(observation.get("failure_class", "unknown")),
        _clean(observation.get("error_signature")),
    ]
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def classify(observation: dict[str, Any]) -> str:
    explicit = _clean(observation.get("failure_class"))
    if explicit:
        return explicit.replace(" ", "-")
    text = " ".join(_clean(observation.get(k)) for k in ("workflow", "job", "failed_step", "error_signature"))
    rules = [
        ("security", ("secret", "permission", "codeql", "vulnerability", "unauthorized")),
        ("dependency-major", ("dependency", "lockfile", "package version", "pip resolver")),
        ("generated-index", ("prospectus", "generated index", "inventory mismatch")),
        ("documentation", ("markdown", "link check", "documentation")),
        ("deployment", ("deploy", "pages", "release")),
        ("test", ("assertion", "pytest", "unittest", "test failed")),
    ]
    for label, needles in rules:
        if any(n in text for n in needles):
            return label
    return "unknown"


def recommend(observation: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    kind = classify(observation)
    key = fingerprint({**observation, "failure_class": kind})
    prior = next((x for x in memory.get("incidents", []) if x.get("fingerprint") == key), None)
    verified = prior.get("verified_lesson") if prior else None
    gated = kind in GATED_CLASSES or bool(observation.get("production_impact"))
    auto = kind in SAFE_CLASSES and not gated
    return {
        "fingerprint": key,
        "failure_class": kind,
        "recurrence_count": int(prior.get("occurrence_count", 0)) + 1 if prior else 1,
        "prior_verified_lesson": verified,
        "recommended_action": "reapply_verified_lesson_in_isolated_branch" if verified and auto else (
            "run_read_only_diagnostics_and_open_repair_pr" if auto else
            "escalate_for_human_approval_before_changes"
        ),
        "automatic_code_change_allowed": bool(auto),
        "requires_human_approval": bool(gated or not auto),
        "must_verify": ["original_failure", "targeted_regression", "dependent_checks"],
    }


def update_memory(memory: dict[str, Any], observation: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    """Persist lessons only when the original failure and regressions passed."""
    if verification.get("original_failure") is not True or verification.get("regressions") is not True:
        raise ValueError("A lesson can only be stored after original failure and regression checks pass.")
    result = dict(memory)
    incidents = list(result.get("incidents", []))
    kind = classify(observation)
    key = fingerprint({**observation, "failure_class": kind})
    item = next((x for x in incidents if x.get("fingerprint") == key), None)
    if item is None:
        item = {"fingerprint": key, "failure_class": kind, "occurrence_count": 0}
        incidents.append(item)
    item["occurrence_count"] = int(item.get("occurrence_count", 0)) + 1
    item["verified_lesson"] = {
        "root_cause": str(verification.get("root_cause", "")),
        "repair": str(verification.get("repair", "")),
        "evidence": list(verification.get("evidence", [])),
        "verified_at": str(verification.get("verified_at", "")),
    }
    result["schema"] = "dreamco.buddy_failure_learning_memory.v1"
    result["incidents"] = incidents
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observation", required=True, help="JSON observation file")
    parser.add_argument("--memory", default=str(DEFAULT_MEMORY))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    observation = json.loads(Path(args.observation).read_text(encoding="utf-8"))
    memory_path = Path(args.memory)
    memory = json.loads(memory_path.read_text(encoding="utf-8")) if memory_path.exists() else {"schema": "dreamco.buddy_failure_learning_memory.v1", "incidents": []}
    result = recommend(observation, memory)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
