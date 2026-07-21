"""
Voice Replicator Bot — Package Initializer
Exports all public classes and helpers.
"""

from bots.voice_replicator_bot.voice_replicator_bot import (
    VoiceReplicatorBot,
    VoiceReplicatorBotError,
)
from bots.voice_replicator_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
)

__all__ = [
    "VoiceReplicatorBot",
    "VoiceReplicatorBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
