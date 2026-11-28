#!/usr/bin/env python3
"""Plan a 10x50 model benchmark shard layout without executing model calls.

The planner accepts only an explicit, rights-reviewed inventory of real pinned
models. Placeholder registry slots are not model inventory. Planning never
downloads weights, calls providers, trains, or scores a model.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "config/verified-model-inventory.json"
EXPECTED_MODELS = 500
SHARD_COUNT = 10
MODELS_PER_SHARD = 50
REQUIRED = (
    "model_id", "provider", "model_revision", "adapter_id", "model_card_uri",
    "access_status", "license_review_status", "evaluation_authorized",
    "benchmark_suites", "review_record_id",
)


def read_inventory(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("verified model inventory must be a JSON object")
    return value


def validate_inventory(inventory: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    blockers: list[str] = []
    models = inventory.get("models")
    if inventory.get("status") != "VERIFIED":
        blockers.append("inventory status must be VERIFIED after owner review")
    if inventory.get("expected_model_count") != EXPECTED_MODELS:
        blockers.append(f"expected_model_count must equal {EXPECTED_MODELS}")
    if not isinstance(models, list):
        return [], blockers + ["models must be a list"]
    if len(models) != EXPECTED_MODELS:
        blockers.append(f"expected exactly {EXPECTED_MODELS} real model records; found {len(models)}")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(models):
        if not isinstance(item, dict):
            blockers.append(f"model record {index} must be an object")
            continue
        missing = [field for field in REQUIRED if item.get(field) in (None, "", [])]
        if missing:
            blockers.append(f"model record {index} missing: {', '.join(missing)}")
            continue
        model_id = str(item["model_id"]).strip()
        if model_id in seen:
            blockers.append(f"duplicate model_id: {model_id}")
            continue
        seen.add(model_id)
        revision = str(item["model_revision"]).strip().lower()
        if revision in {"latest", "main", "master", "head", "default"}:
            blockers.append(f"{model_id}: model_revision must be immutable/pinned")
        if item["access_status"] != "AVAILABLE":
            blockers.append(f"{model_id}: access_status must be AVAILABLE")
        if item["license_review_status"] != "APPROVED":
            blockers.append(f"{model_id}: license_review_status must be APPROVED")
        if item["evaluation_authorized"] is not True:
            blockers.append(f"{model_id}: evaluation_authorized must be true")
        if not str(item["model_card_uri"]).startswith("https://"):
            blockers.append(f"{model_id}: model_card_uri must be an HTTP(S) reference")
        if not isinstance(item["benchmark_suites"], list) or not item["benchmark_suites"]:
            blockers.append(f"{model_id}: at least one applicable benchmark suite is required")
        elif any(not isinstance(suite, str) or not suite.strip() for suite in item["benchmark_suites"]):
            blockers.append(f"{model_id}: benchmark_suites contains an invalid entry")
        normalized.append({
            "model_id": model_id,
            "provider": str(item["provider"]).strip(),
            "model_revision": str(item["model_revision"]).strip(),
            "adapter_id": str(item["adapter_id"]).strip(),
            "benchmark_suites": sorted(set(str(s).strip() for s in item["benchmark_suites"] if str(s).strip())),
            "review_record_id": str(item["review_record_id"]).strip(),
        })
    return normalized, blockers


def build_plan(inventory: dict[str, Any]) -> dict[str, Any]:
    models, blockers = validate_inventory(inventory)
    ready = not blockers and len(models) == EXPECTED_MODELS
    shards = []
    for shard_index in range(SHARD_COUNT):
        shard_models = models[shard_index * MODELS_PER_SHARD:(shard_index + 1) * MODELS_PER_SHARD] if ready else []
        shards.append({
            "shard_id": f"shard-{shard_index:02d}",
            "index": shard_index,
            "expected_models": MODELS_PER_SHARD,
            "planned_models": len(shard_models),
            "status": "READY_FOR_SEPARATE_COMPUTE_APPROVAL" if ready else "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY",
            "models": shard_models,
        })
    return {
        "schema": "dreamco.500_model_shard_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_SEPARATE_COMPUTE_APPROVAL" if ready else "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY",
        "expected_models": EXPECTED_MODELS,
        "verified_model_records": len(models) if ready else 0,
        "shard_count": SHARD_COUNT,
        "models_per_shard": MODELS_PER_SHARD,
        "execution_started": False,
        "provider_calls": 0,
        "training_jobs": 0,
        "paid_calls_enabled": False,
        "blockers": blockers,
        "shards": shards,
        "truth_boundary": "A shard plan is not a benchmark run. No model calls, downloads, training, scores, or certifications are produced.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--shard", type=int, choices=range(SHARD_COUNT))
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/500-model-shards/full-plan.json")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    plan = build_plan(read_inventory(args.inventory))
    output: dict[str, Any] = plan
    if args.shard is not None:
        output = {**plan, "selected_shard": plan["shards"][args.shard]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": plan["status"],
        "verified_model_records": plan["verified_model_records"],
        "shards": plan["shard_count"],
        "models_per_shard": plan["models_per_shard"],
        "execution_started": False,
        "output": str(args.output),
    }, sort_keys=True))
    if args.require_ready and plan["status"] != "READY_FOR_SEPARATE_COMPUTE_APPROVAL":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
