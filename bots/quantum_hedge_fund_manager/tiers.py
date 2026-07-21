"""
Tier configuration for the Quantum Hedge Fund Manager Bot.

Tiers:
  - FREE ($0):        Basic fund monitoring, 3 portfolios, 5 high-yield
                      structures, read-only analytics.
  - PRO ($49):        Dynamic AI-driven reallocation, 50 portfolios, unlimited
                      structures, real-time signals, predictive analytics.
  - ENTERPRISE ($199): Full quantum optimisation, unlimited portfolios,
                       white-label reports, API access, dedicated support.
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
    """Configuration for a Quantum Hedge Fund Manager subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_portfolios: Optional[int]
    max_structures: Optional[int]
    max_allocations_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_portfolios(self) -> bool:
        return self.max_portfolios is None

    def is_unlimited_structures(self) -> bool:
        return self.max_structures is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_FUND_MONITOR = "fund_monitor"
FEATURE_HIGH_YIELD_STRUCTURES = "high_yield_structures"
FEATURE_PORTFOLIO_MANAGER = "portfolio_manager"
FEATURE_DYNAMIC_REALLOCATION = "dynamic_reallocation"
FEATURE_AI_PREDICTOR = "ai_predictor"
FEATURE_REALTIME_SIGNALS = "realtime_signals"
FEATURE_RISK_ANALYTICS = "risk_analytics"
FEATURE_SCENARIO_SIM = "scenario_simulation"
FEATURE_QUANTUM_OPTIMIZER = "quantum_optimizer"
FEATURE_CUSTOM_RULES = "custom_rules"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_ADVANCED_ML = "advanced_ml"

FREE_FEATURES: list = [
    FEATURE_FUND_MONITOR,
    FEATURE_HIGH_YIELD_STRUCTURES,
    FEATURE_PORTFOLIO_MANAGER,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_DYNAMIC_REALLOCATION,
    FEATURE_AI_PREDICTOR,
    FEATURE_REALTIME_SIGNALS,
    FEATURE_RISK_ANALYTICS,
    FEATURE_SCENARIO_SIM,
    FEATURE_CUSTOM_RULES,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_QUANTUM_OPTIMIZER,
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
        max_portfolios=3,
        max_structures=5,
        max_allocations_per_day=5,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_portfolios=50,
        max_structures=None,
        max_allocations_per_day=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_portfolios=None,
        max_structures=None,
        max_allocations_per_day=None,
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
