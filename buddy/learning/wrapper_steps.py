#!/usr/bin/env python3
"""One wrapper per bootcamp step, until that user's own model is trained."""
from __future__ import annotations

import json

STEPS = ("lesson", "practice", "sandbox", "transfer", "score", "remediate", "regression", "evidence")
SOURCES = {"huggingface", "github", "frontier"}


def assign(choices: dict, own_ready: dict | None = None) -> dict:
    ready = own_ready or {}
    rows = []
    for step in STEPS:
        if ready.get(step) is True:
            rows.append({"step": step, "model": "your model", "wrapper": False, "called": False})
            continue
        choice = choices.get(step) or {}
        name = " ".join(str(choice.get("name") or "").split())
        if choice.get("added_by_user") is True and choice.get("source") in SOURCES and name:
            rows.append({"step": step, "model": name, "source": choice["source"], "wrapper": True, "called": False})
        else:
            rows.append({"step": step, "model": "Buddy's own code", "wrapper": False, "called": False})
    return {"steps": rows, "trained": False, "tested": False, "same_for_every_user": False}


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
    made = assign({
        "lesson": {"name": "open-teacher", "source": "huggingface", "added_by_user": True},
        "score": {"name": "not-added", "source": "github", "added_by_user": False},
    }, {"practice": True})
    by_step = {row["step"]: row for row in made["steps"]}
    assert by_step["lesson"]["model"] == "open-teacher" and by_step["lesson"]["called"] is False
    assert by_step["practice"]["model"] == "your model"
    assert by_step["score"]["model"] == "Buddy's own code"
    assert by_step["sandbox"]["model"] != by_step["lesson"]["model"]
    assert made["trained"] is False and made["tested"] is False
    assert rank("lesson", [])["best"] is None
    assert rank("lesson", [{"name": "open-teacher", "score": 80, "ran": True}])["best"] == "open-teacher"
    print(json.dumps({"steps": len(made["steps"]), "tested": False}))
