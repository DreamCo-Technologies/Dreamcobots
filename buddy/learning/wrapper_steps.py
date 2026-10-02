#!/usr/bin/env python3
"""Each bootcamp step gets the model that won the test. Own code still does the work."""
from __future__ import annotations

import json

from buddy.desk.test_models import sweep

STEPS = ("lesson", "practice", "sandbox", "transfer", "score", "remediate", "regression", "evidence")
SOURCES = {"huggingface", "github", "frontier"}
OWN = "Buddy's own code"


def assign(choices: dict, own_ready: dict | None = None, models: list[dict] | None = None) -> dict:
    ready = own_ready or {}
    board = [item for item in models or [] if item.get("added_by_user") is True or item.get("approved") is True]
    report = sweep(list(STEPS), board) if board else {"tasks": [], "tested_all": False}
    winners = {row["task"]: row for row in report.get("tasks") or []}
    rows = []
    for step in STEPS:
        if ready.get(step) is True:
            rows.append({"step": step, "model": "your model", "wrapper": False, "wrapper_needed": False, "tested": True, "called": False})
            continue
        winner = winners.get(step) or {}
        if winner.get("picked") and winner.get("tested") is True:
            rows.append({
                "step": step,
                "model": winner["picked"],
                "source": winner.get("source"),
                "score": winner.get("score"),
                "wrapper": winner["picked"] != OWN,
                "wrapper_needed": False,
                "tested": True,
                "called": False,
            })
            continue
        choice = choices.get(step) or {}
        name = " ".join(str(choice.get("name") or "").split())
        opted_in = choice.get("use_wrapper") is True and choice.get("added_by_user") is True and choice.get("source") in SOURCES and name
        if opted_in:
            rows.append({"step": step, "model": name, "source": choice["source"], "wrapper": True, "wrapper_needed": False, "tested": False, "called": False})
        else:
            rows.append({"step": step, "model": OWN, "wrapper": False, "wrapper_needed": False, "tested": False, "called": False})
    return {
        "steps": rows,
        "trained": False,
        "tested": report.get("tested_all") is True,
        "tested_all": report.get("tested_all") is True,
        "same_for_every_user": False,
        "wrapper_needed": False,
        "called": False,
    }


def rank(step: str, notes: list[dict]) -> dict:
    if step not in STEPS:
        raise ValueError("Unknown bootcamp step.")
    usable = [note for note in notes or [] if note.get("ran") is True and isinstance(note.get("score"), (int, float)) and 0 <= note["score"] <= 100 and note.get("name")]
    if not usable:
        return {"step": step, "best": None, "called": False, "reason": "No bootcamp result is recorded for this step."}
    best = max(note["score"] for note in usable)
    winner = next(note for note in usable if note["score"] == best)
    return {"step": step, "best": winner["name"], "score": best, "called": False, "reason": "Ranked from recorded results. Buddy did not call a model."}


if __name__ == "__main__":
    models = [
        {"name": "open-teacher", "source": "huggingface", "added_by_user": True, "free": True, "trials": {step: 90 for step in STEPS}},
        {"name": "paid-teacher", "source": "frontier", "added_by_user": True, "free": False, "trials": {step: 90 for step in STEPS}},
        {"name": "not-added", "source": "github", "added_by_user": False, "trials": {step: 99 for step in STEPS}},
    ]
    made = assign({}, {"practice": True}, models)
    by_step = {row["step"]: row for row in made["steps"]}
    assert made["tested_all"] is True and made["called"] is False and made["wrapper_needed"] is False
    assert by_step["lesson"]["model"] == "open-teacher" and by_step["lesson"]["tested"] is True
    assert by_step["practice"]["model"] == "your model"
    assert by_step["score"]["model"] == "open-teacher"
    plain = assign({"lesson": {"name": "open-teacher", "source": "huggingface", "added_by_user": True}})
    assert plain["steps"][0]["model"] == OWN and plain["tested_all"] is False
    assert rank("lesson", [])["best"] is None
    assert rank("lesson", [{"name": "open-teacher", "score": 80, "ran": True}])["best"] == "open-teacher"
    print(json.dumps({"steps": len(made["steps"]), "tested_all": made["tested_all"], "lesson": by_step["lesson"]["model"], "called": False}))
