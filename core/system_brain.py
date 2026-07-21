"""
System Brain — orchestrates bot evaluation, revenue tracking, and scaling decisions.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

BOT_REGISTRY: Dict[str, dict] = {}

# Revenue thresholds
SCALE_THRESHOLD = 1000
KILL_THRESHOLD = 0


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


def load_bots(root: str = ".") -> None:
    """Walk *root* and register every directory containing a config.json."""
    for dirpath, _dirs, files in os.walk(root):
        if "config.json" in files:
            config_path = os.path.join(dirpath, "config.json")
            try:
                with open(config_path) as fh:
                    config = json.load(fh)
                BOT_REGISTRY[dirpath] = {
                    "name": config.get("name", "unknown"),
                    "status": "active",
                    "revenue": 0,
                }
            except (json.JSONDecodeError, OSError):
                continue


def update_metrics(bot_path: str, revenue: float) -> None:
    """Add *revenue* to the tracked bot at *bot_path*."""
    if bot_path in BOT_REGISTRY:
        BOT_REGISTRY[bot_path]["revenue"] += revenue


def evaluate_bots() -> list[str]:
    """
    Evaluate every registered bot and return a list of action strings.

    Bots with revenue > SCALE_THRESHOLD are flagged for scaling.
    Bots with revenue < KILL_THRESHOLD are disabled.
    """
    actions: list[str] = []

    for path, bot in BOT_REGISTRY.items():
        if bot["status"] == "disabled":
            continue

        if bot["revenue"] > SCALE_THRESHOLD:
            action = f"🚀 Scaling bot: {bot['name']}"
            print(action)
            actions.append(action)
        elif bot["revenue"] < KILL_THRESHOLD:
            action = f"💀 Killing bot: {bot['name']}"
            print(action)
            bot["status"] = "disabled"
            actions.append(action)

    return actions


def get_registry() -> Dict[str, dict]:
    """Return a copy of the current bot registry."""
    return dict(BOT_REGISTRY)


def run(root: str = ".") -> Dict[str, dict]:
    """Load bots, evaluate them, and return the registry snapshot."""
    load_bots(root)
    evaluate_bots()
    return get_registry()


if __name__ == "__main__":
    run()
