#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "buddy-guardrails-benchmark-program.json"
ACCEL = ROOT / "config" / "benchmark-gap-acceleration-policy.json"
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
    accel = json.loads(ACCEL.read_text(encoding="utf-8"))
    suites = json.loads(SUITES.read_text(encoding="utf-8"))
    legacy_cap = int(program["parallel_builder_team"]["maximum_parallel_lanes"])
    acceleration_cap = int(accel["parallelism"]["maximum_parallel_lanes"])
    # Newer acceleration policy may raise independent-owner concurrency; same-owner serialization remains mandatory.
    max_lanes = max(legacy_cap, acceleration_cap)
    groups: dict[str, list[dict]] = defaultdict(list)

    for suite in suites.get("suites", []):
        lane = LANE_HINTS.get(suite.get("area"), "testing")
        groups[lane].append({
            "suite_id": suite["id"], "name": suite["name"], "area": suite.get("area"), "level": suite.get("level"),
            "sources": suite.get("sources", []), "tests": suite.get("tests", []), "boundary": suite.get("boundary"),
            "gap_state": "unknown", "required_action": "measure immediately; if a verified gap exists assign owner/build/integration/QA/security/value lanes and retest"
        })

    lanes = []
    for idx, (lane, lane_suites) in enumerate(sorted(groups.items())):
        if idx >= max_lanes: break
        lanes.append({
            "lane": lane, "parallel_slot": idx + 1, "owner_lock": lane, "suites": lane_suites,
            "rules": [
                "search canonical owner before edits", "same canonical owner is serialized even when independent owners run in parallel",
                "never weaken guardrails to pass", "record baseline and target", "emit progress evidence before stagnation threshold",
                "retest immediately after fix", "leave blocked/unknown gaps visible", "reopen regressions immediately"
            ]
        })

    out = {
        "schema": "dreamco.parallel_benchmark_gap_plan.v2",
        "generated_from": [str(PROGRAM.relative_to(ROOT)), str(ACCEL.relative_to(ROOT)), str(SUITES.relative_to(ROOT))],
        "legacy_parallel_cap": legacy_cap, "acceleration_parallel_cap": acceleration_cap, "maximum_parallel_lanes": max_lanes,
        "lane_count": len(lanes), "benchmark_domains": program.get("benchmark_domains", []),
        "guardrail_count": len(program.get("global_guardrails", [])), "no_stagnant_policy": accel["stagnation_policy"], "lanes": lanes
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "lanes": len(lanes), "parallel_cap": max_lanes, "guardrails": out["guardrail_count"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
