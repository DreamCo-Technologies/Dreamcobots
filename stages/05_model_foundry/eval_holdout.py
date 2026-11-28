"""Validate externally generated holdout evidence; never trains or runs inference.

The evaluator must produce reports containing the exact held-out task IDs and
benchmark-suite digest. This gate checks evidence completeness and regressions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
try:
    from .guardrails import canonical_json, iter_authorized_records, verify_signed_manifest
except ImportError:
    from guardrails import canonical_json, iter_authorized_records, verify_signed_manifest

METRICS = ("pass_rate", "safety_gate_pass_rate")

def validate_report(report: dict, expected_ids: list[str], manifest_sha256: str,
                    benchmark_sha256: str, label: str) -> None:
    if report.get("schema") != "dreamco.foundry.model_holdout_report.v1":
        raise ValueError(f"{label}: expected a model holdout evaluation report")
    if report.get("holdout_access") != "evaluation_only" or report.get("training_access") is not False:
        raise PermissionError(f"{label}: holdout data must be evaluation-only")
    if report.get("evaluation_split") != "holdout":
        raise ValueError(f"{label}: evaluation_split must be holdout")
    if report.get("source_manifest_sha256") != manifest_sha256:
        raise ValueError(f"{label}: report must reference the exact signed dataset manifest")
    suite_sha = report.get("benchmark_suite_sha256")
    if suite_sha != benchmark_sha256:
        raise ValueError(f"{label}: report does not match the signed holdout benchmark suite")
    config_sha = report.get("evaluation_config_sha256")
    if not isinstance(config_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", config_sha):
        raise ValueError(f"{label}: evaluation_config_sha256 is required")
    tokenizer_sha = report.get("tokenizer_sha256")
    if not isinstance(tokenizer_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", tokenizer_sha):
        raise ValueError(f"{label}: tokenizer_sha256 is required")
    checkpoint_sha = report.get("checkpoint_sha256")
    if not isinstance(checkpoint_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", checkpoint_sha):
        raise ValueError(f"{label}: checkpoint_sha256 is required")
    evaluated = report.get("evaluated_task_ids")
    if not isinstance(evaluated, list) or sorted(set(evaluated)) != expected_ids:
        raise ValueError(f"{label}: report must cover every holdout task exactly once")
    for metric in METRICS:
        value = report.get(metric)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{label}: {metric} must be a number between 0 and 1")

def main():
    parser = argparse.ArgumentParser(description="DreamCo isolated holdout evidence gate")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    rows = list(iter_authorized_records(
        manifest, categories={"holdout_benchmarks"}, splits={"holdout"}
    ))
    if not rows:
        raise ValueError("no isolated holdout records found")
    holdout_ids = sorted(str(row.get("task_id") or row.get("id")) for row in rows)
    if len(holdout_ids) != len(set(holdout_ids)):
        raise ValueError("holdout task IDs must be unique")
    manifest_sha = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    suite = [{
        "task_id": row.get("task_id") or row.get("id"),
        "prompt": row["prompt"],
        "expected_answer": row["expected_answer"],
        "expected_safety": row["expected_safety"],
    } for row in rows]
    benchmark_sha = hashlib.sha256(canonical_json(suite)).hexdigest()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    validate_report(baseline, holdout_ids, manifest_sha, benchmark_sha, "baseline")
    validate_report(candidate, holdout_ids, manifest_sha, benchmark_sha, "candidate")
    if baseline["evaluation_config_sha256"] != candidate["evaluation_config_sha256"]:
        raise ValueError("baseline and candidate must use identical generation and scoring settings")
    if baseline["tokenizer_sha256"] != candidate["tokenizer_sha256"]:
        raise ValueError("baseline and candidate must use the same exact tokenizer artifacts")
    regressions = {
        metric: {"baseline": baseline[metric], "candidate": candidate[metric]}
        for metric in METRICS if candidate[metric] < baseline[metric]
    }
    if candidate.get("thresholds_pass") is not True:
        regressions["minimum_promotion_thresholds"] = {
            "baseline": baseline.get("thresholds_pass"),
            "candidate": candidate.get("thresholds_pass"),
        }
    report = {
        "schema": "dreamco.foundry.holdout_evaluation.v1",
        "holdout_records": len(rows),
        "evaluated_task_ids_sha256": hashlib.sha256("\n".join(holdout_ids).encode()).hexdigest(),
        "source_manifest_sha256": manifest_sha,
        "benchmark_suite_sha256": benchmark_sha,
        "evaluation_config_sha256": candidate["evaluation_config_sha256"],
        "candidate_tokenizer_sha256": candidate["tokenizer_sha256"],
        "evaluation_split": "holdout",
        "holdout_access": "evaluation_only",
        "training_access": False,
        "regressions": regressions,
        "promotion_eligible": not regressions,
        "candidate_checkpoint_sha256": candidate["checkpoint_sha256"],
        "truth_boundary": "Evidence validation only; this script does not execute model inference or certify legal rights.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if regressions:
        raise SystemExit("HOLDOUT REGRESSION: promotion blocked")

if __name__ == "__main__":
    main()
