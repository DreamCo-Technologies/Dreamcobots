#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTS_DIR = REPO_ROOT / "bots"
OUTPUT_PATH = REPO_ROOT / "config" / "generated" / "bot_specializations.json"
TRACKING_PATH = REPO_ROOT / "config" / "generated" / "bot_specialization_tracking.json"

WEBHOOK_COUNT = 100
TOOL_COUNT = 100
API_COUNT = 100


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().strip()).strip("-")


def _load_profiles() -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for profile_path in sorted(BOTS_DIR.glob("*/replit_profile.json")):
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        payload["slug"] = payload.get("slug") or profile_path.parent.name
        payload["displayName"] = payload.get("displayName") or payload["slug"].replace("-", " ").title()
        payload["profile_path"] = str(profile_path.relative_to(REPO_ROOT))
        profiles.append(payload)
    return profiles


def _capability_seed(profile: dict[str, Any], index: int) -> str:
    capabilities = profile.get("capabilities") or []
    if capabilities:
        return _slug(str(capabilities[index % len(capabilities)])) or f"{profile['slug']}-core"
    return f"{profile['slug']}-core"


def _resource_ids(slug: str, prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{slug}-{idx:03d}" for idx in range(1, count + 1)]


def _hash(values: list[str]) -> str:
    joined = "|".join(values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _resource_contract(profile: dict[str, Any], kind: str, prefix: str, count: int, offset: int) -> dict[str, Any]:
    slug = profile["slug"]
    ids = _resource_ids(slug, prefix, count)
    seeds = [_capability_seed(profile, idx + offset) for idx in range(count)]
    unique_seed_count = len(set(seeds))

    return {
        "count": count,
        "id_pattern": f"{prefix}-{slug}-{{index:03d}}",
        "specialization_pattern": f"{kind}.{slug}.{{capability_seed}}.{{index:03d}}",
        "tracking_namespace": f"tracking:{kind}:{prefix}-{slug}-",
        "ids_hash": _hash(ids),
        "seed_hash": _hash(seeds),
        "preview": {
            "first": ids[0],
            "middle": ids[count // 2],
            "last": ids[-1],
            "sample_seeds": [seeds[0], seeds[1], seeds[2], seeds[-1]],
        },
        "uniqueness": {
            "ids_unique_within_bot": len(set(ids)) == count,
            "capability_seed_unique_count": unique_seed_count,
        },
    }


def _build_specializations(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    bots: list[dict[str, Any]] = []

    for profile in profiles:
        webhook_contract = _resource_contract(profile, "webhook", "wh", WEBHOOK_COUNT, 0)
        tool_contract = _resource_contract(profile, "tool", "tool", TOOL_COUNT, 25)
        api_contract = _resource_contract(profile, "api", "api", API_COUNT, 50)
        bots.append(
            {
                "slug": profile["slug"],
                "displayName": profile["displayName"],
                "division": profile.get("division", "unknown"),
                "tier": profile.get("tier", "unknown"),
                "version": profile.get("version", "1.0"),
                "profile_path": profile["profile_path"],
                "webhooks": webhook_contract,
                "tools": tool_contract,
                "apis": api_contract,
                "resource_total": WEBHOOK_COUNT + TOOL_COUNT + API_COUNT,
            }
        )

    return {
        "schema": "dreamco.bot_specializations.v2",
        "generated_at": generated_at,
        "source": "bots/*/replit_profile.json",
        "constraints": {
            "per_bot_webhooks": WEBHOOK_COUNT,
            "per_bot_tools": TOOL_COUNT,
            "per_bot_apis": API_COUNT,
            "unique_per_bot": True,
            "globally_unique_ids": True,
            "tracked_with_hashes": True,
        },
        "bot_count": len(bots),
        "bots": bots,
    }


def _build_tracking(specializations: dict[str, Any]) -> dict[str, Any]:
    webhook_hashes: set[str] = set()
    tool_hashes: set[str] = set()
    api_hashes: set[str] = set()

    duplicates = {"webhooks": [], "tools": [], "apis": []}

    bot_summaries: list[dict[str, Any]] = []
    for bot in specializations["bots"]:
        wh_hash = bot["webhooks"]["ids_hash"]
        tool_hash = bot["tools"]["ids_hash"]
        api_hash = bot["apis"]["ids_hash"]

        if wh_hash in webhook_hashes:
            duplicates["webhooks"].append(bot["slug"])
        webhook_hashes.add(wh_hash)

        if tool_hash in tool_hashes:
            duplicates["tools"].append(bot["slug"])
        tool_hashes.add(tool_hash)

        if api_hash in api_hashes:
            duplicates["apis"].append(bot["slug"])
        api_hashes.add(api_hash)

        bot_summaries.append(
            {
                "slug": bot["slug"],
                "division": bot["division"],
                "profile_path": bot["profile_path"],
                "webhook_count": bot["webhooks"]["count"],
                "tool_count": bot["tools"]["count"],
                "api_count": bot["apis"]["count"],
                "resource_total": bot["resource_total"],
                "webhook_ids_hash": wh_hash,
                "tool_ids_hash": tool_hash,
                "api_ids_hash": api_hash,
            }
        )

    bot_count = specializations["bot_count"]

    return {
        "schema": "dreamco.bot_specialization_tracking.v2",
        "generated_at": specializations["generated_at"],
        "bot_count": bot_count,
        "totals": {
            "webhooks": bot_count * WEBHOOK_COUNT,
            "tools": bot_count * TOOL_COUNT,
            "apis": bot_count * API_COUNT,
            "all_resources": bot_count * (WEBHOOK_COUNT + TOOL_COUNT + API_COUNT),
        },
        "hash_uniqueness": {
            "webhook_hash_count": len(webhook_hashes),
            "tool_hash_count": len(tool_hashes),
            "api_hash_count": len(api_hashes),
        },
        "duplicates": duplicates,
        "bots": bot_summaries,
    }


def _expected_outputs() -> tuple[str, str]:
    profiles = _load_profiles()
    specializations = _build_specializations(profiles)
    tracking = _build_tracking(specializations)
    return json.dumps(specializations, indent=2) + "\n", json.dumps(tracking, indent=2) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate tracked per-bot webhook/tool/API specialization contracts."
    )
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale")
    args = parser.parse_args()

    specializations_text, tracking_text = _expected_outputs()

    if args.check:
        stale: list[str] = []
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != specializations_text:
            stale.append(str(OUTPUT_PATH.relative_to(REPO_ROOT)))
        if not TRACKING_PATH.exists() or TRACKING_PATH.read_text(encoding="utf-8") != tracking_text:
            stale.append(str(TRACKING_PATH.relative_to(REPO_ROOT)))
        if stale:
            print("Specialization outputs are stale. Re-run:")
            print("  python3 tools/generate_bot_specializations.py")
            for rel in stale:
                print(f"  - {rel}")
            return 1
        print("Bot specialization outputs are up to date.")
        return 0

    _write(OUTPUT_PATH, specializations_text)
    _write(TRACKING_PATH, tracking_text)

    print("Generated specialization outputs:")
    print(f"- {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"- {TRACKING_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
