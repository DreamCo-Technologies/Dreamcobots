#!/usr/bin/env python3
"""Small, honest check for the beginner router. Not a world-ranking model."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "easy_github"))
from beginner_buddy import say

CASES = [
    ("i'm new", "map"),
    ("save my work", "save"),
    ("what's broken", "ticket"),
    ("plain words please", "ticket"),
    ("permission denied", "password"),
    ("open a ticket", "expected"),
    ("change request", "change request"),
    ("robot check", "automatic"),
    ("hide a secret", "password"),
    ("where is memory stored", "memory"),
    ("old bot plan", "plan"),
    ("huggingface card", "model card"),
]

def main() -> int:
    hits = 0
    rows = []
    for text, needle in CASES:
        out = say(text)
        blob = (out["buddy_says"] + " " + out["title"]).lower()
        ok = needle in blob and out["did_change_github"] is False
        hits += int(ok)
        rows.append({"prompt": text, "needle": needle, "id": out["id"], "ok": ok})
    report = {
        "name": "dreamco-beginner-router",
        "what_this_is": "A word matcher over 200 written replies.",
        "what_this_is_not": "A Hugging Face leaderboard model.",
        "cases": len(CASES),
        "correct": hits,
        "score": round(hits / len(CASES), 3),
        "rows": rows,
    }
    print(json.dumps(report, indent=2))
    return 0 if hits == len(CASES) else 1

if __name__ == "__main__":
    raise SystemExit(main())
