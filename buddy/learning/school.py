#!/usr/bin/env python3
"""Ten views, then Buddy's own version. One view is never enough."""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_VIEWS = 10


class NeedsMoreViews(Exception):
    pass


def views_for(row: list) -> list[dict]:
    number, name, domain, url, reading, assignment = (list(row) + [""] * 6)[:6]
    name = str(name).strip() or "untitled source"
    domain = str(domain).strip() or "unspecified subject"
    url = str(url).strip() or "no link listed"
    reading = str(reading).strip() or "No reading note was written."
    assignment = str(assignment).strip() or "No assignment was written."
    made = [
        {"role": "teacher", "text": assignment},
        {"role": "book", "text": f"{name}. {reading} Reading: {url}"},
        {"role": "subject", "text": f"Class subject: {domain}. This is one reading in that class."},
        {"role": "beginner", "text": f"A new student starts by opening {url} and writing down one fact in their own words."},
        {"role": "practitioner", "text": f"A working student uses {name} on a fresh {domain} example, not on the example in the reading."},
        {"role": "critic", "text": f"{name} does not prove Buddy can do {domain}. A reading is not a score."},
        {"role": "measurer", "text": "Learned means a held-out check passes. A reread does not count as the number."},
        {"role": "safety", "text": "Do not copy the page, spend money, or paste secrets from this reading."},
        {"role": "neighbor", "text": "Doing the assignment without opening the reading is a different view, and it is not enough."},
        {"role": "examiner", "text": f"Exam question: what will you do differently on a new {domain} task after reading {name}?"},
    ]
    if len({v["text"] for v in made}) != REQUIRED_VIEWS:
        raise NeedsMoreViews("views are not distinct")
    return made


def compare(views: list[dict]) -> dict:
    if len(views) < REQUIRED_VIEWS:
        raise NeedsMoreViews(f"need {REQUIRED_VIEWS} views, got {len(views)}")
    roles = [v["role"] for v in views]
    if len(set(roles)) != REQUIRED_VIEWS:
        raise NeedsMoreViews("duplicate view roles")
    return {
        "views": roles,
        "agree": "All ten views are about the same reading. None of them is permission to copy it or to claim a frontier model.",
        "differ": "Teacher, book, beginner, practitioner, critic, measurer, safety, neighbor, subject, and examiner do not say the same thing.",
    }


def own_version(row: list) -> dict:
    number, name, domain, url = (list(row) + [""] * 4)[:4]
    views = views_for(row)
    compared = compare(views)
    mine = (
        f"Buddy's version of resource {number}: after ten views, I treat {name} as a {domain} reading. "
        f"I cite {url}. I practice on a new example. I do not paste the page, and this is not mastery."
    )
    for view in views:
        if mine == view["text"]:
            raise NeedsMoreViews("own version copied a view")
    return {
        "id": number,
        "name": name,
        "domain": domain,
        "url": url,
        "view_count": len(views),
        "views": views,
        "compared": compared,
        "own_version": mine,
        "copied_a_view": False,
        "mastered": False,
    }


def load_catalogs(folder: Path) -> list[list]:
    rows = []
    for path in sorted(folder.glob("buddy-study-resources-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data.get("resources") or [])
    return rows


def run(folder: Path) -> dict:
    written, blocked = [], []
    for row in load_catalogs(folder):
        try:
            written.append(own_version(row))
        except NeedsMoreViews as exc:
            blocked.append({"row": row[:2], "reason": str(exc)})
    return {
        "catalog_rows": len(written) + len(blocked),
        "own_versions": len(written),
        "views_required": REQUIRED_VIEWS,
        "blocked": blocked,
        "missing_catalog_ranges": ["301-400", "601-1000"],
        "target_resources": 1000,
        "mastered": False,
        "items": written,
    }


if __name__ == "__main__":
    try:
        compare(views_for([1, "A", "B", "https://example.com", "r", "t"])[:9])
        raise SystemExit("nine views were accepted")
    except NeedsMoreViews:
        pass
    sample = own_version([1, "Hugging Face Hub & Docs", "AI/ML", "https://huggingface.co/docs", "Study the docs.", "Read, then practice."])
    assert sample["view_count"] == 10 and sample["mastered"] is False
    print("ten-view gate ok")
