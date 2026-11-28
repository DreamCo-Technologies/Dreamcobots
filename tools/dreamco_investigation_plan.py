"""Create a bounded DreamCo investigation plan for an authorized artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.opensource import BuddyOpenSourceLab, OpenSourceError  # noqa: E402

TARGET_KINDS = ("code_repository", "open_weights_model", "frontier_model_api", "website", "mobile_app", "game", "film_or_media", "general_api")
CUSTOMIZATIONS = ("audience", "workflow", "interface", "accessibility", "privacy", "security", "integrations", "performance", "cost", "original_features")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_kind", choices=TARGET_KINDS)
    parser.add_argument("target_reference", help="Local file/path or credential-free HTTPS URL")
    parser.add_argument("--owner-authorized", action="store_true")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--customize", action="append", choices=CUSTOMIZATIONS, default=[])
    parser.add_argument("--differentiator", required=True)
    parser.add_argument("--revision", default="", help="Required for repositories and open-weight models")
    parser.add_argument("--execution-requested", action="store_true", help="Records intent only; does not start execution")
    parser.add_argument("--allow-network", action="store_true", help="Records intent only; an adapter and separate approval remain required")
    parser.add_argument("--max-cost-usd", type=float, default=0)
    args = parser.parse_args()
    try:
        plan = BuddyOpenSourceLab().investigation_plan(
            args.target_kind, args.target_reference, owner_authorized=args.owner_authorized,
            written_scope=args.scope, customizations=args.customize,
            differentiator=args.differentiator, revision=args.revision,
            execution_requested=args.execution_requested, allow_network=args.allow_network,
            max_cost_usd=args.max_cost_usd,
        )
    except (OpenSourceError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    json.dump(plan, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
