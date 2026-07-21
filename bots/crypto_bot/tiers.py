"""
Tier configuration for the Crypto Bot.

Tiers:
  - FREE:       Track 5 coins, view prices, simulated mining for BTC only.
  - PRO:        Track 50 coins, buy/sell, simulated mining for 20 coins, dashboard.
  - ENTERPRISE: Unlimited coins, full mining suite, API access, tax reporting.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

BOT_FEATURES = {
    Tier.FREE.value: [
        "track 5 cryptocurrencies",
        "view real-time prices",
        "basic portfolio summary",
        "simulated BTC mining",
        "coin prospectus pages",
    ],
    Tier.PRO.value: [
        "track 50 cryptocurrencies",
        "buy & sell transactions",
        "profit/loss tracking",
        "simulated mining (20 coins)",
        "transaction history",
        "interactive dashboard",
        "coin prospectus pages",
        "price alerts",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited cryptocurrencies",
        "full mining suite (all coins)",
        "advanced portfolio analytics",
        "tax reporting",
        "API access",
        "multi-exchange routing",
        "automated trading strategies",
        "full prospectus library",
        "dedicated support",
        "white-label dashboard",
    ],
}

COIN_LIMITS = {
    Tier.FREE: 5,
    Tier.PRO: 50,
    Tier.ENTERPRISE: None,  # unlimited
}

MINING_COIN_LIMITS = {
    Tier.FREE: ["BTC"],
    Tier.PRO: [
        "BTC", "LTC", "DOGE", "XMR",
        "RVN", "ERG", "FLUX", "KAS", "ZEC",
        "VTC", "GRIN", "BEAM", "FIRO",
        "CFX", "ALPH", "AR", "FIL",
    ],
    Tier.ENTERPRISE: None,  # all coins
}


def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
        "coin_limit": COIN_LIMITS[tier],
        "mining_coins": MINING_COIN_LIMITS[tier],
    }
