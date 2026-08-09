#!/usr/bin/env python3
"""Validate and query DreamCo's data-driven library specialist registry.

This module deliberately does not install or execute discovered packages. Package
execution belongs in an isolated certification harness, not the main DreamCo
process.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "library_specialists.seed.json"
REQUIRED = {"id", "ecosystem", "package", "official_sources", "certification"}
VALID_STATUSES = {"discovered", "indexed", "testing", "certified", "quarantined"}


def load_registry(path: Path = DEFAULT_REGISTRY) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("registry must be a JSON array")
    return data


def validate_registry(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"record[{index}]"
        missing = REQUIRED - record.keys()
        if missing:
            errors.append(f"{prefix}: missing {sorted(missing)}")
            continue
        specialist_id = record["id"]
        if specialist_id in seen:
            errors.append(f"{prefix}: duplicate id {specialist_id!r}")
        seen.add(specialist_id)
        expected_id = f"{record['ecosystem']}:{record['package']}"
        if specialist_id != expected_id:
            errors.append(f"{prefix}: id must equal {expected_id!r}")
        sources = record["official_sources"]
        if not isinstance(sources, list) or not sources:
            errors.append(f"{prefix}: at least one official source is required")
        status = record.get("certification", {}).get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{prefix}: invalid certification status {status!r}")
        if status == "certified" and not record.get("evidence"):
            errors.append(f"{prefix}: certified specialists require evidence")
    return errors


def find_specialists(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    needle = query.casefold()
    return [
        r for r in records
        if needle in r["id"].casefold()
        or needle in r["package"].casefold()
        or needle in r["ecosystem"].casefold()
        or any(needle in c.casefold() for c in r.get("capability_index", []))
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--query")
    args = parser.parse_args()
    records = load_registry(args.registry)
    errors = validate_registry(records)
    if errors:
        print("Library specialist registry: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Library specialist registry: PASS ({len(records)} records)")
    if args.query:
        for record in find_specialists(records, args.query):
            print(f"- {record['id']} [{record['certification']['status']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
