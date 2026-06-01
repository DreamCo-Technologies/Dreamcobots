"""Deprecated Buddy entrypoint adapter.

Canonical runtime: BuddyAI.buddy_bot.TaskEngine.
This adapter exists for backward compatibility and delegates execution to the
canonical BuddyAI runtime.
"""

from __future__ import annotations

import warnings

from BuddyAI.buddy_bot import TaskEngine
from framework import GlobalAISourcesFlow

warnings.warn(
    "bots/buddy-bot/buddy_bot.py is deprecated; use BuddyAI/buddy_bot.py TaskEngine.",
    DeprecationWarning,
    stacklevel=2,
)


def create_engine(*args, **kwargs) -> TaskEngine:
    """Compatibility factory returning the canonical TaskEngine."""
    GlobalAISourcesFlow(bot_name="BuddyBotAdapter")
    return TaskEngine(*args, **kwargs)


__all__ = ["TaskEngine", "create_engine"]
