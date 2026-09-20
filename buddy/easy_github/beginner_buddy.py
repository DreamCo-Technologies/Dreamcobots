#!/usr/bin/env python3
"""Beginner Buddy — 200 coded skills that answer in common words."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILLS_PATH = HERE / "beginner_skills.json"


def load_catalog() -> dict[str, Any]:
    if SKILLS_PATH.exists():
        return json.loads(SKILLS_PATH.read_text(encoding="utf-8"))
    skills: list[dict[str, Any]] = []
    for path in (HERE / "skills_part1.json", HERE / "skills_part2.json"):
        if path.exists():
            skills.extend(json.loads(path.read_text(encoding="utf-8")).get("skills") or [])
    if not skills:
        raise FileNotFoundError("beginner skill files missing")
    return {"schema": "dreamco.beginner_buddy.skills.v1", "version": "1.0.0", "count": len(skills), "skills": skills}


def load_skills() -> list[dict[str, Any]]:
    return list(load_catalog().get("skills") or [])


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
    scored = []
    for skill in load_skills():
        s = score_skill(skill, text)
        if s:
            scored.append((s, skill))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [sk for _, sk in scored[:limit]]


def run_skill(skill: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "id": skill["id"],
        "title": skill["title"],
        "kind": skill["kind"],
        "you_said": text,
        "buddy_says": skill["reply"],
        "steps": list(skill.get("steps") or []),
        "optional_command": skill.get("command"),
        "needs_your_yes": bool(skill.get("ask_yes")),
        "did_change_github": False,
        "note": "I show the next step. I do not send, delete, spend, or publish unless you say yes.",
    }


def say(text: str) -> dict[str, Any]:
    hits = match(text)
    if not hits:
        fallback = {
            "id": "bf000",
            "title": "help",
            "kind": "coach",
            "reply": "Try: hi, show the map, save my work, what's broken, or plain words please.",
            "steps": ["Open START_HERE.md", "Pick a sentence from SAY_THIS.md"],
            "command": None,
            "ask_yes": False,
        }
        result = run_skill(fallback, text)
        result["also_try"] = [s["title"] for s in load_skills()[:8]]
        return result
    result = run_skill(hits[0], text)
    result["other_matches"] = [{"id": h["id"], "title": h["title"]} for h in hits[1:]]
    return result


def list_by_kind(kind: str | None = None) -> list[dict[str, Any]]:
    skills = load_skills()
    if kind:
        skills = [s for s in skills if s.get("kind") == kind]
    return [{"id": s["id"], "title": s["title"], "kind": s["kind"]} for s in skills]


def first_run() -> dict[str, Any]:
    order = ["new", "map", "save my work", "what's broken", "plain words please"]
    steps = [say(item) for item in order]
    return {
        "tour": "first ten minutes",
        "skills_used": [s["id"] for s in steps],
        "buddy_says": "Start here: you are new, here is the map, then a safe save, then how to look at tickets.",
        "steps": steps,
        "needs_your_yes": True,
    }


def explain_error(line: str) -> dict[str, Any]:
    return say(line)


HELP = """Beginner Buddy (200 coded skills)

  python3 buddy/easy_github/beginner_buddy.py say "i'm new"
  python3 buddy/easy_github/beginner_buddy.py say "save my work"
  python3 buddy/easy_github/beginner_buddy.py say "permission denied"
  python3 buddy/easy_github/beginner_buddy.py tour
  python3 buddy/easy_github/beginner_buddy.py list
  python3 buddy/easy_github/beginner_buddy.py count
"""


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"help", "-h", "--help"}:
        print(HELP)
        return 0
    cmd = argv[0]
    if cmd == "count":
        print(json.dumps({"count": len(load_skills())}, indent=2))
        return 0
    if cmd == "list":
        kind = argv[1] if len(argv) > 1 else None
        print(json.dumps(list_by_kind(kind), indent=2))
        return 0
    if cmd == "tour":
        print(json.dumps(first_run(), indent=2))
        return 0
    if cmd == "say":
        print(json.dumps(say(" ".join(argv[1:]) or "help"), indent=2))
        return 0
    if cmd == "error":
        print(json.dumps(explain_error(" ".join(argv[1:])), indent=2))
        return 0
    print(HELP)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
