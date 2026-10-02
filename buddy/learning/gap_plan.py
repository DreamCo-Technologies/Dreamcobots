#!/usr/bin/env python3
"""Plan practice for every task Buddy cannot do, then retest every approved model."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASKED = (
    "build a world map",
    "count the free datasets",
    "plan an idea for a sorting game",
    "write a caption for the cake",
    "send the private email",
    "charge a card",
    "book a flight",
    "diagnose a patient",
    "file a lawsuit",
    "control a robot arm",
    "trade stocks",
)
PRACTICE = (
    "Write one new example in Buddy's own file for this task.",
    "Run that example and record pass or fail. Do not call a remote model.",
    "Test every user-approved model on this same task and keep the highest score.",
    "Prefer a free model on a tie, then Buddy's own code. Own code still does the work.",
    "Repeat the example on a new case before calling the task learned.",
)


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(tasks: tuple[str, ...] = ASKED, models: list[dict] | None = None) -> dict:
    run = _load("own_task_gap", "buddy/desk/own_task.py").run
    sweep = _load("test_models_gap", "buddy/desk/test_models.py").sweep
    rows = []
    for task in tasks:
        result = run(task)
        known = result.get("completed") is True and result.get("planned") is not True
        if known:
            rows.append({
                "task": task,
                "status": "known",
                "can_do": True,
                "lesson": "Buddy already does this with its own code.",
                "steps": [],
                "wrapper_used": False,
            })
            continue
        if result.get("refused") is True:
            rows.append({
                "task": task,
                "status": "refused",
                "can_do": False,
                "lesson": result.get("reason"),
                "steps": ["Do not practice this by handing it to another company."],
                "wrapper_used": False,
            })
            continue
        rows.append({
            "task": task,
            "status": "needs_practice",
            "can_do": False,
            "lesson": "Practice this with Buddy's own code on a new example. A wrapper is optional and is not the lesson.",
            "steps": list(PRACTICE),
            "wrapper_used": False,
        })
    gaps = [row["task"] for row in rows if row["status"] == "needs_practice"]
    tested = sweep(gaps, models or []) if gaps else {"tasks": [], "tested_all": False, "called": False}
    by_task = {row["task"]: row for row in tested.get("tasks") or []}
    for row in rows:
        winner = by_task.get(row["task"])
        if not winner:
            continue
        row["best_model"] = winner.get("picked")
        row["best_score"] = winner.get("score")
        row["tested"] = winner.get("tested") is True
        row["called"] = False
    return {
        "asked": len(rows),
        "known": sum(1 for row in rows if row["status"] == "known"),
        "needs_practice": sum(1 for row in rows if row["status"] == "needs_practice"),
        "refused": sum(1 for row in rows if row["status"] == "refused"),
        "weights_trained": False,
        "called": False,
        "wrapper_needed": False,
        "tested_all_gaps": tested.get("tested_all") is True,
        "rows": rows,
    }


if __name__ == "__main__":
    models = [
        {"name": "open-coder", "source": "huggingface", "added_by_user": True, "free": True, "trials": {"book a flight": 80, "diagnose a patient": 10}},
        {"name": "paid-coder", "source": "frontier", "added_by_user": True, "free": False, "trials": {"book a flight": 80, "diagnose a patient": 40}},
    ]
    report = build(models=models)
    assert report["weights_trained"] is False and report["called"] is False and report["wrapper_needed"] is False
    assert report["known"] >= 3 and report["needs_practice"] >= 1 and report["refused"] >= 1
    flight = next(row for row in report["rows"] if row["task"] == "book a flight")
    assert flight["status"] == "needs_practice" and flight["best_model"] == "open-coder" and flight["called"] is False
    assert len(flight["steps"]) == 5
    print(json.dumps({"known": report["known"], "needs_practice": report["needs_practice"], "refused": report["refused"], "trained": False}))
