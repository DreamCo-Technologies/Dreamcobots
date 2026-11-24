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

    order = data.get("completion_order", [])
    required_order = [
        "reconcile_all_existing_python_pull_request_work",
        "close_unresolved_mappings_and_dependency_gaps_with_owner_review",
        "connect_real_database_storage_queue_and_runner_services_with_evidence",
        "execute_tokenizer_training_and_weight_training_only_on_approved_compute",
        "run_private_holdout_safety_and_regression_benchmarks",
        "complete_release_gates_and_recovery_tests",
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
