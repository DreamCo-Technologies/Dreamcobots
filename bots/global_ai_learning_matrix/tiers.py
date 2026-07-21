"""
Tier configuration for the Global AI Learning Matrix bot.

Tiers:
  - FREE ($0):       5 countries, basic learning methods, read-only dashboard
  - PRO ($49):       50 countries, all learning methods, evolution tools, governance
  - ENTERPRISE ($199): Unlimited countries, custom models, white-label, API access
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
    max_countries: Optional[int]
    features: list

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_countries(self) -> bool:
        return self.max_countries is None


FEATURE_COUNTRY_TRACKING = "country_tracking"
FEATURE_LEARNING_BENCHMARKS = "learning_benchmarks"
FEATURE_EVOLUTION_ENGINE = "evolution_engine"
FEATURE_GOVERNANCE = "governance"
FEATURE_DASHBOARD = "dashboard"
FEATURE_CUSTOM_MODELS = "custom_models"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_FEDERATED_LEARNING = "federated_learning"
FEATURE_REAL_TIME_MONITORING = "real_time_monitoring"

FREE_FEATURES = [FEATURE_COUNTRY_TRACKING, FEATURE_LEARNING_BENCHMARKS, FEATURE_DASHBOARD]
PRO_FEATURES = FREE_FEATURES + [
    FEATURE_EVOLUTION_ENGINE,
    FEATURE_GOVERNANCE,
    FEATURE_FEDERATED_LEARNING,
    FEATURE_REAL_TIME_MONITORING,
]
ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CUSTOM_MODELS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

TIER_CATALOGUE = {
    Tier.FREE: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_countries=5,
        features=FREE_FEATURES,
    ),
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_countries=50,
        features=PRO_FEATURES,
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_countries=None,
        features=ENTERPRISE_FEATURES,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier]


def list_tiers():
    return list(TIER_CATALOGUE.values())
