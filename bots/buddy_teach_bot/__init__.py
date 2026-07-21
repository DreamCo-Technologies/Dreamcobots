"""Buddy Teach Bot — Multi-platform teaching & broadcasting bot."""

from .buddy_teach_bot import BuddyTeachBot, BuddyTeachBotError, BuddyTeachBotTierError
from .tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = [
    "BuddyTeachBot",
    "BuddyTeachBotError",
    "BuddyTeachBotTierError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
]
