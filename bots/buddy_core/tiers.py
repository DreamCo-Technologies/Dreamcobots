"""
Tier configuration for the Buddy Core System.

Tiers:
  - FREE:            3 bots/day, 50 leads/day, basic features.
  - PRO ($49):       20 bots/day, 5000 leads/day, all main features.
  - ENTERPRISE ($199): Unlimited bots/day, unlimited leads/day, all features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_INTENT_PARSER = "intent_parser"
FEATURE_TOOL_INJECTION = "tool_injection"
FEATURE_BOT_GENERATOR = "bot_generator"
FEATURE_FEEDBACK_LOOP = "feedback_loop"
FEATURE_PRIVACY_VAULT = "privacy_vault"
FEATURE_LEAD_ENGINE = "lead_engine"
FEATURE_ADVANCED_AI = "advanced_ai"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_CUSTOM_ENCRYPTION = "custom_encryption"
FEATURE_ENTERPRISE_LOGS = "enterprise_logs"
FEATURE_TOOL_SCRAPER = "tool_scraper"
FEATURE_TOOL_REPLICATION = "tool_replication"


@dataclass
class TierConfig:
    """Configuration for a Buddy Core subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots_per_day: Optional[int]
    max_leads_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_bots_per_day is None

    def is_unlimited_leads(self) -> bool:
        return self.max_leads_per_day is None


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

_FREE_FEATURES = [
    FEATURE_INTENT_PARSER,
    FEATURE_BOT_GENERATOR,
    FEATURE_LEAD_ENGINE,
]

_PRO_FEATURES = _FREE_FEATURES + [
    FEATURE_TOOL_INJECTION,
    FEATURE_FEEDBACK_LOOP,
    FEATURE_PRIVACY_VAULT,
    FEATURE_ADVANCED_AI,
    FEATURE_TOOL_SCRAPER,
]

_ENTERPRISE_FEATURES = _PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_ENCRYPTION,
    FEATURE_ENTERPRISE_LOGS,
    FEATURE_TOOL_REPLICATION,
]

_TIER_CONFIGS: dict[Tier, TierConfig] = {
    Tier.FREE: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_bots_per_day=3,
        max_leads_per_day=50,
        features=_FREE_FEATURES,
        support_level="community",
    ),
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bots_per_day=20,
        max_leads_per_day=5000,
        features=_PRO_FEATURES,
        support_level="priority",
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bots_per_day=None,
        max_leads_per_day=None,
        features=_ENTERPRISE_FEATURES,
        support_level="dedicated",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier."""
    return _TIER_CONFIGS[tier]


def list_tiers() -> list[TierConfig]:
    """Return all tier configurations."""
    return list(_TIER_CONFIGS.values())


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next tier up, or None if already at ENTERPRISE."""
    order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
    idx = order.index(current)
    if idx + 1 < len(order):
        return _TIER_CONFIGS[order[idx + 1]]
    return None
