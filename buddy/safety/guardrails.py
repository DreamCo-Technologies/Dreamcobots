#!/usr/bin/env python3
"""Public checks. Not a United States certification."""
from __future__ import annotations

import json
import re

SECRET = re.compile(r"ghp_|github_pat_|sk-|hf_|AKIA")
REFUSED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "mine a coin",
    "wire the money",
    "official us certification",
    "united states certified",
)


def review(text: str) -> dict:
    blob = (text or "").lower().replace("-", " ").replace("_", " ")
    reasons = []
    if SECRET.search(text or ""):
        reasons.append("A key-shaped string is in the text. Remove it.")
    for phrase in REFUSED:
        if phrase in blob:
            reasons.append("Blocked: " + phrase)
            break
    return {
        "allowed": not reasons,
        "reasons": reasons or ["No blocked phrase and no key-shaped string."],
        "official_us_certification": False,
        "trains_a_model": False,
    }


if __name__ == "__main__":
    assert review("sort the mail")["allowed"] is True
    assert review("please copy gpt weights")["allowed"] is False
    assert review("token ghp_abc")["allowed"] is False
    assert review("we are united states certified")["official_us_certification"] is False
    assert review("we are united states certified")["allowed"] is False
    print(json.dumps(review("sort the mail")))
