#!/usr/bin/env python3
"""What Buddy can do for each GitHub connection. Writes stay blocked."""
from __future__ import annotations

import json

PUBLIC_READS = {"files", "commits", "branches", "checks"}
WRITES = {"tickets", "changes", "pages", "releases", "packages", "webhooks", "codespaces", "secrets", "dependabot", "projects", "discussions", "deploys", "security"}


def task(name: str, action: str) -> dict:
    name = (name or "").strip().lower()
    action = (action or "").strip().lower()
    if name in PUBLIC_READS and action == "read":
        return {"buddy_does_it": True, "writes": False, "reason": "Buddy can list this from the public repository."}
    if name in WRITES or action == "write":
        return {
            "buddy_does_it": False,
            "writes": False,
            "reason": "A write needs a GitHub App you install. This page will not pretend the write happened.",
        }
    return {"buddy_does_it": False, "writes": False, "reason": "Unknown connection."}


if __name__ == "__main__":
    assert task("commits", "read")["buddy_does_it"] is True
    assert task("tickets", "write")["buddy_does_it"] is False
    assert task("webhooks", "write")["writes"] is False
    print(json.dumps(task("commits", "read")))
