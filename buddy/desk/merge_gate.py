#!/usr/bin/env python3
"""A pull request is safe to merge only when it has no conflict and no failing check."""
from __future__ import annotations

import json


def review(pull: dict) -> dict:
    number = pull.get("number")
    if pull.get("draft") is True:
        return {"number": number, "safe": False, "reason": "A draft is not ready."}
    if pull.get("mergeable") != "MERGEABLE":
        return {"number": number, "safe": False, "reason": "It conflicts or GitHub has not confirmed it can merge."}
    checks = pull.get("checks") or []
    if not checks:
        return {"number": number, "safe": False, "reason": "No checks have finished."}
    failed = [row.get("name") or "check" for row in checks if row.get("conclusion") not in {"success", "skipped", "neutral"}]
    if failed:
        return {"number": number, "safe": False, "reason": "Failing checks: " + ", ".join(failed) + "."}
    return {"number": number, "safe": True, "reason": "No conflict and every finished check passed."}


if __name__ == "__main__":
    green = review({"number": 1, "draft": False, "mergeable": "MERGEABLE", "checks": [{"name": "tests", "conclusion": "success"}]})
    red = review({"number": 2, "draft": False, "mergeable": "MERGEABLE", "checks": [{"name": "trusted-code", "conclusion": "failure"}]})
    conflict = review({"number": 12082, "draft": False, "mergeable": "CONFLICTING", "checks": [{"name": "tests", "conclusion": "success"}]})
    assert green["safe"] is True
    assert red["safe"] is False and conflict["safe"] is False
    print(json.dumps({"green": True, "red_merged": False, "conflict_merged": False}))
