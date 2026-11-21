"""Fail-closed, zero-cost evidence gate for Buddy Master Teacher evaluations.

Input JSON must be produced by an authorized runner; this module does not run models.
"""
import argparse
import hashlib
import json
from pathlib import Path


REQUIRED = ("suite", "suite_version", "dataset_sha256", "champion_sha256",
            "candidate_sha256", "seed", "configuration", "environment",
            "baseline", "pass_criteria", "trials", "holdout_provenance",
            "contamination_review", "safety_review", "rollback_plan",
            "independent_verification")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def evaluate(record):
    missing = [key for key in REQUIRED if key not in record or record[key] is None]
    reasons = ["missing: " + ", ".join(missing)] if missing else []
    provenance = record.get("holdout_provenance") or {}
    review = record.get("contamination_review") or {}
    if not isinstance(provenance, dict) or provenance.get("isolated") is not True or provenance.get("authorized") is not True:
        reasons.append("holdout isolation/authorization not verified")
    for key in ("exact_overlap", "near_duplicate_overlap", "shared_templates",
                "source_lineage_leak", "timestamp_leak", "task_family_leak",
                "answer_exposure"):
        if not isinstance(review, dict) or review.get(key) is not False:
            reasons.append("contamination unresolved: " + key)
    trials = record.get("trials")
    if not isinstance(trials, list) or len(trials) < 2:
        reasons.append("reproducible paired trials missing")
    else:
        for trial in trials:
            if not isinstance(trial, dict) or any(k not in trial for k in
                    ("champion_correct", "candidate_correct", "latency_ms",
                     "cost_usd", "tool_use", "safety", "regressions", "evidence")):
                reasons.append("trial evidence incomplete")
                break
    if record.get("safety_review") != "passed":
        reasons.append("safety review not passed")
    if record.get("independent_verification") != "passed":
        reasons.append("independent verification not passed")
    if not record.get("rollback_plan"):
        reasons.append("rollback plan missing")
    if record.get("regressions"):
        reasons.append("regressions unresolved")
    if record.get("promotion_approved") is not True:
        reasons.append("owner promotion approval missing")
    if record.get("training_requested"):
        reasons.append("training requires separate explicit authorization; not executed")
    return {"status": "blocked" if reasons else "eligible_for_manual_review",
            "reasons": reasons, "training_launched": False,
            "promotion_executed": False, "tests_executed_by_gate": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    result = evaluate(record)
    result["input_sha256"] = sha256_file(args.record)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
