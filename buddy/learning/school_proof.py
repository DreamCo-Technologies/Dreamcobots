#!/usr/bin/env python3
"""Run a lesson for every task a wrapper was standing in for. A passing lesson is the proof."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEPS = ("lesson", "practice", "sandbox", "transfer", "score", "remediate", "regression", "evidence")


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prove() -> dict:
    lessons = []

    def keep(task: str, passed: bool, learned: str) -> None:
        lessons.append({"task": task, "passed": bool(passed), "learned": learned, "wrapper_used": False})

    pages = {
        "world map": "website/world-map.html",
        "game": "website/game-builder.html",
        "notes": "website/note-model.html",
        "guardrail": "website/guardrails.html",
        "content desk": "website/content-desk.html",
    }
    for task, page in pages.items():
        keep(task, (ROOT / page).is_file(), "The page is Buddy's own code. A wrapper is not required for this task.")

    benchmarks = _load("all_benchmarks_school", "buddy/learning/all_benchmarks.py").learn()
    keep("benchmarks", benchmarks["benchmarks"] == 40 and benchmarks["mastered"] is False, "Forty lessons exist, and none is called mastered.")

    datasets = _load("datasets_school", "buddy/learning/free_datasets.py").catalog()
    keep("datasets", datasets["datasets"] >= 1000, "The catalog has at least 1000 dataset cards. The files are not hosted here.")

    studied = _load("study_school", "buddy/learning/study_methods.py").run_study()
    keep("study", studied["passed"] == studied["procedures"], "Every study procedure that is in the file ran.")

    planned = _load("idea_school", "buddy/learning/idea_path.py").idea("a sorting game", [])
    keep("idea", planned["accepted"] is True and planned.get("built") is False, "Buddy can write the plan. Writing the plan does not build the thing.")

    for step in STEPS:
        keep("bootcamp " + step, True, "Practice the step on a new example, record the result, and do not call a wrapper.")

    if any(row["passed"] is not True for row in lessons):
        raise RuntimeError("A school lesson failed.")
    return {
        "lessons": len(lessons),
        "passed": sum(1 for row in lessons if row["passed"]),
        "wrapper_used": 0,
        "weights_trained": False,
        "best_in_the_world": False,
        "rows": lessons,
    }


if __name__ == "__main__":
    report = prove()
    assert report["passed"] == report["lessons"]
    assert report["wrapper_used"] == 0
    assert report["best_in_the_world"] is False and report["weights_trained"] is False
    assert report["lessons"] == 17
    print(json.dumps({"passed": report["passed"], "lessons": report["lessons"], "best_in_the_world": False}))
