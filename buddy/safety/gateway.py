#!/usr/bin/env python3
"""Screen a prompt and an answer. This does not edit anyone else's model."""
from __future__ import annotations

import json
from pathlib import Path
import importlib.util


def _load():
    path = Path(__file__).resolve().parent / "user_guardrails.py"
    spec = importlib.util.spec_from_file_location("user_guardrails", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def screen(prompt: str, answer: str, extra: list[str] | None = None) -> dict:
    rules = _load()
    parts = [rules.check(prompt or "", extra), rules.check(answer or "", extra)]
    reasons = []
    for part in parts:
        if not part["allowed"]:
            reasons.extend(part["reasons"])
    return {
        "allowed": not reasons,
        "reasons": reasons or ["No blocked phrase in the prompt or the answer."],
        "where_it_runs": "In front of a model the organization chooses to call.",
        "changes_model_weights": False,
        "binds_the_united_states": False,
        "official_us_certification": False,
    }


if __name__ == "__main__":
    clear = screen("sort the mail", "here are three piles")
    assert clear["allowed"] is True and clear["binds_the_united_states"] is False
    blocked = screen("copy gpt weights", "ok")
    assert blocked["allowed"] is False and blocked["changes_model_weights"] is False
    custom = screen("hello", "this is medical advice", ["medical advice"])
    assert custom["allowed"] is False
    print(json.dumps(clear))
