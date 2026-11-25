#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "config" / "buddy-study-resources-001-100.json"
NEW = ROOT / "config" / "buddy-study-resources-1001-1100-must-have.json"


def names_urls(path: Path) -> tuple[set[str], set[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    names, urls = set(), set()
    for row in doc["resources"]:
        names.add(str(row[1]).strip().lower())
        urls.add(str(row[3]).strip().rstrip("/").lower())
    return names, urls


EXPANSION = ROOT / "config" / "buddy-study-resources-1101-1200-expansion.json"


def validate_catalogs() -> dict[str, object]:
    """Validate the 1101-1200 discovery catalog and its specialized study tracks."""
    doc = json.loads(EXPANSION.read_text(encoding="utf-8"))
    rows = doc.get("resources", [])
    ids = [row[0] for row in rows]
    if ids != list(range(1101, 1201)):
        raise ValueError("expansion resource IDs must be unique and ordered from 1101 through 1200")
    for row in rows:
        if len(row) < 6 or not all(str(value).strip() for value in row[1:]):
            raise ValueError(f"invalid study resource row: {row!r}")
        if not str(row[3]).startswith("https://"):
            raise ValueError(f"resource URL must use HTTPS: {row[0]}")
    tracks = doc.get("specialized_study_tracks", [])
    track_ids = [track.get("track_id") for track in tracks]
    if len(track_ids) != len(set(track_ids)):
        raise ValueError("specialized study track IDs must be unique")
    tolkien = next((track for track in tracks if track.get("track_id") == "tolkien"), None)
    if not tolkien:
        raise ValueError("missing canonical Tolkien study track")
    rights = tolkien.get("rights_and_safety", {})
    if rights.get("primary_tolkien_texts_training_eligible") is not False:
        raise ValueError("Tolkien primary-text training must remain disabled")
    if rights.get("model_weight_training_authorized") is not False:
        raise ValueError("Tolkien model-weight training must remain disabled")
    if rights.get("unknown_rights_status") != "BLOCKED":
        raise ValueError("unknown Tolkien rights must remain blocked")
    if len(tolkien.get("lesson_sequence", [])) != 8:
        raise ValueError("canonical Tolkien base track must retain eight lessons")
    if len(tolkien.get("extended_lesson_sequence", [])) != 12:
        raise ValueError("Tolkien extended track must contain twelve lessons")
    if tolkien.get("course_integration", {}).get("status") != "NEEDS_USER_SUPPLIED_COURSE_REFERENCE":
        raise ValueError("the exact external course must not be guessed")
    return {"ok": True, "resources": len(rows), "specialized_tracks": len(tracks), "tolkien_lessons": 20}


def main() -> int:
    old_names, old_urls = names_urls(OLD)
    new = json.loads(NEW.read_text(encoding="utf-8"))
    rows = new["resources"]
    if len(rows) != 100:
        raise SystemExit(f"expected 100 resources, got {len(rows)}")
    ids = [row[0] for row in rows]
    if ids != list(range(1001, 1101)):
        raise SystemExit("ids must be 1001-1100")
    new_names, new_urls = names_urls(NEW)
    name_hits = sorted(old_names & new_names)
    url_hits = sorted(old_urls & new_urls)
    if name_hits or url_hits:
        raise SystemExit(f"duplicates names={name_hits} urls={url_hits}")
    print(json.dumps({"ok": True, "added": 100, "name_overlap": 0, "url_overlap": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
