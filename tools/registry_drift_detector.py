"""Detect drift between bot profile directories and generated registries."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "drift_report.json"


def parse_seed_bots() -> set[str]:
    seed_file = ROOT / "empire-os" / "server" / "seed-bots.ts"
    text = seed_file.read_text()
    return set(re.findall(r'bot\("([a-z0-9-]+)"', text)) | set(re.findall(r'slug:\s*"([a-z0-9-]+)"', text))


def parse_profiles() -> set[str]:
    return {path.parent.name for path in (ROOT / "bots").glob("*/bot_profile.json")}


def parse_master_registry() -> set[str]:
    payload = json.loads((ROOT / "config" / "master_bot_registry.json").read_text())
    return {str(bot["slug"]) for bot in payload["bots"]}


def parse_control_tower_catalog() -> set[str]:
    payload = json.loads(
        (ROOT / "dreamco-control-tower" / "config" / "generated" / "bots.catalog.json").read_text()
    )
    return {str(bot["slug"]) for bot in payload["bots"]}


def main() -> None:
    seed = parse_seed_bots()
    profiles = parse_profiles()
    registry = parse_master_registry()
    catalog = parse_control_tower_catalog()
    payload = {
        "profile_count": len(profiles),
        "registry_count": len(registry),
        "catalog_count": len(catalog),
        "seed_count": len(seed),
        "registry_only": sorted(registry - profiles),
        "profile_only": sorted(profiles - registry),
        "catalog_only": sorted(catalog - profiles),
        "missing_from_catalog": sorted(profiles - catalog),
        "seed_only": sorted(seed - profiles),
        "not_in_seed": sorted(profiles - seed),
    }
    payload["drift"] = (
        len(payload["registry_only"])
        + len(payload["profile_only"])
        + len(payload["catalog_only"])
        + len(payload["missing_from_catalog"])
        + len(payload["seed_only"])
    )
    REPORT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["drift"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
