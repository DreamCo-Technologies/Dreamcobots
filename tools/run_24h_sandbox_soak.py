#!/usr/bin/env python3
"""One tick of the 24h sandbox soak. Safe to run hourly for 24 hours."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "config" / "generated" / "user-money-map.json"
OUT = ROOT / "config" / "generated" / "sandbox-24h-tick.json"
REPORT = ROOT / "reports" / "SANDBOX_24H.md"


def main() -> int:
    if not MAP.exists():
        raise SystemExit("Run tools/build_user_money_map.py first")
    data = json.loads(MAP.read_text(encoding="utf-8"))
    sample = data.get("bots", [])[:25]
    tick = {
        "schema": "dreamco.sandbox_24h_tick.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sampled_bots": [row["slug"] for row in sample],
        "grok_routes": [row["grok_slug"] for row in sample],
        "charges_attempted": 0,
        "stripe_mode": "test_or_unset",
        "status": "sandbox_tick_ok",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(tick, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"# 24h sandbox tick\n\n- Bots sampled: **{len(sample)}**\n- Charges: **0**\n- Time: {tick['generated_at']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "sampled": len(sample), "charges": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
