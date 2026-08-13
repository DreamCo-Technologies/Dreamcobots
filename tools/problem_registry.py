#!/usr/bin/env python3
"""Build a deterministic problem registry from Actions and benchmark evidence.

This tool never changes a problem to resolved merely because it was observed once.
A problem is closed only when explicit passing evidence references are recorded by
an upstream verifier. The registry is safe to publish because it contains no
secrets and treats unknown state as unknown.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ROOT / "config" / "generated" / "actions-health-report.json"
OUT = ROOT / "config" / "generated" / "problem-registry.json"
PUBLIC = ROOT / "website" / "data" / "problem-registry.json"
REPORT = ROOT / "reports" / "PROBLEM_REGISTRY.md"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def main() -> int:
    health = load_json(ACTIONS, {})
    problems = []
    for item in health.get("findings", []):
        workflow = item.get("workflow", "unknown")
        for message in item.get("errors", []):
            key = f"actions:{workflow}:error:{message}"
            problems.append({
                "id": key,
                "class": "actions_health",
                "severity": "high",
                "status": "observed",
                "title": message,
                "source": workflow,
                "evidence": {"source_file": "config/generated/actions-health-report.json"},
                "repair": {
                    "strategy": "reproduce_root_cause_smallest_shared_safe_fix",
                    "sandbox_only": True,
                    "rollback_required": True,
                    "targeted_test_required": True,
                    "dependent_regression_required": True,
                    "benchmark_rerun_required": False,
                },
            })
        for message in item.get("warnings", []):
            problems.append({
                "id": f"actions:{workflow}:warning:{message}",
                "class": "actions_health",
                "severity": "medium",
                "status": "observed",
                "title": message,
                "source": workflow,
                "evidence": {"source_file": "config/generated/actions-health-report.json"},
                "repair": {"strategy": "review_and_prioritize", "sandbox_only": True},
            })

    registry = {
        "schema": "dreamco.problem_registry.v1",
        "generated_at": now(),
        "truth_policy": {
            "unknown_is_not_success": True,
            "observed_is_not_resolved": True,
            "passing_evidence_required_to_close": True,
            "no_fabricated_results": True,
            "preserve_history": True,
        },
        "summary": {
            "total": len(problems),
            "high": sum(p["severity"] == "high" for p in problems),
            "medium": sum(p["severity"] == "medium" for p in problems),
            "observed": sum(p["status"] == "observed" for p in problems),
            "resolved": 0,
        },
        "problems": problems,
        "next_cycle": [
            "reproduce the highest-severity observed problem",
            "capture root-cause evidence",
            "apply the smallest shared repair on a review branch or sandbox",
            "run targeted verification",
            "rerun dependent suites",
            "record before/after evidence",
            "close only with explicit passing evidence; otherwise retain as blocked or observed",
        ],
    }
    for path in (OUT, PUBLIC):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# DreamCo Problem Registry",
        "",
        f"Generated: `{registry['generated_at']}`",
        "",
        "This registry is evidence-first. Observation is not resolution; only explicit passing verification may close a problem.",
        "",
        f"- Total: **{len(problems)}**",
        f"- High: **{registry['summary']['high']}**",
        f"- Medium: **{registry['summary']['medium']}**",
        f"- Observed: **{registry['summary']['observed']}**",
        "- Resolved by this generator: **0**",
        "",
        "## Problems",
    ]
    for problem in problems:
        lines += [
            f"### `{problem['id']}`",
            f"- Severity: **{problem['severity']}**",
            f"- Status: **{problem['status']}**",
            f"- Source: `{problem['source']}`",
            f"- Evidence: `{problem['evidence']['source_file']}`",
            f"- Repair: {problem['repair']['strategy']}",
            "",
        ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(registry["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
