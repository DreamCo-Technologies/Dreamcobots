#!/usr/bin/env python3
"""Plain-language map of GitHub. Buddy explains GitHub. It does not replace it."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_offers(path: Path | None = None) -> list[dict]:
    source = path or (HERE / "github_offers.json")
    return json.loads(source.read_text(encoding="utf-8"))


def explain(text: str, offers: list[dict] | None = None) -> dict:
    said = (text or "").lower()
    offers = offers if offers is not None else load_offers()
    best = None
    best_score = 0
    for item in offers:
        score = 0
        for word in (item["plain"], item["github"], item["id"]):
            piece = str(word).lower()
            if piece and piece in said:
                score += 3 if len(piece) > 3 else 1
        if score > best_score:
            best, best_score = item, score
    if not best:
        return {
            "matched": False,
            "say": "Try a plain word such as ticket, change request, robots, or ping.",
            "replaces_github": False,
        }
    return {
        "matched": True,
        "github": best["github"],
        "plain": best["plain"],
        "say": best["say"] + " This still happens on GitHub. Buddy only translates the word.",
        "doc": best["doc"],
        "replaces_github": False,
    }


if __name__ == "__main__":
    rows = load_offers()
    ticket = explain("what is a ticket", rows)
    change = explain("open a change request", rows)
    assert ticket["github"] == "Issue"
    assert change["github"] == "Pull request"
    assert ticket["replaces_github"] is False
    assert len(rows) >= 40
    print(json.dumps({"offers": len(rows), "ticket": ticket["plain"]}, indent=2))
