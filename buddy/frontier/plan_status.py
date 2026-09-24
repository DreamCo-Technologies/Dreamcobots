#!/usr/bin/env python3
"""The frontier build plan as code. A phase is met only when its check passes."""
from __future__ import annotations

import json

LOOP = [
    "Pin an evaluation and record a baseline.",
    "Run the smallest check that can pass or fail.",
    "Save the failure in plain words.",
    "Group failures that have the same cause.",
    "Write a small job to fix one cause.",
    "Apply that fix in code.",
    "Run the checks that already passed.",
    "Run a hidden test the fix did not study.",
    "Keep the fix only if the hidden test and the old checks pass.",
    "Save the evidence.",
]

PHASES = [
    {
        "id": "foundation",
        "plain": "Checks we can run",
        "code": "buddy/bench/scorecard.py",
        "met": True,
        "because": "The scorecard runs 13 gates and records the result.",
    },
    {
        "id": "coding",
        "plain": "Open and review a repository",
        "code": "buddy/desk/open_target.py",
        "met": False,
        "because": "Buddy can open a text file and flag a key. It does not patch a repository by itself.",
    },
    {
        "id": "breadth",
        "plain": "Science, math, and long plans",
        "code": "",
        "met": False,
        "because": "There is no exam for these, so the phase is not met.",
    },
    {
        "id": "native",
        "plain": "Do the task without another company's model",
        "code": "buddy/learning/native_capability_score.py",
        "met": False,
        "because": "The score function exists. No native model has passed a hidden exam.",
    },
    {
        "id": "frontier",
        "plain": "Evidence against a strong model",
        "code": "",
        "met": False,
        "because": "No frontier weights and no shared exam. Astra is not compared.",
    },
]

DOCUMENTS = [
    {"path": "docs/DREAMCO_MASTER_ROADMAP_2026.md", "state": "document", "why": "A roadmap. It is not a runner."},
    {"path": "docs/BUDDY_ACTIONS_MASTER_ROADMAP.md", "state": "document", "why": "A roadmap. The action pages are separate."},
    {"path": "docs/MEDIA_GAME_CAPABILITY_ROADMAP.md", "state": "document", "why": "The game lab code already validates a brief. The roadmap is not a game."},
    {"path": "buddy_os/actions/actions_page_implementation_roadmap.yaml", "state": "document", "why": "A list of pages, not a completed build."},
]
GUARDS = [
    "Do not train on the hidden test.",
    "Do not hard-code a benchmark answer.",
    "Do not delete a failing test to raise the score.",
    "Do not ship a live action from an unverified job.",
    "Do not put secrets in the evidence.",
    "Do not delete the original bot notes.",
]


def status() -> dict:
    met = [phase for phase in PHASES if phase["met"]]
    return {
        "loop": LOOP,
        "phases": PHASES,
        "guards": GUARDS,
        "documents": DOCUMENTS,
        "phases_met": len(met),
        "phases_total": len(PHASES),
        "frontier_ready": False,
        "astra_compared": False,
    }


if __name__ == "__main__":
    report = status()
    assert report["phases_total"] == 5
    assert report["frontier_ready"] is False
    assert report["astra_compared"] is False
    assert report["phases_met"] == 1
    assert len(report["guards"]) == 6
    assert len(report["documents"]) == 4
    print(json.dumps({"phases_met": report["phases_met"], "frontier_ready": False}))
