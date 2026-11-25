#!/usr/bin/env python3
"""Validate DreamCo's shared three-runtime contract without side effects."""
from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "config" / "cross-runtime-contract.json"
REQUIRED_IMPLEMENTATIONS = {
    ("DreamCo-Technologies/Dreamcobots", "python"): "python-reference",
    ("ireanjordan24/dreamcobots", "c"): "apple-c",
    ("ireanjordan24/dreamcobots", "swift"): "apple-swift",
}
REQUIRED_PATHS = {
    "python-reference": {"buddy/", "bots/", "tests/", "config/"},
    "apple-c": {
        "core-c/CMakeLists.txt",
        "core-c/include/dreamco_runtime.h",
        "core-c/src/dreamco_runtime.c",
        "core-c/tests/",
    },
    "apple-swift": {
        "dreamco/ContentView.swift",
        "dreamco/OpenRouterService.swift",
        "dreamco/dreamcoApp.swift",
        "dreamcoTests/",
        "dreamcoUITests/",
    },
}
REQUIRED_SHARED = {
    "division_identity_and_version",
    "task_request_and_response",
    "model_provider_capability_manifest",
    "tokenizer_identity_and_revision",
    "dataset_provenance_rights_and_split_hashes",
    "training_job_and_compute_approval",
    "checkpoint_manifest_and_sha256",
    "benchmark_case_and_scorecard",
    "run_event_and_failure_taxonomy",
    "release_gate_and_rollback",
    "runtime_capability_and_environment_manifest",
    "cross_runtime_conformance_fixture",
}
REQUIRED_CANDIDATES = {"python-reference", "apple-c", "apple-swift"}
REQUIRED_PARITY = {
    "same_task_packets",
    "same_model_and_tokenizer_revisions",
    "same_prompts_and_tool_permissions",
    "same_dataset_and_benchmark_versions",
    "same_quality_and_safety_gates",
    "hardware_and_environment_recorded_and_comparable",
}
REQUIRED_GATES = {
    "task_capability_match",
    "license_and_data_rights",
    "privacy_and_security",
    "tool_and_modality_support",
    "minimum_quality_threshold",
    "reproducible_evidence",
    "shared_contract_conformance",
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "dreamco.cross_runtime_contract.v1":
        errors.append("unsupported or missing schema")

    implementations = data.get("implementations", [])
    if not isinstance(implementations, list):
        implementations = []
        errors.append("implementations must be a list")
    by_id = {item.get("id"): item for item in implementations if isinstance(item, dict)}
    for (repository, language), candidate_id in REQUIRED_IMPLEMENTATIONS.items():
        item = by_id.get(candidate_id)
        if not item or (item.get("repository"), item.get("language")) != (repository, language):
            errors.append(f"{candidate_id} must map to {repository} ({language})")
            continue
        paths = set(item.get("tracked_paths", []))
        if not REQUIRED_PATHS[candidate_id].issubset(paths):
            errors.append(f"{candidate_id} is missing required tracked paths")

    if not REQUIRED_CANDIDATES.issubset(by_id):
        errors.append("all three runtime candidate IDs must be declared")

    shared = set(data.get("shared_contracts", []))
    if not REQUIRED_SHARED.issubset(shared):
        errors.append("one or more required shared contracts are missing")

    competition = data.get("competition", {})
    if competition.get("selection") != "best_eligible_model_per_task":
        errors.append("competition must select the best eligible model per task")
    if not REQUIRED_CANDIDATES.issubset(set(competition.get("runtime_candidates", []))):
        errors.append("competition must include Python, C, and Swift candidates")
    if not REQUIRED_PARITY.issubset(set(competition.get("parity_requirements", []))):
        errors.append("competition is missing parity requirements")
    if not REQUIRED_GATES.issubset(set(competition.get("hard_gates", []))):
        errors.append("competition is missing one or more eligibility hard gates")
    if competition.get("benchmark_suite_version_required") is not True:
        errors.append("competition must pin a benchmark suite version")
    if competition.get("fallback_required") is not True:
        errors.append("competition must provide a fallback route")
    fairness = competition.get("compute_fairness", {})
    required_fairness_fields = {"policy", "budgets", "environments", "comparison", "anti_cheating", "selection"}
    if not required_fairness_fields.issubset(fairness):
        errors.append("competition is missing the detailed equal-compute fairness contract")
    environment_ids = {item.get("id") for item in fairness.get("environments", []) if isinstance(item, dict)}
    if not {"owner-laptop", "github-hosted"}.issubset(environment_ids):
        errors.append("compute fairness must define owner-laptop and GitHub-hosted cohorts")
    if not fairness.get("anti_cheating"):
        errors.append("compute fairness must retain anti-cheating controls")

    order = data.get("completion_order", [])
    required_order = [
        "reconcile_all_existing_python_pull_request_work",
        "close_unresolved_mappings_and_dependency_gaps_with_owner_review",
        "connect_real_database_storage_queue_and_runner_services_with_evidence",
        "execute_tokenizer_training_and_weight_training_only_on_approved_compute",
        "run_private_holdout_safety_and_regression_benchmarks",
        "complete_release_gates_and_recovery_tests",
        "complete_and_verify_python_repository_runs_and_goals_with_no_unresolved_critical_failures_or_unowned_blockers",
        "complete_buddy_operational_readiness_and_bootcamp_resource_catalog_and_curriculum",
        "freeze_versioned_shared_contracts",
        "implement_and_test_apple_c_runtime_after_python_completion",
        "preserve_and_adapt_apple_swift_runtime_to_shared_contract_after_python_completion",
        "run_python_vs_c_vs_swift_competition_on_parity_controlled_tasks",
    ]
    try:
        positions = [order.index(item) for item in required_order]
    except (ValueError, AttributeError):
        errors.append("completion order is missing one or more required Python-first or three-runtime phases")
    else:
        if positions != sorted(positions):
            errors.append("Python completion, contract freeze, Apple adaptation, and competition are out of order")

    if data.get("training", {}).get("scheduled_planning_is_not_training") is not True:
        errors.append("planning must remain distinct from actual training")
    resource_catalog = data.get("training", {}).get("resource_catalog", {})
    source_families = {item.get("family") for item in resource_catalog.get("source_families", []) if isinstance(item, dict)}
    required_source_families = {
        "open_model_and_dataset_hubs",
        "research_and_benchmark_repositories",
        "open_knowledge_and_web_corpora",
        "code_and_technical_corpora",
        "approved_enterprise_and_user_owned_data",
        "teacher_models_and_providers",
        "compute_and_training_frameworks",
    }
    if not required_source_families.issubset(source_families):
        errors.append("training resource catalog is missing one or more governed source families")
    if "No crawler or adapter may auto-download or train by discovery alone" not in resource_catalog.get("ingestion_gate", ""):
        errors.append("resource discovery must not grant automatic download or training permission")
    apple_ci = data.get("integration", {}).get("apple_repository_ci", {})
    if "until the canonical Python repository completion gate is satisfied" not in apple_ci.get("phase_gate", ""):
        errors.append("Apple cross-runtime execution must remain gated behind Python-first completion")
    if data.get("truth_rules", {}).get("all_required_runs_green_before_cross_runtime_clone") is not True:
        errors.append("all required Python runs must be green before cross-runtime cloning")
    if data.get("truth_rules", {}).get("no_candidate_receives_extra_compute_or_hidden_benchmark_advantage") is not True:
        errors.append("cross-runtime competition must enforce equal compute and no hidden benchmark advantage")
    if data.get("truth_rules", {}).get("data_discovery_does_not_grant_data_access_or_training_rights") is not True:
        errors.append("data discovery must not grant data access or training rights")
    governance = data.get("data_governance", {})
    required_governance_sections = {"shared_catalog", "division_isolation", "shared_corpora", "buddy_access", "privacy"}
    if not required_governance_sections.issubset(governance):
        errors.append("data governance must separate shared metadata from isolated division data")
    if data.get("integration", {}).get("no_credentials_or_private_chat_transcripts_in_git") is not True:
        errors.append("private chat transcripts and credentials must be excluded from Git")
    if data.get("truth_rules", {}).get("native_language_does_not_imply_better_performance") is not True:
        errors.append("native language must not be treated as proof of better performance")
    if data.get("truth_rules", {}).get("incomparable_hardware_results_must_not_be_ranked_as_direct_wins") is not True:
        errors.append("incomparable hardware results must not be ranked as direct wins")
    return errors


def main() -> int:
    try:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CONTRACT_INVALID: {type(exc).__name__}: {exc}")
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("CONTRACT_VALID: three candidates, Python-first gates, tracked assets, parity and eligibility checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
