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
    canonical = {}
    for path in sorted((ROOT / "config").glob("buddy-study-resources-*.json")):
        if path == NEW:
            continue
        for row in json.loads(path.read_text(encoding="utf-8"))["resources"]:
            canonical[row[0]] = row
    new = json.loads(NEW.read_text(encoding="utf-8"))
    rows = new["resources"]
    references = new.get("resource_references", [])
    if len(rows) + len(references) != 100:
        raise SystemExit("expected 100 study selections (new sources plus canonical references)")
    ids = [row[0] for row in rows] + [ref["selection_id"] for ref in references]
    if sorted(ids) != list(range(1001, 1101)):
        raise SystemExit("selection ids must be 1001-1100, each exactly once")
    urls = {row[3].strip().rstrip("/").lower() for row in canonical.values()}
    for row in rows:
        if len(row) < 6 or not row[3].startswith(("https://", "http://")):
            raise SystemExit(f"incomplete resource: {row[0]}")
        url = row[3].strip().rstrip("/").lower()
        if url in urls:
            raise SystemExit(f"duplicate source URL: {url}")
        urls.add(url)
    referenced_ids = [ref["resource_id"] for ref in references]
    if len(referenced_ids) != len(set(referenced_ids)):
        raise SystemExit("duplicate canonical resource reference")
    for ref in references:
        if ref["resource_id"] not in canonical or not ref.get("usage") or not ref.get("adoption_rule"):
            raise SystemExit(f"invalid canonical reference: {ref['selection_id']}")
    print(json.dumps({"ok": True, "added": len(rows), "reused": len(references), "selections": 100}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
