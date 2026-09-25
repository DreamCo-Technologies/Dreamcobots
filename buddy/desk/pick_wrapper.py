#!/usr/bin/env python3
"""Pick the best wrapper the user added. Do not call a model they did not add."""
from __future__ import annotations

import json

SOURCES = {"huggingface", "github", "frontier"}


def choose(task: str, wrappers: list[dict]) -> dict:
    text = " ".join((task or "").split()).lower()
    usable = []
    for item in wrappers or []:
        if item.get("added_by_user") is not True:
            continue
        if item.get("source") not in SOURCES:
            continue
        if not isinstance(item.get("quality"), (int, float)) or not 0 <= item["quality"] <= 100:
            continue
        names = [" ".join(str(name).split()).lower() for name in item.get("tasks") or []]
        if text not in names:
            continue
        usable.append(item)
    if not usable:
        return {"picked": None, "used_wrapper": False, "called": False, "reason": "No wrapper you added covers this task. Buddy uses its own code."}
    best = max(item["quality"] for item in usable)
    tied = [item for item in usable if item["quality"] == best]
    free = [item for item in tied if item.get("free") is True]
    winner = free[0] if free else tied[0]
    return {
        "picked": winner["name"],
        "source": winner["source"],
        "free": winner.get("free") is True,
        "quality": best,
        "used_wrapper": True,
        "called": False,
        "reason": "This is the best wrapper you added for this task. Buddy did not call it.",
    }


def route(tasks: list[str], wrappers: list[dict]) -> list[dict]:
    return [{"task": task, **choose(task, wrappers)} for task in tasks]


if __name__ == "__main__":
    wrappers = [
        {"name": "paid-coder", "source": "frontier", "tasks": ["write code"], "quality": 90, "free": False, "added_by_user": True},
        {"name": "open-coder", "source": "huggingface", "tasks": ["write code"], "quality": 90, "free": True, "added_by_user": True},
        {"name": "map-maker", "source": "github", "tasks": ["world map"], "quality": 70, "free": True, "added_by_user": True},
        {"name": "not-mine", "source": "huggingface", "tasks": ["write code"], "quality": 99, "free": True, "added_by_user": False},
    ]
    code = choose("write code", wrappers)
    assert code["picked"] == "open-coder" and code["free"] is True and code["called"] is False
    world = choose("world map", wrappers)
    assert world["picked"] == "map-maker"
    missing = choose("send email", wrappers)
    assert missing["used_wrapper"] is False and missing["picked"] is None
    print(json.dumps({"code": code["picked"], "map": world["picked"], "called": False}))
