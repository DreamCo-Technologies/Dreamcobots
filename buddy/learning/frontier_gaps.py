#!/usr/bin/env python3
"""What is still missing before this repo can compete with a frontier model."""
from __future__ import annotations

import json

# Measured in this repository on 2026-09-25. Not a live leaderboard.
GAPS = [
    {"have": False, "need": "A weight file you are allowed to train."},
    {"have": False, "need": "A hidden exam and a published score."},
    {"have": False, "need": "Runtime results for the benchmark workflows. The actions report had 72 unknown and 0 recorded failures."},
    {"have": False, "need": "A completed live benchmark. The index said 0 live programs."},
    {"have": False, "need": "The release file says production_ready is false."},
    {"have": True, "need": "Ten views can each keep a source link. That is a citation, not a downloaded library."},
    {"have": True, "need": "67 weight settings can be changed. Changing them does not train a model."},
]


def report() -> dict:
    missing = [gap["need"] for gap in GAPS if not gap["have"]]
    return {
        "competes_with_frontier_models": False,
        "missing": missing,
        "have": [gap["need"] for gap in GAPS if gap["have"]],
        "next": "Cite ten free sources, write your own line, then train on a machine you control when you have weights and a hidden test.",
    }


if __name__ == "__main__":
    made = report()
    assert made["competes_with_frontier_models"] is False
    assert len(made["missing"]) == 5
    print(json.dumps({"missing": len(made["missing"]), "competes": False}))
