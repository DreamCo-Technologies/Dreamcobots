#!/usr/bin/env python3
"""Run the plans that already have code. Do not train or publish."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bootcamp(unit: dict) -> dict:
    missing = [key for key in ("capability_id", "objective", "benchmark", "provenance") if not str(unit.get(key) or "").strip()]
    return {
        "status": "blocked" if missing else "ready",
        "missing": missing,
        "stages": ["lesson", "practice", "sandbox", "transfer", "score", "remediate", "regression", "evidence"],
        "trained": False,
    }


def verify(required: list[str], known: list[str], simulated: bool) -> dict:
    missing = [asset for asset in required if asset not in set(known)]
    issues = []
    if missing:
        issues.append("Missing assets: " + ", ".join(missing))
    if not simulated:
        issues.append("Plan has not completed a simulation preflight")
    return {"issues": issues, "approved": False, "reason": "A check does not grant permission to act."}


def utility(steps: list[dict]) -> dict:
    total = 0.0
    for step in steps:
        probability = float(step.get("probability", 1))
        value = float(step.get("utility", 0))
        cost = float(step.get("cost", 0))
        if not 0 <= probability <= 1 or cost < 0:
            return {"accepted": False, "reason": "Probability must be 0 to 1 and cost cannot be negative."}
        total += probability * value - cost
    reversible = 0 if not steps else sum(1 for step in steps if step.get("reversible", True)) / len(steps)
    return {"accepted": True, "expected_utility": round(total, 4), "reversibility": reversible, "executed": False}


def bundle() -> dict:
    lora = _load("lora_plan", ROOT / "foundry" / "lora_plan.py")
    customer = _load("customer_model", ROOT / "foundry" / "customer_model_builder.py")
    frontier = _load("plan_status", ROOT / "buddy" / "frontier" / "plan_status.py")
    catalog = json.loads((ROOT / "config" / "lora-recipe-catalog.json").read_text(encoding="utf-8"))
    recipes = [lora.plan("sample", row["id"], "not-loaded") for row in catalog["recipes"]]
    tracks = [customer.build_plan(track, "coding") for track in customer.TRACKS]
    lesson = bootcamp({})
    checked = verify(["consent.txt"], [], False)
    scored = utility([{"probability": 1, "utility": 1, "cost": 0, "reversible": True}])
    return {
        "production_ready": False,
        "weights_trained": False,
        "lora": recipes,
        "customers": tracks,
        "frontier_loop": frontier.LOOP,
        "bootcamp_example": lesson,
        "verify_example": checked,
        "utility_example": scored,
        "counts": {"lora": len(recipes), "customers": len(tracks), "frontier_steps": len(frontier.LOOP)},
    }


if __name__ == "__main__":
    made = bundle()
    assert made["production_ready"] is False and made["weights_trained"] is False
    assert all(row["launch_in_ci"] is False for row in made["lora"])
    assert all(row["trained_weights_exist"] is False for row in made["customers"])
    assert made["bootcamp_example"]["status"] == "blocked"
    assert made["verify_example"]["approved"] is False
    assert bootcamp({"capability_id": "a", "objective": "b", "benchmark": "c", "provenance": "d"})["status"] == "ready"
    assert utility([{"probability": 2, "utility": 1, "cost": 0}])["accepted"] is False
    print(json.dumps({"lora": made["counts"]["lora"], "customers": made["counts"]["customers"], "trained": False}))
