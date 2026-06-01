#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_REGISTRY_PATH = REPO_ROOT / "config" / "master_bot_registry.json"
CONTROL_TOWER_GENERATED_PATH = (
    REPO_ROOT / "dreamco-control-tower" / "config" / "generated" / "bots.catalog.json"
)
DIVISION_INDEX_PATH = REPO_ROOT / "divisions" / "generated" / "catalog_index.json"
CSV_EXPORT_PATH = REPO_ROOT / "config" / "generated" / "master_registry_export.csv"
README_PATH = REPO_ROOT / "README.md"

RISK_LEVELS = {"low", "medium", "high"}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _display(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _tier_for_bot(bot: dict[str, Any]) -> str:
    risks = {c.get("risk_level", "low") for c in bot.get("capabilities", [])}
    monetized = bool(bot.get("monetization", {}).get("enabled"))
    if "high" in risks and monetized:
        return "ELITE"
    if "high" in risks:
        return "ENTERPRISE"
    if "medium" in risks:
        return "PRO"
    return "FREE"


def _load_master() -> dict[str, Any]:
    return json.loads(MASTER_REGISTRY_PATH.read_text(encoding="utf-8"))


def _validate_master(registry: dict[str, Any]) -> None:
    if registry.get("schema") != "master_bot_registry.v1":
        raise ValueError("master registry schema must be 'master_bot_registry.v1'")
    bots = registry.get("bots")
    if not isinstance(bots, list):
        raise ValueError("master registry must contain a 'bots' array")

    seen_ids: set[str] = set()
    for bot in bots:
        for field in ("id", "name", "division", "status", "version", "capabilities"):
            if field not in bot:
                raise ValueError(f"bot missing required field '{field}': {bot}")

        bot_id = bot["id"]
        if bot_id in seen_ids:
            raise ValueError(f"duplicate bot id: {bot_id}")
        seen_ids.add(bot_id)

        if not isinstance(bot["capabilities"], list):
            raise ValueError(f"bot '{bot_id}' capabilities must be a list")

        seen_intents: set[str] = set()
        for capability in bot["capabilities"]:
            for field in (
                "intent",
                "enabled",
                "risk_level",
                "approval_required",
                "division",
                "revenue_generating",
                "spends_money",
            ):
                if field not in capability:
                    raise ValueError(
                        f"capability in '{bot_id}' missing required field '{field}'"
                    )

            intent = capability["intent"]
            if intent in seen_intents:
                raise ValueError(f"duplicate capability intent '{intent}' in bot '{bot_id}'")
            seen_intents.add(intent)

            if capability["risk_level"] not in RISK_LEVELS:
                raise ValueError(
                    f"capability '{bot_id}:{intent}' has invalid risk level "
                    f"'{capability['risk_level']}'"
                )
            if not isinstance(capability["enabled"], bool):
                raise ValueError(f"capability '{bot_id}:{intent}' enabled must be bool")
            if capability["spends_money"] and not capability["approval_required"]:
                raise ValueError(
                    f"capability '{bot_id}:{intent}' spends_money requires approval_required=true"
                )


def _build_control_tower_catalog(registry: dict[str, Any]) -> dict[str, Any]:
    bots = registry["bots"]
    generated_at = registry.get("updated_at") or datetime.now(timezone.utc).isoformat()
    out: list[dict[str, Any]] = []

    for bot in bots:
        enabled = [c for c in bot["capabilities"] if c.get("enabled")]
        out.append(
            {
                "bot_id": bot["id"],
                "name": bot["name"],
                "repoName": "Dreamcobots",
                "repoPath": f"./bots/{_slug(bot['id'])}",
                "status": bot["status"],
                "tier": _tier_for_bot(bot),
                "category": bot["division"],
                "description": f"{bot['name']} ({bot['division']})",
                "price_usd": 49 if bot.get("monetization", {}).get("enabled") else 0,
                "features": [c["intent"] for c in enabled],
                "lastHeartbeat": None,
                "lastUpdate": None,
                "pendingPRs": 0,
                "governance": {
                    "risk_level": bot.get("safety", {}).get("risk_level", "low"),
                    "approval_required": bool(
                        bot.get("safety", {}).get("approval_required", False)
                    ),
                    "monetization_enabled": bool(
                        bot.get("monetization", {}).get("enabled", False)
                    ),
                },
            }
        )

    return {
        "schema": "generated.control_tower_bots.v1",
        "generated_from": str(MASTER_REGISTRY_PATH.relative_to(REPO_ROOT)),
        "generated_at": generated_at,
        "editable": False,
        "bots": out,
    }


def _build_division_index(registry: dict[str, Any]) -> dict[str, Any]:
    generated_at = registry.get("updated_at") or datetime.now(timezone.utc).isoformat()
    division_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for bot in registry["bots"]:
        for capability in bot.get("capabilities", []):
            division = capability["division"]
            intent = capability["intent"]
            tier = (
                "Elite"
                if capability["risk_level"] == "high" and capability.get("revenue_generating")
                else "Enterprise"
                if capability["risk_level"] == "high"
                else "Pro"
                if capability["risk_level"] == "medium"
                else "Free"
            )
            price = "$199/mo" if capability.get("revenue_generating") else "$0/mo"
            division_entries[division].append(
                {
                    "botId": f"{bot['id']}__{_slug(intent)}",
                    "botName": f"{bot['name']} — {_display(intent)}",
                    "division": division,
                    "category": "Capability",
                    "tier": tier,
                    "price": price,
                    "description": (
                        f"{_display(intent)} capability powered by {bot['name']} "
                        f"with {capability['risk_level']} governance profile."
                    ),
                    "features": [
                        f"Intent: {intent}",
                        f"Risk: {capability['risk_level']}",
                        f"Approval required: {str(capability['approval_required']).lower()}",
                    ],
                    "sourceBotId": bot["id"],
                    "enabled": capability["enabled"],
                }
            )

    divisions = []
    all_bots: list[dict[str, Any]] = []
    for division, bots in sorted(division_entries.items(), key=lambda kv: kv[0].lower()):
        sorted_bots = sorted(bots, key=lambda item: item["botId"])
        divisions.append({"name": division, "count": len(sorted_bots), "bots": sorted_bots})
        all_bots.extend(sorted_bots)

    return {
        "schema": "generated.division_catalog_index.v1",
        "generated_from": str(MASTER_REGISTRY_PATH.relative_to(REPO_ROOT)),
        "generated_at": generated_at,
        "editable": False,
        "division_count": len(divisions),
        "total_bots": len(all_bots),
        "divisions": divisions,
        "all_bots": all_bots,
    }


def _build_export_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bot in registry["bots"]:
        for capability in bot.get("capabilities", []):
            rows.append(
                {
                    "bot_id": bot["id"],
                    "bot_name": bot["name"],
                    "bot_division": bot["division"],
                    "bot_status": bot["status"],
                    "bot_version": bot["version"],
                    "capability_intent": capability["intent"],
                    "capability_division": capability["division"],
                    "capability_enabled": capability["enabled"],
                    "risk_level": capability["risk_level"],
                    "approval_required": capability["approval_required"],
                    "revenue_generating": capability["revenue_generating"],
                    "spends_money": capability["spends_money"],
                }
            )
    return rows


def _update_readme(registry: dict[str, Any], existing: str) -> str:
    bot_count = len(registry["bots"])
    divisions = {
        bot["division"] for bot in registry["bots"]
    } | {
        capability["division"]
        for bot in registry["bots"]
        for capability in bot.get("capabilities", [])
    }
    division_count = len(divisions)

    tier_counts = Counter(_tier_for_bot(bot).lower() for bot in registry["bots"])

    updated = existing
    updated = re.sub(
        r"> \*\*.*?AI bots · .*? divisions ·",
        f"> **{bot_count} AI bots · {division_count} divisions ·",
        updated,
        count=1,
    )
    updated = re.sub(
        r"Active%20Bots-\d+",
        f"Active%20Bots-{bot_count}",
        updated,
        count=1,
    )
    updated = re.sub(
        r"Divisions-\d+",
        f"Divisions-{division_count}",
        updated,
        count=1,
    )
    updated = re.sub(
        r"## 🏢 Divisions \(\d+\)",
        f"## 🏢 Divisions ({division_count})",
        updated,
        count=1,
    )

    tier_block = "\n".join(
        [
            f"- **free**: {tier_counts.get('free', 0)} bots",
            f"- **pro**: {tier_counts.get('pro', 0)} bots",
            f"- **enterprise**: {tier_counts.get('enterprise', 0)} bots",
            f"- **elite**: {tier_counts.get('elite', 0)} bots",
        ]
    )
    updated = re.sub(
        r"## 💰 Bot Tiers\n(?:- \*\*.*\*\*: .* bots\n){4}",
        f"## 💰 Bot Tiers\n{tier_block}\n",
        updated,
        count=1,
    )
    return updated


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        if headers:
            writer.writeheader()
            writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate all downstream bot catalogs from config/master_bot_registry.json"
    )
    parser.add_argument("--check", action="store_true", help="Fail if outputs are stale")
    args = parser.parse_args()

    registry = _load_master()
    _validate_master(registry)

    catalog = _build_control_tower_catalog(registry)
    division_index = _build_division_index(registry)
    export_rows = _build_export_rows(registry)
    readme_new = _update_readme(registry, README_PATH.read_text(encoding="utf-8"))

    desired_files: dict[Path, str] = {
        CONTROL_TOWER_GENERATED_PATH: json.dumps(catalog, indent=2) + "\n",
        DIVISION_INDEX_PATH: json.dumps(division_index, indent=2) + "\n",
        README_PATH: readme_new,
    }

    csv_headers = list(export_rows[0].keys()) if export_rows else []
    csv_lines = []
    if csv_headers:
        csv_lines.append(",".join(csv_headers))
        for row in export_rows:
            csv_lines.append(",".join(str(row[h]) for h in csv_headers))
    desired_files[CSV_EXPORT_PATH] = "\n".join(csv_lines) + ("\n" if csv_lines else "")

    if args.check:
        stale: list[str] = []
        for path, expected in desired_files.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(REPO_ROOT)))
        if stale:
            print("Generated outputs are stale. Re-run:")
            print("  python3 tools/generate_master_registry_outputs.py")
            for rel in stale:
                print(f"  - {rel}")
            return 1
        print("Generated master registry outputs are up to date.")
        return 0

    _write_json(CONTROL_TOWER_GENERATED_PATH, catalog)
    _write_json(DIVISION_INDEX_PATH, division_index)
    _write_csv(CSV_EXPORT_PATH, export_rows)
    README_PATH.write_text(readme_new, encoding="utf-8")

    print("Generated registry outputs:")
    print(f"- {CONTROL_TOWER_GENERATED_PATH.relative_to(REPO_ROOT)}")
    print(f"- {DIVISION_INDEX_PATH.relative_to(REPO_ROOT)}")
    print(f"- {CSV_EXPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"- {README_PATH.relative_to(REPO_ROOT)} (counts refreshed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
