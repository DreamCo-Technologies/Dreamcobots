"""
Tier configuration for the Open Claw Bot.

Tiers:
  - FREE:       Basic strategy templates, 3 client profiles, 5 analyses/day.
  - PRO ($49):  Full AI-driven strategy engine, 50 client profiles,
                unlimited analyses, ML model suite, custom rules.
  - ENTERPRISE ($199): Unlimited clients, white-label reports, API access,
                       advanced ML ensemble, dedicated support.
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
    """Configuration for an Open Claw Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_clients: Optional[int]
    max_analyses_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_clients(self) -> bool:
        return self.max_clients is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_STRATEGY_ENGINE = "strategy_engine"
FEATURE_AI_MODELS = "ai_models"
FEATURE_CLIENT_MANAGER = "client_manager"
FEATURE_DATA_ANALYSIS = "data_analysis"
FEATURE_CUSTOM_RULES = "custom_rules"
FEATURE_ML_ENSEMBLE = "ml_ensemble"
FEATURE_REALTIME_SIGNALS = "realtime_signals"
FEATURE_BOT_STRATEGIES = "bot_strategies"
FEATURE_SCENARIO_SIM = "scenario_simulation"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_ADVANCED_ML = "advanced_ml"

FREE_FEATURES: list = [
    FEATURE_STRATEGY_ENGINE,
    FEATURE_DATA_ANALYSIS,
    FEATURE_CLIENT_MANAGER,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_AI_MODELS,
    FEATURE_CUSTOM_RULES,
    FEATURE_ML_ENSEMBLE,
    FEATURE_REALTIME_SIGNALS,
    FEATURE_BOT_STRATEGIES,
    FEATURE_SCENARIO_SIM,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_ADVANCED_ML,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_clients=3,
        max_analyses_per_day=5,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_clients=50,
        max_analyses_per_day=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_clients=None,
        max_analyses_per_day=None,
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
