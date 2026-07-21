"""LegalMoneyBot — AI-powered legal claim discovery and settlement assistant."""

from .legal_money_bot import LegalMoneyBot, LegalMoneyBotTierError
from .tiers import Tier, get_tier_config, get_upgrade_path

__all__ = [
    "LegalMoneyBot",
    "LegalMoneyBotTierError",
    "Tier",
    "get_tier_config",
    "get_upgrade_path",
]
