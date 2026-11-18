"""Run DreamCo's read-only, clean-room repository evidence analyzer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.opensource import BuddyOpenSourceLab, OpenSourceError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, help="Local repository directory to analyze")
    parser.add_argument("--owner-authorized", action="store_true", help="Attest that you own or may analyze this repository")
    parser.add_argument("--customize", action="append", default=[], choices=(
        "audience", "workflow", "interface", "accessibility", "privacy", "security",
        "integrations", "performance", "cost", "original_features",
    ), help="DreamCo customization area; provide at least two")
    parser.add_argument("--differentiator", required=True, help="Describe the original DreamCo implementation (30+ characters)")
    args = parser.parse_args()
    try:
        report = BuddyOpenSourceLab().analyze_clean_room(
            args.repository,
            owner_authorized=args.owner_authorized,
            customizations=args.customize,
            differentiator=args.differentiator,
        )
    except OpenSourceError as error:
        parser.error(str(error))
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
