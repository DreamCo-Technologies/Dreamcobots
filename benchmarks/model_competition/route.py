"""Task router. A model is eligible only with a measured score.

Sources can be open source, GitHub, frontier, or open weight. No weights are
downloaded here, and a missing score does not get a guess.
"""

from __future__ import annotations

import json
from pathlib import Path

SOURCES = ["open-source", "github", "frontier", "open-weight", "hugging-face"]
ROOT = Path(__file__).resolve().parents[2]


def register(name: str, source: str, task: str, quality: float, efficiency: float) -> dict:
    if source not in SOURCES:
        raise ValueError(f"unknown source: {source}")
    if not 0 <= quality <= 1 or not 0 <= efficiency <= 1:
        raise ValueError("scores must be measured between 0 and 1")
    return {"name": name, "source": source, "task": task, "quality": quality, "efficiency": efficiency, "weights_downloaded": False}


def route(task: str, models: list[dict]) -> dict:
    eligible = [row for row in models if row["task"] == task]
    if not eligible:
        return {"task": task, "model": None, "reason": "no measured score for this task"}
    winner = max(eligible, key=lambda row: (row["quality"], row["efficiency"], row["name"]))
    return {"task": task, "model": winner["name"], "source": winner["source"], "quality": winner["quality"], "efficiency": winner["efficiency"], "guessed": False}


def main() -> int:
    models = [register("example-a", "open-weight", "summarize", 0.8, 0.7), register("example-b", "github", "summarize", 0.6, 0.9)]
    report = {"sources": SOURCES, "route": route("summarize", models), "weights_downloaded": False}
    path = ROOT / "reports" / "MODEL_TASK_ROUTE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["route"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
