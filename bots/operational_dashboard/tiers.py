"""
Tier configuration for the Operational Dashboard bot.

Tiers:
  - FREE ($0):        Basic health monitoring, read-only metrics
  - PRO ($49):        Auto-fix engine, security auditing, revenue leak detection
  - ENTERPRISE ($199): Custom alerts, white-label, API access, dedicated support
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
    features: list

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


FEATURE_HEALTH_MONITORING = "health_monitoring"
FEATURE_AUTO_FIX_ENGINE = "auto_fix_engine"
FEATURE_SECURITY_AUDITING = "security_auditing"
FEATURE_REVENUE_LEAKAGE = "revenue_leakage"
FEATURE_REAL_TIME_ALERTS = "real_time_alerts"
FEATURE_CUSTOM_ALERTS = "custom_alerts"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"

FREE_FEATURES = [FEATURE_HEALTH_MONITORING]
PRO_FEATURES = FREE_FEATURES + [
    FEATURE_AUTO_FIX_ENGINE,
    FEATURE_SECURITY_AUDITING,
    FEATURE_REVENUE_LEAKAGE,
    FEATURE_REAL_TIME_ALERTS,
]
ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CUSTOM_ALERTS,
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
        features=FREE_FEATURES,
    ),
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        features=PRO_FEATURES,
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        features=ENTERPRISE_FEATURES,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier]


def list_tiers():
    return list(TIER_CATALOGUE.values())
