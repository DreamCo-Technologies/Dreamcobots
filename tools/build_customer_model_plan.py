#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from foundry.customer_model_builder import TRACKS, build_plan

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "customer-model-plans.json"
REPORT = ROOT / "reports" / "CUSTOMER_MODEL_BUILDER.md"
LABS = ROOT / "config" / "public-lab-learning-methods.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--specialty", default="coding")
    args = parser.parse_args()
    labs = json.loads(LABS.read_text(encoding="utf-8"))
    plans = [build_plan(track, args.specialty) for track in TRACKS]
    payload = {
        "labs_studied": len(labs["labs"]),
        "rule": labs["rule"],
        "plans": plans,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Customer Model Builder", "", labs["rule"], "", f"Labs studied: **{len(labs['labs'])}**", ""]
    for lab in labs["labs"]:
        lines.append(f"- {lab['org']} ({lab['region']}): {', '.join(lab['methods'])}")
    lines += ["", "## Tracks", ""]
    for plan in plans:
        lines.append(f"- `{plan['track']}` → {plan['base']}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "tracks": list(TRACKS), "labs": len(labs["labs"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
