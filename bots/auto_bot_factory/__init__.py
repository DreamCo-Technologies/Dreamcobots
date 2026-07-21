"""DreamCo Auto-Bot Generator Factory package."""

from bots.auto_bot_factory.auto_bot_factory import (
    AutoBotFactory,
    AutoBotFactoryError,
    AutoBotFactoryTierError,
    BotBlueprint,
    DeploymentRecord,
)
from bots.auto_bot_factory.tiers import Tier, TierConfig, get_tier_config
from bots.auto_bot_factory.competitor_analyzer import (
    CompetitorAnalyzer,
    CompetitorProfile,
    MarketGap,
    AnalysisReport,
)
from bots.auto_bot_factory.strategy_framework import (
    StrategyFramework,
    Strategy,
    StrategyCategory,
)
from bots.auto_bot_factory.safety_controller import (
    SafetyController,
    SafetyLimitError,
    MAX_BOTS,
    MAX_MESSAGES_PER_CYCLE,
)

__all__ = [
    "AutoBotFactory",
    "AutoBotFactoryError",
    "AutoBotFactoryTierError",
    "BotBlueprint",
    "DeploymentRecord",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "CompetitorAnalyzer",
    "CompetitorProfile",
    "MarketGap",
    "AnalysisReport",
    "StrategyFramework",
    "Strategy",
    "StrategyCategory",
    "SafetyController",
    "SafetyLimitError",
    "MAX_BOTS",
    "MAX_MESSAGES_PER_CYCLE",
]
