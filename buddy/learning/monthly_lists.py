#!/usr/bin/env python3
"""Refresh the shared lists once a month. A plugin is a study route, not a training run."""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {"huggingface", "github", "frontier"}
PLUGINS = (
    {"kind": "grok", "name": "grok-research", "path": ".github/agents/grok-research.agent.md", "use": "Study a new task from the files already in the repository."},
    {"kind": "grok", "name": "grok-safety-gate", "path": ".github/agents/grok-safety-gate.agent.md", "use": "Stop a task that would send mail, move money, or give medical or legal advice."},
    {"kind": "grok", "name": "grok-repo-scanner", "path": ".github/agents/grok-repo-scanner.agent.md", "use": "Look through the repository for a local way to practice the task."},
    {"kind": "github", "name": "Benchmark lessons daily", "path": ".github/workflows/benchmark-lessons-daily.yml", "use": "Rerun the lesson for every benchmark. A lesson is not a score."},
    {"kind": "github", "name": "System scan hourly", "path": ".github/workflows/system-scan-hourly.yml", "use": "Count the routes and the lessons. It does not open an issue."},
    {"kind": "github", "name": "Buddy learning proof", "path": ".github/workflows/buddy-learning-proof.yml", "use": "Run the learning checks that already exist."},
)
UNSAFE = ("email", "charge", "card", "flight", "patient", "lawsuit", "robot", "trade", "stock")


def pick(name: str, source: str, shared: bool = False) -> dict:
    clean = " ".join((name or "").split())
    if source not in SOURCES or len(clean) < 2:
        return {"accepted": False, "called": False, "reason": "Name your model and pick Hugging Face, GitHub, or frontier."}
    return {
        "accepted": True,
        "name": clean,
        "source": source,
        "shared": bool(shared),
        "called": False,
        "weights_trained": False,
        "reason": "Saved for you. It is shared only if you said so. Buddy did not call it.",
    }


def route_for(task: str) -> dict:
    text = task.lower()
    plugin = PLUGINS[1] if any(word in text for word in UNSAFE) else PLUGINS[0]
    return {"task": task, "plugin": plugin["name"], "kind": plugin["kind"], "use": plugin["use"], "trained": False}


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refresh() -> dict:
    school = _load("school_monthly", "buddy/learning/school.py").run(ROOT / "config")
    practice = _load("self_train_monthly", "buddy/learning/self_train.py").learn()
    failed = [route_for(row["task"]) for row in practice["rows"] if row["can_do"] is False]
    missing = [row["path"] for row in PLUGINS if not (ROOT / row["path"]).is_file()]
    if missing:
        raise RuntimeError("Missing plugin file: " + ", ".join(missing))
    return {
        "refreshed_on": date.today().isoformat(),
        "cadence": "monthly",
        "resources": school["own_versions"],
        "catalog_rows": school["catalog_rows"],
        "missing_ranges": school["missing_catalog_ranges"],
        "needs_practice": practice["needs_practice"],
        "failed_routes": failed,
        "plugins": list(PLUGINS),
        "weights_trained": False,
        "plugins_called": False,
    }


if __name__ == "__main__":
    chosen = pick("my-open-model", "huggingface", False)
    assert chosen["accepted"] is True and chosen["shared"] is False and chosen["called"] is False
    assert pick("", "huggingface")["accepted"] is False
    mail = route_for("send the private email")
    assert mail["plugin"] == "grok-safety-gate" and mail["trained"] is False
    report = refresh()
    assert report["weights_trained"] is False and report["plugins_called"] is False
    assert report["resources"] == 600 and report["needs_practice"] >= 1
    out = ROOT / "website/data/monthly-lists.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"resources": report["resources"], "practice": report["needs_practice"], "plugins_called": False}))
