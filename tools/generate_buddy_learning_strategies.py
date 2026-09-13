#!/usr/bin/env python3
"""Validate and publish Buddy's learning-strategy research catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-learning-strategies.json"
GENERATED = ROOT / "config" / "generated" / "buddy_learning_strategies.json"
PUBLIC = ROOT / "website" / "data" / "buddy-learning-strategies.js"
OPEN_MODEL_SOURCE = ROOT / "config" / "buddy-open-model-coding-lab.json"


def validate(payload: dict) -> dict:
    if payload.get("schema") != "dreamco.buddy_learning_strategies.v1":
        raise ValueError("Unsupported Buddy learning-strategy schema.")
    techniques = payload.get("techniques", [])
    ids = [item.get("id") for item in techniques]
    categories = {item.get("category") for item in techniques}
    if len(techniques) < 45 or len(categories) < 7:
        raise ValueError("Buddy needs broad coverage across at least seven learning categories.")
    if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("Learning technique ids must be present and unique.")
    for item in techniques:
        source = urlsplit(str(item.get("official_source", "")))
        if source.scheme != "https" or not source.netloc:
            raise ValueError(f"Learning technique requires an official HTTPS research source: {item.get('id')}")
        if item.get("status") != "catalogued":
            raise ValueError("Research techniques cannot be labeled implemented without executable evidence.")
    controls = payload.get("failure_controls", [])
    required_failures = {"endless_repetition", "poor_readability", "language_mixing", "reward_hacking", "catastrophic_forgetting", "data_contamination", "memorization_and_privacy"}
    if not required_failures.issubset({item.get("id") for item in controls}):
        raise ValueError("Required learning failure controls are missing.")
    optimizer = payload.get("study_optimizer", {})
    if optimizer.get("automatic_production_promotion") is not False or optimizer.get("minimum_repetitions", 0) < 3:
        raise ValueError("Learning studies need repeat runs and must never auto-promote to production.")
    weights = optimizer.get("default_score_weights", {})
    if abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
        raise ValueError("Learning study score weights must sum to one.")
    return {
        **payload,
        "summary": {"techniques": len(techniques), "categories": len(categories), "failure_controls": len(controls), "live_trials_run": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = validate(json.loads(SOURCE.read_text(encoding="utf-8")))
    open_model = json.loads(OPEN_MODEL_SOURCE.read_text(encoding="utf-8"))
    core_methods = set(open_model.get("buddy_open_core", {}).get("learning_system", {}).get("methods", []))
    technique_ids = {item["id"] for item in payload["techniques"]}
    if not core_methods.issubset(technique_ids):
        raise ValueError(f"Open Core learning methods missing from strategy catalog: {sorted(core_methods - technique_ids)}")
    generated = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    public = f"window.BUDDY_LEARNING_STRATEGIES = {json.dumps(payload, separators=(',', ':'))};\n"
    if args.check:
        for path, expected in ((GENERATED, generated), (PUBLIC, public)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated file is stale: {path.relative_to(ROOT)}")
    else:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(generated, encoding="utf-8")
        PUBLIC.write_text(public, encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
