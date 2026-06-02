"""Generate investor prospectus markdown pages for every DreamCo bot."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "prospectus"


TEMPLATE = """# {display_name}

## Capabilities
{capabilities}

## Revenue Model
- {revenue_model}

## Target Users
- {target_users}

## Pricing
- {pricing}

## Purchase CTA
- Contact DreamCo sales to activate `{slug}` in Empire OS.
"""


def render(profile: dict) -> str:
    capabilities = "\n".join(f"- {item}" for item in profile.get("capabilities", [])) or "- Capability data unavailable"
    return TEMPLATE.format(
        display_name=profile.get("displayName", profile.get("slug", "Unknown Bot")),
        capabilities=capabilities,
        revenue_model=profile.get("revenueModel", "Unspecified"),
        target_users=profile.get("targetUsers", "Unspecified"),
        pricing=profile.get("priceRange", "Unspecified"),
        slug=profile.get("slug", "unknown"),
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted((ROOT / "bots").glob("*/replit_profile.json")):
        profile = json.loads(path.read_text())
        slug = profile.get("slug", path.parent.name)
        (OUTPUT_DIR / f"{slug}.md").write_text(render(profile))
        count += 1
    print(count)


if __name__ == "__main__":
    main()
