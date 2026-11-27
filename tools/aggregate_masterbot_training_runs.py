#!/usr/bin/env python3
"""Aggregate plan/checkpoint records without misrepresenting them as training."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.input)
    paths = set(root.rglob("latest-plan.json")) | set(root.rglob("latest-checkpoint.json"))
    records = []
    for path in sorted(paths):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            records.append({
                "schema": record.get("schema"),
                "artifact_kind": record.get("artifact_kind", "LEGACY_CHECKPOINT_RECORD"),
                "masterbot_id": record.get("masterbot_id"),
                "masterbot": record.get("masterbot"),
                "run_id": record.get("run_id"),
                "run_attempt": record.get("run_attempt"),
                "record_path": str(path),
                "lifecycle_status": record.get("status", "UNKNOWN_LEGACY_STATUS"),
                "next_actions": record.get("next_actions", []),
                "shareable_lesson_refs": record.get("shareable_lesson_refs", []),
                "weights_trained": record.get("weights_trained") is True,
                "training_job_executed": record.get("training_job_executed") is True,
                "compute_consumed": record.get("compute_consumed") is True,
                "mastery_claim": record.get("mastery_claim", "not_claimed_without_evidence"),
            })
        except (OSError, json.JSONDecodeError) as exc:
            records.append({"record_path": str(path), "error": type(exc).__name__})

    names = {record.get("masterbot") for record in records if record.get("masterbot")}
    payload = {
        "schema": "dreamco.cross_division_learning_queue.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "records_received": len(records),
        "unique_divisions_reported": len(names),
        "expected_divisions": 65,
        "missing_divisions_count": max(0, 65 - len(names)),
        "shared_learning_policy": (
            "Share only versioned lesson metadata, benchmark learnings and verified fixes; "
            "consumers must recheck rights and compatibility."
        ),
        "raw_dataset_pooling": False,
        "automatic_weight_merging": False,
        "status": "AGGREGATED_RUN_EVIDENCE_NOT_MODEL_TRAINING",
        "records": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        key: payload[key]
        for key in (
            "records_received",
            "unique_divisions_reported",
            "missing_divisions_count",
            "status",
        )
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
