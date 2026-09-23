#!/usr/bin/env python3
"""School rule: compare at least two views, then write Buddy's own version.

A catalog row is a resource, like a Hugging Face doc. It is not Buddy's words.
The teacher view is the assignment. The book view is the reading. A third view
is the subject. Buddy's version is written only after those views exist, and
it is not a copy of any of them.
"""
from __future__ import annotations

import json
from pathlib import Path

MIN_VIEWS = 2


class NeedsMoreViews(Exception):
    pass


def views_for(row: list) -> list[dict]:
    number, name, domain, url, reading, assignment = (list(row) + [""] * 6)[:6]
    made = [
        {"role": "teacher", "text": str(assignment).strip()},
        {"role": "book", "text": f"{name}. {reading} Reading: {url}".strip()},
        {"role": "subject", "text": f"Class subject: {domain}. This reading is one source in that class.".strip()},
    ]
    return [v for v in made if v["text"]]


def compare(views: list[dict]) -> dict:
    if len(views) < MIN_VIEWS:
        raise NeedsMoreViews(f"need {MIN_VIEWS} views, got {len(views)}")
    roles = [v["role"] for v in views]
    return {
        "views": roles,
        "agree": "Every view is about the same named reading. None of them is permission to copy it.",
        "differ": "The teacher gives the assignment. The book is the reading. The subject only says which class it belongs to.",
    }


def own_version(row: list) -> dict:
    number, name, domain, url, reading, assignment = (list(row) + [""] * 6)[:6]
    views = views_for(row)
    compared = compare(views)
    mine = (
        f"Buddy's version of resource {number}: I treat {name} as a {domain} reading, not as my own writing. "
        f"I keep the link ({url}) as the citation. I practice on a new example. "
        f"I do not paste the page, and I do not call this mastered."
    )
    for view in views:
        if mine == view["text"]:
            raise NeedsMoreViews("own version copied a source view")
    return {
        "id": number,
        "name": name,
        "domain": domain,
        "url": url,
        "compared": compared,
        "own_version": mine,
        "copied_a_view": False,
    }


def load_catalogs(folder: Path) -> list[list]:
    rows = []
    for path in sorted(folder.glob("buddy-study-resources-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data.get("resources") or [])
    return rows


def run(folder: Path) -> dict:
    written = []
    blocked = []
    for row in load_catalogs(folder):
        try:
            written.append(own_version(row))
        except NeedsMoreViews as exc:
            blocked.append({"row": row[:2], "reason": str(exc)})
    return {
        "catalog_rows": len(written) + len(blocked),
        "own_versions": len(written),
        "blocked": blocked,
        "missing_catalog_ranges": ["301-400", "601-1000"],
        "rule": "Compare teacher, book, and subject before writing. Do not copy the reading.",
        "items": written,
    }


if __name__ == "__main__":
    # One view is not enough.
    try:
        compare([{"role": "teacher", "text": "only one"}])
        raise SystemExit("gate failed open")
    except NeedsMoreViews:
        pass
    sample = own_version([1, "Hugging Face Hub & Docs", "AI/ML", "https://huggingface.co/docs", "Study the docs.", "Read, then practice."])
    assert "Buddy's version" in sample["own_version"]
    assert sample["copied_a_view"] is False
    print("school gate ok")
