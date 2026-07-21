"""
Tier configuration for the DreamCo Quantum Decision Bot.

Tiers:
  - FREE:       Basic simulation (10 runs), core quantum decision, simple scoring.
  - PRO ($49):  Full simulation (1000 runs), dimension mapping, bot routing, money engine.
  - ENTERPRISE ($199): Hyper simulation (10,000 runs), self-improving AI, god mode, unlimited paths.
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
    """Configuration for a Quantum Decision Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_simulation_runs: int
    max_active_paths: int
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_SIMULATION = "simulation"
FEATURE_QUANTUM_DECISION = "quantum_decision"
FEATURE_PROBABILITY_MODEL = "probability_model"
FEATURE_DIMENSION_MAPPER = "dimension_mapper"
FEATURE_BOT_ROUTER = "bot_router"
FEATURE_MONEY_ENGINE = "money_engine"
FEATURE_HYPER_SIMULATION = "hyper_simulation"
FEATURE_SELF_IMPROVING_AI = "self_improving_ai"
FEATURE_GOD_MODE = "god_mode"
FEATURE_AUTONOMOUS_EXECUTION = "autonomous_execution"
FEATURE_MULTI_PATH_TRACKER = "multi_path_tracker"

FREE_FEATURES: list = [
    FEATURE_SIMULATION,
    FEATURE_QUANTUM_DECISION,
    FEATURE_PROBABILITY_MODEL,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_DIMENSION_MAPPER,
    FEATURE_BOT_ROUTER,
    FEATURE_MONEY_ENGINE,
    FEATURE_MULTI_PATH_TRACKER,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_HYPER_SIMULATION,
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_GOD_MODE,
    FEATURE_AUTONOMOUS_EXECUTION,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_simulation_runs=10,
        max_active_paths=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_simulation_runs=1000,
        max_active_paths=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_simulation_runs=10_000,
        max_active_paths=100,
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
