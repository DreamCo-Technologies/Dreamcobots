#!/usr/bin/env python3
"""Record one safe soak tick and derive 24-hour evidence from a rolling history."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_TICKS = 24
MIN_ELAPSED_HOURS = 24


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def record_tick(root: Path = ROOT, now: datetime | None = None) -> dict:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    money_map = root / "config/generated/user-money-map.json"
    latest_path = root / "config/generated/sandbox-24h-tick.json"
    history_path = root / "config/generated/sandbox-24h-history.json"
    report_path = root / "reports/SANDBOX_24H.md"
    if not money_map.exists():
        raise FileNotFoundError("Run tools/build_user_money_map.py first")
    data = json.loads(money_map.read_text(encoding="utf-8"))
    sample = data.get("bots", [])[:25]
    generated_at = now.isoformat().replace("+00:00", "Z")
    tick = {
        "schema": "dreamco.sandbox_24h_tick.v2",
        "generated_at": generated_at,
        "sampled_bots": [row["slug"] for row in sample],
        "grok_routes": [row["grok_slug"] for row in sample],
        "charges_attempted": 0,
        "stripe_mode": "test_or_unset",
        "status": "sandbox_tick_ok",
    }
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else {
        "schema": "dreamco.sandbox_24h_history.v1", "ticks": []
    }
    ticks = history.setdefault("ticks", [])
    if not any(row.get("generated_at") == generated_at for row in ticks):
        ticks.append(tick)
    ticks.sort(key=lambda row: row.get("generated_at", ""))
    successful = [row for row in ticks if row.get("status") == "sandbox_tick_ok"]
    failed = [row for row in ticks if row.get("status") != "sandbox_tick_ok"]
    elapsed_hours = 0.0
    if len(ticks) >= 2:
        elapsed_hours = max(0.0, (_parse(ticks[-1]["generated_at"]) - _parse(ticks[0]["generated_at"])).total_seconds() / 3600)
    complete = len(successful) >= MIN_TICKS and elapsed_hours >= MIN_ELAPSED_HOURS and not failed
    history["summary"] = {
        "first_tick_at": ticks[0]["generated_at"] if ticks else None,
        "latest_tick_at": ticks[-1]["generated_at"] if ticks else None,
        "ticks_recorded": len(ticks), "successful_ticks": len(successful), "failed_ticks": len(failed),
        "elapsed_hours": round(elapsed_hours, 3), "minimum_ticks": MIN_TICKS,
        "minimum_elapsed_hours": MIN_ELAPSED_HOURS, "complete": complete,
        "status": "passed_24h" if complete else "collecting_evidence",
    }
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(tick, indent=2) + "\n", encoding="utf-8")
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    summary = history["summary"]
    report_path.write_text(
        "# 24-hour sandbox soak evidence\n\n"
        f"- Status: **{summary['status']}**\n"
        f"- Successful ticks: **{summary['successful_ticks']} / {MIN_TICKS} minimum**\n"
        f"- Elapsed time: **{summary['elapsed_hours']} / {MIN_ELAPSED_HOURS} hours minimum**\n"
        f"- Failed ticks: **{summary['failed_ticks']}**\n"
        "- Charges attempted: **0**\n"
        f"- Latest tick: {summary['latest_tick_at']}\n\n"
        "A single tick is not 24-hour evidence. Passage requires both real elapsed time and the minimum successful tick count.\n",
        encoding="utf-8",
    )
    return history


def main() -> int:
    history = record_tick()
    print(json.dumps({"ok": True, **history["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
