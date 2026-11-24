#!/usr/bin/env python3
"""Validate DreamCo's shared Python/Apple runtime contract without side effects."""
from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "config" / "cross-runtime-contract.json"
REQUIRED_IMPLEMENTATIONS = {
    ("DreamCo-Technologies/Dreamcobots", "python"),
    ("ireanjordan24/dreamcobots", "c"),
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
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "dreamco.cross_runtime_contract.v1":
        errors.append("unsupported or missing schema")
    found = {
        (item.get("repository"), item.get("language"))
        for item in data.get("implementations", [])
    }
    if not REQUIRED_IMPLEMENTATIONS.issubset(found):
        errors.append("both canonical Python and Apple C implementations must be declared")
    shared = set(data.get("shared_contracts", []))
    if not REQUIRED_SHARED.issubset(shared):
        errors.append("one or more required shared contracts are missing")
    order = data.get("completion_order", [])
    if not order or order.index("implement_and_test_apple_c_runtime") < order.index("freeze_versioned_shared_contracts"):
        errors.append("C runtime work must follow Python completion and contract freeze")
    if data.get("competition", {}).get("selection") != "best_eligible_model_per_task":
        errors.append("competition must select the best eligible model per task")
    if data.get("training", {}).get("scheduled_planning_is_not_training") is not True:
        errors.append("planning must remain distinct from actual training")
    if data.get("integration", {}).get("no_credentials_or_private_chat_transcripts_in_git") is not True:
        errors.append("private chat transcripts and credentials must be excluded from Git")
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
    print("CONTRACT_VALID: Python-first completion, shared contracts, Apple C competition gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
