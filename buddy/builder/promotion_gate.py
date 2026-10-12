"""Champion and challenger gate. Missing evidence does not promote."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def promote(champion: dict | None, challenger: dict | None) -> dict:
    if not challenger or challenger.get("runs", 0) < 2:
        return {"promoted": False, "reason": "two saved runs required", "rollback": "keep champion"}
    if challenger.get("failure_rate") is None or challenger.get("quality") is None:
        return {"promoted": False, "reason": "quality and failure rate required", "rollback": "keep champion"}
    if champion and challenger["failure_rate"] > champion.get("failure_rate", 1):
        return {"promoted": False, "reason": "failure rate worse", "rollback": "keep champion"}
    if champion and challenger["quality"] <= champion.get("quality", 0):
        return {"promoted": False, "reason": "quality not better", "rollback": "keep champion"}
    return {"promoted": True, "reason": "median quality better and failure rate not worse", "rollback": "restore previous champion"}


def main() -> int:
    decision = promote(None, None)
    (ROOT / "reports" / "PROMOTION_GATE.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
