"""
Photo Editing Bot — Package Initializer
Exports all public classes and helpers.
"""

from bots.photo_editing_bot.photo_editing_bot import (
    PhotoEditingBot,
    PhotoEditingBotError,
)
from bots.photo_editing_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)

__all__ = [
    "PhotoEditingBot",
    "PhotoEditingBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
