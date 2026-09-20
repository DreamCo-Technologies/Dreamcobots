#!/usr/bin/env python3
"""Buddy Easy GitHub — translate common words to GitHub actions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLOSSARY = json.loads((HERE / "glossary.json").read_text(encoding="utf-8"))

HELP = """Buddy Easy GitHub

Commands:
  help                         Show this page
  words                        Print easy-word table
  say "your sentence"          Translate a plain request
  map                          Where folders live

Examples:
  python3 buddy/easy_github/buddy_easy_github.py say "what's broken"
  python3 buddy/easy_github/buddy_easy_github.py say "save my work"
  python3 buddy/easy_github/buddy_easy_github.py say "review this change"
"""

ROUTES = [
    (("what's broken", "what is broken", "problems", "tickets"),
     "Look at tickets (GitHub issues). Prefer human tickets over robot-noise.",
     "gh issue list --state open --limit 20"),
    (("save my work", "save this", "snapshot"),
     "Save a snapshot (git commit) after you review the file list.",
     "git add -A && git status"),
    (("send up", "send my work", "upload"),
     "Send the latest save to GitHub (git push).",
     "git push"),
    (("get the latest", "download newest"),
     "Get the newest official copy (git pull).",
     "git pull"),
    (("review this", "change request", "ask for review"),
     "Open a change request (pull request) for a human yes.",
     "gh pr create --fill"),
    (("did the check", "robot check", "did it pass"),
     "Read the latest robot checks (GitHub Actions).",
     "gh run list --limit 10"),
    (("clean noise", "fake tickets", "close copies"),
     "Run the intelligent ticket cleaner on auto-filed robot failures.",
     "python3 tools/issue_cleaner/clean_issues.py"),
    (("which helper", "which bot", "who should"),
     "Ask Buddy to route to a specialist bot.",
     "python3 buddy/learning/reasoning_and_learning_registry.py select \"your task\""),
    (("learn", "reasoning", "strategy"),
     "Open the reasoning + learning catalogs.",
     "python3 buddy/learning/reasoning_and_learning_registry.py discover"),
]


def translate_sentence(text: str) -> dict:
    t = text.lower().strip()
    for keys, meaning, cmd in ROUTES:
        if any(k in t for k in keys):
            return {"you_said": text, "buddy_means": meaning, "safe_next_command": cmd, "needs_your_yes": True}
    matched = []
    for row in GLOSSARY.get("terms", []):
        if any(e in t for e in row.get("easy", [])) or any(g.lower() in t for g in row.get("github", [])):
            matched.append(row)
    return {
        "you_said": text,
        "buddy_means": "I heard a general request. Say save, send, review, what's broken, or robot check.",
        "matched_words": matched,
        "needs_your_yes": True,
        "safe_next_command": None,
    }


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"help", "-h", "--help"}:
        print(HELP)
        return 0
    if argv[0] == "words":
        print((HERE / "WORDS.md").read_text(encoding="utf-8"))
        return 0
    if argv[0] == "map":
        print((HERE / "MAP.md").read_text(encoding="utf-8"))
        return 0
    if argv[0] == "say":
        sentence = " ".join(argv[1:]) or "help"
        print(json.dumps(translate_sentence(sentence), indent=2))
        return 0
    print(HELP)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
