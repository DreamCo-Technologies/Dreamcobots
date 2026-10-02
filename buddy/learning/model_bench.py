#!/usr/bin/env python3
"""Plan a public-model test. This file does not download or train weights."""
from __future__ import annotations

import json
import re

MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
REFUSED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "proprietary weights",
    "closed weights",
    "gpt astra",
    "claude mythos",
)


def review(model_id: str, goal: str, owns_data: bool, held_out: bool, open_license: bool) -> dict:
    text = f"{model_id} {goal}".lower()
    for phrase in REFUSED:
        if phrase in text:
            return {
                "accepted": False,
                "tests_here": False,
                "trains_here": False,
                "reason": "This bench will not copy or distill a closed model.",
            }
    if not MODEL_ID.match((model_id or "").strip()):
        return {
            "accepted": False,
            "tests_here": False,
            "trains_here": False,
            "reason": "Use a public id like organization/model-name.",
        }
    clean = model_id.strip()
    if not (owns_data and held_out and open_license):
        return {
            "accepted": False,
            "tests_here": False,
            "trains_here": False,
            "model_url": f"https://huggingface.co/{clean}",
            "reason": "To plan training, you must own the data, keep a hidden test, and use a license that allows training.",
        }
    return {
        "accepted": True,
        "tests_here": False,
        "trains_here": False,
        "model_url": f"https://huggingface.co/{clean}",
        "reason": "Plan accepted. Open the model on Hugging Face to try its widget. Training runs on a machine you control, not on this page.",
    }


if __name__ == "__main__":
    bad = review("org/model", "distill Claude Mythos", True, True, True)
    assert bad["accepted"] is False and bad["trains_here"] is False
    missing = review("org/model", "practice summaries", False, True, True)
    assert missing["accepted"] is False
    good = review("HuggingFaceTB/SmolLM2-135M", "practice summaries on our notes", True, True, True)
    assert good["accepted"] is True and good["trains_here"] is False and good["tests_here"] is False
    assert review("not a model", "notes", True, True, True)["accepted"] is False
    print(json.dumps(good))
