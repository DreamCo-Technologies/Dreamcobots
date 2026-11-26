#!/usr/bin/env python3
"""Prepare an auditable plan; no model training or external service call is performed."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ALLOWED = {"MEASURE_BASELINE", "TRAIN_TARGETED", "REGRESSION_RETEST", "SANDBOX_VALIDATE"}


def build_execution_plan(queue_doc: dict, limit: int = 20) -> dict:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    selected = queue_doc.get("queue", [])[:limit]
    runs = []
    for item in selected:
        action = item.get("action")
        scope = item.get("scope")
        identity_valid = (
            scope == "masterbot" and isinstance(item.get("masterbot_id"), int)
        ) or (
            scope == "domain_division" and bool(item.get("domain_id"))
        )
        if action not in ALLOWED:
            status, reason = "rejected", "unsupported action"
        elif not item.get("requires_evidence", True):
            status, reason = "rejected", "evidence contract missing"
        elif not identity_valid:
            status, reason = "rejected", "canonical scope identity missing"
        else:
            status, reason = "planned", "awaiting concrete registered runner"
        runs.append({
            "rank": item.get("rank"),
            "scope": scope,
            "masterbot_id": item.get("masterbot_id"),
            "domain_id": item.get("domain_id"),
            "division": item.get("division"),
            "benchmark": item.get("benchmark"),
            "action": action,
            "status": status,
            "reason": reason,
            "started_at": time.time(),
        })
    return {
        "schema": "dreamco.benchmark_training_plan.v1",
        "runs": runs,
        "executed": 0,
        "planned": sum(row["status"] == "planned" for row in runs),
        "rejected": sum(row["status"] == "rejected" for row in runs),
        "policy": "planning only; never claim training or mastery until a registered runner returns reproducible evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    result = build_execution_plan(json.loads(Path(args.queue).read_text(encoding="utf-8")), args.limit)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected": len(result["runs"]),
        "planned": result["planned"],
        "executed": result["executed"],
        "rejected": result["rejected"],
    }, indent=2))


if __name__ == "__main__":
    main()
