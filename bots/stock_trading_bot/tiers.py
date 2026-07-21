"""
Tier configuration for the Dreamcobots Stock Trading Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
)

# Bot-specific features per tier
STOCK_TRADING_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["5 watchlist stocks", "daily signals", "basic indicators"],
    Tier.PRO.value: ["100 stocks", "real-time signals", "20+ technical indicators", "backtesting"],
    Tier.ENTERPRISE.value: ["unlimited stocks", "algorithmic strategies", "options flow", "institutional data", "API trading"],
}


def get_stock_trading_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": STOCK_TRADING_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
