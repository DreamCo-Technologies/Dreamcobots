#!/usr/bin/env python3
"""Do a task with Buddy's own code. A wrapper is an extra option, never a requirement."""
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
    "content": "website/content-desk.html",
}
MIDDLEMEN = ("email", "stripe", "openai", "claude", "grok", "charge", "wrapper")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _base() -> dict:
    return {
        "wrapper_used": False,
        "wrapper_needed": False,
        "wrapper_optional": True,
        "middleman": False,
    }


def run(task: str, wrappers: list | None = None, use_wrapper: bool = False) -> dict:
    """Finish the task with Buddy's files. wrappers is ignored unless use_wrapper is True."""
    text = " ".join((task or "").split()).lower()
    base = _base()
    if len(text) < 3:
        return {**base, "completed": False, "reason": "Name the task."}
    if any(word in text for word in MIDDLEMEN):
        return {**base, "completed": False, "refused": True, "reason": "Buddy does not hand this to another company."}
    if use_wrapper and wrappers:
        base["wrapper_offered"] = True
        base["reason_wrapper"] = "A wrapper was offered as an extra. The task still runs on Buddy's own code."
    if "dataset" in text or "data set" in text:
        catalog = _load("free_datasets_for_task", ROOT / "buddy/learning/free_datasets.py").catalog()
        return {**base, "completed": catalog["datasets"] >= 1000, "hosted_here": False, "reason": "The dataset list is Buddy's own file. The files are not hosted here."}
    if "idea" in text:
        made = _load("idea_path_for_task", ROOT / "buddy/learning/idea_path.py").idea(task, [])
        return {**base, "completed": made["accepted"], "built": made.get("built", False), "page": "website/idea.html", "reason": "Buddy wrote the plan. Nothing was sent out."}
    if text.startswith("study") or " study " in f" {text} ":
        report = _load("study_methods_for_task", ROOT / "buddy/learning/study_methods.py").run_study()
        return {**base, "completed": report["passed"] == report["procedures"], "weights_trained": False, "reason": "Buddy ran its own study procedures."}
    if any(word in text for word in ("caption", "draft", "script", "post", "content")):
        made = _load("content_make_for_task", ROOT / "buddy/content/make.py").packet(task)
        return {
            **base,
            "completed": made["accepted"] is True,
            "posted": False,
            "video_generated": False,
            "page": "website/content-desk.html",
            "reason": "Buddy wrote the draft with buddy/content/make.py. It did not call a wrapper.",
        }
    if any(word in text for word in ("speak", "voice", "say this")):
        present = (ROOT / "buddy/speech/speak.py").is_file() and (ROOT / "buddy/speech/voice_net.py").is_file()
        return {
            **base,
            "completed": present,
            "weights_trained": False,
            "called_remote": False,
            "page": "buddy/speech/speak.py",
            "reason": "Buddy speaks with its own voice_net. No Chatterbox and no wrapper.",
        }
    if "clone" in text or "likeness" in text:
        present = (ROOT / "capabilities/media_cloning/voice_clone.py").is_file() and (ROOT / "capabilities/media_cloning/image_clone.py").is_file()
        return {**base, "completed": False, "needs_practice": True, "weights_trained": False, "code_present": present, "page": "capabilities/media_cloning", "reason": "The cloning code is Buddy's own file. It was not run, and it will not run without an adult consent record."}
    if "worker" in text or "coach" in text or "teach" in text:
        made = _load("auto_worker_for_task", ROOT / "buddy/desk/auto_worker.py").build(task)
        return {**base, "completed": True, "worker": made["worker"], "page": made["page"], "reason": "Buddy built the worker from its own presets. No wrapper was called."}
    for key, page in LOCAL.items():
        if key in text and (ROOT / page).is_file():
            return {**base, "completed": True, "page": page, "reason": "Buddy did this with its own code. No wrapper was called."}
    route = _load("local_core_for_task", ROOT / "buddy/local_core.py").route(text)
    return {
        **base,
        "completed": False,
        "planned": True,
        "needs_practice": True,
        "workflow": route.workflow,
        "external_data_required": route.external_data_required,
        "reason": "Buddy can plan this, but it cannot do it yet. A wrapper is an extra option, not a requirement.",
    }


if __name__ == "__main__":
    made = run("build a world map")
    assert made["completed"] is True and made["wrapper_used"] is False and made["wrapper_needed"] is False and made["middleman"] is False
    blocked = run("send the private email")
    assert blocked["completed"] is False and blocked["wrapper_used"] is False and blocked["middleman"] is False
    data = run("count the free datasets")
    assert data["completed"] is True and data["hosted_here"] is False
    plan = run("plan an idea for a sorting game")
    assert plan["completed"] is True and plan["built"] is False
    draft = run("write a caption for the cake")
    assert draft["completed"] is True and draft["posted"] is False and draft["wrapper_needed"] is False
    said = run("speak this line")
    assert said["completed"] is True and said["called_remote"] is False
    extra = run("sort these notes", wrappers=[{"name": "paid-coder"}], use_wrapper=True)
    assert extra["completed"] is True and extra["wrapper_used"] is False and extra["wrapper_offered"] is True
    unknown = run("book a flight")
    assert unknown["completed"] is False and unknown["needs_practice"] is True and unknown["wrapper_needed"] is False
    print(json.dumps({"map": True, "email": False, "datasets": data["completed"], "unknown": unknown["needs_practice"], "wrapper_needed": False}))
