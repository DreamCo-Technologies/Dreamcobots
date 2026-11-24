#!/usr/bin/env python3
"""Validate DreamCo's shared three-runtime contract without side effects."""
from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "config" / "cross-runtime-contract.json"
REQUIRED_IMPLEMENTATIONS = {
    ("DreamCo-Technologies/Dreamcobots", "python"),
    ("ireanjordan24/dreamcobots", "c"),
    ("ireanjordan24/dreamcobots", "swift"),
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


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "dreamco.cross_runtime_contract.v1":
        errors.append("unsupported or missing schema")
    implementations = data.get("implementations", [])
    found = {
        (item.get("repository"), item.get("language"))
        for item in implementations
    }
    if not REQUIRED_IMPLEMENTATIONS.issubset(found):
        errors.append("canonical Python, Apple C, and Apple Swift implementations must all be declared")
    candidate_ids = {item.get("id") for item in implementations}
    if not REQUIRED_CANDIDATES.issubset(candidate_ids):
        errors.append("all three runtime candidate IDs must be declared")
    shared = set(data.get("shared_contracts", []))
    if not REQUIRED_SHARED.issubset(shared):
        errors.append("one or more required shared contracts are missing")
    competition = data.get("competition", {})
    if competition.get("selection") != "best_eligible_model_per_task":
        errors.append("competition must select the best eligible model per task")
    if not REQUIRED_CANDIDATES.issubset(set(competition.get("runtime_candidates", []))):
        errors.append("competition must include Python, C, and Swift candidates")
    order = data.get("completion_order", [])
    try:
        freeze_index = order.index("freeze_versioned_shared_contracts")
        c_index = order.index("implement_and_test_apple_c_runtime_after_python_completion")
        swift_index = order.index("preserve_and_adapt_apple_swift_runtime_to_shared_contract_after_python_completion")
        competition_index = order.index("run_python_vs_c_vs_swift_competition_on_parity_controlled_tasks")
    except (ValueError, AttributeError):
        errors.append("completion order must include contract freeze, both Apple candidates, and three-way competition")
    else:
        if c_index < freeze_index or swift_index < freeze_index:
            errors.append("C and Swift runtime work must follow Python completion and contract freeze")
        if competition_index < max(c_index, swift_index):
            errors.append("three-way competition must follow both Apple runtime gates")
    if data.get("training", {}).get("scheduled_planning_is_not_training") is not True:
        errors.append("planning must remain distinct from actual training")
    if data.get("integration", {}).get("no_credentials_or_private_chat_transcripts_in_git") is not True:
        errors.append("private chat transcripts and credentials must be excluded from Git")
    if data.get("truth_rules", {}).get("native_language_does_not_imply_better_performance") is not True:
        errors.append("native language must not be treated as proof of better performance")
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
    print("CONTRACT_VALID: Python, Apple C, and Apple Swift candidates; Python-first completion; parity-gated competition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
