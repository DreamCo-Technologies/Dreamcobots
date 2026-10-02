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


def main() -> int:
    old_names, old_urls = names_urls(OLD)
    # Compare against every other study-resource set, not only 001-100.
    for other in sorted((ROOT / "config").glob("buddy-study-resources-*.json")):
        if other == NEW:
            continue
        n, u = names_urls(other)
        old_names |= n
        old_urls |= u
    new = json.loads(NEW.read_text(encoding="utf-8"))
    rows = new["resources"]
    if len(rows) != 100:
        raise SystemExit(f"expected 100 resources, got {len(rows)}")
    ids = [row[0] for row in rows]
    if ids != list(range(1001, 1101)):
        raise SystemExit("ids must be 1001-1100")
    short = [row[0] for row in rows if len(row) < 6]
    if short:
        raise SystemExit(f"rows missing practice_method (need 6 fields): {short}")
    new_names, new_urls = names_urls(NEW)
    name_hits = sorted(old_names & new_names)
    url_hits = sorted(old_urls & new_urls)
    if name_hits or url_hits:
        raise SystemExit(f"duplicates names={name_hits} urls={url_hits}")
    print(json.dumps({"ok": True, "added": 100, "name_overlap": 0, "url_overlap": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
