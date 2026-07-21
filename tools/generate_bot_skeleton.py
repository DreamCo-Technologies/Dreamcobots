#!/usr/bin/env python3
"""
DreamCobots Bot Skeleton Generator
===================================
Generates a compliant bot skeleton that includes the required
GLOBAL AI SOURCES FLOW framework reference and a standard tier structure.

Usage:
    python tools/generate_bot_skeleton.py <BotName> [output_dir]

Examples:
    python tools/generate_bot_skeleton.py MyNewBot
    python tools/generate_bot_skeleton.py MyNewBot bots/my_new_bot
"""

import argparse
import os
import sys


BOT_TEMPLATE = '''\
# GLOBAL AI SOURCES FLOW
"""
{bot_name}
{underline}
Part of the DreamCObots framework.

Complies with the GlobalAISourcesFlow pipeline (framework/global_ai_sources_flow.py).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from framework import GlobalAISourcesFlow


class {class_name}(GlobalAISourcesFlow):
    """
    {bot_name} — autonomous AI bot built on GlobalAISourcesFlow.

    Tiers
    -----
    FREE       : Basic functionality, no charge.
    PRO        : Advanced features, $49/month.
    ENTERPRISE : Full suite, $199/month, unlimited usage.
    """

    BOT_NAME: str = "{bot_name}"
    BOT_VERSION: str = "1.0.0"

    def run(self, data: dict) -> dict:
        """Execute the full 8-stage GLOBAL AI SOURCES FLOW pipeline."""
        return self.run_pipeline(raw_data=data)


if __name__ == "__main__":
    bot = {class_name}(bot_name="{bot_name}")
    result = bot.run({{}})
    print(f"{{bot.BOT_NAME}} completed pipeline: {{result}}")
'''

TIERS_TEMPLATE = '''\
# GLOBAL AI SOURCES FLOW
"""
Tier definitions for {bot_name}.
"""

from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_PRICING: dict[str, float] = {{
    Tier.FREE: 0.0,
    Tier.PRO: 49.0,
    Tier.ENTERPRISE: 199.0,
}}

FREE_FEATURES: list[str] = ["basic_access"]
PRO_FEATURES: list[str] = FREE_FEATURES + ["advanced_features", "priority_support"]
ENTERPRISE_FEATURES: list[str] = PRO_FEATURES + ["unlimited_usage", "white_label", "sla"]


def get_tier_price(tier: Tier) -> float:
    """Return the monthly price for the given tier."""
    return TIER_PRICING[tier]
'''

INIT_TEMPLATE = '''\
# GLOBAL AI SOURCES FLOW
"""
{bot_name} package.
"""

from .{module_name} import {class_name}

__all__ = ["{class_name}"]
'''

README_TEMPLATE = '''\
# {bot_name}

Part of the DreamCObots framework, compliant with the
**GLOBAL AI SOURCES FLOW** pipeline.

## Tiers

| Tier       | Price      | Features            |
|------------|------------|---------------------|
| FREE       | $0/month   | Basic access        |
| PRO        | $49/month  | Advanced features   |
| ENTERPRISE | $199/month | Full suite          |

## Usage

```python
from bots.{module_name} import {class_name}

bot = {class_name}(bot_name="{bot_name}")
result = bot.run({{}})
```

## Framework Compliance

This bot extends `GlobalAISourcesFlow` and implements all 8 pipeline stages:
1. Data Ingestion
2. Learning Method Classification
3. Sandbox Testing
4. Performance Analytics
5. Hybrid Evolution
6. Deployment
7. Profit & Market Intelligence
8. Governance & Security
'''


def to_class_name(name: str) -> str:
    """Convert 'my bot name' or 'my_bot_name' to 'MyBotName'."""
    return "".join(
        word.capitalize()
        for word in name.replace("-", "_").replace(" ", "_").split("_")
        if word
    )


def to_module_name(name: str) -> str:
    """Convert 'MyBotName' or 'My Bot Name' to 'my_bot_name'."""
    import re
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower().replace(" ", "_").replace("-", "_")


def generate_bot(bot_name: str, output_dir: str) -> None:
    """Generate all skeleton files for a new bot."""
    class_name = to_class_name(bot_name)
    module_name = to_module_name(class_name)
    underline = "=" * len(bot_name)

    os.makedirs(output_dir, exist_ok=True)

    files = {
        f"{module_name}.py": BOT_TEMPLATE.format(
            bot_name=bot_name,
            class_name=class_name,
            underline=underline,
            module_name=module_name,
        ),
        "tiers.py": TIERS_TEMPLATE.format(bot_name=bot_name),
        "__init__.py": INIT_TEMPLATE.format(
            bot_name=bot_name,
            class_name=class_name,
            module_name=module_name,
        ),
        "README.md": README_TEMPLATE.format(
            bot_name=bot_name,
            class_name=class_name,
            module_name=module_name,
        ),
    }

    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  Created {filepath}")

    print(f"\n✅  Bot skeleton for '{bot_name}' created in {output_dir}")
    print(f"    Main class : {class_name}")
    print(f"    Module     : {module_name}")
    print(f"\nNext steps:")
    print(f"  1. Implement the bot logic in {output_dir}/{module_name}.py")
    print(f"  2. Run: python tools/check_bot_framework.py")
    print(f"  3. Add tests in tests/test_{module_name}.py")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a GLOBAL AI SOURCES FLOW compliant bot skeleton."
    )
    parser.add_argument("bot_name", help="Human-readable bot name (e.g. 'My New Bot')")
    parser.add_argument(
        "output_dir",
        nargs="?",
        help="Output directory (default: bots/<module_name>/)",
    )
    args = parser.parse_args()

    module_name = to_module_name(to_class_name(args.bot_name))
    output_dir = args.output_dir or os.path.join("bots", module_name)

    print(f"Generating bot skeleton for '{args.bot_name}' in {output_dir}/")
    generate_bot(args.bot_name, output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
