"""Champion and challenger gate. Missing evidence does not promote."""

from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _valid_score(value: object) -> bool:
    """Only finite numeric quality measurements count as benchmark evidence."""
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _valid_failure_rate(value: object) -> bool:
    return _valid_score(value) and 0 <= value <= 1


def promote(champion: dict | None, challenger: dict | None) -> dict:
    """Promote only with a measured, comparable champion and challenger."""
    blocked = lambda reason: {"promoted": False, "reason": reason, "rollback": "keep champion"}
    if not isinstance(challenger, dict):
        return blocked("two saved runs required")
    runs = challenger.get("runs")
    if type(runs) is not int or runs < 2:
        return blocked("two saved runs required")
    if not _valid_score(challenger.get("quality")) or not _valid_failure_rate(challenger.get("failure_rate")):
        return blocked("finite quality and failure rate in [0, 1] required")
    if not isinstance(champion, dict) or not _valid_score(champion.get("quality")) or not _valid_failure_rate(champion.get("failure_rate")):
        return blocked("valid measured champion baseline required")
    if challenger["failure_rate"] > champion["failure_rate"]:
        return blocked("failure rate worse")
    if challenger["quality"] <= champion["quality"]:
        return blocked("quality not better")
    return {"promoted": True, "reason": "quality better and failure rate not worse", "rollback": "restore previous champion"}


def main() -> int:
    decision = promote(None, None)
    (ROOT / "reports" / "PROMOTION_GATE.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
