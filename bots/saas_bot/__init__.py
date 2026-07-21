"""
SaaS Bot package.

Usage::

    from bots.saas_bot import SaasBot, Tier

    bot = SaasBot(tier=Tier.PROFESSIONAL)
    sub = bot.create_subscription("customer@example.com")
"""

from bots.saas_bot.saas_bot import (
    SaasBot,
    SaasBotError,
    SaasBotTierError,
    Subscription,
)
from bots.saas_bot.tiers import Tier, get_tier_config, list_tiers

__all__ = [
    "SaasBot",
    "SaasBotError",
    "SaasBotTierError",
    "Subscription",
    "Tier",
    "get_tier_config",
    "list_tiers",
]
