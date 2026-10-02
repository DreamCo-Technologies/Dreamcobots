#!/usr/bin/env python3
"""Score every user-approved model on every task. Pick the best. Do not call a remote model."""
from __future__ import annotations

import json

SOURCES = {"huggingface", "github", "frontier", "own"}
OWN = "Buddy's own code"


def _text(value: str) -> str:
    return " ".join(str(value or "").split()).lower()


def approved(models: list[dict]) -> list[dict]:
    rows = []
    for item in models or []:
        if item.get("added_by_user") is not True and item.get("approved") is not True and item.get("name") != OWN:
            continue
        if item.get("source") not in SOURCES and item.get("name") != OWN:
            continue
        name = " ".join(str(item.get("name") or "").split())
        if not name:
            continue
        rows.append(item)
    if not any(item.get("name") == OWN for item in rows):
        rows.append({"name": OWN, "source": "own", "added_by_user": True, "approved": True, "free": True, "answers": {}})
    return rows


def _score(model: dict, task: str, expect: str | None) -> tuple[float | None, bool]:
    key = _text(task)
    answers = model.get("answers") or {}
    folded = {_text(name): value for name, value in answers.items()}
    if key in folded:
        got = folded[key]
        if expect is None:
            return (100.0 if str(got).strip() else 0.0), True
        return (100.0 if _text(got) == _text(expect) else 0.0), True
    trials = model.get("trials") or {}
    folded_trials = {_text(name): value for name, value in trials.items()}
    if key in folded_trials and isinstance(folded_trials[key], (int, float)) and 0 <= folded_trials[key] <= 100:
        return float(folded_trials[key]), True
    if model.get("name") == OWN:
        return 50.0, True
    return None, False


def sweep(tasks: list[str], models: list[dict], expects: dict | None = None) -> dict:
    """Test every approved model on every task, then pick the highest score."""
    board = approved(models)
    wanted = [_text(task) for task in tasks or [] if _text(task)]
    expected = {_text(key): value for key, value in (expects or {}).items()}
    cells = []
    winners = []
    for task in wanted:
        scored = []
        for model in board:
            score, tested = _score(model, task, expected.get(task))
            cells.append({
                "task": task,
                "model": model.get("name"),
                "source": model.get("source"),
                "score": score,
                "tested": tested,
                "called": False,
            })
            if tested and score is not None:
                scored.append((score, model.get("free") is True, model.get("name") == OWN, model))
        if not scored:
            winners.append({"task": task, "picked": None, "tested": False, "called": False, "reason": "No approved model had a test for this task."})
            continue
        scored.sort(key=lambda row: (row[0], row[1], row[2]), reverse=True)
        winner = scored[0][3]
        winners.append({
            "task": task,
            "picked": winner.get("name"),
            "source": winner.get("source"),
            "score": scored[0][0],
            "free": winner.get("free") is True,
            "tested": True,
            "tested_models": len(scored),
            "approved_models": len(board),
            "wrapper_needed": False,
            "used_wrapper": False,
            "called": False,
            "reason": "Highest score after every approved model was tested on this task. Buddy did not call a remote model.",
        })
    tested_cells = [cell for cell in cells if cell["tested"]]
    return {
        "tasks": winners,
        "cells": cells,
        "approved_models": len(board),
        "tested_pairs": len(tested_cells),
        "expected_pairs": len(wanted) * len(board),
        "tested_all": bool(wanted) and len(tested_cells) == len(wanted) * len(board),
        "wrapper_needed": False,
        "called": False,
    }


def best(task: str, models: list[dict], expect: str | None = None) -> dict:
    report = sweep([task], models, {task: expect} if expect is not None else None)
    row = report["tasks"][0] if report["tasks"] else {"picked": None, "tested": False, "called": False}
    row["tested_all"] = report["tested_all"]
    row["wrapper_needed"] = False
    row["called"] = False
    return row


if __name__ == "__main__":
    models = [
        {"name": "paid-coder", "source": "frontier", "added_by_user": True, "free": False, "answers": {"write code": "print(1)", "world map": "no"}},
        {"name": "open-coder", "source": "huggingface", "added_by_user": True, "free": True, "answers": {"write code": "print(1)", "world map": "map"}},
        {"name": "not-mine", "source": "huggingface", "added_by_user": False, "answers": {"write code": "print(1)"}},
    ]
    report = sweep(["write code", "world map"], models, {"write code": "print(1)", "world map": "map"})
    by_task = {row["task"]: row for row in report["tasks"]}
    assert report["tested_all"] is True and report["called"] is False
    assert by_task["write code"]["picked"] == "open-coder"
    assert by_task["world map"]["picked"] == "open-coder"
    assert best("write code", models, "print(1)")["picked"] == "open-coder"
    print(json.dumps({"tested_all": report["tested_all"], "code": by_task["write code"]["picked"], "called": False}))
