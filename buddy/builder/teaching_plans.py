"""Teaching plans. One short plan per file. A plan is not a finished lesson."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def plans() -> list[dict]:
    rows = []
    for path in sorted((ROOT / "bots").glob("*.md")):
        rows.append({"file": path.as_posix(), "resource": "bots file plus a second view", "steps": ["read the file", "compare a second view", "record a score"], "learned": False})
    for path in sorted((ROOT / "study_packs").rglob("*")):
        if path.is_file():
            rows.append({"file": path.relative_to(ROOT).as_posix(), "resource": "study pack", "steps": ["read the pack", "retry the task", "record a score"], "learned": False})
    for path in sorted((ROOT / "benchmarks").rglob("*")):
        if path.is_file():
            rows.append({"file": path.relative_to(ROOT).as_posix(), "resource": "benchmark file", "steps": ["run the same task twice", "keep the median", "record a score"], "learned": False})
    return rows


def main() -> int:
    rows = plans()
    (ROOT / "reports" / "TEACHING_PLANS.json").write_text(json.dumps({"count": len(rows), "learned": 0, "plans": rows[:20]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(rows), "learned": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
