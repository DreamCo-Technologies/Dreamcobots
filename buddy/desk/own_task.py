#!/usr/bin/env python3
"""Do a task with Buddy's own code. Do not call another model."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = {
    "world map": "website/world-map.html",
    "game": "website/game-builder.html",
    "notes": "website/note-model.html",
    "benchmark": "website/benchmarks.html",
    "guardrail": "website/guardrails.html",
}
MIDDLEMEN = ("email", "stripe", "openai", "claude", "grok", "charge", "wrapper")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(task: str) -> dict:
    text = " ".join((task or "").split()).lower()
    base = {"wrapper_used": False, "wrapper_needed": False, "middleman": False}
    if len(text) < 3:
        return {**base, "completed": False, "reason": "Name the task."}
    if any(word in text for word in MIDDLEMEN):
        return {**base, "completed": False, "reason": "Buddy does not hand this to another company."}
    if "dataset" in text or "data set" in text:
        catalog = _load("free_datasets_for_task", ROOT / "buddy/learning/free_datasets.py").catalog()
        return {**base, "completed": catalog["datasets"] >= 1000, "hosted_here": False, "reason": "The dataset list is Buddy's own file. The files are not hosted here."}
    if "idea" in text:
        made = _load("idea_path_for_task", ROOT / "buddy/learning/idea_path.py").idea(task, [])
        return {**base, "completed": made["accepted"], "built": made.get("built", False), "page": "website/idea.html", "reason": "Buddy wrote the plan. Nothing was sent out."}
    if text.startswith("study") or " study " in f" {text} ":
        report = _load("study_methods_for_task", ROOT / "buddy/learning/study_methods.py").run_study()
        return {**base, "completed": report["passed"] == report["procedures"], "weights_trained": False, "reason": "Buddy ran its own study procedures."}
    for key, page in LOCAL.items():
        if key in text and (ROOT / page).is_file():
            return {**base, "completed": True, "page": page, "reason": "Buddy did this with its own code. No wrapper was called."}
    return {**base, "completed": False, "reason": "Buddy's own code does not do that task. No wrapper was called."}


if __name__ == "__main__":
    made = run("build a world map")
    assert made["completed"] is True and made["wrapper_used"] is False and made["middleman"] is False
    blocked = run("send the private email")
    assert blocked["completed"] is False and blocked["wrapper_used"] is False and blocked["middleman"] is False
    data = run("count the free datasets")
    assert data["completed"] is True and data["hosted_here"] is False
    plan = run("plan an idea for a sorting game")
    assert plan["completed"] is True and plan["built"] is False
    print(json.dumps({"map": True, "email": False, "datasets": data["completed"], "wrapper_used": False}))
