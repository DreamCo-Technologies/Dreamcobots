"""Append verified Buddy teacher traces for student distillation.

Only task prompts, final answers, tool-call records and short explanation
summaries are retained. Private chain-of-thought fields are rejected. The
resulting dataset must be separately rights-reviewed and signed before training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

EVIDENCE_HASHES = ("grader_attestation_sha256", "rubric_sha256", "test_suite_sha256")
FORBIDDEN_REASONING_FIELDS = {"chain_of_thought", "reasoning_trace", "private_reasoning"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verified_trace(row: dict[str, Any]) -> dict[str, Any] | None:
    if FORBIDDEN_REASONING_FIELDS.intersection(row):
        return None
    required = ("task_id", "division_id", "prompt", "final_response", "sandbox_run_id")
    if not all(isinstance(row.get(key), str) and row[key].strip() for key in required):
        return None
    if row.get("sandbox_status") != "LAB_PASSED" or row.get("teach_back_status") != "TEACH_BACK_VERIFIED":
        return None
    if not all(_valid_sha(row.get(key)) for key in EVIDENCE_HASHES):
        return None
    tool_calls = row.get("tool_calls", [])
    if not isinstance(tool_calls, list) or any(not isinstance(item, dict) for item in tool_calls):
        return None
    summary = row.get("explanation_summary", "")
    if not isinstance(summary, str) or len(summary) > 2000:
        return None
    payload = {
        "schema": "dreamco.foundry.distilled_trace.v1",
        "task_id": row["task_id"],
        "division_id": row["division_id"],
        "prompt": row["prompt"],
        "final_response": row["final_response"],
        "explanation_summary": summary,
        "tool_calls": tool_calls,
        "sandbox_run_id": row["sandbox_run_id"],
        "grader_attestation_sha256": row["grader_attestation_sha256"],
        "rubric_sha256": row["rubric_sha256"],
        "test_suite_sha256": row["test_suite_sha256"],
        "sandbox_status": "LAB_PASSED",
        "teach_back_status": "TEACH_BACK_VERIFIED",
        "training_authorized": False,
    }
    payload["trace_id"] = hashlib.sha256(_canonical(payload)).hexdigest()
    return payload


def append_verified_traces(rows: list[dict[str, Any]], output: Path) -> dict[str, int]:
    output.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if output.exists():
        with output.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                parsed = json.loads(line)
                trace_id = parsed.get("trace_id")
                if not isinstance(trace_id, str):
                    raise ValueError(f"existing trace line {line_number} is missing trace_id")
                existing.add(trace_id)
    appended = duplicates = rejected = 0
    with output.open("a", encoding="utf-8") as stream:
        for row in rows:
            trace = verified_trace(row)
            if trace is None:
                rejected += 1
                continue
            if trace["trace_id"] in existing:
                duplicates += 1
                continue
            stream.write(json.dumps(trace, sort_keys=True, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            existing.add(trace["trace_id"])
            appended += 1
    return {"appended": appended, "duplicates": duplicates, "rejected": rejected}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/clean_room/distilled_traces.jsonl"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    counts = append_verified_traces(rows, args.output)
    report = {
        "schema": "dreamco.foundry.distilled_trace_ingestion.v1",
        **counts,
        "training_started": False,
        "authorization_required": True,
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
