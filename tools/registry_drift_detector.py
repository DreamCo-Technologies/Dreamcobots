"""Detect drift between seed-bots.ts and bot profile directories."""

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
    return {path.parent.name for path in (ROOT / "bots").glob("*/replit_profile.json")}


def main() -> None:
    seed = parse_seed_bots()
    profiles = parse_profiles()
    missing_from_bots = sorted(seed - profiles)
    missing_from_seed = sorted(profiles - seed)
    payload = {"seed_only": missing_from_bots, "profile_only": missing_from_seed, "drift": len(missing_from_bots) + len(missing_from_seed)}
    REPORT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["drift"] > 10:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
