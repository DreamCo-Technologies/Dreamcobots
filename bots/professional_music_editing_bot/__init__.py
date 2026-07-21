"""
Professional Music Editing Bot — Package Initializer
Exports all public classes and helpers.
"""

from bots.professional_music_editing_bot.professional_music_editing_bot import (
    ProfessionalMusicEditingBot,
    ProfessionalMusicEditingBotError,
)
from bots.professional_music_editing_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)

__all__ = [
    "ProfessionalMusicEditingBot",
    "ProfessionalMusicEditingBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
