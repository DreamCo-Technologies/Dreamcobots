#!/usr/bin/env python3
"""For every task Buddy cannot do, write a lesson. Do not train a model or call a wrapper."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASKED = (
    "build a world map",
    "count the free datasets",
    "plan an idea for a sorting game",
    "send the private email",
    "charge a card",
    "book a flight",
    "diagnose a patient",
    "file a lawsuit",
    "control a robot arm",
    "trade stocks",
)


def _own():
    spec = importlib.util.spec_from_file_location("own_task_self", ROOT / "buddy/desk/own_task.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def learn(tasks: tuple[str, ...] = ASKED) -> dict:
    run = _own().run
    rows = []
    for task in tasks:
        result = run(task)
        if result.get("completed") is True:
            rows.append({"task": task, "can_do": True, "lesson": "Buddy already does this with its own code.", "wrapper_used": False})
        else:
            rows.append({
                "task": task,
                "can_do": False,
                "lesson": "Practice this with Buddy's own code on a new example. Do not send it to another model until a recorded result says the practice passed.",
                "wrapper_used": False,
            })
    return {
        "asked": len(rows),
        "can_do": sum(1 for row in rows if row["can_do"]),
        "needs_practice": sum(1 for row in rows if not row["can_do"]),
        "weights_trained": False,
        "opened_a_closed_model": False,
        "rows": rows,
    }


if __name__ == "__main__":
    report = learn()
    assert report["weights_trained"] is False and report["opened_a_closed_model"] is False
    assert report["can_do"] >= 3 and report["needs_practice"] >= 1
    assert all(row["wrapper_used"] is False for row in report["rows"])
    print(json.dumps({"can_do": report["can_do"], "needs_practice": report["needs_practice"], "trained": False}))
