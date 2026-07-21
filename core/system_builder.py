"""
System Builder — automates bot creation based on AI-determined market opportunities.

Scales bot-building dynamically across different industries.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from core.ai_brain import find_opportunity, decide_bot_type

# ---------------------------------------------------------------------------
# Bot scaffold template
# ---------------------------------------------------------------------------

_TEMPLATE: dict[str, str] = {
    "config.json": json.dumps({"name": "NEW_BOT", "version": "1.0"}, indent=2),
    "main.py": "# Auto-generated bot entry point\nprint('Bot running')\n",
    "metrics.py": "# Auto-generated metrics module\ndef track():\n    pass\n",
    "README.md": "# Auto-generated bot\n",
    "__init__.py": "",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_bot(bot_name: str, bots_dir: str = "./bots") -> str:
    """
    Scaffold a new bot directory under *bots_dir*.

    Parameters
    ----------
    bot_name : str
        Name of the new bot (used as the directory name and in config.json).
    bots_dir : str
        Parent directory under which the bot folder is created.

    Returns
    -------
    str
        Absolute path of the created bot directory.
    """
    path = os.path.join(bots_dir, bot_name)
    os.makedirs(path, exist_ok=True)

    for filename, content in _TEMPLATE.items():
        file_path = os.path.join(path, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fh:
                fh.write(content.replace("NEW_BOT", bot_name))

    print(f"✅ Created bot: {bot_name}")
    return os.path.abspath(path)


def generate_from_gap(bots_dir: str = "./bots") -> str:
    """
    Use the AI Brain to identify a market gap and build a bot for it.

    Returns
    -------
    str
        Name of the created bot.
    """
    market = find_opportunity()
    bot_name = decide_bot_type(market)

    print(f"🧠 AI chose market: {market}")
    create_bot(bot_name, bots_dir=bots_dir)
    return bot_name


def build(bots_dir: str = "./bots") -> str:
    """Entry point: identify an opportunity and build a bot for it."""
    return generate_from_gap(bots_dir=bots_dir)


if __name__ == "__main__":
    build()
