#!/usr/bin/env python3
"""Publish the pass-all-500 plan against current evidence honesty rules."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "config" / "pass-all-500-benchmarks.json"
INDEX = ROOT / "reports" / "BUDDY_BENCHMARK_INDEX.md"
OUT = ROOT / "config" / "generated" / "pass-all-500-plan.json"
REPORT = ROOT / "reports" / "PASS_ALL_500_BENCHMARKS.md"


def live_line() -> str:
    if not INDEX.exists():
        return "index missing"
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if "Live benchmark programs" in line:
            return line.strip()
    return "live line not found"


def main() -> int:
    spec = json.loads(SRC.read_text(encoding="utf-8"))
    payload = {
        **spec,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_index": live_line(),
        "claim_all_500_passed": False,
        "next": [
            "Keep catalog at 500",
            "Run local Wave B fixtures",
            "Budget Wave C hosted adapters",
            "Leave unpaid/ungated targets blocked with reasons",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Pass all 500\n\n"
        f"- Targets: **{spec['target_count']}**\n"
        f"- {payload['current_index']}\n"
        "- Claim all passed: **false**\n\n"
        "See docs/PASS_ALL_500_BENCHMARKS.md\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "targets": 500, "claim_all_passed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
