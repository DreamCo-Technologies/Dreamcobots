#!/usr/bin/env python3
"""Generate Buddy's app category catalog and comparison system."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "dreamco_app_category_catalog.json"
INVENTORY_FILE = ROOT / "reports" / "buddy_capability_inventory.json"
OUTPUT_JSON = ROOT / "reports" / "app_category_catalog.json"
OUTPUT_MD = ROOT / "reports" / "APP_CATEGORY_CATALOG.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def keyword_matches(category: dict[str, Any], bot: dict[str, Any]) -> bool:
    terms = [category["id"], category["label"], *category.get("examples", [])]
    haystack = " ".join(
        str(value)
        for value in [
            bot.get("slug"),
            bot.get("name"),
            bot.get("category"),
            bot.get("description"),
            bot.get("division"),
            " ".join(str(cap) for cap in bot.get("capabilities", [])),
        ]
    ).lower()
    for term in terms:
        for token in str(term).replace("_", " ").replace("-", " ").lower().split():
            if len(token) >= 5 and token in haystack:
                return True
    return False


def build_catalog() -> dict[str, Any]:
    config = read_json(CONFIG_FILE, {})
    inventory = read_json(INVENTORY_FILE, {})
    bots = inventory.get("bots", [])
    categories = []

    for category in config.get("app_categories", []):
        matched_bots = [
            {
                "slug": bot.get("slug"),
                "name": bot.get("name"),
                "division": bot.get("division"),
                "category": bot.get("category"),
            }
            for bot in bots
            if keyword_matches(category, bot)
        ][:25]
        categories.append(
            {
                **category,
                "comparison_template": {
                    criterion: None for criterion in config.get("comparison_criteria", [])
                },
                "buddy_web_management": [
                    "research public app pages",
                    "compare public pricing and features",
                    "summarize reviews and risks",
                    "draft client recommendations",
                    "prepare approval packets before live actions",
                ],
                "buddy_device_management": [
                    "prepare install/setup checklist",
                    "compare permission risks",
                    "draft settings guidance",
                    "track client-approved app workflows",
                ],
                "matched_dreamco_bots": matched_bots,
                "matched_bot_count": len(matched_bots),
            }
        )

    return {
        "schema": "dreamco.app_category_catalog_report.v1",
        "generated_at": utc_now(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode"),
        "summary": {
            "app_categories": len(categories),
            "comparison_criteria": len(config.get("comparison_criteria", [])),
            "buddy_management_modes": len(config.get("buddy_management_modes", [])),
            "blocked_without_approval": len(config.get("blocked_without_approval", [])),
            "categories_with_matched_bots": sum(1 for category in categories if category["matched_bot_count"] > 0),
            "device_and_web_management_ready": True,
        },
        "comparison_criteria": config.get("comparison_criteria", []),
        "buddy_management_modes": config.get("buddy_management_modes", []),
        "blocked_without_approval": config.get("blocked_without_approval", []),
        "categories": categories,
        "client_workflows": [
            "Compare apps in a category by price, features, reviews, risk, privacy, and automation support.",
            "Ask Buddy to recommend the best app stack for a client goal.",
            "Ask Buddy to manage safe web research and device setup checklists.",
            "Ask Buddy to build a better in-house alternative when existing apps are weak.",
            "Ask Buddy to prepare approval packets before installs, purchases, account actions, or money movement.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# App Category Catalog",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- App categories: {summary['app_categories']}",
        f"- Comparison criteria: {summary['comparison_criteria']}",
        f"- Buddy management modes: {summary['buddy_management_modes']}",
        f"- Blocked without approval: {summary['blocked_without_approval']}",
        f"- Categories with matched DreamCo bots: {summary['categories_with_matched_bots']}",
        "",
        "## Categories",
        "",
    ]
    for category in report["categories"]:
        lines.append(
            f"- **{category['label']}** (`{category['id']}`): risk `{category['risk']}`, "
            f"matched bots `{category['matched_bot_count']}`"
        )
    lines.extend(["", "## Blocked Without Approval", ""])
    for item in report["blocked_without_approval"]:
        lines.append(f"- {item}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_catalog()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("app category catalog report missing; run the generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("app category catalog report stale; run the generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        "app_category_catalog_ready=True categories={categories} criteria={criteria} modes={modes}".format(
            categories=report["summary"]["app_categories"],
            criteria=report["summary"]["comparison_criteria"],
            modes=report["summary"]["buddy_management_modes"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

