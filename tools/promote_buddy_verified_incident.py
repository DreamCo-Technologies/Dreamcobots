#!/usr/bin/env python3
"""Promote a repair into Buddy's durable incident memory only with full evidence lineage.

This is a manual, evidence-gated operation. It never creates training data or
trains a model. Unverified history remains investigation-only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from tools.buddy_failure_learning import classify, fingerprint, update_memory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY = ROOT / "artifacts" / "failure-learning-memory.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_RE = re.compile(r"^\d+$")
GITHUB_RUN_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/actions/runs/\d+(?:/attempts/\d+)?$")
GITHUB_PR_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/pull/\d+$")
SECRET_RE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16})")
PII_RE = re.compile(r"(?:\b\d{3}-\d{2}-\d{4}\b|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b)", re.I)


def _required_text(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not value:
        raise ValueError(f"Missing required verification field: {key}")
    if SECRET_RE.search(value) or PII_RE.search(value):
        raise ValueError(f"Sensitive content is not permitted in field: {key}")
    return value


def validate(observation: dict[str, Any], verification: dict[str, Any]) -> None:
    for key in ("repository", "workflow", "job", "failed_step", "error_signature"):
        _required_text(observation, key)

    if verification.get("original_failure") is not True:
        raise ValueError("The original failure must be independently confirmed.")
    if verification.get("regressions") is not True:
        raise ValueError("Targeted regression and dependent checks must pass.")
    if verification.get("verification_run_conclusion") != "success":
        raise ValueError("The verification workflow run must have success conclusion.")
    if verification.get("repair_pr_state") != "merged":
        raise ValueError("The repair PR must be merged before memory promotion.")
    if verification.get("human_reviewed") is not True:
        raise ValueError("A human must review the evidence before memory promotion.")
    if verification.get("source_ownership_confirmed") is not True:
        raise ValueError("Repository ownership/provenance must be confirmed.")
    for key in ("contains_secrets", "contains_personal_data", "third_party_content_included"):
        if verification.get(key) is not False:
            raise ValueError(f"{key} must be explicitly false.")

    for key in ("failure_commit", "repair_merge_commit", "verified_commit"):
        if not SHA_RE.fullmatch(_required_text(verification, key).lower()):
            raise ValueError(f"{key} must be a full immutable 40-character commit SHA.")
    for key in ("original_failure_run_id", "verification_run_id"):
        if not RUN_RE.fullmatch(_required_text(verification, key)):
            raise ValueError(f"{key} must be a numeric GitHub Actions run ID.")
    for key in ("original_failure_url", "verification_run_url"):
        if not GITHUB_RUN_URL_RE.fullmatch(_required_text(verification, key)):
            raise ValueError(f"{key} must be a GitHub Actions run URL.")
    if not GITHUB_PR_URL_RE.fullmatch(_required_text(verification, "repair_pr_url")):
        raise ValueError("repair_pr_url must identify a GitHub pull request.")
    for key in ("reviewer", "root_cause", "repair"):
        _required_text(verification, key)

    original_test = _required_text(verification, "original_failure_test")
    regression_tests = verification.get("regression_tests")
    evidence = verification.get("evidence")
    if not isinstance(regression_tests, list) or not regression_tests:
        raise ValueError("At least one named regression test is required.")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("At least one evidence reference is required.")
    for value in [original_test, *regression_tests, *evidence]:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Test names and evidence references must be non-empty strings.")
        if SECRET_RE.search(value) or PII_RE.search(value):
            raise ValueError("Evidence references must not contain secrets or personal data.")


def promote(memory: dict[str, Any], observation: dict[str, Any],
            verification: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    validate(observation, verification)
    kind = classify(observation)
    key = fingerprint({**observation, "failure_class": kind})
    incidents = list(memory.get("incidents", []))
    incident = next((item for item in incidents if item.get("fingerprint") == key), None)
    verification_id = str(verification["verification_run_id"])
    if incident:
        events = incident.get("verification_events", [])
        if any(str(event.get("verification_run_id")) == verification_id for event in events):
            return memory, False

    result = update_memory(memory, {**observation, "failure_class": kind}, {
        "original_failure": True,
        "regressions": True,
        "root_cause": verification["root_cause"],
        "repair": verification["repair"],
        "evidence": list(verification["evidence"]),
        "verified_at": str(verification.get("verified_at") or ""),
    })
    incident = next(item for item in result["incidents"] if item.get("fingerprint") == key)
    incident.setdefault("verification_events", []).append({
        "original_failure_run_id": str(verification["original_failure_run_id"]),
        "original_failure_url": verification["original_failure_url"],
        "failure_commit": verification["failure_commit"].lower(),
        "repair_pr_url": verification["repair_pr_url"],
        "repair_merge_commit": verification["repair_merge_commit"].lower(),
        "verification_run_id": verification_id,
        "verification_run_url": verification["verification_run_url"],
        "verified_commit": verification["verified_commit"].lower(),
        "verification_run_conclusion": "success",
        "original_failure_test": verification["original_failure_test"],
        "regression_tests": list(verification["regression_tests"]),
        "reviewer": verification["reviewer"],
    })
    result["schema"] = "dreamco.buddy_failure_learning_memory.v2"
    result["promotion_policy"] = {
        "requires_merged_repair": True,
        "requires_successful_verification_run": True,
        "requires_human_review": True,
        "training_eligible_by_default": False,
        "automatic_code_application": False,
    }
    return result, True


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--memory", default=str(DEFAULT_MEMORY))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    observation = json.loads(Path(args.observation).read_text(encoding="utf-8"))
    verification = json.loads(Path(args.verification).read_text(encoding="utf-8"))
    memory_path = Path(args.memory)
    memory = json.loads(memory_path.read_text(encoding="utf-8")) if memory_path.exists() else {"incidents": []}
    result, promoted = promote(memory, observation, verification)
    if promoted:
        atomic_write(memory_path, result)
    report = {
        "schema": "dreamco.buddy_incident_memory_promotion_result.v1",
        "promoted": promoted,
        "memory_path": str(memory_path),
        "fingerprint": fingerprint({**observation, "failure_class": classify(observation)}),
        "verification_run_id": str(verification["verification_run_id"]),
        "training_approved": False,
        "weights_trained": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
