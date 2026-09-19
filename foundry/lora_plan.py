#!/usr/bin/env python3
"""Turn a capability pack + recipe id into a train plan. Does not launch GPUs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "config" / "lora-recipe-catalog.json"


def plan(pack_id: str, recipe_id: str, base_model: str) -> dict:
    catalog = json.loads(RECIPES.read_text(encoding="utf-8"))
    recipe = next((row for row in catalog["recipes"] if row["id"] == recipe_id), None)
    if recipe is None:
        raise ValueError(f"unknown recipe: {recipe_id}")
    return {
        "schema": "dreamco.lora_train_plan.v1",
        "pack_id": pack_id,
        "recipe": recipe,
        "base_model": base_model,
        "launch_in_ci": False,
        "requires": ["license_ok", "revision_pinned", "eval_baseline", "holdout", "owner_approval"],
        "output": f"adapters/{pack_id}/{recipe_id}",
        "truth": "Plan only. No weights are trained by this function.",
    }
