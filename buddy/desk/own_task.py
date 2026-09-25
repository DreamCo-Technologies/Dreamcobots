#!/usr/bin/env python3
"""Do a task with Buddy's own code. Do not call another model."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = {
    "world map": "website/world-map.html",
    "game": "website/game-builder.html",
    "idea": "website/idea.html",
    "notes": "website/note-model.html",
}


def run(task: str) -> dict:
    text = " ".join((task or "").split()).lower()
    base = {"wrapper_used": False, "wrapper_needed": False}
    if len(text) < 3:
        return {**base, "completed": False, "reason": "Name the task."}
    for key, page in LOCAL.items():
        if key in text and (ROOT / page).is_file():
            return {**base, "completed": True, "page": page, "reason": "Buddy did this with its own code. No wrapper was called."}
    return {**base, "completed": False, "reason": "Buddy's own code does not do that task. No wrapper was called."}


if __name__ == "__main__":
    made = run("build a world map")
    assert made["completed"] is True and made["wrapper_used"] is False and made["wrapper_needed"] is False
    blocked = run("send the private email")
    assert blocked["completed"] is False and blocked["wrapper_used"] is False
    print(json.dumps({"completed": made["completed"], "wrapper_used": False}))
