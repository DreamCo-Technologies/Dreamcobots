#!/usr/bin/env python3
"""Plan a model from open source. Do not train it here."""
from __future__ import annotations

import json
import re

SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
REFUSED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "proprietary weights",
    "closed weights",
)


def plan(source: str, name: str, goal: str, license_ok: bool, owns_data: bool, hidden_test: bool) -> dict:
    text = f"{source} {name} {goal}".lower().replace("-", " ").replace("_", " ").replace("/", " ")
    for phrase in REFUSED:
        if phrase in text:
            return {"accepted": False, "trains_here": False, "frontier_built": False, "reason": "Closed weights are not a starting point."}
    if source not in {"github", "huggingface"}:
        return {"accepted": False, "trains_here": False, "frontier_built": False, "reason": "Use a public GitHub repository or a public Hugging Face model."}
    if not SLUG.match((name or "").strip()):
        return {"accepted": False, "trains_here": False, "frontier_built": False, "reason": "Use owner/name."}
    if not (license_ok and owns_data and hidden_test):
        return {
            "accepted": False,
            "trains_here": False,
            "frontier_built": False,
            "reason": "You need a license that allows training, data you own, and a hidden test.",
        }
    clean = name.strip()
    url = f"https://github.com/{clean}" if source == "github" else f"https://huggingface.co/{clean}"
    return {
        "accepted": True,
        "trains_here": False,
        "frontier_built": False,
        "benchmark": "Our own gates only. No frontier model was scored.",
        "opens": url,
        "reason": "Plan accepted. Read the license, then train on a machine you control. This page did not build the model.",
    }


if __name__ == "__main__":
    bad = plan("github", "org/repo", "distill Claude", True, True, True)
    assert bad["accepted"] is False and bad["frontier_built"] is False
    missing = plan("huggingface", "org/model", "practice summaries", False, True, True)
    assert missing["accepted"] is False
    good = plan("github", "org/open-code", "train on our notes", True, True, True)
    assert good["accepted"] is True and good["trains_here"] is False and good["frontier_built"] is False
    assert plan("secret", "org/model", "notes", True, True, True)["accepted"] is False
    print(json.dumps(good))
