#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "buddy-guardrails-benchmark-program.json"
SUITES = ROOT / "config" / "repository-test-suites.json"
OUT = ROOT / "config" / "generated" / "parallel-benchmark-gap-plan.json"

LANE_HINTS = {
    "Security": "security", "Privacy": "privacy_permissions", "Website": "frontend", "Application": "backend",
    "Bots": "architecture", "Quality": "testing", "Buddy": "architecture", "Testing": "testing", "Models": "models",
    "Connections": "integrations", "Media": "creator_media", "Creative": "games_simulation", "Calculators": "business_sales",
    "Launch": "deployment", "Social": "integrations", "Sales": "business_sales", "Government": "integrations",
    "Crypto": "security", "Repository": "testing", "Payments": "integrations", "Operations": "observability",
    "Automation": "backend", "Coding": "architecture", "Platform": "backend", "Search": "backend"
}


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    suites = json.loads(SUITES.read_text(encoding="utf-8"))
    max_lanes = int(program["parallel_builder_team"]["maximum_parallel_lanes"])
    if not 1 <= max_lanes <= 20:
        raise ValueError('maximum_parallel_lanes must be between 1 and 20')
    groups: dict[str, list[dict]] = defaultdict(list)

    for suite in suites.get("suites", []):
        lane = LANE_HINTS.get(suite.get("area"), "testing")
        groups[lane].append({
            "suite_id": suite["id"],
            "name": suite["name"],
            "area": suite.get("area"),
            "level": suite.get("level"),
            "sources": suite.get("sources", []),
            "tests": suite.get("tests", []),
            "boundary": suite.get("boundary"),
            "gap_state": "unknown",
            "gap_closure_contract": {
                "schema": "dreamco.suite_gap_closure.v1",
                "suite_definition_sha256": hashlib.sha256(json.dumps(suite, sort_keys=True).encode()).hexdigest(),
                "canonical_sources": suite.get("sources", []),
                "required_regressions": suite.get("tests", []),
                "required_scripts": suite.get("scripts", []),
                "acceptance": "Nonzero passing execution evidence, measured target, source and artifact hashes, passing affected regressions, and evidence review are required to close a gap.",
                "review": {"status": "reviewed", "reviewer": "Codex implementation review", "scope": "Shared closure contract only; not suite execution, owner approval, or capability certification."},
                "closure_evaluator": "tools/benchmark_gap_closure.py",
                "production_ready": False,
            },
            "required_action": "measure suite, compare against benchmark targets, create/fix only verified gaps, retest"
        })

    lanes = []
    for idx, (lane, lane_suites) in enumerate(sorted(groups.items())):
        lanes.append({
            "lane": lane,
            "parallel_slot": idx % max_lanes + 1,
            "batch": idx // max_lanes + 1,
            "owner_lock": lane,
            "suites": lane_suites,
            "rules": [
                "search canonical owner before edits",
                "avoid overlapping file ownership with other active lanes",
                "never weaken guardrails to pass",
                "record baseline and target",
                "retest after fix",
                "leave blocked/unknown gaps visible"
            ]
        })

    out = {
        "schema": "dreamco.parallel_benchmark_gap_plan.v1",
        "generated_from": [str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p) for p in (PROGRAM, SUITES)],
        "maximum_parallel_lanes": max_lanes,
        "lane_count": len(lanes),
        "benchmark_domains": program.get("benchmark_domains", []),
        "guardrail_count": len(program.get("global_guardrails", [])),
        "lanes": lanes
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "lanes": len(lanes), "guardrails": out["guardrail_count"], "output": str(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
