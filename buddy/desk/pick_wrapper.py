#!/usr/bin/env python3
"""Pick the best approved model by testing all of them. Do not call it, and do not require it."""
from __future__ import annotations

import json

from buddy.desk.test_models import best, sweep

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
        if text not in names and not item.get("answers") and not item.get("trials"):
            continue
        usable.append(item)
    tested = [item for item in usable if item.get("answers") or item.get("trials")]
    if tested:
        picked = best(text, tested)
        picked["used_wrapper"] = False
        picked["wrapper_needed"] = False
        picked["optional"] = True
        picked["called"] = False
        if picked.get("picked"):
            picked["reason"] = "Best score after testing every approved model on this task. Buddy did not call it."
        return picked
    if not usable:
        return {"picked": None, "used_wrapper": False, "wrapper_needed": False, "called": False, "tested": False, "reason": "No wrapper you added covers this task. Buddy uses its own code."}
    best_quality = max(item["quality"] for item in usable)
    tied = [item for item in usable if item["quality"] == best_quality]
    free = [item for item in tied if item.get("free") is True]
    winner = free[0] if free else tied[0]
    return {
        "picked": winner["name"],
        "source": winner["source"],
        "free": winner.get("free") is True,
        "quality": best_quality,
        "used_wrapper": False,
        "wrapper_needed": False,
        "optional": True,
        "tested": False,
        "called": False,
        "reason": "Recorded quality only. This is not a test of every model. Buddy did not call it.",
    }


def offer(task: str, wrappers: list[dict] | None = None, use_wrapper: bool = False) -> dict:
    """Always name the tested winner. use_wrapper only marks the extra option."""
    picked = choose(task, wrappers or [])
    picked["used_wrapper"] = False
    picked["wrapper_needed"] = False
    picked["use_wrapper"] = use_wrapper is True
    if use_wrapper is not True:
        picked["reason"] = "Best approved model is recorded. Buddy still uses its own code unless you opt in."
    return picked


def across(task: str, boards: list[dict]) -> dict:
    """Best shared model for a task, no matter which user published it."""
    shared = []
    for board in boards or []:
        owner = " ".join(str(board.get("user") or "").split()) or "unknown"
        for item in board.get("models") or []:
            if item.get("shared") is not True and item.get("approved") is not True:
                continue
            shared.append({**item, "added_by_user": True, "shared_by": owner})
    if any(item.get("answers") or item.get("trials") for item in shared):
        picked = best(task, shared)
    else:
        picked = choose(task, shared)
    picked["from_all_shared_users"] = True
    picked["private_models_seen"] = False
    picked["used_wrapper"] = False
    picked["wrapper_needed"] = False
    if picked.get("picked"):
        owner = next((item["shared_by"] for item in shared if item["name"] == picked["picked"]), None)
        if owner:
            picked["shared_by"] = owner
        picked["reason"] = "Best score among models users approved and shared. A private list is not included. Buddy did not call it."
    else:
        picked["reason"] = "No shared model covers this task. Buddy uses its own code."
    return picked


def for_tasks(tasks: list[str], wrappers: list[dict], expects: dict | None = None) -> dict:
    approved = [item for item in wrappers or [] if item.get("added_by_user") is True or item.get("approved") is True]
    report = sweep(tasks, approved, expects)
    report["wrapper_needed"] = False
    report["called"] = False
    return report


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
    assert code["picked"] == "open-coder" and code["free"] is True and code["called"] is False and code["used_wrapper"] is False and code["wrapper_needed"] is False
    world = choose("world map", wrappers)
    assert world["picked"] == "map-maker"
    missing = choose("send email", wrappers)
    assert missing["used_wrapper"] is False and missing["picked"] is None
    tested = for_tasks(
        ["write code", "world map"],
        [
            {"name": "paid-coder", "source": "frontier", "added_by_user": True, "free": False, "answers": {"write code": "print(1)", "world map": "no"}},
            {"name": "open-coder", "source": "huggingface", "added_by_user": True, "free": True, "answers": {"write code": "print(1)", "world map": "map"}},
        ],
        {"write code": "print(1)", "world map": "map"},
    )
    by_task = {row["task"]: row for row in tested["tasks"]}
    assert tested["tested_all"] is True and by_task["write code"]["picked"] == "open-coder" and by_task["world map"]["picked"] == "open-coder"
    boards = [
        {"user": "ada", "models": [{"name": "ada-coder", "source": "huggingface", "tasks": ["write code"], "quality": 70, "free": True, "shared": True}]},
        {"user": "bo", "models": [
            {"name": "bo-coder", "source": "github", "tasks": ["write code"], "quality": 90, "free": False, "shared": True},
            {"name": "bo-private", "source": "huggingface", "tasks": ["write code"], "quality": 99, "free": True, "shared": False},
        ]},
    ]
    shared = across("write code", boards)
    assert shared["picked"] == "bo-coder" and shared["called"] is False and shared["used_wrapper"] is False and shared["private_models_seen"] is False
    print(json.dumps({"code": code["picked"], "tested_all": tested["tested_all"], "shared": shared["picked"], "called": False}))
