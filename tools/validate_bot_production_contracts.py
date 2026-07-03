#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECIALIZATIONS_PATH = REPO_ROOT / "config" / "generated" / "bot_specializations.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(payload: dict[str, Any]) -> list[str]:
    constraints = payload.get("constraints", {})
    required_sections = constraints.get("required_production_contract_sections") or []
    shared_webhooks = (
        payload.get("shared_capability_library", {})
        .get("webhook_library", {})
        .get("required_for_every_bot", [])
    )
    shared_apis = (
        payload.get("shared_capability_library", {})
        .get("api_library", {})
        .get("required_for_every_bot", [])
    )
    model_count = int(payload.get("top_model_training_catalog", {}).get("count", 0))

    issues: list[str] = []
    for idx, bot in enumerate(payload.get("bots", [])):
        slug = bot.get("slug", f"index-{idx}")
        contract = bot.get("production_contract")
        if not isinstance(contract, dict):
            issues.append(f"{slug}: missing production_contract object")
            continue

        if not contract.get("enforced"):
            issues.append(f"{slug}: production_contract.enforced must be true")

        for section in required_sections:
            if section not in contract:
                issues.append(f"{slug}: missing production contract section '{section}'")

        shared = contract.get("shared_webhook_coverage", {})
        shared_ids = shared.get("shared_required_ids") or []
        missing_shared_webhooks = sorted(set(shared_webhooks) - set(shared_ids))
        if missing_shared_webhooks:
            issues.append(
                f"{slug}: shared webhook coverage missing ids {missing_shared_webhooks[:3]}"
            )

        builders = contract.get("builder_systems", {})
        shared_api_ids = builders.get("shared_api_ids") or []
        missing_shared_apis = sorted(set(shared_apis) - set(shared_api_ids))
        if missing_shared_apis:
            issues.append(f"{slug}: shared api coverage missing ids {missing_shared_apis[:3]}")

        if not contract.get("self_learning", {}).get("promptable_learning_enabled"):
            issues.append(f"{slug}: self_learning.promptable_learning_enabled must be true")

        if int(contract.get("self_learning", {}).get("top_model_count", 0)) != model_count:
            issues.append(f"{slug}: self_learning.top_model_count must equal training catalog count")

        if contract.get("data_storage_policy", {}).get("mode") != "local_first":
            issues.append(f"{slug}: data_storage_policy.mode must be local_first")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated bot production contracts.")
    parser.add_argument(
        "--input",
        type=Path,
        default=SPECIALIZATIONS_PATH,
        help="Path to generated bot_specializations.json",
    )
    parser.add_argument("--json", action="store_true", help="Print validation output as JSON")
    args = parser.parse_args()

    payload = _load(args.input)
    issues = _validate(payload)
    result = {
        "input": str(args.input.relative_to(REPO_ROOT) if args.input.is_absolute() else args.input),
        "issue_count": len(issues),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    elif issues:
        print("❌ Bot production contract validation failed:")
        for issue in issues:
            print(f" - {issue}")
    else:
        print("✅ Bot production contract validation passed.")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
