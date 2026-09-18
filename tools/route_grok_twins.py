#!/usr/bin/env python3
"""Resolve a bot job to its Grok twin and frontier Grok route."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TWINS = ROOT / "config" / "generated" / "grok-bot-twins.json"
OUT = ROOT / "config" / "generated" / "grok-twin-route.json"


def load_twins() -> dict:
    if not TWINS.exists():
        raise SystemExit("Run tools/build_grok_bot_twins.py first")
    return json.loads(TWINS.read_text(encoding="utf-8"))


def route(slug: str, twins_doc: dict) -> dict:
    wanted = slug.strip()
    for row in twins_doc.get("twins", []):
        if row.get("source_slug") == wanted or row.get("grok_slug") == wanted:
            return {
                "ok": True,
                "input": wanted,
                "source_slug": row["source_slug"],
                "grok_slug": row["grok_slug"],
                "model_route": row.get("model_route", "xai/grok-best-available"),
                "division": row.get("division"),
                "autonomy_ceiling": row.get("autonomy_ceiling", "sandbox_execute"),
                "live_money_outreach": False,
            }
    return {
        "ok": False,
        "input": wanted,
        "model_route": "xai/grok-best-available",
        "fallback": "grok-buddy-bridge",
        "reason": "no twin row; use Grok Buddy Bridge",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="buddy-bot")
    args = parser.parse_args()
    twins_doc = load_twins()
    result = route(args.slug, twins_doc)
    sample = [route(row["source_slug"], twins_doc) for row in twins_doc.get("twins", [])[:25]]
    payload = {
        "schema": "dreamco.grok_twin_route.v1",
        "query": result,
        "sample_routes": sample,
        "twin_count": twins_doc.get("twin_count", 0),
        "truth_boundary": "Routing selects a Grok twin profile. It does not train weights or prove frontier parity.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") or twins_doc.get("twin_count", 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
