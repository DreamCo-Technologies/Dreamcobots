#!/usr/bin/env python3
"""Generate Buddy's public multi-device distribution and service catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.launch import BuddyDistributionService


CONFIG_OUT = ROOT / "config" / "generated" / "buddy_distribution_catalog.json"
WEB_OUT = ROOT / "website" / "data" / "buddy-distribution-catalog.json"
REPORT_OUT = ROOT / "reports" / "BUDDY_DISTRIBUTION_CATALOG.md"


def build_catalog() -> dict:
    return BuddyDistributionService.catalog()


def stable_json(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_report(catalog: dict) -> str:
    summary = catalog["summary"]
    lines = [
        "# Buddy Distribution Catalog",
        "",
        "Buddy can serve the HTTPS web app immediately and prepare governed packaging and publishing plans for native targets.",
        "",
        "## Coverage",
        "",
        f"- Distribution targets: {summary['targets']}",
        f"- Target families: {summary['families']}",
        f"- Launch service packages: {summary['services']}",
        f"- Immediately available web/install routes: {summary['available_now']}",
        "",
        "## Boundaries",
        "",
        "No single native package runs on every device. Native stores require target-specific builds, owner-controlled accounts, provider terms, review, and fees where applicable. This catalog prepares release evidence; it does not claim automatic acceptance or completed paid delivery.",
        "",
        "## Targets",
        "",
        "| Target | Family | Install mode | Status |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {target['name']} | {target['family']} | {target['install_mode']} | {target['public_status']} |"
        for target in catalog["targets"]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = build_catalog()
    outputs = (
        (CONFIG_OUT, stable_json(catalog)),
        (WEB_OUT, stable_json(catalog)),
        (REPORT_OUT, build_report(catalog)),
    )
    if args.check:
        for path, expected in outputs:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated output is stale: {path.relative_to(ROOT)}")
    else:
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(json.dumps({"ok": True, **catalog["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
