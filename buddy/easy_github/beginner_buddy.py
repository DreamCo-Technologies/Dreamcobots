#!/usr/bin/env python3
"""Beginner Buddy — 200 coded skills that answer in common words."""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
HERE = Path(__file__).resolve().parent

def load_skills() -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    full = HERE / "beginner_skills.json"
    if full.exists():
        skills.extend(json.loads(full.read_text(encoding="utf-8")).get("skills") or [])
    for path in sorted(HERE.glob("skills_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        skills.extend(payload.get("skills") or [])
    # de-dupe by id, keep last
    by_id = {}
    for s in skills:
        if s.get("id"):
            by_id[s["id"]] = s
    return [by_id[k] for k in sorted(by_id)]

def score_skill(skill: dict[str, Any], text: str) -> int:
    t = text.lower().strip()
    score = 0
    title = str(skill.get("title") or "").lower()
    if title and title in t:
        score += 5
    for trig in skill.get("triggers") or []:
        trig = str(trig).lower()
        if trig and trig in t:
            score += 3 if len(trig) > 3 else 2
    return score

def match(text: str, limit: int = 3) -> list[dict[str, Any]]:
    scored = [(score_skill(s, text), s) for s in load_skills()]
    scored = [x for x in scored if x[0]]
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [s for _, s in scored[:limit]]

def run_skill(skill: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "id": skill["id"], "title": skill["title"], "kind": skill["kind"],
        "you_said": text, "buddy_says": skill["reply"],
        "steps": list(skill.get("steps") or []),
        "optional_command": skill.get("command"),
        "needs_your_yes": bool(skill.get("ask_yes")),
        "did_change_github": False,
        "note": "I show the next step. I do not send, delete, spend, or publish unless you say yes.",
    }

def say(text: str) -> dict[str, Any]:
    hits = match(text)
    if not hits:
        fallback = {"id":"bf000","title":"help","kind":"coach",
                    "reply":"Try: hi, show the map, save my work, what's broken, or plain words please.",
                    "steps":["Open START_HERE.md"],"command":None,"ask_yes":False}
        return run_skill(fallback, text)
    result = run_skill(hits[0], text)
    result["other_matches"] = [{"id":h["id"],"title":h["title"]} for h in hits[1:]]
    return result

def list_by_kind(kind: str | None = None):
    skills = load_skills()
    if kind:
        skills = [s for s in skills if s.get("kind")==kind]
    return [{"id":s["id"],"title":s["title"],"kind":s["kind"]} for s in skills]

def first_run():
    order = ["new","map","save my work","what's broken","plain words please"]
    steps = [say(item) for item in order]
    return {"tour":"first ten minutes","skills_used":[s["id"] for s in steps],
            "buddy_says":"Start here: you are new, here is the map, then a safe save, then tickets.",
            "steps":steps,"needs_your_yes":True}

def main(argv):
    if not argv or argv[0] in {"help","-h","--help"}:
        print("python3 beginner_buddy.py say \"i'm new\" | tour | count | list")
        return 0
    if argv[0]=="count":
        print(json.dumps({"count":len(load_skills())},indent=2)); return 0
    if argv[0]=="list":
        print(json.dumps(list_by_kind(argv[1] if len(argv)>1 else None),indent=2)); return 0
    if argv[0]=="tour":
        print(json.dumps(first_run(),indent=2)); return 0
    if argv[0]=="say":
        print(json.dumps(say(" ".join(argv[1:]) or "help"),indent=2)); return 0
    print("help"); return 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
