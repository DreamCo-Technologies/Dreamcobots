#!/usr/bin/env python3
"""Inventory historical bot implementations for Superbot consolidation.

This is intentionally read-only: it discovers candidate bot directories/files
and emits an inventory for later classification. It does not delete or move code.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "legacy_bot_inventory.json"
BOT_MARKERS = {"bot", "bots", "agent", "agents", "worker", "workers"}
IGNORED = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


def looks_like_bot(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    name = path.name.lower()
    return bool(parts & BOT_MARKERS) or bool(re.search(r"(^|[-_])(bot|agent|worker)(s)?($|[-_])", name))


def main() -> int:
    records = []
    seen = set()
    for path in ROOT.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in IGNORED for part in path.parts):
            continue
        if not looks_like_bot(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        records.append({
            "path": rel,
            "name": path.name,
            "status": "unclassified",
            "division": "unresolved",
            "superbot": "unresolved",
            "lifecycle": "unresolved"
        })

    records.sort(key=lambda x: x["path"])
    payload = {
        "schema": "dreamco.legacy_bot_inventory.v1",
        "generatedBy": "tools/build_legacy_bot_inventory.py",
        "readOnly": True,
        "count": len(records),
        "records": records
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Discovered {len(records)} candidate bot directories")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
