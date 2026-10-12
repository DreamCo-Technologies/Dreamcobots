"""Select a listed model for a task. Null metrics do not count as quality."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def select(task: str) -> dict:
    registry = json.loads((ROOT / "config" / "buddy-model-selection-registry.json").read_text())
    matches = [row for row in registry["models"] if task in row["task_types"]]
    if not matches:
        return {"task": task, "model": None, "reason": "no listed model", "weight_modification": False}
    return {"task": task, "model": matches[0]["id"], "reason": "first listed match; scores not measured", "weight_modification": False}


def main() -> int:
    report = {"selections": [select(task) for task in ["plan", "code", "deploy"]], "weight_modification": False}
    (ROOT / "reports" / "MODEL_SELECTION.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
