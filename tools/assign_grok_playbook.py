#!/usr/bin/env python3
"""Attach Grok learn/earn playbooks to every App_bots slug."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "App_bots"
V1 = ROOT / "config" / "grok-help-playbook.json"
V2 = ROOT / "config" / "grok-help-playbook-vol2.json"
OUT = ROOT / "config" / "generated" / "grok-playbook-by-bot.json"
REPORT = ROOT / "reports" / "GROK_PLAYBOOK_BY_BOT.md"


def load_play(path: Path) -> dict:
    if not path.exists():
        return {"learn": [], "earn": []}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    learn, earn = [], []
    for path in (V1, V2):
        doc = load_play(path)
        learn.extend(doc.get("learn", []))
        earn.extend(doc.get("earn", []))
    # de-dupe preserve order
    def uniq(items: list[str]) -> list[str]:
        seen, out = set(), []
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out
    learn, earn = uniq(learn), uniq(earn)
    bots = []
    if APP.exists():
        for path in sorted(APP.glob("*.json")):
            if path.name.startswith("masterbots"):
                continue
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            division = doc.get("division") or path.stem
            for bot in doc.get("bots", []) if isinstance(doc, dict) else []:
                if not isinstance(bot, dict) or not bot.get("slug"):
                    continue
                bots.append({
                    "slug": bot["slug"],
                    "division": division,
                    "grok_slug": f"grok-{bot['slug']}"[:140],
                    "learn_count": len(learn),
                    "earn_count": len(earn),
                    "learn": learn,
                    "earn": earn,
                    "live_money": False,
                })
    payload = {
        "schema": "dreamco.grok_playbook_by_bot.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bot_count": len(bots),
        "learn_actions": len(learn),
        "earn_actions": len(earn),
        "assignments": bots,
        "truth": "Every bot gets the same Grok playbook plus its own mission. Live charges stay off.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Grok playbook by bot",
        "",
        f"- Bots: **{len(bots)}**",
        f"- Learn actions each: **{len(learn)}**",
        f"- Earn actions each: **{len(earn)}**",
        "",
        "| Bot | Division | Grok |",
        "| --- | --- | --- |",
    ]
    for row in bots[:120]:
        lines.append(f"| `{row['slug']}` | {row['division']} | `{row['grok_slug']}` |")
    if len(bots) > 120:
        lines.append(f"| … | {len(bots) - 120} more | … |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bots": len(bots), "learn": len(learn), "earn": len(earn)}))
    return 0 if bots else 1


if __name__ == "__main__":
    raise SystemExit(main())
