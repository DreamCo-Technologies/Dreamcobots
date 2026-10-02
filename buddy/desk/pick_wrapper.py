#!/usr/bin/env python3
"""Offer a shared model as an extra. Do not call it, and do not require it."""
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
        return {"picked": None, "used_wrapper": False, "wrapper_needed": False, "called": False, "reason": "No wrapper you added covers this task. Buddy uses its own code."}
    best = max(item["quality"] for item in usable)
    tied = [item for item in usable if item["quality"] == best]
    free = [item for item in tied if item.get("free") is True]
    winner = free[0] if free else tied[0]
    return {
        "picked": winner["name"],
        "source": winner["source"],
        "free": winner.get("free") is True,
        "quality": best,
        "used_wrapper": False,
        "wrapper_needed": False,
        "optional": True,
        "called": False,
        "reason": "This wrapper is an extra option. Buddy did not call it and does not need it.",
    }


def offer(task: str, wrappers: list[dict] | None = None, use_wrapper: bool = False) -> dict:
    """Return a wrapper only when the caller opted in. Own code stays the path."""
    picked = choose(task, wrappers or [])
    if use_wrapper is not True:
        picked["picked"] = None
        picked["used_wrapper"] = False
        picked["reason"] = "Wrapper not requested. Buddy uses its own code."
    return picked


def across(task: str, boards: list[dict]) -> dict:
    """Best shared model for a task, no matter which user published it."""
    shared = []
    for board in boards or []:
        owner = " ".join(str(board.get("user") or "").split()) or "unknown"
        for item in board.get("models") or []:
            if item.get("shared") is not True:
                continue
            shared.append({**item, "added_by_user": True, "shared_by": owner})
    picked = choose(task, shared)
    picked["from_all_shared_users"] = True
    picked["private_models_seen"] = False
    picked["used_wrapper"] = False
    picked["wrapper_needed"] = False
    if picked["picked"]:
        owner = next(item["shared_by"] for item in shared if item["name"] == picked["picked"])
        picked["shared_by"] = owner
        picked["reason"] = "Highest recorded score among models users marked shared. Optional only. Buddy did not call it."
    else:
        picked["reason"] = "No shared model covers this task. Buddy uses its own code."
    return picked


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
    skipped = offer("write code", wrappers, use_wrapper=False)
    assert skipped["picked"] is None and skipped["wrapper_needed"] is False
    boards = [
        {"user": "ada", "models": [{"name": "ada-coder", "source": "huggingface", "tasks": ["write code"], "quality": 70, "free": True, "shared": True}]},
        {"user": "bo", "models": [
            {"name": "bo-coder", "source": "github", "tasks": ["write code"], "quality": 90, "free": False, "shared": True},
            {"name": "bo-private", "source": "huggingface", "tasks": ["write code"], "quality": 99, "free": True, "shared": False},
        ]},
    ]
    shared = across("write code", boards)
    assert shared["picked"] == "bo-coder" and shared["called"] is False and shared["used_wrapper"] is False and shared["private_models_seen"] is False
    print(json.dumps({"code": code["picked"], "shared": shared["picked"], "called": False, "wrapper_needed": False}))
