#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = REPO_ROOT / "config" / "master_bot_registry.json"


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _load_registry(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bot_registry(registry: dict[str, Any]) -> list[str]:
    bots = registry.get("bots")
    if not isinstance(bots, list):
        return ["master registry must contain a 'bots' array"]

    seen_ids: dict[str, int] = {}
    seen_slugs: dict[str, int] = {}
    issues: list[str] = []

    for index, bot in enumerate(bots):
        bot_id = str(bot.get("id", "")).strip()
        if not bot_id:
            issues.append(f"bot[{index}] missing required id")
        elif bot_id in seen_ids:
            issues.append(
                f"duplicate bot ID '{bot_id}' (indexes {seen_ids[bot_id]} and {index})"
            )
        else:
            seen_ids[bot_id] = index

        slug = str(bot.get("slug") or _slugify(bot.get("id") or bot.get("name", ""))).strip()
        if not slug:
            issues.append(f"bot[{index}] missing slug (and unable to derive from id/name)")
        elif slug in seen_slugs:
            issues.append(
                f"duplicate slug '{slug}' (indexes {seen_slugs[slug]} and {index})"
            )
        else:
            seen_slugs[slug] = index

        category = bot.get("category") or bot.get("division")
        if not isinstance(category, str) or not category.strip():
            issues.append(f"bot[{index}] ({bot_id or 'unknown'}) missing category/division")

        capabilities = bot.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            issues.append(f"bot[{index}] ({bot_id or 'unknown'}) missing capabilities")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DreamCo bot registry consistency.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Path to master bot registry JSON.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print findings as JSON.",
    )
    args = parser.parse_args()

    registry = _load_registry(args.registry)
    issues = validate_bot_registry(registry)
    payload = {
        "registry": str(args.registry),
        "issue_count": len(issues),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    elif issues:
        print("❌ Bot registry validation failed:")
        for issue in issues:
            print(f" - {issue}")
    else:
        print("✅ Bot registry validation passed.")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
