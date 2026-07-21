"""
Research Analyzer Bot — Package Initializer
Exports all public classes and helpers.
"""

from bots.research_analyzer_bot.research_analyzer_bot import (
    ResearchAnalyzerBot,
    ResearchAnalyzerBotError,
)
from bots.research_analyzer_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)

__all__ = [
    "ResearchAnalyzerBot",
    "ResearchAnalyzerBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
