"""
Tier configuration for the DreamCo AI Brain (Decision Engine).

Tiers:
  - FREE ($0):       Basic decision logic, no persistence.
  - PRO ($99):       Full decision engine, persistent memory, real metrics.
  - ENTERPRISE ($299): Full autonomy, usage-based billing, advanced analytics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


FEATURE_DECISION_ENGINE = "decision_engine"
FEATURE_PERSISTENT_MEMORY = "persistent_memory"
FEATURE_REAL_METRICS = "real_metrics"
FEATURE_AUTO_SCALE = "auto_scale"
FEATURE_RECOVERY_BOT = "recovery_bot"
FEATURE_FULL_AUTONOMY = "full_autonomy"

FREE_FEATURES: list[str] = [FEATURE_DECISION_ENGINE]

PRO_FEATURES: list[str] = FREE_FEATURES + [
    FEATURE_PERSISTENT_MEMORY,
    FEATURE_REAL_METRICS,
    FEATURE_AUTO_SCALE,
]

ENTERPRISE_FEATURES: list[str] = PRO_FEATURES + [
    FEATURE_RECOVERY_BOT,
    FEATURE_FULL_AUTONOMY,
]


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    features: list[str] = field(default_factory=list)

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        features=FREE_FEATURES,
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=99.0,
        features=PRO_FEATURES,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        features=ENTERPRISE_FEATURES,
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


BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}


def get_bot_tier_info(tier: Tier) -> dict:
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
    }
