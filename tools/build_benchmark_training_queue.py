#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ACTIONS = {
    "CLOSE_GAPS": "TRAIN_TARGETED",
    "RUN_BENCHMARKS": "MEASURE_BASELINE",
    "RETEST_FAILURES": "REGRESSION_RETEST",
    "RUN_SANDBOX": "SANDBOX_VALIDATE",
}


def build_training_queue(gaps: dict) -> dict:
    queue = []
    for index, gap in enumerate(gaps.get("queue", [])):
        action = gap.get("action", "RUN_BENCHMARKS")
        queue.append({
            "rank": index + 1,
            "scope": gap.get("scope"),
            "masterbot_id": gap.get("masterbot_id"),
            "domain_id": gap.get("domain_id"),
            "division": gap.get("division"),
            "benchmark": gap.get("benchmark"),
            "score": gap.get("score"),
            "target": gap.get("target"),
            "priority": gap.get("priority", 99),
            "action": ACTIONS.get(action, "MEASURE_BASELINE"),
            "source_action": action,
            "reason": gap.get("reason", ""),
            "requires_evidence": True,
        })
    return {
        "schema": "dreamco.benchmark_training_queue.v2",
        "queue": queue,
        "scope_counts": {
            "masterbot": sum(row["scope"] == "masterbot" for row in queue),
            "domain_division": sum(row["scope"] == "domain_division" for row in queue),
        },
        "policy": "plan only; a registered scope-specific runner must return reproducible evidence before execution or mastery",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = build_training_queue(json.loads(Path(args.gaps).read_text(encoding="utf-8")))
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"training_items": len(result["queue"]), "scope_counts": result["scope_counts"]}, indent=2))


if __name__ == "__main__":
    main()
