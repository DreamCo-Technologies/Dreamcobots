#!/usr/bin/env python3
"""Build an evidence-gated Buddy Bootcamp plan without starting model training."""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

REQUIRED = ("capability_id", "objective", "benchmark", "provenance")
STAGES = [
    "lesson", "practice", "sandbox", "transfer", "score",
    "remediate", "regression", "evidence",
]
DAILY_GROWTH_LOOP = [
    "capture a baseline before changing behavior",
    "select the largest verified capability gap",
    "study one approved source and record its provenance",
    "practice in an isolated sandbox with synthetic or rights-cleared fixtures",
    "run targeted tests and an untouched holdout",
    "compare against the baseline and run regression tests",
    "store lesson, score, run manifest, and failure analysis",
    "promote only versioned, reproducible improvements; otherwise retain the prior model",
]


def build_plan(data: dict | list, days: int = 14, start: date | None = None) -> dict:
    if days < 1:
        raise ValueError("--days must be at least 1")
    units = data if isinstance(data, list) else data.get("units", [])
    start = start or date.today()
    plan = []
    for index, unit in enumerate(units):
        missing = [key for key in REQUIRED if not unit.get(key)]
        day = min(index + 1, days)
        plan.append({
            "capability_id": unit.get("capability_id"),
            "objective": unit.get("objective"),
            "status": "blocked" if missing else "ready",
            "missing": missing,
            "scheduled_day": day,
            "scheduled_date": (start + timedelta(days=day - 1)).isoformat(),
            "stages": STAGES,
            "execution_status": "PLANNED_NOT_EXECUTED",
            "weights_trained": False,
            "evidence_required": [
                "source_and_dataset_provenance",
                "reproducible_run_config_and_seed",
                "targeted_test_result",
                "held_out_transfer_result",
                "regression_result",
                "checkpoint_or_artifact_hash",
            ],
        })

    # The final four days are reserved for integration, repeatability and graduation.
    milestones = [
        {"day": min(11, days), "name": "integration_and_registry", "gate": "model registry, lineage, permissions and routing contract tests pass"},
        {"day": min(12, days), "name": "benchmark_and_gap_closure", "gate": "before/after scores use the same pinned fixtures and isolated holdout"},
        {"day": min(13, days), "name": "reproducibility_and_safety", "gate": "second-seed rerun, regression, adversarial and safety checks pass"},
        {"day": days, "name": "graduation_review", "gate": "independent evidence review; unresolved blockers remain visible"},
    ]
    policy = {} if isinstance(data, list) else data.get("training_policy", {})
    return {
        "schema": "dreamco.bootcamp_plan.v2",
        "track_id": None if isinstance(data, list) else data.get("track_id"),
        "created_for_days": days,
        "start_date": start.isoformat(),
        "target_date": (start + timedelta(days=days - 1)).isoformat(),
        "status": "PLAN_ONLY_NOT_EXECUTED",
        "training_policy": {
            "weight_updates_authorized": bool(policy.get("weight_updates_authorized", False)),
            "paid_compute_authorized": bool(policy.get("paid_compute_authorized", False)),
            "unknown_dataset_rights": "BLOCKED",
            "proprietary_weights": "FORBIDDEN",
        },
        "daily_growth_loop": DAILY_GROWTH_LOOP,
        "units": plan,
        "milestones": milestones,
        "completion_rule": "Do not mark complete by elapsed time. Require passing evidence, independent review, and explicit reporting of any blocked or unrun work.",
        "safety_note": "Generating this plan does not ingest data, call a model provider, update weights, create checkpoints, or authorize compute.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default="bootcamp-plan.json")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--start-date", help="ISO date; defaults to the machine's local date")
    args = parser.parse_args()
    start = date.fromisoformat(args.start_date) if args.start_date else date.today()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = build_plan(data, days=args.days, start=start)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    ready = sum(unit["status"] == "ready" for unit in result["units"])
    blocked = len(result["units"]) - ready
    print(json.dumps({
        "units": len(result["units"]),
        "ready": ready,
        "blocked": blocked,
        "target_date": result["target_date"],
        "status": result["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
