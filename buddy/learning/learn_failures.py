#!/usr/bin/env python3
"""Learn from the actions page. Unknown is not a pass."""
from __future__ import annotations

import json


def learn(summary: dict) -> dict:
    unknown = int(summary.get("runtime_unknown_workflows") or 0)
    failed = int(summary.get("runtime_failing_workflows") or 0)
    static_fail = int(summary.get("static_failing_workflows") or 0)
    lessons = []
    if static_fail == 0:
        lessons.append("The static checks passed. A static pass is not a benchmark score.")
    if failed:
        lessons.append(f"{failed} runtime failures stay on the list. Do not hide them.")
    else:
        lessons.append("No runtime failure is recorded.")
    if unknown:
        lessons.append(f"{unknown} workflows have no runtime result. Unknown is not a pass and not mastery.")
    return {
        "mastered": False,
        "frontier_model": False,
        "year_end_mastery_of_every_benchmark": False,
        "lessons": lessons,
        "missing": [
            "A runtime result for each benchmark workflow.",
            "A weight file you are allowed to train.",
            "A hidden exam and a published score.",
            "No frontier comparison until that score exists.",
        ],
        "by_december_31_2026": "Get a real run for every benchmark check that can run without a secret. Leave the others unknown.",
    }


if __name__ == "__main__":
    report = learn({
        "runtime_unknown_workflows": 72,
        "runtime_failing_workflows": 0,
        "static_failing_workflows": 0,
    })
    assert report["mastered"] is False and report["frontier_model"] is False
    assert any("Unknown is not a pass" in line for line in report["lessons"])
    failed = learn({"runtime_unknown_workflows": 0, "runtime_failing_workflows": 3, "static_failing_workflows": 1})
    assert any("3 runtime failures" in line for line in failed["lessons"])
    print(json.dumps(report))
