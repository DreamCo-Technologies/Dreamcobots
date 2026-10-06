"""Read-only expert scan. It never deletes or rewrites source files.

A section is reviewed, not approved, until a named check passes. Duplicate
paths are reported, not removed.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "__pycache__", "dist", "logs"}
OUT = ROOT / "reports" / "EXPERT_SECTION_SCAN.json"


def scan() -> dict:
    sections: dict[str, int] = defaultdict(int)
    names: dict[str, list[str]] = defaultdict(list)
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        section = relative.split("/", 1)[0]
        sections[section] += 1
        names[path.name].append(relative)
    duplicates = {name: rows for name, rows in names.items() if len(rows) > 1 and name not in {"__init__.py", "README.md"}}
    return {
        "sections": dict(sorted(sections.items())),
        "duplicate_names": len(duplicates),
        "deleted": False,
        "expert_approved": False,
        "reason": "A scan is a review. Approval needs a passing check for that section.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = scan()
    if args.write:
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sections": len(report["sections"]), "duplicate_names": report["duplicate_names"], "expert_approved": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
