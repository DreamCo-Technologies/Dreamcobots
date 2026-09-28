#!/usr/bin/env python3
"""Look up models, record a score only when a test exists, and show what the vision still lacks."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def models() -> list[dict]:
    lab = json.loads((ROOT / "config/generated/buddy_open_model_coding_lab.json").read_text(encoding="utf-8"))
    study = json.loads((ROOT / "website/data/weight-study.json").read_text(encoding="utf-8"))
    rows = []
    for row in lab["frontier_references"]:
        rows.append({"id": row["id"], "label": row["label"], "access": "frontier", "source": row["official_source"], "scored": False, "score": None})
    for row in lab["model_families"]:
        rows.append({"id": row["id"], "label": row["label"], "access": row["access"], "source": row["official_source"], "scored": False, "score": None})
    for row in study["models"]:
        rows.append({"id": row["repo"], "label": row["repo"], "access": row["access"], "source": "https://huggingface.co/" + row["repo"], "scored": False, "score": None})
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Two models share an id.")
    return rows


def pick(task: str, step: str, choice: str | None = None, scores: list[dict] | None = None) -> dict:
    known = {row["id"]: row for row in models()}
    text = " ".join((task or "").split())
    if len(text) < 2 or not step:
        raise ValueError("Name the task and the step.")
    evidence = [row for row in scores or [] if row.get("task") == text and row.get("step") == step and row.get("scored") is True and isinstance(row.get("score"), (int, float))]
    if choice in known:
        return {"task": text, "step": step, "model": choice, "by": "user", "called": False, "scored": False}
    if evidence:
        winner = max(evidence, key=lambda row: row["score"])
        return {"task": text, "step": step, "model": winner["model"], "by": "recorded score", "called": False, "scored": True, "score": winner["score"]}
    return {"task": text, "step": step, "model": None, "by": "none", "called": False, "scored": False, "reason": "No test score is recorded for this step. A lookup is not a score."}


def train_from_wrappers() -> dict:
    spec = importlib.util.spec_from_file_location("self_train_lab", ROOT / "buddy/learning/self_train.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.learn()
    lessons = [{"task": row["task"], "lesson": row["lesson"], "weights_trained": False} for row in report["rows"] if row["can_do"] is False]
    return {"lessons": len(lessons), "weights_trained": False, "rows": lessons}


def scan() -> dict:
    bots = len(list((ROOT / "App_bots").glob("*.json")))
    resources = len(list((ROOT / "config").glob("buddy-study-resources-*.json")))
    return {
        "bot_files": bots,
        "resource_files": resources,
        "resource_target": 1000,
        "models": len(models()),
        "scored_models": 0,
        "missing_resource_ranges": ["301-400", "601-1000"],
        "fits_all_vision": False,
        "weights_trained": False,
        "reason": "Folders and bots were counted. A count is not mastery, and no model was tested.",
    }


def pull_request(title: str, files: list[str]) -> dict:
    clean = " ".join((title or "").split())
    if len(clean) < 8 or not files:
        return {"opened": False, "reason": "A pull request needs a title and at least one file."}
    return {"opened": False, "title": clean, "files": files, "reason": "The request is ready to open. This process did not open it."}


if __name__ == "__main__":
    found = models()
    assert any(row["access"] == "frontier" for row in found)
    assert any(row["access"] == "open_source" for row in found)
    assert all(row["scored"] is False for row in found)
    assert pick("write code", "lesson")["model"] is None
    assert pick("write code", "lesson", choice=found[0]["id"])["by"] == "user"
    scored = pick("write code", "lesson", scores=[{"task": "write code", "step": "lesson", "model": "qwen-coder", "score": 80, "scored": True}])
    assert scored["model"] == "qwen-coder" and scored["scored"] is True
    lessons = train_from_wrappers()
    assert lessons["weights_trained"] is False and lessons["lessons"] >= 1
    report = scan()
    assert report["fits_all_vision"] is False and report["scored_models"] == 0
    assert pull_request("Add a lesson", ["buddy/learning/model_lab.py"])["opened"] is False
    out = ROOT / "website/data/model-lab.json"
    out.write_text(json.dumps({"models": found, "scan": report, "wrapper_lessons": lessons, "scored_models": 0}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"models": len(found), "bots": report["bot_files"], "scored": 0, "fits": False}))
