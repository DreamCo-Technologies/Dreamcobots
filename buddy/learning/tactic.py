#!/usr/bin/env python3
"""Pick a learning tactic that is already in the catalog. A pick is not a score."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "config/buddy-learning-strategies.json"
ROUTES = (
    ("remember", "retrieval_augmented_training"),
    ("reason", "star_self_taught_reasoner"),
    ("tool", "tool_augmented_reasoning"),
    ("compare", "contrastive_representation_learning"),
    ("order", "curriculum_learning"),
)


def choose(task: str) -> dict:
    text = " ".join((task or "").split())
    if len(text) < 3:
        raise ValueError("Name the task.")
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    known = {row["id"]: row for row in catalog["techniques"]}
    picked = "causal_language_modeling"
    for word, tactic in ROUTES:
        if word in text.lower() and tactic in known:
            picked = tactic
            break
    row = known[picked]
    return {
        "task": text,
        "tactic": row["id"],
        "label": row["label"],
        "stored_in": "config/buddy-learning-strategies.json",
        "score": None,
        "weights_trained_by_this_pick": False,
    }


if __name__ == "__main__":
    made = choose("reason about the next step")
    assert made["tactic"] == "star_self_taught_reasoner" and made["score"] is None
    print(made["tactic"])
