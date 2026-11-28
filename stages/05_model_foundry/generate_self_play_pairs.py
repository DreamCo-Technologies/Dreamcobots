"""Build DPO preferences from already sandbox-verified Buddy rollout records.

This tool does not generate candidates or grade them. It only transforms
rights-authorized rollout rows carrying deterministic sandbox and teach-back
evidence. Output still requires owner review and a separate signed dataset
authorization manifest before a DPO trainer can consume it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .guardrails import split_name
except ImportError:
    from guardrails import split_name

REQUIRED_HASHES = ("test_suite_sha256", "rubric_sha256", "grader_attestation_sha256")


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def build_pairs(records: list[dict[str, Any]], max_candidates: int = 8) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not 2 <= max_candidates <= 8:
        raise ValueError("max_candidates must be between 2 and 8")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for row in records:
        task_id, candidate_id, response = row.get("task_id"), row.get("candidate_id"), row.get("response")
        prompt = row.get("prompt")
        if not all(isinstance(value, str) and value.strip() for value in (task_id, candidate_id, response, prompt)):
            continue
        # Preference construction is a training consumer: only train buckets are eligible.
        if split_name(task_id) != "train":
            continue
        identity = (task_id, candidate_id)
        if identity in seen:
            raise ValueError(f"duplicate candidate_id for task {task_id}")
        seen.add(identity)
        if not all(_valid_sha(row.get(field)) for field in REQUIRED_HASHES):
            continue
        if not isinstance(row.get("sandbox_run_id"), str) or not row["sandbox_run_id"].strip():
            continue
        if not isinstance(row.get("grader_version"), str) or not row["grader_version"].strip():
            continue
        if row.get("sandbox_status") not in {"LAB_PASSED", "LAB_FAILED"}:
            continue
        if row.get("teach_back_status") not in {"TEACH_BACK_VERIFIED", "NOT_VERIFIED"}:
            continue
        grouped[task_id].append(row)

    pairs: list[dict[str, Any]] = []
    emitted: set[str] = set()
    tasks_with_preferences = 0
    for task_id in sorted(grouped):
        candidates = sorted(grouped[task_id], key=lambda row: row["candidate_id"])[:max_candidates]
        if len(candidates) < 2:
            continue
        suite_versions = {
            (row["test_suite_sha256"], row["rubric_sha256"], row["grader_version"])
            for row in candidates
        }
        if len(suite_versions) != 1 or len({row["prompt"] for row in candidates}) != 1:
            continue
        chosen = [
            row for row in candidates
            if row["sandbox_status"] == "LAB_PASSED"
            and row["teach_back_status"] == "TEACH_BACK_VERIFIED"
        ]
        rejected = [row for row in candidates if row["sandbox_status"] == "LAB_FAILED"]
        if not chosen or not rejected:
            continue
        tasks_with_preferences += 1
        for good in chosen:
            for bad in rejected:
                digest = hashlib.sha256(
                    (task_id + "\\0" + good["response"] + "\\0" + bad["response"]).encode("utf-8")
                ).hexdigest()
                if digest in emitted:
                    continue
                emitted.add(digest)
                pairs.append({
                    "task_id": task_id,
                    "prompt": str(good.get("prompt", "")),
                    "chosen": good["response"],
                    "rejected": bad["response"],
                    "chosen_status": "LAB_PASSED",
                    "teach_back_verified": True,
                    "rejected_status": "LAB_FAILED",
                    "sandbox_run_id": good["sandbox_run_id"],
                    "rejected_sandbox_run_id": bad["sandbox_run_id"],
                    "grader_version": good["grader_version"],
                    "test_suite_sha256": good["test_suite_sha256"],
                    "rubric_sha256": good["rubric_sha256"],
                    "grader_attestation_sha256": good["grader_attestation_sha256"],
                    "rejected_grader_attestation_sha256": bad["grader_attestation_sha256"],
                })
    report = {
        "schema": "dreamco.foundry.self_play_pairs.v1",
        "input_records": len(records),
        "excluded_non_train_records": sum(
            1 for row in records
            if isinstance(row.get("task_id"), str) and split_name(row["task_id"]) != "train"
        ),
        "tasks_with_verified_preferences": tasks_with_preferences,
        "preference_pairs": len(pairs),
        "max_candidates_per_task": max_candidates,
        "training_started": False,
        "authorization_required": True,
    }
    return pairs, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollouts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--max-candidates", type=int, default=8)
    args = parser.parse_args()
    records = [
        json.loads(line)
        for line in args.rollouts.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pairs, report = build_pairs(records, args.max_candidates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in pairs),
        encoding="utf-8",
    )
    report["output_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
