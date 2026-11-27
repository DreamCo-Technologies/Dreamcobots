"""Authorized reverse-engineering evidence -> benchmark candidate registry.

This adapter does not install or execute REA. It only accepts reviewed findings
from a separately authorized REA run. No third-party code is copied.
"""
import argparse
import hashlib
import json
from pathlib import Path

def build_candidates(findings):
    if not isinstance(findings, list):
        raise ValueError("expected list of findings")
    candidates, rejected, seen = [], 0, set()
    for item in findings:
        if not isinstance(item, dict) or item.get("owner_authorized") is not True or item.get("license_reviewed") is not True or item.get("privacy_reviewed") is not True:
            rejected += 1
            continue
        if item.get("contains_secrets") is not False or item.get("protected_holdout") is not False:
            rejected += 1
            continue
        fields = ("target", "feature", "observed_behavior", "evidence_ref",
                  "independent_spec", "test_case", "quality_metric",
                  "efficiency_metric", "baseline")
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in fields):
            rejected += 1
            continue
        row = {key: item[key].strip() for key in fields}
        digest = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        row["id"] = digest
        row["status"] = "unverified_candidate"
        row["benchmark_score"] = None
        row["model_trained"] = False
        candidates.append(row)
    return {"schema_version": 1, "candidates": candidates,
            "rejected": rejected, "reverse_engineering_executed": False,
            "model_inference_executed": False, "weight_training_executed": False,
            "performance_improvement_verified": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("findings", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_candidates(json.loads(args.findings.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": len(result["candidates"]), "rejected": result["rejected"]}))

if __name__ == "__main__":
    main()
