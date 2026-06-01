#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = REPO_ROOT / "config" / "master_bot_registry.json"
DEFAULT_BOT_LIBRARY_PATH = REPO_ROOT / "bots" / "global_bot_network" / "bot_library.py"


def _load_registry(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registered_capabilities(bot_library_path: Path) -> set[str]:
    source = bot_library_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    capabilities: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "BotEntry":
            continue
        for keyword in node.keywords:
            if keyword.arg != "capabilities":
                continue
            if isinstance(keyword.value, ast.List):
                for item in keyword.value.elts:
                    if isinstance(item, ast.Constant) and isinstance(item.value, str):
                        capabilities.add(item.value)
    return capabilities


def audit_capabilities(
    registry: dict[str, Any], registered_capabilities: set[str]
) -> list[str]:
    bots = registry.get("bots")
    if not isinstance(bots, list):
        return ["master registry must contain a 'bots' array"]

    issues: list[str] = []
    for index, bot in enumerate(bots):
        bot_id = str(bot.get("id", f"bot[{index}]"))
        capabilities = bot.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            issues.append(f"{bot_id}: empty capability list")
            continue

        seen: set[str] = set()
        for cap_index, capability in enumerate(capabilities):
            intent = capability.get("intent") if isinstance(capability, dict) else None
            if not isinstance(intent, str) or not intent.strip():
                issues.append(f"{bot_id}: capability[{cap_index}] missing intent")
                continue

            if intent in seen:
                issues.append(f"{bot_id}: duplicate capability '{intent}'")
            else:
                seen.add(intent)

            if intent not in registered_capabilities:
                issues.append(f"{bot_id}: unregistered capability '{intent}'")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit capability health for DreamCo bots.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Path to master bot registry JSON.",
    )
    parser.add_argument(
        "--bot-library",
        type=Path,
        default=DEFAULT_BOT_LIBRARY_PATH,
        help="Path to bot library Python file with registered capabilities.",
    )
    parser.add_argument("--json", action="store_true", help="Print findings as JSON.")
    args = parser.parse_args()

    registry = _load_registry(args.registry)
    registered = load_registered_capabilities(args.bot_library)
    issues = audit_capabilities(registry, registered)

    payload = {
        "registry": str(args.registry),
        "bot_library": str(args.bot_library),
        "registered_capability_count": len(registered),
        "issue_count": len(issues),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    elif issues:
        print("❌ Capability audit failed:")
        for issue in issues:
            print(f" - {issue}")
    else:
        print("✅ Capability audit passed.")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
