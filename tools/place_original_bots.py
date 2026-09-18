#!/usr/bin/env python3
"""Place every original-bots catalog entry into the current App_bots divisions.

Does not delete historical files. Does not expand the 1,051 canonical count.
Outputs a placement ledger for review and sandbox promotion.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "original-bots"
APP = ROOT / "App_bots"
OUT_JSON = ROOT / "config" / "generated" / "original-bot-placement.json"
OUT_MD = ROOT / "reports" / "ORIGINAL_BOT_PLACEMENT.md"

TABLE_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\*?\*?([^|*]+?)\*?\*?\s*\|\s*(.+?)\s*\|\s*$",
    re.M,
)
HEADING = re.compile(r"^#\s+(.+)$", re.M)

CATEGORY_DEFAULT = {
    "category-1-digital-saas.md": "DreamAutomation",
    "category-2-finance-trading.md": "DreamFinance",
    "category-3-ecommerce-retail.md": "DreamRetail",
    "category-4-media-content.md": "DreamContent",
    "category-5-ai-robotics.md": "DreamAIInfra",
    "category-6-franchising-licensing.md": "DreamBizLaunch",
    "category-7-ecommerce-automation.md": "DreamRetail",
    "category-8-services-global.md": "DreamGlobal",
}

SYSTEM_DEFAULT = {
    "master-bot-system.md": "CommandCore",
    "saas-automation-bot.md": "DreamAutomation",
    "api-automation-bot.md": "DreamAIInfra",
    "crypto-mining-bot.md": "DreamCrypto",
    "import-export-bot.md": "DreamTrade",
    "drop-shipping-bot.md": "DreamRetail",
    "schools-coaching-bot.md": "DreamEducation",
    "penny-stock-trading-bot.md": "DreamFinance",
    "ai-leaps-robot-bot.md": "DreamAIInfra",
    "contracts-legal-bot.md": "DreamLegal",
    "youtube-streaming-bot.md": "DreamContent",
    "consulting-agency-bot.md": "DreamProServices",
}

KEYWORD_OWNERS = [
    ("real estate|property|mortgage|housing", "DreamRealEstate"),
    ("loan|credit|lending", "DreamLoans"),
    ("payment|stripe|checkout|wallet", "DreamPayments"),
    ("crypto|token|blockchain|mining", "DreamCrypto"),
    ("stock|trading|invest|hedge|forex", "DreamFinance"),
    ("legal|contract|license|compliance", "DreamLegal"),
    ("health|medical|wellness", "DreamHealth"),
    ("school|course|coach|tutor|education", "DreamEducation"),
    ("youtube|stream|content|blog|seo|publish", "DreamContent"),
    ("social|influencer|community", "DreamSocial"),
    ("import|export|trade|supplier|logistics", "DreamTrade"),
    ("transport|travel|fleet", "DreamTransport"),
    ("food|restaurant|kitchen", "DreamFood"),
    ("retail|shop|ecommerce|drop ?ship|affiliate|print-on-demand", "DreamRetail"),
    ("sales|funnel|lead|crm", "DreamSalesPro"),
    ("code|api|app builder|plugin|github", "DreamCodeLab"),
    ("robot|ai infra|model|automation plugin", "DreamAIInfra"),
    ("saas|subscription|workflow|scheduler", "DreamAutomation"),
    ("consult|agency|franchise", "DreamProServices"),
    ("art|design|brand|music|film", "DreamArts"),
]


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:120] or "legacy-bot"


def infer_owner(text: str, fallback: str) -> str:
    blob = text.lower()
    for pattern, owner in KEYWORD_OWNERS:
        if re.search(pattern, blob):
            return owner
    return fallback


def canonical_slugs() -> set[str]:
    slugs: set[str] = set()
    if not APP.exists():
        return slugs
    for path in APP.glob("*.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for bot in doc.get("bots", []) if isinstance(doc, dict) else []:
            if isinstance(bot, dict) and bot.get("slug"):
                slugs.add(slugify(str(bot["slug"])))
            elif isinstance(bot, str):
                slugs.add(slugify(bot))
    return slugs


def parse_category(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fallback = CATEGORY_DEFAULT.get(path.name, "DreamAgents")
    rows = []
    for match in TABLE_ROW.finditer(text):
        number, name, mission = match.group(1), match.group(2).strip(), match.group(3).strip()
        owner = infer_owner(f"{name} {mission} {path.name}", fallback)
        rows.append({
            "kind": "income_network_bot",
            "source": str(path.relative_to(ROOT)),
            "index": int(number),
            "display_name": name,
            "slug": slugify(name),
            "mission": mission,
            "primary_division": owner,
            "fallback_division": fallback,
        })
    return rows


def parse_system(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    heading = HEADING.search(text)
    name = heading.group(1).strip() if heading else path.stem.replace("-", " ").title()
    fallback = SYSTEM_DEFAULT.get(path.name, "CommandCore")
    owner = infer_owner(f"{name} {path.name} {text[:1500]}", fallback)
    return {
        "kind": "major_system",
        "source": str(path.relative_to(ROOT)),
        "display_name": name,
        "slug": slugify(path.stem),
        "mission": "Historical 200-feature system archive; promote capabilities into shared fleet, do not fork a second OS.",
        "primary_division": owner,
        "fallback_division": fallback,
        "feature_claim": 200,
    }


def classify(row: dict, canonical: set[str]) -> str:
    slug = row["slug"]
    if slug in canonical:
        return "already_canonical"
    stem = slug.replace("-bot", "")
    if any(stem and stem in item for item in canonical):
        return "merge_review"
    return "place_as_supplemental"


def main() -> int:
    canonical = canonical_slugs()
    placements: list[dict] = []
    network = ORIGINAL / "autonomous-income-network"
    systems = ORIGINAL / "systems"
    if network.exists():
        for path in sorted(network.glob("category-*.md")):
            placements.extend(parse_category(path))
    if systems.exists():
        for path in sorted(systems.glob("*.md")):
            placements.append(parse_system(path))
    for row in placements:
        row["placement_state"] = classify(row, canonical)
        row["runtime_target"] = "runtime/compiled_bots" if row["kind"] == "income_network_bot" else "systems/" + row["primary_division"]
        row["promotion_gates"] = [
            "identity_unique",
            "division_confirmed",
            "sandbox_only",
            "focused_tests",
            "no_live_money_or_outreach",
        ]
        row["canonical_counted"] = False

    by_division: dict[str, int] = {}
    by_state: dict[str, int] = {}
    for row in placements:
        by_division[row["primary_division"]] = by_division.get(row["primary_division"], 0) + 1
        by_state[row["placement_state"]] = by_state.get(row["placement_state"], 0) + 1

    payload = {
        "schema": "dreamco.original_bot_placement.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "original-bots",
        "canonical_baseline_preserved": 1051,
        "placed_count": len(placements),
        "by_division": by_division,
        "by_state": by_state,
        "placements": placements,
        "truth_boundary": "Placement is an owner map, not a live fleet expansion or proof the old implementation still runs.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Original Bot Intelligent Placement",
        "",
        f"- Placed records: **{len(placements)}**",
        f"- Canonical App_bots baseline stays **1051** (not incremented by this ledger)",
        "",
        "## By division",
        "",
    ]
    for division, count in sorted(by_division.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {division}: {count}")
    lines += ["", "## By state", ""]
    for state, count in sorted(by_state.items()):
        lines.append(f"- {state}: {count}")
    lines += ["", "## Ledger", "", "| Name | Division | State | Source |", "| --- | --- | --- | --- |"]
    for row in placements:
        lines.append(
            f"| {row['display_name']} | {row['primary_division']} | {row['placement_state']} | `{row['source']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "placed": len(placements), "by_division": by_division, "by_state": by_state}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
