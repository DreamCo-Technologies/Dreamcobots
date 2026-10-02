#!/usr/bin/env python3
"""Name the build order. Do not move files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def status() -> dict:
    catalog = json.loads((ROOT / "website/data/original-bots.json").read_text(encoding="utf-8"))
    release = json.loads((ROOT / "website/data/command-center/release-readiness.json").read_text(encoding="utf-8"))
    health = json.loads((ROOT / "website/data/actions-health-report.json").read_text(encoding="utf-8"))["summary"]
    benchmarks = json.loads((ROOT / "website/data/benchmarks.json").read_text(encoding="utf-8"))
    markdown = len(list((ROOT / "bots").glob("*.md")))
    stages = [
        {
            "id": "use",
            "plain": "Use what already runs in the browser",
            "paths": ["website/", "buddy/desk/", "buddy/learning/note_model.py"],
            "met": True,
            "because": "The site, the local task runner, and the small note model are in the repository.",
        },
        {
            "id": "checks",
            "plain": "Local checks",
            "paths": ["buddy/bench/scorecard.py", "website/data/benchmarks.json"],
            "met": benchmarks.get("passed") == benchmarks.get("checks") and benchmarks.get("checks", 0) > 0,
            "because": f"The scorecard file records {benchmarks.get('passed')} of {benchmarks.get('checks')} gates.",
        },
        {
            "id": "bots",
            "plain": "Bot notes are not a live fleet",
            "paths": ["bots/", "original-bots/", "App_bots/", "website/data/original-bots.json"],
            "met": False,
            "because": f"{markdown} markdown bots and {catalog.get('count')} catalog bots. The readiness report marks 0 bots production ready.",
        },
        {
            "id": "actions",
            "plain": "Workflow files are not runtime proof",
            "paths": [".github/workflows/", "website/data/actions-health-report.json"],
            "met": health.get("runtime_passing_workflows", 0) > 0,
            "because": f"{health.get('static_passing_workflows')} workflows pass a static check. {health.get('runtime_unknown_workflows')} have no runtime result.",
        },
        {
            "id": "release",
            "plain": "The release gate",
            "paths": ["website/data/command-center/release-readiness.json", "tools/production_readiness_gate.py"],
            "met": release.get("production_ready") is True,
            "because": "production_ready is false. Run the three commands named in the release file.",
        },
        {
            "id": "frontier",
            "plain": "A frontier model",
            "paths": ["buddy/frontier/", "buddy/learning/frontier_path.py"],
            "met": False,
            "because": "No frontier weights and no hidden exam. This stage is not required to publish the site.",
        },
    ]
    return {"files_moved": False, "production_ready": False, "stages_met": sum(1 for stage in stages if stage["met"]), "stages": stages}


if __name__ == "__main__":
    made = status()
    assert made["files_moved"] is False
    assert made["production_ready"] is False
    assert made["stages_met"] == 2
    print(json.dumps({"met": made["stages_met"], "files_moved": False}))
