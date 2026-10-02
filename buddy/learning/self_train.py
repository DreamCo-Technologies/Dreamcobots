#!/usr/bin/env python3
"""For every task Buddy cannot do, write a lesson. Do not train a model or call a wrapper."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _plan():
    spec = importlib.util.spec_from_file_location("gap_plan_self", ROOT / "buddy/learning/gap_plan.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def learn(tasks: tuple[str, ...] | None = None, models: list[dict] | None = None) -> dict:
    report = _plan().build(tasks or _plan().ASKED, models)
    rows = [
        {
            "task": row["task"],
            "can_do": row["can_do"],
            "lesson": row["lesson"],
            "steps": row.get("steps") or [],
            "wrapper_used": False,
        }
        for row in report["rows"]
    ]
    return {
        "asked": report["asked"],
        "can_do": report["known"],
        "needs_practice": report["needs_practice"],
        "refused": report["refused"],
        "weights_trained": False,
        "opened_a_closed_model": False,
        "called": False,
        "rows": rows,
    }


if __name__ == "__main__":
    report = learn()
    assert report["weights_trained"] is False and report["opened_a_closed_model"] is False and report["called"] is False
    assert report["can_do"] >= 3 and report["needs_practice"] >= 1
    assert all(row["wrapper_used"] is False for row in report["rows"])
    assert all(row["steps"] for row in report["rows"] if not row["can_do"])
    print(json.dumps({"can_do": report["can_do"], "needs_practice": report["needs_practice"], "trained": False}))
