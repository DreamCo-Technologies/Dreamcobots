#!/usr/bin/env python3
"""Build and execute bounded, dependency-aware DreamCo division mastery lanes.

This coordinator runs only allowlisted read-only validation and plan-generation
commands. It never merges, deploys, spends, changes credentials, or trains/
promotes production weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIVISIONS = ROOT / "config/masterbot-65-registry.json"
GOALS = ROOT / "config/dreamco-mastery-continuity-registry.json"
OUT = ROOT / "artifacts/division-mastery"
ALLOWED_TASKS = {
    "registry_validation": [sys.executable, "tools/validate_dreamco_mastery_registry.py"],
    "division_lane_plan": [sys.executable, "tools/buddy_masterbot_training_lane.py"],
}
# Dependencies are explicit and topologically ordered. Division-specific
# implementation tasks remain blocked until their code/test/runtime evidence is mapped.
TASK_DAG = [
    {"id": "registry_validation", "depends_on": [], "kind": "safe_audit"},
    {"id": "division_lane_plan", "depends_on": ["registry_validation"], "kind": "sandbox_plan"},
    {"id": "division_contract_benchmark", "depends_on": ["registry_validation"], "kind": "benchmark_contract"},
    {"id": "evidence_review", "depends_on": ["division_lane_plan", "division_contract_benchmark"], "kind": "promotion_gate"},
]
ROUTES = {
    "DCO-001": ["DreamCo", "Buddy"],
    "DCO-002": ["DreamCo", "Buddy"],
    "DCO-003": ["Buddy", "OS", "Orchestration"],
    "DCO-004": ["Brain", "Memory", "Knowledge"],
    "DCO-005": ["Dream", "Bot", "Master"],
    "DCO-006": ["Model", "AI", "Research"],
    "DCO-007": ["Buddy", "Learning", "Training"],
    "DCO-008": ["Model", "AI", "Research"],
    "DCO-009": ["Privacy", "Data", "Finance"],
    "DCO-010": ["Integration", "Dev", "Code", "Cloud"],
    "DCO-011": ["Command", "Dashboard", "Marketing"],
    "DCO-012": ["Finance", "RealEstate", "Sales", "Commerce", "Marketing"],
    "DCO-013": ["Vision", "Robot", "Research", "Media"],
    "DCO-014": ["Security", "Legal", "Compliance", "Governance", "DevOps"],
}
PRIORITY = {"critical": 0, "high": 1, "medium": 2, "low": 3, "untriaged": 4}
GOAL_DEPENDENCIES = {
    "DCO-001": [],
    "DCO-002": ["DCO-001"],
    "DCO-003": ["DCO-002"],
    "DCO-004": ["DCO-001", "DCO-003"],
    "DCO-005": ["DCO-001", "DCO-002"],
    "DCO-006": ["DCO-005"],
    "DCO-007": ["DCO-005", "DCO-006"],
    "DCO-008": ["DCO-006", "DCO-007"],
    "DCO-009": ["DCO-002"],
    "DCO-010": ["DCO-002", "DCO-009"],
    "DCO-011": ["DCO-002", "DCO-003"],
    "DCO-012": ["DCO-009", "DCO-010"],
    "DCO-013": ["DCO-006", "DCO-014"],
    "DCO-014": ["DCO-002"]
}
# Known implementation anchors are references to inspect, not claims that
# the whole workstream is complete. Empty discovery fields remain explicit.
TRACEABILITY_ANCHORS = {
    "DCO-001": {"implementation_paths": ["tools/dreamco_division_mastery_orchestrator.py", "tools/validate_dreamco_mastery_registry.py"], "test_paths": ["tests/test_dreamco_division_mastery_orchestrator.py"], "runtime_routes": [], "benchmark": "historical-reconciliation-completeness"},
    "DCO-002": {"implementation_paths": ["tools/audit_actions_health.py", ".github/workflows/actions-health.yml"], "test_paths": ["tests/test_actions_health.py"], "runtime_routes": [], "benchmark": "workflow-health-and-production-isolation"},
    "DCO-003": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "buddy-end-to-end-task-success"},
    "DCO-004": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "dream-brain-retrieval-quality-and-rights"},
    "DCO-005": {"implementation_paths": ["config/masterbot-65-registry.json", "tools/buddy_masterbot_training_lane.py"], "test_paths": [], "runtime_routes": [], "benchmark": "bot-capability-contract-and-certification"},
    "DCO-006": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "model-quality-cost-latency-and-fallback"},
    "DCO-007": {"implementation_paths": ["config/buddy-continuous-learning-policy.json", "tools/aggregate_masterbot_training_runs.py"], "test_paths": [], "runtime_routes": [], "benchmark": "per-masterbot-benchmark-gap-closure"},
    "DCO-008": {"implementation_paths": ["tools/run_daily_division_benchmarks.ts"], "test_paths": [], "runtime_routes": [], "benchmark": "held-out-model-training-and-generalization"},
    "DCO-009": {"implementation_paths": ["config/user-data-and-subscription-control-policy.json", "server/user-control-center-policy.ts"], "test_paths": ["tests/task-and-data-policy.test.ts"], "runtime_routes": [], "benchmark": "consent-revocation-and-tenant-isolation"},
    "DCO-010": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "connector-contract-and-revocation"},
    "DCO-011": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "dashboard-freshness-and-data-correctness"},
    "DCO-012": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "workflow-unit-economics-and-policy-compliance"},
    "DCO-013": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "simulation-transfer-and-safety"},
    "DCO-014": {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "security-regression-and-recovery-drills"}
}


def load_inputs():
    division_doc = json.loads(DIVISIONS.read_text(encoding="utf-8"))
    goal_doc = json.loads(GOALS.read_text(encoding="utf-8"))
    divisions = division_doc.get("divisions", [])
    if division_doc.get("canonical_count") != 65 or len(divisions) != 65:
        raise ValueError(f"Expected 65 canonical MasterBots; found {len(divisions)}")
    ids = [str(d.get("id")) for d in divisions]
    names = [d.get("name") for d in divisions]
    if len(set(ids)) != 65 or len(set(names)) != 65 or any(not n for n in names):
        raise ValueError("MasterBot registry has missing or duplicate IDs/names")
    goals = goal_doc.get("workstreams", [])
    goal_ids = [g.get("id") for g in goals]
    if len(set(goal_ids)) != len(goal_ids):
        raise ValueError("Duplicate canonical goal IDs")
    return divisions, goals


def route_goals(division, goals):
    name = division["name"].lower()
    selected = []
    for goal in goals:
        terms = ROUTES.get(goal["id"], [])
        if any(term.lower() in name for term in terms):
            selected.append(goal)
    # Every MasterBot has a lane for shared repository readiness, registry,
    # and continuous learning even when no domain-specific keyword matches.
    for required in ("DCO-002", "DCO-005", "DCO-007"):
        match = next((g for g in goals if g.get("id") == required), None)
        if match and match not in selected:
            selected.append(match)
    return sorted(selected, key=lambda g: (PRIORITY.get(g.get("priority"), 4), g.get("id", "")))


def build_plan():
    divisions, goals = load_inputs()
    known_goal_ids = {g["id"] for g in goals}
    for goal_id, deps in GOAL_DEPENDENCIES.items():
        if goal_id not in known_goal_ids or any(dep not in known_goal_ids for dep in deps):
            raise ValueError(f"Unknown goal dependency in {goal_id}: {deps}")
    lanes = []
    for division in divisions:
        assigned = route_goals(division, goals)
        lanes.append({
            "division_id": division["id"],
            "division_name": division["name"],
            "lane_id": f"masterbot-{division['id']}",
            "goal_ids": [g["id"] for g in assigned],
            "priority_order": [g["id"] for g in assigned],
            "goal_dependency_map": {g["id"]: GOAL_DEPENDENCIES.get(g["id"], []) for g in assigned},
            "goal_traceability": {
                g["id"]: {
                    **TRACEABILITY_ANCHORS.get(g["id"], {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "discovery_required"}),
                    "traceability_status": "partial_inventory_not_verified",
                    "missing": ["implementation_paths" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("implementation_paths") else None,
                                "test_paths" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("test_paths") else None,
                                "runtime_routes" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("runtime_routes") else None,
                                "benchmark_evidence"]
                } for g in assigned
            },
            "task_dag": TASK_DAG,
            "task_status": {
                "registry_validation": "runnable",
                "division_lane_plan": "runnable_after_registry_validation",
                "division_contract_benchmark": "runnable_after_registry_validation",
                "evidence_review": "blocked_until_independent_evidence"
            },
            "next_action": "run_allowlisted_sandbox_lane_and_collect_benchmark_evidence",
            "promotion_policy": "evidence_required_no_automatic_production_promotion"
        })
    return {
        "schema": "dreamco.division_mastery_queue.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expected_divisions": 65,
        "division_lanes": len(lanes),
        "unique_goal_count": len(goals),
        "task_dag": TASK_DAG,
        "goal_dependency_map": GOAL_DEPENDENCIES,
        "traceability_policy": "Paths are discovery anchors only; no implementation, test, runtime route, or benchmark is marked verified without run evidence.",
        "dependency_policy": "A task runs only after all dependencies succeed; failed/unknown dependencies block descendants.",
        "cross_division_exchange": "Versioned verified lesson metadata, test fixtures, benchmark deltas, and reusable fixes only; each consumer rechecks rights and compatibility.",
        "raw_private_data_pooling": False,
        "automatic_weight_merging": False,
        "automatic_promotion": False,
        "production_safety_hold": True,
        "lanes": lanes
    }


def write_plan(plan):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "division-mastery-queue.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    matrix = {"include": [{"division_id": x["division_id"], "division_name": x["division_name"]} for x in plan["lanes"]]}
    print(json.dumps(matrix, separators=(",", ":")))


def run_lane(division_id: str, run_id: str, commit_sha: str):
    divisions, _ = load_inputs()
    division = next((d for d in divisions if str(d["id"]) == str(division_id)), None)
    if division is None:
        raise ValueError(f"Unknown division ID: {division_id}")
    lane_dir = OUT / f"division-{division_id}"
    lane_dir.mkdir(parents=True, exist_ok=True)
    results = []
    env = os.environ.copy()
    env["MASTERBOT_NAME"] = division["name"]
    env["GITHUB_RUN_ID"] = run_id
    env["GITHUB_RUN_ATTEMPT"] = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    for task_id in ("registry_validation", "division_lane_plan"):
        command = ALLOWED_TASKS[task_id]
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
        results.append({
            "task_id": task_id,
            "command": command,
            "status": "passed" if completed.returncode == 0 else "failed",
            "return_code": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:]
        })
        if completed.returncode != 0:
            break
    payload = {
        "schema": "dreamco.division_lane_evidence.v1",
        "division_id": division["id"],
        "division_name": division["name"],
        "run_id": run_id,
        "commit_sha": commit_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_results": results,
        "task_graph_status": "blocked_on_failed_dependency" if any(x["status"] != "passed" for x in results) else "safe_tasks_passed",
        "benchmark_status": "not_measured_by_lane_planner",
        "weights_trained": False,
        "production_promotion": "not_authorized",
        "mastery_status": "not_claimed",
        "evidence_hash": hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest(),
        "next_actions": [
            "Run the independent division contract benchmark and capability-specific held-out benchmark.",
            "Map this division's capabilities to implementation paths, tests, runtime routes, and benchmark definitions.",
            "Do not promote without before/after scores, holdout, regression, provenance, and approval evidence."
        ]
    }
    (lane_dir / f"run-{run_id}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["task_graph_status"] == "safe_tasks_passed" else 1


def promotion_eligible(evidence):
    required = ["baseline_score", "candidate_score", "holdout_passed", "regression_passed",
                "provenance_verified", "rights_verified", "review_approved", "tested_commit_sha"]
    if any(key not in evidence for key in required):
        return False, "missing_required_evidence"
    if not all(evidence[k] is True for k in
               ["holdout_passed", "regression_passed", "provenance_verified", "rights_verified", "review_approved"]):
        return False, "one_or_more_gates_failed"
    if not isinstance(evidence["baseline_score"], (int, float)) or not isinstance(evidence["candidate_score"], (int, float)):
        return False, "scores_must_be_numeric"
    if evidence["candidate_score"] < evidence["baseline_score"]:
        return False, "candidate_regressed"
    if not evidence["tested_commit_sha"]:
        return False, "missing_tested_commit_sha"
    return True, "eligible_for_human_review_not_automatic_release"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--run-lane", action="store_true")
    parser.add_argument("--division-id")
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    parser.add_argument("--commit-sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--promotion-evidence")
    args = parser.parse_args()
    if args.promotion_evidence:
        evidence = json.loads(Path(args.promotion_evidence).read_text(encoding="utf-8"))
        eligible, reason = promotion_eligible(evidence)
        print(json.dumps({"eligible": eligible, "reason": reason, "automatic_release": False}, indent=2))
        return 0 if eligible else 1
    if args.run_lane:
        if not args.division_id:
            parser.error("--run-lane requires --division-id")
        return run_lane(args.division_id, args.run_id, args.commit_sha)
    plan = build_plan()
    write_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
