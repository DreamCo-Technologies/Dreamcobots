"""
Tier configuration for the Bot Generator Bot.

Tiers:
  - FREE:             Generate up to 3 bots/month, 5 industries, basic templates.
  - PRO ($49):        Generate up to 30 bots/month, 20 industries, advanced templates,
                      tool injection, auto-deploy.
  - ENTERPRISE ($199): Unlimited bots, all industries, custom DNA, white-label deploy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots_per_month: Optional[int]
    max_industries: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_bots_per_month is None


FEATURE_BASIC_GENERATION = "basic_generation"
FEATURE_TOOL_INJECTION = "tool_injection"
FEATURE_ADVANCED_TEMPLATES = "advanced_templates"
FEATURE_AUTO_DEPLOY = "auto_deploy"
FEATURE_CUSTOM_DNA = "custom_dna"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_MULTI_INDUSTRY = "multi_industry"
FEATURE_MONETIZATION_HOOKS = "monetization_hooks"
FEATURE_STRIPE_INTEGRATION = "stripe_integration"
FEATURE_ANALYTICS_HOOKS = "analytics_hooks"

FREE_FEATURES = [
    FEATURE_BASIC_GENERATION,
    FEATURE_MULTI_INDUSTRY,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_TOOL_INJECTION,
    FEATURE_ADVANCED_TEMPLATES,
    FEATURE_AUTO_DEPLOY,
    FEATURE_MONETIZATION_HOOKS,
    FEATURE_STRIPE_INTEGRATION,
    FEATURE_ANALYTICS_HOOKS,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CUSTOM_DNA,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_bots_per_month=3,
        max_industries=5,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bots_per_month=30,
        max_industries=20,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bots_per_month=None,
        max_industries=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
