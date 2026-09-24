#!/usr/bin/env python3
"""Forty plain shortcuts. Twenty for the repository, twenty for the site."""
from __future__ import annotations

import json

REPO = "https://github.com/DreamCo-Technologies/Dreamcobots"
SITE = "https://dreamco-technologies.github.io/Dreamcobots"

REPOSITORY = [
    ("New file", f"{REPO}/new/main"),
    ("Edit the readme", f"{REPO}/edit/main/README.md"),
    ("Open a ticket", f"{REPO}/issues/new"),
    ("Propose a change", f"{REPO}/compare"),
    ("See commits", f"{REPO}/commits/main"),
    ("See branches", f"{REPO}/branches"),
    ("Search the code", f"{REPO}/search"),
    ("See checks", f"{REPO}/actions"),
    ("Read a file", f"{REPO}/blob/main/README.md"),
    ("Start a discussion", f"{REPO}/discussions"),
    ("Make a release", f"{REPO}/releases/new"),
    ("Site settings", f"{REPO}/settings/pages"),
    ("Secret settings", f"{REPO}/settings/secrets/actions"),
    ("Dependency alerts", f"{REPO}/security/dependabot"),
    ("Open a work room", f"{REPO}/codespaces"),
    ("Add a webhook", f"{REPO}/settings/hooks"),
    ("Project board", f"{REPO}/projects"),
    ("New bot note", f"{REPO}/new/main/bots"),
    ("Ask for a review", f"{REPO}/pulls"),
    ("See who changed a line", f"{REPO}/blame/main/README.md"),
]

PAGES = [
    ("Command center", "github-center.html"),
    ("Bot prospectus", "bots.html"),
    ("Original bots", "bots.html#original-bot-section"),
    ("Actions", "actions.html"),
    ("Benchmarks", "benchmarks.html"),
    ("All files", "repo-live.html"),
    ("Test a model", "model-bench.html"),
    ("Weight sheet", "weight-hub.html"),
    ("Their own model", "your-model.html"),
    ("Easy GitHub", "github-hub.html"),
    ("Easy Hugging Face", "hf-hub.html"),
    ("School", "school.html"),
    ("Build a bot", "github-center.html#bot-form"),
    ("Guardrails", "guardrails.html"),
    ("Sign in", "sign-in.html"),
    ("Plans", "plans.html"),
    ("This chat", "this-chat.html"),
    ("Unlock", "hf-unlock.html"),
    ("Lessons", "frontier-shop.html"),
    ("Test center", "test-center.html"),
]


def shortcuts() -> dict:
    if len(REPOSITORY) != 20 or len(PAGES) != 20:
        raise ValueError("each list needs 20 shortcuts")
    return {
        "repository": [{"plain": name, "href": href} for name, href in REPOSITORY],
        "pages": [{"plain": name, "href": href} for name, href in PAGES],
    }


if __name__ == "__main__":
    made = shortcuts()
    assert len(made["repository"]) == 20 and len(made["pages"]) == 20
    print(json.dumps({"repository": 20, "pages": 20}))
