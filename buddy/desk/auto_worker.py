#!/usr/bin/env python3
"""Build a worker for a task from the bots and personalities already on file."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = (
    ("game", "Games", "game-builder.html", "creative_partner"),
    ("map", "Maps", "world-map.html", "steady_operator"),
    ("guard", "Guardrails", "guardrails.html", "skeptical_analyst"),
    ("model", "Models", "model-lab.html", "friendly_nerd"),
    ("content", "Content", "content-desk.html", "storyteller"),
    ("teach", "Buddy", "buddy.html", "patient_teacher"),
    ("coach", "Buddy", "buddy.html", "no_nonsense_coach"),
)
FALLBACK = ("Buddy", "buddy.html", "straight_shooter")


def presets() -> list[dict]:
    data = json.loads((ROOT / "config/buddy-personality-presets.json").read_text(encoding="utf-8"))
    return [{"id": row["id"], "name": row["name"]} for row in data["presets"]]


def build(task: str, personality: str | None = None) -> dict:
    text = " ".join((task or "").split())
    if len(text) < 3:
        raise ValueError("Name the task.")
    known = {row["id"] for row in presets()}
    lowered = text.lower()
    worker, page, preset = FALLBACK
    for word, name, href, choice in ROUTES:
        if word in lowered:
            worker, page, preset = name, href, choice
            break
    chosen = personality if personality in known else preset
    if chosen not in known:
        raise RuntimeError("The personality preset is not in the file.")
    return {
        "task": text,
        "worker": worker,
        "page": page,
        "personality": chosen,
        "tuned": True,
        "weights_trained": False,
        "impersonates_a_person": False,
    }


if __name__ == "__main__":
    made = build("teach a sorting game")
    assert made["worker"] == "Games" and made["personality"] == "creative_partner"
    assert made["weights_trained"] is False and made["tuned"] is True
    coach = build("coach the lesson", "patient_teacher")
    assert coach["personality"] == "patient_teacher"
    out = ROOT / "website/data/worker-rules.json"
    out.write_text(json.dumps({"routes": [{"word": row[0], "worker": row[1], "page": row[2], "personality": row[3]} for row in ROUTES], "fallback": {"worker": FALLBACK[0], "page": FALLBACK[1], "personality": FALLBACK[2]}, "presets": presets(), "weights_trained": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"worker": made["worker"], "personality": made["personality"], "trained": False}))
