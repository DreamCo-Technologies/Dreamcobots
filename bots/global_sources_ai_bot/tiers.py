"""
Tier configuration for the GlobalSourcesAIBot.

Tiers:
  - FREE ($0):         5 use-case categories, top-3 models per task, basic routing
  - PRO ($49):         All 100 use-case categories, top-10 models, benchmarking
  - ENTERPRISE ($199): Unlimited categories, full model registry, custom API keys,
                       continuous benchmarking, autonomous model upgrades
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    max_categories: Optional[int]  # None = unlimited
    max_models_per_task: int
    features: list

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# Feature flags
FEATURE_BASIC_ROUTING = "basic_routing"
FEATURE_FULL_ROUTING = "full_routing"
FEATURE_BENCHMARKING = "benchmarking"
FEATURE_CUSTOM_API_KEYS = "custom_api_keys"
FEATURE_AUTONOMOUS_UPGRADE = "autonomous_upgrade"
FEATURE_MULTI_AGENT = "multi_agent"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_REAL_TIME_BENCHMARK = "real_time_benchmark"
FEATURE_COLLABORATION_ENGINE = "collaboration_engine"

FREE_FEATURES = [FEATURE_BASIC_ROUTING]
PRO_FEATURES = FREE_FEATURES + [
    FEATURE_FULL_ROUTING,
    FEATURE_BENCHMARKING,
    FEATURE_COLLABORATION_ENGINE,
]
ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CUSTOM_API_KEYS,
    FEATURE_AUTONOMOUS_UPGRADE,
    FEATURE_MULTI_AGENT,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_REAL_TIME_BENCHMARK,
]

TIER_CATALOGUE = {
    Tier.FREE: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_categories=5,
        max_models_per_task=3,
        features=FREE_FEATURES,
    ),
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_categories=100,
        max_models_per_task=10,
        features=PRO_FEATURES,
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_categories=None,
        max_models_per_task=100,
        features=ENTERPRISE_FEATURES,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier]


def list_tiers() -> list[TierConfig]:
    return list(TIER_CATALOGUE.values())
