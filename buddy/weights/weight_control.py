#!/usr/bin/env python3
"""Weight-control sheet. Settings are real. Weight files are not on this site."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REFUSED = ("copy gpt", "copy claude", "distill gpt", "distill claude", "proprietary weights", "closed weights")


def load_settings(path: Path | None = None) -> list[dict]:
    source = path or (HERE / "settings.json")
    return json.loads(source.read_text(encoding="utf-8"))["settings"]


def sheet(overrides: dict | None = None, catalog: list[dict] | None = None) -> dict:
    catalog = catalog if catalog is not None else load_settings()
    overrides = overrides or {}
    unknown = [key for key in overrides if key not in {item["id"] for item in catalog}]
    if unknown:
        raise ValueError("unknown settings: " + ", ".join(unknown))
    if overrides.get("trust_remote_code") is True:
        raise ValueError("remote code stays off")
    values = {item["id"]: item["default"] for item in catalog}
    values.update(overrides)
    return {
        "goal": "Full control of your own weight files",
        "settings": len(catalog),
        "values": values,
        "weight_files_on_this_site": False,
        "applies_to_a_file": False,
        "reason": "The sheet is saved. It does not change a weight file, because no weight file is here.",
    }


def debug_target(kind: str, name: str, goal: str = "") -> dict:
    blob = f"{name} {goal}".lower()
    for phrase in REFUSED:
        if phrase in blob:
            return {"ok": False, "kind": kind, "reason": "Buddy will not debug by copying a closed model."}
    if not REPO.match((name or "").strip()):
        return {"ok": False, "kind": kind, "reason": "Use owner/name."}
    steps = [
        "Read the license before loading anything.",
        "Check that the id exists on GitHub or Hugging Face.",
        "Look for a config, a tokenizer, and a weight file name. Do not download the weights here.",
        "Refuse remote code.",
        "Run a small held-out check on a machine you control.",
        "Write down what failed. A missing file is not a trained model.",
    ]
    if kind == "repository":
        steps.insert(0, "Open the repository file list and the latest check results.")
    else:
        steps.insert(0, "Open the model card and the file list.")
    return {
        "ok": True,
        "kind": kind,
        "name": name.strip(),
        "runs_here": False,
        "steps": steps,
        "reason": "Debug plan ready. Buddy did not load the repository or the model.",
    }


if __name__ == "__main__":
    catalog = load_settings()
    made = sheet({}, catalog)
    assert made["settings"] >= 60 and made["weight_files_on_this_site"] is False
    try:
        sheet({"trust_remote_code": True}, catalog)
        raise SystemExit("remote code was allowed")
    except ValueError:
        pass
    assert debug_target("model", "org/model", "distill Claude")["ok"] is False
    plan = debug_target("repository", "DreamCo-Technologies/Dreamcobots")
    assert plan["ok"] and plan["runs_here"] is False
    print(json.dumps({"settings": made["settings"], "files": False}))
