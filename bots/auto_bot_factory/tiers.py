"""
Tier configuration for the DreamCo Auto-Bot Generator Factory.

Tiers:
  - BASIC ($99/month):      Core bot generation, 10 bots/month, standard strategies.
  - ADVANCED ($299/month):  Competitor analysis, 50 bots/month, full 200-strategy framework.
  - ENTERPRISE (usage):     Unlimited bots, all features, usage-based revenue tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature constants
# ---------------------------------------------------------------------------

FEATURE_BOT_GENERATION = "bot_generation"
FEATURE_COMPETITOR_ANALYSIS = "competitor_analysis"
FEATURE_STRATEGY_FRAMEWORK = "strategy_framework"
FEATURE_AUTO_DEPLOY = "auto_deploy"
FEATURE_SAFETY_CONTROLLER = "safety_controller"
FEATURE_SELF_HEALING = "self_healing"
FEATURE_PERSISTENT_MEMORY = "persistent_memory"
FEATURE_REAL_METRICS = "real_metrics"
FEATURE_DECISION_ENGINE = "decision_engine"
FEATURE_USAGE_BILLING = "usage_billing"
FEATURE_FULL_AUTONOMY = "full_autonomy"
FEATURE_GITHUB_DEPLOY = "github_deploy"

BASIC_FEATURES: list[str] = [
    FEATURE_BOT_GENERATION,
    FEATURE_SAFETY_CONTROLLER,
    FEATURE_PERSISTENT_MEMORY,
    FEATURE_REAL_METRICS,
    FEATURE_GITHUB_DEPLOY,
]

ADVANCED_FEATURES: list[str] = BASIC_FEATURES + [
    FEATURE_COMPETITOR_ANALYSIS,
    FEATURE_STRATEGY_FRAMEWORK,
    FEATURE_AUTO_DEPLOY,
    FEATURE_SELF_HEALING,
    FEATURE_DECISION_ENGINE,
]

ENTERPRISE_FEATURES: list[str] = ADVANCED_FEATURES + [
    FEATURE_USAGE_BILLING,
    FEATURE_FULL_AUTONOMY,
]


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots_per_month: Optional[int]
    features: list[str] = field(default_factory=list)
    support_level: str = "Community"
    usage_rate_usd: float = 0.0

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.max_bots_per_month is None


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.BASIC.value: TierConfig(
        name="Basic",
        tier=Tier.BASIC,
        price_usd_monthly=99.0,
        max_bots_per_month=10,
        features=BASIC_FEATURES,
        support_level="Email",
        usage_rate_usd=0.0,
    ),
    Tier.ADVANCED.value: TierConfig(
        name="Advanced",
        tier=Tier.ADVANCED,
        price_usd_monthly=299.0,
        max_bots_per_month=50,
        features=ADVANCED_FEATURES,
        support_level="Priority Email (12 h SLA)",
        usage_rate_usd=0.0,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=0.0,
        max_bots_per_month=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
        usage_rate_usd=0.10,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
