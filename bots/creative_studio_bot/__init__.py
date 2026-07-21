"""
Creative Studio Bot — Package Initializer

Exports all public classes and helpers for the Creative Studio Bot.
"""

from bots.creative_studio_bot.creative_studio_bot import (
    CreativeStudioBot,
    CreativeStudioBotError,
)
from bots.creative_studio_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)
from bots.creative_studio_bot.content_creator import (
    MusicCreator,
    FilmCreator,
    ArtCreator,
    GENRES,
    STYLES,
)
from bots.creative_studio_bot.influencer_engine import (
    ContentStrategyEngine,
    MemeGenerator,
    PLATFORMS,
)

__all__ = [
    "CreativeStudioBot",
    "CreativeStudioBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
    "MusicCreator",
    "FilmCreator",
    "ArtCreator",
    "GENRES",
    "STYLES",
    "ContentStrategyEngine",
    "MemeGenerator",
    "PLATFORMS",
]
