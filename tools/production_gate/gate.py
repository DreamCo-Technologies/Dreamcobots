#!/usr/bin/env python3
"""Report what is actually in the repo. A passing file check is not a live bot."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "original-bots/systems/master-bot-system.md",
    "original-bots/systems/saas-automation-bot.md",
    "original-bots/systems/api-automation-bot.md",
    "original-bots/systems/crypto-mining-bot.md",
    "original-bots/systems/import-export-bot.md",
    "original-bots/systems/drop-shipping-bot.md",
    "original-bots/systems/schools-coaching-bot.md",
    "original-bots/systems/penny-stock-trading-bot.md",
    "original-bots/systems/ai-leaps-robot-bot.md",
    "original-bots/systems/contracts-legal-bot.md",
    "original-bots/systems/youtube-streaming-bot.md",
    "original-bots/systems/consulting-agency-bot.md",
    "buddy/learning/MODEL_CARD.md",
    "website/data/fleet-manifest.json",
]

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file() or (ROOT / p).stat().st_size < 40]
    skills = []
    easy = ROOT / "buddy" / "easy_github"
    if easy.is_dir():
        for path in sorted(easy.glob("skills_*.json")):
            skills.extend(json.loads(path.read_text(encoding="utf-8")).get("skills") or [])
    pastes = list((ROOT / "attached_assets").glob("*.txt")) if (ROOT / "attached_assets").is_dir() else []
    report = {
        "original_plans_present": len(REQUIRED) - len(missing),
        "original_plans_missing": missing,
        "pasted_source_notes": len(pastes),
        "beginner_replies": len({s.get("id") for s in skills}),
        "hugging_face_account_linked": False,
        "fleet_is_production_ready": False,
        "reason": "Plans and notes are files. They are not running products, and trading or mining plans stay plans.",
    }
    print(json.dumps(report, indent=2))
    return 0 if not missing else 1

if __name__ == "__main__":
    raise SystemExit(main())
