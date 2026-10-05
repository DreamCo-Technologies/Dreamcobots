"""Trainable bot ledger. A bot can be trained. It has not learned yet."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ledger() -> dict:
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    return {"bots": len(bots), "trainable": len(bots), "learning_scan": True, "learned": 0}


def main() -> int:
    report = ledger()
    (ROOT / "reports" / "TRAINABLE_BOTS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
