#!/usr/bin/env python3
"""Turn a user's idea and their own notes into a plan. Do not claim the thing was built."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOLEN = ("copy the course", "download the lessons", "scrape codecademy", "scrape the course")
KINDS = {
    "game": "vibe-game-builder.html",
    "simulation": "vibe-game-builder.html",
    "music": "music-creator.html",
    "video": "studio.html",
    "software": "codelab.html",
    "school": "train-own.html",
    "course": "train-own.html",
    "hardware": "",
    "invention": "",
}


def _kind(text: str) -> str:
    lowered = text.lower()
    for name in ("simulation", "game", "music", "video", "hardware", "invention", "school", "course", "software"):
        if name in lowered:
            return name
    return "software"


def idea(text: str, notes: list[str] | None = None) -> dict:
    words = " ".join((text or "").split())
    own = [" ".join(note.split()) for note in (notes or []) if len(" ".join(note.split())) >= 20]
    blob = (words + " " + " ".join(own)).lower()
    refused = {"accepted": False, "built": False, "learned": False, "stores_other_users_data": False}
    if any(phrase in blob for phrase in STOLEN):
        return {**refused, "reason": "Do not copy a course. Paste notes you wrote."}
    if len(words) < 8:
        return {**refused, "reason": "Describe the idea in a sentence."}
    kind = _kind(words)
    page = KINDS[kind]
    if page and not (ROOT / "website" / page).is_file():
        page = ""
    learned = len(own) >= 2
    return {
        "accepted": True,
        "kind": kind,
        "page": page,
        "built": False,
        "learned": learned,
        "stores_other_users_data": False,
        "course": {"name": "Codecademy", "href": "https://www.codecademy.com/", "copied": False},
        "reason": "This is a plan. The game, song, video, device, or program was not created. Codecademy lessons are not stored here. Only notes you paste are used.",
    }


if __name__ == "__main__":
    game = idea("Build a small sorting game", ["I practiced loops in my own course notes today.", "I wrote a new example that was not in the lesson."])
    assert game["accepted"] and game["built"] is False and game["kind"] == "game" and game["learned"] is True
    assert idea("copy the course and scrape codecademy lessons now", [])["accepted"] is False
    assert idea("study my biology course", ["Only one note is long enough here."])["learned"] is False
    assert idea("design a hardware invention for a sensor", [])["page"] == ""
    print(json.dumps({"built": False, "learned": game["learned"], "kind": game["kind"]}))
