#!/usr/bin/env python3
"""Run an original bot from its note. Live money actions stay off."""
from __future__ import annotations

import json
from pathlib import Path

from original_bots import BLOCKED, ask, catalog


def run(root: Path, bot_id: str, task: str) -> dict:
    made = catalog(root)
    wanted = (bot_id or "").strip().lower()
    bot = next((item for item in made["bots"] if item["id"] == wanted or item["name"].lower() == wanted), None)
    if bot is None:
        return {"ok": False, "ran_live": False, "reason": "That original bot is not in the notes."}
    text = (root / bot["file"].split("/", 1)[1]).read_text(encoding="utf-8", errors="replace")
    result = ask(bot["file"], text, task)
    result["mission"] = bot["mission"]
    result["production"] = "answers from the original note"
    result["ran_live"] = False
    if result["ok"]:
        words = [word for word in task.lower().split() if len(word) > 3 and word not in BLOCKED]
        lines = []
        for line in text.splitlines():
            if words and any(word in line.lower() for word in words) and line.strip():
                lines.append(line.strip()[:180])
            if len(lines) == 5:
                break
        result["from_the_note"] = lines or [bot["mission"]]
    return result


def ready(root: Path) -> dict:
    made = catalog(root)
    return {
        "bots": made["count"],
        "systems": made["systems"],
        "income_notes": made["income_notes"],
        "production": "each bot answers from its original note",
        "ran_live": False,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    if not (root / "systems").is_dir():
        raise SystemExit("original notes are missing")
    report = ready(root)
    assert report["bots"] == 212 and report["ran_live"] is False
    sample = run(root, "master-bot-system", "list the features")
    assert sample["ok"] is True and sample["ran_live"] is False
    blocked = run(root, "crypto-mining-bot", "mine a coin")
    assert blocked["ok"] is False and blocked["ran_live"] is False
    print(json.dumps(report))
