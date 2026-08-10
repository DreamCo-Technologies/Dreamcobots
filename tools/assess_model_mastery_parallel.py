#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "model-mastery-benchmark-program.json"
MANIFEST = ROOT / "config" / "model-capability-manifest.json"
OUT = ROOT / "config" / "generated" / "model-mastery-gap-report.json"


def evidence_for_dimension(dimension: dict, manifest: dict) -> dict:
    dimension_id = dimension["id"]
    models = manifest.get("models", [])
    providers = manifest.get("providers", [])
    evidence_files = [
        "config/model-mastery-benchmark-program.json",
        "config/model-capability-manifest.json",
        "server/model-intelligence-router.ts",
        "server/model-protocol-compiler.ts",
        "tests/model-intelligence-router.test.ts",
        "tests/model-protocol-compiler.test.ts",
    ]
    checks = {
        "program_declared": True,
        "owner_declared": bool(dimension.get("owner")),
        "goal_declared": bool(dimension.get("goal")),
        "frontier_candidates_present": any(model.get("class") in {"frontier_api", "frontier_model", "specialized_api"} for model in models),
        "open_weight_candidates_present": any(model.get("weight_access") in {"open_weight", "open_weight_base", "weights_available"} for model in models),
        "provider_capabilities_present": bool(providers),
        "runtime_router_present": (ROOT / "server/model-intelligence-router.ts").exists(),
        "protocol_compiler_present": (ROOT / "server/model-protocol-compiler.ts").exists(),
    }

    task_specific_evidence = {
        "tool_selection": "server/model-intelligence-router.ts",
        "tool_call_correctness": "server/model-protocol-compiler.ts",
        "multi_tool_planning": "server/model-protocol-compiler.ts",
        "agent_handoff": "server/intelligent-task-router.ts",
        "task_decomposition": "server/intelligent-task-router.ts",
        "subbot_compilation": "server/intelligent-task-router.ts",
        "cost_efficiency": "config/buddy-intelligent-task-router.json",
        "context_efficiency": "config/buddy-intelligent-task-router.json",
        "local_inference_efficiency": "config/model-capability-manifest.json",
        "task_specific_leaderboard": "server/model-intelligence-router.ts",
        "fallback_quality": "config/buddy-model-router.json",
    }.get(dimension_id)
    if task_specific_evidence:
        checks["task_specific_contract_present"] = (ROOT / task_specific_evidence).exists()
        evidence_files.append(task_specific_evidence)
    else:
        checks["task_specific_contract_present"] = False

    missing = [name for name, passed in checks.items() if not passed]
    state = "passing_contract" if not missing else "gap_found"
    return {
        "dimension": dimension_id,
        "owner": dimension["owner"],
        "goal": dimension["goal"],
        "state": state,
        "checks": checks,
        "missing": missing,
        "evidence_files": sorted(set(evidence_files)),
        "live_model_benchmark_state": "not_run_requires_shortlist_provider_or_local_runtime",
        "mastery_state": "fixture_ready" if state == "passing_contract" else "gap_found",
        "truth_boundary": "Static/runtime contracts can make a dimension fixture-ready; mastered_current_revision requires actual task fixtures and applicable live/local model evidence.",
    }


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dimensions = program.get("mastery_dimensions", [])
    max_parallel = int(program["parallel_gap_policy"]["maximum_parallel_lanes"])
    if len(dimensions) != 32:
        raise SystemExit(f"Expected exactly 32 mastery dimensions, found {len(dimensions)}")
    if max_parallel != 32:
        raise SystemExit(f"Expected 32 max parallel lanes, found {max_parallel}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        results = list(pool.map(lambda dimension: evidence_for_dimension(dimension, manifest), dimensions))

    results.sort(key=lambda row: row["dimension"])
    payload = {
        "schema": "dreamco.model_mastery_gap_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parallel_lane_count": len(results),
        "maximum_parallel_lanes": max_parallel,
        "catalog_target_count": program.get("catalog_target_count"),
        "passing_contract_count": sum(row["state"] == "passing_contract" for row in results),
        "gap_count": sum(row["state"] == "gap_found" for row in results),
        "live_calls_executed": 0,
        "cost_strategy": "shared repository evidence plus 32 parallel lightweight assessors; shortlist before any paid/live benchmark",
        "dimensions": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "lanes": payload["parallel_lane_count"],
        "passing_contracts": payload["passing_contract_count"],
        "gaps": payload["gap_count"],
        "live_calls": 0,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
