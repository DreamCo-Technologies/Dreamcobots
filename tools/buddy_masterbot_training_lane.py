"""Emit a plan-only record for a canonical MasterBot; this does not train weights."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "masterbot-65-registry.json"
OUT = ROOT / "artifacts" / "masterbot-training"


def build_plan(bot: dict, *, run_id: str, run_attempt: str, lifecycle: list) -> dict:
    """Build explicit plan-only evidence without invoking a model or compute worker."""
    return {
        "schema": "dreamco.masterbot_training_plan.v1",
        "artifact_kind": "PLAN_ONLY_NOT_A_MODEL_CHECKPOINT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "run_attempt": run_attempt,
        "masterbot_id": bot["id"],
        "masterbot": bot["name"],
        "mode": "sandbox_first",
        "status": "PLAN_ONLY_NOT_EXECUTED",
        "lifecycle": lifecycle,
        "shared_learning_inputs": [
            "approved_lesson_metadata",
            "verified_benchmark_deltas",
            "reusable_test_fixtures",
            "verified_fixes_from_other_dreamco_runs",
        ],
        "shareable_lesson_refs": [],
        "next_actions": [
            "load_this_division_capability_gap_inventory",
            "ingest_rights_cleared_shared_lesson_metadata",
            "select_highest_priority_unresolved_gap",
            "run_a_pinned_baseline",
            "study_authorized_sources",
            "practice_in_an_isolated_sandbox",
            "run_domain_and_held_out_benchmarks",
            "record_lineage_and_reproducibility_evidence",
            "publish_verified_reusable_lesson_metadata",
            "requeue_unresolved_or_regressed_gaps",
        ],
        "raw_dataset_pooling": False,
        "automatic_weight_merging": False,
        "weights_trained": False,
        "training_job_executed": False,
        "compute_consumed": False,
        "production_side_effects": "disabled",
        "mastery_claim": "not_claimed_without_evidence",
    }


def main() -> int:
    name = os.environ.get("MASTERBOT_NAME", "").strip()
    if not name:
        raise SystemExit("MASTERBOT_NAME is required")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    bots = registry.get("divisions") or registry.get("masterbots") or []
    bot = next((item for item in bots if item.get("name") == name), None)
    if bot is None:
        raise SystemExit(f"Unknown MasterBot: {name}")

    plan = build_plan(
        bot,
        run_id=os.environ.get("GITHUB_RUN_ID", "local"),
        run_attempt=os.environ.get("GITHUB_RUN_ATTEMPT", "1"),
        lifecycle=registry.get("training_lifecycle", []),
    )
    destination = OUT / bot["name"]
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / "latest-plan.json"
    output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
