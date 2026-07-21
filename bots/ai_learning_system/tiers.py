"""
Tier definitions for the DreamCo Global AI Learning System.

Tiers:
  - FREE:       $0/month, 100 ingestion jobs, basic features.
  - PRO:        $199/month, 5,000 ingestion jobs, sandbox, hybrid engine.
  - ENTERPRISE: $999/month, unlimited jobs, Kubernetes, genetic algorithms.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature constants
# ---------------------------------------------------------------------------

FEATURE_SCRAPER = "web_scraper"
FEATURE_CLASSIFIER = "method_classifier"
FEATURE_SANDBOX = "sandbox_testing"
FEATURE_ANALYTICS = "performance_analytics"
FEATURE_HYBRID_ENGINE = "hybrid_evolution_engine"
FEATURE_DEPLOYMENT = "deployment_orchestration"
FEATURE_GOVERNANCE = "governance_security"
FEATURE_SCHEDULER = "automation_scheduler"
FEATURE_KUBERNETES = "kubernetes_orchestration"
FEATURE_GENETIC_ALGO = "genetic_algorithms"

FREE_FEATURES: List[str] = [
    FEATURE_SCRAPER,
    FEATURE_CLASSIFIER,
    FEATURE_ANALYTICS,
    FEATURE_SCHEDULER,
]

PRO_FEATURES: List[str] = FREE_FEATURES + [
    FEATURE_SANDBOX,
    FEATURE_HYBRID_ENGINE,
    FEATURE_DEPLOYMENT,
    FEATURE_GOVERNANCE,
]

ENTERPRISE_FEATURES: List[str] = PRO_FEATURES + [
    FEATURE_KUBERNETES,
    FEATURE_GENETIC_ALGO,
]


# ---------------------------------------------------------------------------
# TierConfig dataclass
# ---------------------------------------------------------------------------

@dataclass
class TierConfig:
    """Configuration for an AI Learning System subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    ingestion_jobs_per_month : int | None
        Maximum ingestion jobs per month. ``None`` means unlimited.
    sandbox_containers : int | None
        Maximum simultaneous sandbox containers. ``None`` means unlimited.
    features : List[str]
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    ingestion_jobs_per_month: Optional[int]
    sandbox_containers: Optional[int]
    features: List[str] = field(default_factory=list)
    support_level: str = "Community"

    def is_unlimited_ingestion(self) -> bool:
        """Return True if this tier has no ingestion job cap."""
        return self.ingestion_jobs_per_month is None

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        ingestion_jobs_per_month=100,
        sandbox_containers=0,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=199.0,
        ingestion_jobs_per_month=5_000,
        sandbox_containers=10,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=999.0,
        ingestion_jobs_per_month=None,
        sandbox_containers=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> List[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next higher TierConfig, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
