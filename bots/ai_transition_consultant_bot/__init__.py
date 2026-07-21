"""
AI Transition Consultant Bot — Package Initializer
Exports all public classes and helpers.
"""

from bots.ai_transition_consultant_bot.ai_transition_consultant_bot import (
    AITransitionConsultantBot,
    AITransitionConsultantBotError,
)
from bots.ai_transition_consultant_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)

__all__ = [
    "AITransitionConsultantBot",
    "AITransitionConsultantBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
