#!/usr/bin/env python3
"""Decide which repository problems may be auto-repaired safely.

This is deliberately a policy gate, not an arbitrary self-modifying agent.
Only deterministic, low-risk classes are eligible for automatic remediation.
Everything else becomes a tracked blocker requiring review.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED = {
    "missing_artifact_directory",
    "stale_generated_report",
    "invalid_generated_json",
    "formatting_only",
}
FORBIDDEN = {
    "secret",
    "credential",
    "permission_escalation",
    "security_control",
    "branch_protection",
    "workflow_trigger_change",
    "production_deploy",
    "dependency_major_upgrade",
    "destructive_change",
}


def classify(problem: dict) -> str:
    text = json.dumps(problem).lower()
    for marker in FORBIDDEN:
        if marker in text:
            return "owner_review_required"
    declared = problem.get("auto_repair_class")
    if declared in ALLOWED:
        return "bounded_auto_repair"
    return "owner_review_required"


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config/generated/problem-registry.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = {"bounded_auto_repair": 0, "owner_review_required": 0}
    for problem in data.get("problems", []):
        decision = classify(problem)
        problem["automation"] = {
            "decision": decision,
            "requires_tests": True,
            "requires_before_after_evidence": True,
            "rollback_on_regression": True,
            "max_attempts_per_hour": 1,
        }
        counts[decision] += 1
    data["automation_policy"] = {
        "mode": "bounded_self_healing",
        "hourly": True,
        "unknown_is_not_success": True,
        "no_secret_or_permission_changes": True,
        "no_production_deploy": True,
        "no_destructive_repairs": True,
        "no_test_weakening": True,
        "no_unbounded_self_modification": True,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
