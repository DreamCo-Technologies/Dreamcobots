"""Buildabot language choice.

The choice is the smallest compatible implementation for the task. It does not
rewrite the repo, and it does not claim one language is best for everything.
"""

from __future__ import annotations

import json
from pathlib import Path

CHOICES = {
    "pages": "html",
    "catalog": "python",
    "workflow": "javascript",
    "hot-loop": "c",
    "bot-file": "markdown",
}
ROOT = Path(__file__).resolve().parents[2]


def choose(task: str) -> dict:
    language = CHOICES.get(task)
    if language is None:
        raise ValueError(f"unknown task: {task}")
    return {"task": task, "language": language, "rewritten": False, "compatible": True}


def main() -> int:
    report = {"choices": [choose(task) for task in CHOICES], "rewritten": False}
    path = ROOT / "reports" / "BUILDABOT_CHOICES.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tasks": len(report["choices"]), "rewritten": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
