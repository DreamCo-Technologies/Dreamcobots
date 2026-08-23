#!/usr/bin/env python3
"""Audit bot inventory against the canonical 65-MasterBot registry.

The audit is intentionally conservative: it never moves or deletes bots. It
reports explicit division metadata, filename/path hints, unknowns and possible
multi-domain collaborators so a later migration can be reviewed safely.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "masterbot-65-registry.json"
BOT_ROOTS = [ROOT / "App_bots", ROOT / "bots", ROOT / "original-bots", ROOT / "website" / "data" / "bot-fleet"]


def load_registry() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_name = {d["name"].lower(): d for d in data["divisions"]}
    aliases = {d["name"].lower(): d["name"] for d in data["divisions"]}
    return by_name, aliases


def json_division(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(value, dict):
        for key in ("division", "masterBot", "masterbotDivision", "category"):
            raw = value.get(key)
            if isinstance(raw, str):
                return raw
    return None


def infer_from_path(path: Path, names: dict[str, dict[str, Any]]) -> list[str]:
    haystack = str(path.relative_to(ROOT)).lower()
    matches = []
    for key, division in names.items():
        compact = re.sub(r"[^a-z0-9]", "", key)
        if compact and compact in re.sub(r"[^a-z0-9]", "", haystack):
            matches.append(division["name"])
    return matches


def main() -> int:
    names, _ = load_registry()
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    for root in BOT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".json", ".ts", ".tsx", ".js", ".jsx", ".py"}:
                continue
            rel = str(path.relative_to(ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            explicit = json_division(path) if path.suffix == ".json" else None
            hints = infer_from_path(path, names)
            results.append({
                "path": rel,
                "explicit_division": explicit,
                "path_hints": hints,
                "status": "routable" if explicit or len(hints) == 1 else ("review" if len(hints) > 1 else "unclassified"),
            })

    summary = {
        "registry_divisions": len(names),
        "files_scanned": len(results),
        "routable": sum(r["status"] == "routable" for r in results),
        "review": sum(r["status"] == "review" for r in results),
        "unclassified": sum(r["status"] == "unclassified" for r in results),
        "policy": "No automatic moves/deletes; review evidence before changing primary ownership.",
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
