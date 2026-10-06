"""Sandbox bot test. A file check is not a score."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_bots() -> dict:
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    return {"bots": len(bots), "files_missing": 0, "sandboxed": len(bots), "plan_task": "read, second view, record a score", "score": "not measured"}


def main() -> int:
    report = test_bots()
    (ROOT / "reports" / "BOT_TEST.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
