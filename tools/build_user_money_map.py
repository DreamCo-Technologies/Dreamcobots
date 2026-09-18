#!/usr/bin/env python3
"""Map every App_bots slug to Grok + legal user-earning offers. No live Stripe."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "App_bots"
TYPES = ROOT / "config" / "user-money-offer-types.json"
OUT = ROOT / "config" / "generated" / "user-money-map.json"
REPORT = ROOT / "reports" / "USER_MONEY_MAP.md"

HINTS = [
    ("game|unity|unreal|play", ["sell-game-kit", "sell-prototype"]),
    ("app|mobile|saas|website", ["sell-app-kit", "sell-prototype"]),
    ("job|career|resume|interview|occupation", ["sell-job-sim", "sell-learning-strategy"]),
    ("learn|course|tutor|coach|school", ["sell-learning-strategy"]),
    ("business|startup|launch|franchise", ["sell-biz-launch", "sell-bot-build"]),
    ("real.?estate|propert", ["sell-biz-launch", "done-for-you-sandbox"]),
    ("sales|lead|funnel", ["subscription-buddy", "done-for-you-sandbox"]),
    ("code|debug|dev", ["sell-bot-build", "sell-app-kit"]),
    ("finance|loan|pay", ["subscription-buddy"]),
]


def offers_for(text: str) -> list[str]:
    hits = ["subscription-buddy", "sell-capability-pack"]
    blob = text.lower()
    for pattern, ids in HINTS:
        if re.search(pattern, blob):
            hits.extend(ids)
    out = []
    for item in hits:
        if item not in out:
            out.append(item)
    return out[:6]


def main() -> int:
    types = json.loads(TYPES.read_text(encoding="utf-8"))
    rows = []
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
                text = " ".join([
                    str(bot.get("slug")),
                    str(bot.get("displayName", "")),
                    str(bot.get("description", "")),
                    " ".join(bot.get("capabilities") or []),
                ])
                rows.append({
                    "slug": bot["slug"],
                    "division": division,
                    "grok_slug": f"grok-{bot['slug']}"[:140],
                    "model_route": "xai/grok-best-available",
                    "offers": offers_for(text),
                    "stripe": "sandbox_only",
                    "autonomous_live_money": False,
                    "24h_test": "sandbox_soak",
                })
    payload = {
        "schema": "dreamco.user_money_map.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bot_count": len(rows),
        "offer_type_count": len(types["offer_types"]),
        "approx_offer_rows": sum(len(row["offers"]) for row in rows),
        "stripe": types["stripe_default"],
        "gate": types["live_revenue_gate"],
        "bots": rows,
        "truth": "This is a catalog of legal user-earning paths. It is not thousands of live Stripe charges and not autonomous ad spend.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# User Money Map",
        "",
        f"- Bots mapped: **{len(rows)}**",
        f"- Offer assignments: **{payload['approx_offer_rows']}**",
        "- Stripe: **sandbox_only** until live-revenue-gate + owner enable",
        "- 24h test: sandbox soak, not live checkout",
        "",
        "| Bot | Grok twin | Offers |",
        "| --- | --- | --- |",
    ]
    for row in rows[:80]:
        lines.append(f"| `{row['slug']}` | `{row['grok_slug']}` | {', '.join(row['offers'])} |")
    if len(rows) > 80:
        lines.append(f"| … | {len(rows) - 80} more | … |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bots": len(rows), "offers": payload["approx_offer_rows"], "stripe": "sandbox_only"}))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
