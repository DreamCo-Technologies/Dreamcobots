#!/usr/bin/env python3
"""User guardrails sit on top of locks that cannot be removed."""
from __future__ import annotations

import json
import re

LOCKED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "official us certification",
    "united states certified",
)
SECRET = re.compile(r"ghp_|github_pat_|sk-|hf_|AKIA")


def _clean(phrase: str) -> str:
    return " ".join((phrase or "").lower().replace("-", " ").replace("_", " ").split())


def rules(extra: list[str] | None = None) -> dict:
    added = []
    for phrase in extra or []:
        clean = _clean(phrase)
        if clean and clean not in LOCKED and clean not in added:
            added.append(clean[:80])
    return {"locked": list(LOCKED), "yours": added, "removable_locks": False}


def check(text: str, extra: list[str] | None = None) -> dict:
    blob = _clean(text)
    made = rules(extra)
    reasons = []
    if SECRET.search(text or ""):
        reasons.append("A key-shaped string is in the text.")
    for phrase in made["locked"] + made["yours"]:
        if phrase in blob:
            reasons.append("Blocked: " + phrase)
    return {
        "allowed": not reasons,
        "reasons": reasons or ["No blocked phrase and no key-shaped string."],
        "loaded_weights": False,
        "official_us_certification": False,
        "rules": made,
    }


if __name__ == "__main__":
    assert check("hello", ["no refunds"])["allowed"] is True
    assert check("we offer no refunds", ["no refunds"])["allowed"] is False
    assert check("copy gpt now", [])["allowed"] is False
    assert "copy gpt" in rules(["copy gpt"])["locked"]
    assert "copy gpt" not in rules(["copy gpt"])["yours"]
    print(json.dumps(check("hello", ["be kind"])))
