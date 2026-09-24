#!/usr/bin/env python3
"""Read the original bot notes. Do not run mining, trading, or payments."""
from __future__ import annotations

import json
import re
from pathlib import Path

SYSTEMS = [
    "ai-leaps-robot-bot.md",
    "api-automation-bot.md",
    "consulting-agency-bot.md",
    "contracts-legal-bot.md",
    "crypto-mining-bot.md",
    "drop-shipping-bot.md",
    "import-export-bot.md",
    "master-bot-system.md",
    "penny-stock-trading-bot.md",
    "saas-automation-bot.md",
    "schools-coaching-bot.md",
    "youtube-streaming-bot.md",
]
CATEGORIES = [f"category-{n}.md" for n in [
    "1-digital-saas",
    "2-finance-trading",
    "3-ecommerce-retail",
    "4-media-content",
    "5-ai-robotics",
    "6-franchising-licensing",
    "7-ecommerce-automation",
    "8-services-global",
]]
BLOCKED = ("mine", "trade", "buy", "sell", "pay", "send", "wire", "order")
TITLE = re.compile(r"^#\s+(.+)$", re.M)


def ask(name: str, text: str, task: str = "") -> dict:
    title = TITLE.search(text or "")
    if title is None:
        return {"ok": False, "reason": "The original note has no title."}
    words = (task or "").lower()
    if any(word in words.split() for word in BLOCKED):
        return {
            "ok": False,
            "title": title.group(1).strip(),
            "reason": "The original file is a feature note. It does not mine, trade, pay, or send anything.",
        }
    return {
        "ok": True,
        "title": title.group(1).strip(),
        "file": name,
        "ran_live": False,
        "reason": "Read the original note. Nothing was bought, sold, mined, or sent.",
    }


def inventory(root: Path) -> dict:
    missing = []
    found = []
    for folder, names in (("systems", SYSTEMS), ("autonomous-income-network", CATEGORIES)):
        for name in names:
            path = root / folder / name
            if not path.is_file() or TITLE.search(path.read_text(encoding="utf-8", errors="replace")) is None:
                missing.append(str(path))
            else:
                found.append(str(path))
    return {"found": len(found), "missing": missing, "expected": len(SYSTEMS) + len(CATEGORIES)}


if __name__ == "__main__":
    sample = "# DreamCo Master Bot System\n\n> Mission: coordinate the other notes.\n"
    assert ask("master-bot-system.md", sample, "list the features")["ok"] is True
    assert ask("crypto-mining-bot.md", sample, "mine a coin")["ok"] is False
    root = Path(__file__).resolve().parent
    report = inventory(root) if (root / "systems").is_dir() else {"found": 0, "expected": len(SYSTEMS) + len(CATEGORIES), "missing": []}
    print(json.dumps({"systems": len(SYSTEMS), "categories": len(CATEGORIES), "found": report["found"], "live": False}))
