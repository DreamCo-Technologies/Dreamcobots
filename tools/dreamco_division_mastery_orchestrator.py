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
RESOURCE_MAP = ROOT / "config/generated/division-resource-readiness-map.json"
GOALS = ROOT / "config/dreamco-mastery-continuity-registry.json"
OUT = ROOT / "artifacts/division-mastery"
MODEL_MANIFEST = ROOT / "config/generated/division-model-manifest.json"
OWNER_REVIEW_QUEUE = ROOT / "config/generated/division-owner-review-queue.json"
BENCHMARK_ADAPTER_MAP = ROOT / "config/benchmark-adapter-map.json"
RECONCILIATION = ROOT / "config/generated/division-reconciliation.json"
RUNTIME_ROUTER = "buddy/fleet_runtime/routing.py"
ALLOWED_TASKS = {
    "registry_validation": [sys.executable, "tools/validate_dreamco_mastery_registry.py"],
    "platform_regression_suite": [sys.executable, "-m", "unittest", "tests.test_dreamco_division_mastery_orchestrator", "tests.test_buddy_failure_learning", "tests.test_buddy_conversation_learning_policy"],
    "division_lane_plan": [sys.executable, "tools/buddy_masterbot_training_lane.py"],
}
# Dependencies are explicit and topologically ordered. Division-specific
# implementation tasks remain blocked until their code/test/runtime evidence is mapped.
TASK_DAG = [
    {"id": "registry_validation", "depends_on": [], "kind": "safe_audit"},
    {"id": "platform_regression_suite", "depends_on": ["registry_validation"], "kind": "shared_regression_tests"},
    {"id": "division_lane_plan", "depends_on": ["registry_validation", "platform_regression_suite"], "kind": "sandbox_plan"},
    {"id": "division_contract_benchmark", "depends_on": ["registry_validation"], "kind": "benchmark_contract"},
    {"id": "evidence_review", "depends_on": ["division_lane_plan", "division_contract_benchmark", "platform_regression_suite"], "kind": "promotion_gate"},
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


def load_resource_routes():
    payload = json.loads(RESOURCE_MAP.read_text(encoding="utf-8"))
    if payload.get("status") != "requirements_defined_not_provisioned":
        raise ValueError("Division resource map must preserve honest readiness status")
    routes = {int(row["masterbot_id"]): row for row in payload.get("routes", [])}
    if len(routes) != 65:
        raise ValueError("Expected exactly 65 unique division resource bundles")
    return payload, routes




def _read_json_with_hash(path):
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def build_capability_evidence():
    """Build a source-hashed, fail-closed gap inventory for all 65 MasterBots and 55 domains."""
    sources = {
        "masterbot_registry": DIVISIONS,
        "resource_readiness_map": RESOURCE_MAP,
        "owner_review_queue": OWNER_REVIEW_QUEUE,
        "division_model_manifest": MODEL_MANIFEST,
        "benchmark_adapter_map": BENCHMARK_ADAPTER_MAP,
        "division_reconciliation": RECONCILIATION,
    }
    documents = {}
    source_hashes = {}
    for key, path in sources.items():
        documents[key], source_hashes[key] = _read_json_with_hash(path)

    router_path = ROOT / RUNTIME_ROUTER
    if not router_path.is_file():
        raise ValueError("division_runtime_route_resolver_missing")
    source_hashes["runtime_router"] = hashlib.sha256(router_path.read_bytes()).hexdigest()
    source_hashes["mastery_orchestrator"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    registry = documents["masterbot_registry"]
    resources = documents["resource_readiness_map"]
    owner_queue = documents["owner_review_queue"]
    models = documents["division_model_manifest"]
    benchmark_map = documents["benchmark_adapter_map"]
    reconciliation = documents["division_reconciliation"]

    bots = registry.get("divisions", [])
    resource_routes = resources.get("routes", [])
    domain_routes = resources.get("domain_routes", [])
    model_rows = models.get("records", [])
    core_reviews = owner_queue.get("masterbot_domain_decisions", [])
    shared_reviews = owner_queue.get("shared_platform_masterbots", [])
    supplemental_reviews = owner_queue.get("unassigned_domain_profiles", [])
    benchmark_rows = benchmark_map.get("routing", [])
    domain_rows = reconciliation.get("domain_divisions", [])
    shared_rows = reconciliation.get("shared_platform_masterbots", [])

    if registry.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError("capability_evidence_requires_65_canonical_masterbots")
    if resources.get("counts", {}).get("masterbots") != 65 or len(resource_routes) != 65:
        raise ValueError("capability_evidence_requires_65_resource_routes")
    if resources.get("counts", {}).get("domain_divisions") != 55 or len(domain_routes) != 55:
        raise ValueError("capability_evidence_requires_55_domain_routes")
    if models.get("division_count") != 65 or len(model_rows) != 65:
        raise ValueError("capability_evidence_requires_65_model_manifest_records")
    if len(domain_rows) != 55 or len(shared_rows) != 20:
        raise ValueError("capability_evidence_reconciliation_count_mismatch")
    if len(core_reviews) != 45 or len(shared_reviews) != 20 or len(supplemental_reviews) != 10:
        raise ValueError("capability_evidence_owner_review_queue_count_mismatch")

    bot_by_id = {int(row["id"]): row for row in bots}
    resource_by_id = {int(row["masterbot_id"]): row for row in resource_routes}
    model_by_id = {int(row["division_id"]): row for row in model_rows}
    core_by_id = {int(row["masterbot_id"]): row for row in core_reviews}
    shared_by_id = {int(row["masterbot_id"]): row for row in shared_reviews}
    supplemental_by_domain = {str(row["domain_id"]): row for row in supplemental_reviews}
    domain_route_by_id = {str(row["domain_id"]): row for row in domain_routes}
    domain_by_id = {str(row["id"]): row for row in domain_rows}
    benchmark_by_id = {int(row["division"]): row for row in benchmark_rows}

    expected_bot_ids = set(range(1, 66))
    if (set(bot_by_id) != expected_bot_ids or set(resource_by_id) != expected_bot_ids
            or set(model_by_id) != expected_bot_ids):
        raise ValueError("capability_evidence_masterbot_identity_set_mismatch")
    if set(core_by_id) != set(range(1, 46)) or set(shared_by_id) != set(range(46, 66)):
        raise ValueError("capability_evidence_owner_review_identity_set_mismatch")
    if set(domain_route_by_id) != set(domain_by_id) or len(domain_route_by_id) != 55:
        raise ValueError("capability_evidence_domain_identity_set_mismatch")
    if len(benchmark_by_id) != len(benchmark_rows):
        raise ValueError("capability_evidence_duplicate_benchmark_division")
    if benchmark_map.get("adapter_status") != "planned-until-verified":
        raise ValueError("capability_evidence_benchmark_map_status_changed")

    shared_test_modules = list(ALLOWED_TASKS["platform_regression_suite"][3:])
    masterbot_evidence = []
    for ident in range(1, 66):
        bot = bot_by_id[ident]
        resource = resource_by_id[ident]
        model = model_by_id[ident]
        benchmark = benchmark_by_id.get(ident)
        if int(resource.get("masterbot_id")) != ident or str(model.get("division_name")) != str(bot.get("name")):
            raise ValueError(f"capability_evidence_identity_mismatch_for_masterbot_{ident}")

        if ident in core_by_id:
            review = core_by_id[ident]
            ownership = {
                "classification": "core_domain_masterbot",
                "status": "pending_owner_review_and_github_identity_attestation",
                "proposed_primary_domain_id": review.get("proposed_primary_domain_id"),
                "approved_primary_domain_id": None,
                "user_approval_status": review.get("user_approval_status"),
                "owner_approval": review.get("owner_approval"),
            }
            runtime_status = "proposed_core_route_pending_github_identity_attestation"
            ownership_blocker = "The exact-name crosswalk remains a proposal: owner_approval is null and GitHub identity attestation is pending."
        else:
            review = shared_by_id[ident]
            ownership = {
                "classification": "shared_platform_service",
                "status": "shared_platform_role_confirmation_pending",
                "proposed_primary_domain_id": None,
                "approved_primary_domain_id": None,
                "user_approval_status": review.get("user_approval_status"),
                "owner_approval": review.get("owner_approval"),
            }
            runtime_status = "shared_platform_service_no_primary_domain_owner"
            ownership_blocker = "This MasterBot is a shared platform service, not a domain owner; shared-role confirmation remains pending."

        if benchmark:
            if benchmark.get("masterbot") != bot.get("name"):
                raise ValueError(f"capability_evidence_benchmark_identity_mismatch_for_masterbot_{ident}")
            benchmark_status = "planned_unverified"
            benchmark_ids = list(benchmark.get("benchmarks", []))
        else:
            benchmark_status = "missing_adapter"
            benchmark_ids = []

        evaluation = model.get("evaluation") or {}
        training = model.get("training") or {}
        serving = model.get("serving") or {}
        route = resource.get("domain_mapping") or {}
        blockers = [
            ownership_blocker,
            "The resource bundle is requirements-defined, not provisioned.",
            "No MasterBot-specific task runner is registered in the division mastery orchestrator; current lane tasks are shared validation, regression, and planning only.",
            "No MasterBot-specific test path is mapped in the division mastery orchestrator.",
            "No measured benchmark baseline or candidate result exists; the adapter is not verified and the private holdout is not registered.",
            "Dataset rights remain unverified and dataset_training_approved is false.",
            "The model manifest is plan-only: no selected base model, trained weights, or deployed endpoint.",
        ]
        next_actions = [
            "Complete the owner review and GitHub identity attestation for this proposed mapping or shared-platform role; do not infer a primary owner.",
            "Provision the isolated resource bundle and verify rights-cleared dataset evidence before any training use.",
            "Register a capability-specific task runner with implementation, sandbox, runtime-route, and MasterBot-specific test evidence.",
            "Register a domain benchmark adapter and private holdout, then measure quality, safety, privacy, reliability, latency, cost, and regression against a baseline.",
            "Select and pin a license-compatible base model and tokenizer; obtain separate dataset-rights and compute approval before training.",
        ]
        masterbot_evidence.append({
            "masterbot_id": ident,
            "masterbot_name": bot["name"],
            "ownership": ownership,
            "resource": {
                "resource_bundle_id": resource.get("resource_bundle_id"),
                "readiness_status": resource.get("readiness_status"),
                "dataset_rights_status": resource.get("dataset_rights_status"),
                "dataset_training_approved": resource.get("dataset_training_approved") is True,
                "capability_pack_ids": list(resource.get("capability_pack_ids") or []),
            },
            "task_runner": {
                "status": "not_registered_in_mastery_orchestrator",
                "capability_specific_runner_path": None,
                "planner_path": "tools/buddy_masterbot_training_lane.py",
                "planner_is_capability_runner": False,
                "shared_lane_tasks": list(ALLOWED_TASKS.keys()),
            },
            "runtime_route": {
                "implementation_path": RUNTIME_ROUTER,
                "status": runtime_status,
                "route_authorized": False,
                "privileged_execution_enabled": False,
                "live_external_actions_enabled": False,
                "training_execution_enabled": False,
            },
            "tests": {
                "shared_regression_status": "configured",
                "shared_regression_modules": shared_test_modules,
                "domain_specific_status": "not_mapped_in_mastery_orchestrator",
                "domain_specific_test_paths": [],
            },
            "benchmark": {
                "adapter_status": benchmark_status,
                "adapter_map_status": benchmark_map.get("adapter_status"),
                "benchmark_ids": benchmark_ids,
                "baseline_status": "not_measured",
                "result_status": "not_measured",
                "private_holdout_status": "not_registered",
            },
            "model": {
                "lifecycle_state": model.get("lifecycle_state"),
                "base_model_selection_status": model.get("base_model_selection_status"),
                "training_status": training.get("status"),
                "weights_trained": training.get("weights_trained") is True,
                "evaluation_status": evaluation.get("benchmark_status"),
                "serving_status": serving.get("status"),
                "endpoint_present": bool(serving.get("endpoint")),
            },
            "mastery_status": "not_claimed",
            "blockers": blockers,
            "next_actions": next_actions,
        })

    domain_evidence = []
    for domain in domain_rows:
        domain_id = str(domain["id"])
        route = domain_route_by_id[domain_id]
        tier = domain.get("domain_tier")
        if tier == "original_core":
            masterbot_id = int(route["masterbot_id"])
            if masterbot_id not in core_by_id or route.get("mapping_status") != "proposed_exact_name_match":
                raise ValueError(f"capability_evidence_core_domain_not_pending_owner_review_{domain_id}")
            review = core_by_id[masterbot_id]
            proposed_masterbot_id = masterbot_id
            proposed_collaborator_id = None
            owner_status = "pending_owner_review_and_github_identity_attestation"
            runtime_status = "proposed_core_route_pending_github_identity_attestation"
            benchmark_status = "planned_unverified" if masterbot_id in benchmark_by_id else "missing_adapter"
            ownership_blocker = "The proposed exact-name primary mapping is not owner-approved."
        elif tier == "promoted_supplemental":
            masterbot_id = None
            review = supplemental_by_domain.get(domain_id)
            if review is None:
                raise ValueError(f"capability_evidence_supplemental_domain_review_missing_{domain_id}")
            proposed_masterbot_id = None
            proposed_collaborator_id = review.get("proposed_collaborator_masterbot_id")
            owner_status = "pending_owner_review_and_github_identity_attestation"
            runtime_status = "supplemental_domain_unassigned_pending_owner_review"
            benchmark_status = "no_primary_masterbot_benchmark_route_pending_owner_review"
            ownership_blocker = "The supplemental domain has no approved primary MasterBot; its collaborator link remains a proposal."
        else:
            raise ValueError(f"capability_evidence_unknown_domain_tier_{domain_id}")

        domain_blockers = [
            ownership_blocker,
            "The domain resource bundle is requirements-defined, not provisioned.",
            "No capability-specific domain task runner and mapped runtime route are verified.",
            "No domain-specific test path is mapped in the division mastery orchestrator.",
            "No measured domain benchmark baseline, candidate result, or private holdout evidence exists.",
        ]
        domain_evidence.append({
            "domain_id": domain_id,
            "domain_name": domain["name"],
            "domain_tier": tier,
            "proposed_masterbot_id": proposed_masterbot_id,
            "proposed_collaborator_masterbot_id": proposed_collaborator_id,
            "approved_primary_masterbot_id": None,
            "owner_review_status": owner_status,
            "owner_approval": review.get("owner_approval"),
            "resource": {
                "route_type": route.get("route_type"),
                "resource_bundle_id": route.get("resource_bundle_id"),
                "readiness_status": route.get("readiness_status"),
                "dataset_rights_status": route.get("dataset_rights_status"),
                "dataset_training_approved": route.get("dataset_training_approved") is True,
                "capability_pack_ids": list(route.get("capability_pack_ids") or []),
            },
            "runtime_route_status": runtime_status,
            "capability_specific_task_runner_status": "not_registered_in_mastery_orchestrator",
            "domain_specific_test_status": "not_mapped_in_mastery_orchestrator",
            "benchmark_status": benchmark_status,
            "mastery_status": "not_claimed",
            "blockers": domain_blockers,
        })

    weights_trained = sum(1 for row in masterbot_evidence if row["model"]["weights_trained"])
    endpoints_deployed = sum(1 for row in masterbot_evidence if row["model"]["endpoint_present"])
    measured_results = sum(1 for row in masterbot_evidence if row["benchmark"]["result_status"] != "not_measured")
    summary = {
        "canonical_masterbots": 65,
        "original_core_domain_divisions": 45,
        "promoted_supplemental_domain_profiles": 10,
        "shared_platform_masterbots": 20,
        "pending_core_owner_reviews": len(core_by_id),
        "pending_shared_platform_confirmations": len(shared_by_id),
        "pending_supplemental_collaborator_reviews": len(supplemental_by_domain),
        "capability_specific_task_runners_registered": 0,
        "masterbot_specific_test_paths_mapped": 0,
        "benchmark_adapter_entries": len(benchmark_by_id),
        "benchmark_adapter_entries_core_masterbots": sum(1 for ident in benchmark_by_id if ident <= 45),
        "benchmark_adapter_entries_shared_platform_masterbots": sum(1 for ident in benchmark_by_id if ident >= 46),
        "benchmark_adapters_verified": 0,
        "measured_benchmark_results": measured_results,
        "weights_trained": weights_trained,
        "serving_endpoints_deployed": endpoints_deployed,
        "mastery_claimed": 0,
    }
    return {
        "schema": "dreamco.division_capability_evidence_inventory.v1",
        "status": "audit_only_gaps_explicit_no_mastery_claimed",
        "summary": summary,
        "source_hashes": source_hashes,
        "masterbots": masterbot_evidence,
        "domain_profiles": domain_evidence,
        "truth_boundary": "Repository-declared evidence inventory only. A configured route, generic smoke test, resource blueprint, benchmark target, or scheduled run is not proof of domain task execution, model quality, training, mastery, or production readiness.",
    }


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
    resource_payload, resource_routes = load_resource_routes()
    capability_inventory = build_capability_evidence()
    capability_by_id = {row["masterbot_id"]: row for row in capability_inventory["masterbots"]}
    if {int(d["id"]) for d in divisions} != set(resource_routes):
        raise ValueError("Division resource bundles do not match the canonical MasterBot registry")
    known_goal_ids = {g["id"] for g in goals}
    for goal_id, deps in GOAL_DEPENDENCIES.items():
        if goal_id not in known_goal_ids or any(dep not in known_goal_ids for dep in deps):
            raise ValueError(f"Unknown goal dependency in {goal_id}: {deps}")
    lanes = []
    for division in divisions:
        assigned = route_goals(division, goals)
        resource = resource_routes[int(division["id"])]
        lanes.append({
            "division_id": division["id"],
            "division_name": division["name"],
            "lane_id": f"masterbot-{division['id']}",
            "resource_bundle_id": resource["resource_bundle_id"],
            "resource_readiness_status": resource["readiness_status"],
            "logical_database_namespace": resource["logical_database_namespace"],
            "dataset_discovery_lane_id": resource["dataset_discovery_lane_id"],
            "capability_pack_ids": resource["capability_pack_ids"],
            "capability_evidence": capability_by_id[int(division["id"])],
            "goal_ids": [g["id"] for g in assigned],
            "priority_order": [g["id"] for g in assigned],
            "goal_dependency_map": {g["id"]: GOAL_DEPENDENCIES.get(g["id"], []) for g in assigned},
            "goal_traceability": {
                g["id"]: {
                    **TRACEABILITY_ANCHORS.get(g["id"], {"implementation_paths": [], "test_paths": [], "runtime_routes": [], "benchmark": "discovery_required"}),
                    "traceability_status": "partial_inventory_not_verified",
                    "missing": [item for item in [
                        "implementation_paths" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("implementation_paths") else None,
                        "test_paths" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("test_paths") else None,
                        "runtime_routes" if not TRACEABILITY_ANCHORS.get(g["id"], {}).get("runtime_routes") else None,
                        "benchmark_evidence"
                    ] if item is not None]
                } for g in assigned
            },
            "task_dag": TASK_DAG,
            "task_status": {
                "registry_validation": "runnable",
                "division_lane_plan": "runnable_after_registry_validation",
                "division_contract_benchmark": "runnable_after_registry_validation",
                "platform_regression_suite": "runnable_after_registry_validation",
                "evidence_review": "blocked_until_independent_evidence"
            },
            "next_action": "run_allowlisted_sandbox_lane_and_collect_benchmark_evidence",
            "promotion_policy": "evidence_required_no_automatic_production_promotion"
        })
    return {
        "schema": "dreamco.division_mastery_queue.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expected_divisions": 65,
        "resource_bundle_count": len(resource_routes),
        "resource_readiness_status": resource_payload["status"],
        "capability_evidence_summary": capability_inventory["summary"],
        "capability_evidence_source_hashes": capability_inventory["source_hashes"],
        "domain_capability_evidence": capability_inventory["domain_profiles"],
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
    resource_payload, resource_routes = load_resource_routes()
    resource = resource_routes[int(division_id)]
    capability_inventory = build_capability_evidence()
    capability_by_id = {row["masterbot_id"]: row for row in capability_inventory["masterbots"]}
    capability_evidence = capability_by_id[int(division_id)]
    capability_evidence_hash = hashlib.sha256(
        json.dumps(capability_evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    lane_dir = OUT / f"division-{division_id}"
    lane_dir.mkdir(parents=True, exist_ok=True)
    results = []
    env = os.environ.copy()
    env["MASTERBOT_NAME"] = division["name"]
    env["GITHUB_RUN_ID"] = run_id
    env["GITHUB_RUN_ATTEMPT"] = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    for task_id in ("registry_validation", "platform_regression_suite", "division_lane_plan"):
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
        "resource_bundle_id": resource["resource_bundle_id"],
        "resource_readiness_status": resource["readiness_status"],
        "logical_database_namespace": resource["logical_database_namespace"],
        "dataset_discovery_lane_id": resource["dataset_discovery_lane_id"],
        "capability_pack_ids": resource["capability_pack_ids"],
        "run_id": run_id,
        "run_attempt": run_attempt,
        "commit_sha": commit_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_hashes": capability_inventory["source_hashes"],
        "capability_evidence": capability_evidence,
        "capability_evidence_hash": capability_evidence_hash,
        "task_results": results,
        "task_graph_status": "blocked_on_failed_dependency" if any(x["status"] != "passed" for x in results) else "safe_tasks_passed",
        "shared_regression_status": next((x["status"] for x in results if x["task_id"] == "platform_regression_suite"), "not_run"),
        "benchmark_status": capability_evidence["benchmark"]["result_status"],
        "benchmark_baseline": None,
        "benchmark_result": None,
        "weights_trained": capability_evidence["model"]["weights_trained"],
        "production_promotion": "not_authorized",
        "mastery_status": capability_evidence["mastery_status"],
        "resource_templates": list(resource_payload["resource_templates"].keys()),
        "evidence_hash": hashlib.sha256(json.dumps({
            "run_id": run_id,
            "run_attempt": run_attempt,
            "commit_sha": commit_sha,
            "task_results": results,
            "capability_evidence_hash": capability_evidence_hash,
            "source_hashes": capability_inventory["source_hashes"],
        }, sort_keys=True).encode()).hexdigest(),
        "next_actions": capability_evidence["next_actions"] + [
            "Preserve the GitHub Actions artifact digest with this run; no automatic mastery or production promotion is permitted."
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
