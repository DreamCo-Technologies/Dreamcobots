"""Offline evidence-to-lesson distillation; no model calls or weight training."""
import argparse
import hashlib
import json
from pathlib import Path

FIELDS = ("capability", "failure_mode", "repair", "regression_test", "source_ref")

def distill(records):
    if not isinstance(records, list):
        raise ValueError("input must be a JSON list")
    lessons, seen, rejected = [], set(), 0
    for row in records:
        if not isinstance(row, dict) or row.get("authorized") is not True or row.get("privacy_reviewed") is not True:
            rejected += 1
            continue
        if any(row.get(key) is not False for key in ("holdout", "contains_answer_key", "sensitive")):
            rejected += 1
            continue
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            rejected += 1
            continue
        lesson = {k: row[k].strip() for k in FIELDS}
        digest = hashlib.sha256(json.dumps(lesson, sort_keys=True).encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        lesson["sha256"] = digest
        lesson["status"] = "candidate_requires_independent_review"
        lessons.append(lesson)
    return {"schema_version": 1, "input_records": len(records),
            "rejected_records": rejected, "candidate_lessons": lessons,
            "model_inference_executed": False, "model_training_executed": False,
            "holdout_evaluations_executed": False, "mastery_claimed": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    result = distill(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"candidate_lessons": len(result["candidate_lessons"]), "rejected_records": result["rejected_records"]}))

if __name__ == "__main__":
    main()
