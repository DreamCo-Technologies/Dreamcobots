"""
LocalizationBot — app localization and i18n manager.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class LocalizationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class LocalizationBot:
    """Tier-aware app localization and i18n manager."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'APP001', 'app': 'App 1', 'platform': 'Android', 'users': 1500, 'retention_pct': 31.8, 'revenue_usd': 800, 'score': 42.5, 'category': 'Utility'}, {'id': 'APP002', 'app': 'App 2', 'platform': 'Web', 'users': 2000, 'retention_pct': 33.6, 'revenue_usd': 1100, 'score': 45.0, 'category': 'Game'}, {'id': 'APP003', 'app': 'App 3', 'platform': 'iOS', 'users': 2500, 'retention_pct': 35.4, 'revenue_usd': 1400, 'score': 47.5, 'category': 'Finance'}, {'id': 'APP004', 'app': 'App 4', 'platform': 'Android', 'users': 3000, 'retention_pct': 37.2, 'revenue_usd': 1700, 'score': 50.0, 'category': 'Social'}, {'id': 'APP005', 'app': 'App 5', 'platform': 'Web', 'users': 3500, 'retention_pct': 39.0, 'revenue_usd': 2000, 'score': 52.5, 'category': 'Utility'}, {'id': 'APP006', 'app': 'App 6', 'platform': 'iOS', 'users': 4000, 'retention_pct': 40.8, 'revenue_usd': 2300, 'score': 55.0, 'category': 'Game'}, {'id': 'APP007', 'app': 'App 7', 'platform': 'Android', 'users': 4500, 'retention_pct': 42.6, 'revenue_usd': 2600, 'score': 57.5, 'category': 'Finance'}, {'id': 'APP008', 'app': 'App 8', 'platform': 'Web', 'users': 5000, 'retention_pct': 44.4, 'revenue_usd': 2900, 'score': 60.0, 'category': 'Social'}, {'id': 'APP009', 'app': 'App 9', 'platform': 'iOS', 'users': 5500, 'retention_pct': 46.2, 'revenue_usd': 3200, 'score': 62.5, 'category': 'Utility'}, {'id': 'APP010', 'app': 'App 10', 'platform': 'Android', 'users': 6000, 'retention_pct': 48.0, 'revenue_usd': 3500, 'score': 65.0, 'category': 'Game'}, {'id': 'APP011', 'app': 'App 11', 'platform': 'Web', 'users': 6500, 'retention_pct': 49.8, 'revenue_usd': 3800, 'score': 67.5, 'category': 'Finance'}, {'id': 'APP012', 'app': 'App 12', 'platform': 'iOS', 'users': 7000, 'retention_pct': 51.6, 'revenue_usd': 4100, 'score': 70.0, 'category': 'Social'}, {'id': 'APP013', 'app': 'App 13', 'platform': 'Android', 'users': 7500, 'retention_pct': 53.4, 'revenue_usd': 4400, 'score': 72.5, 'category': 'Utility'}, {'id': 'APP014', 'app': 'App 14', 'platform': 'Web', 'users': 8000, 'retention_pct': 55.2, 'revenue_usd': 4700, 'score': 75.0, 'category': 'Game'}, {'id': 'APP015', 'app': 'App 15', 'platform': 'iOS', 'users': 8500, 'retention_pct': 57.0, 'revenue_usd': 5000, 'score': 77.5, 'category': 'Finance'}, {'id': 'APP016', 'app': 'App 16', 'platform': 'Android', 'users': 9000, 'retention_pct': 58.8, 'revenue_usd': 5300, 'score': 80.0, 'category': 'Social'}, {'id': 'APP017', 'app': 'App 17', 'platform': 'Web', 'users': 9500, 'retention_pct': 60.6, 'revenue_usd': 5600, 'score': 82.5, 'category': 'Utility'}, {'id': 'APP018', 'app': 'App 18', 'platform': 'iOS', 'users': 10000, 'retention_pct': 62.4, 'revenue_usd': 5900, 'score': 85.0, 'category': 'Game'}, {'id': 'APP019', 'app': 'App 19', 'platform': 'Android', 'users': 10500, 'retention_pct': 64.2, 'revenue_usd': 6200, 'score': 87.5, 'category': 'Finance'}, {'id': 'APP020', 'app': 'App 20', 'platform': 'Web', 'users': 11000, 'retention_pct': 66.0, 'revenue_usd': 6500, 'score': 90.0, 'category': 'Social'}]

    def __init__(self, tier: Tier = Tier.FREE):
        # Normalize cross-module Tier enum instances by value string
        if isinstance(tier, Tier):
            self.tier = tier
        else:
            self.tier = Tier(getattr(tier, "value", str(tier)))
        self._usage_count = 0

    # ── Revenue helpers ──────────────────────────────────────────────────

    def monthly_price(self) -> int:
        """Return the monthly subscription price for the current tier."""
        return TIER_MONTHLY_PRICE[self.tier.value]

    def get_tier_info(self) -> Dict[str, Any]:
        """Return tier metadata."""
        return {
            "tier": self.tier.value,
            "monthly_price_usd": self.monthly_price(),
            "result_limit": self.RESULT_LIMITS[self.tier.value],
            "usage_count": self._usage_count,
        }

    def _enforce_tier(self, required_value: str) -> None:
        """Raise TierError if current tier is below required_value."""
        order = ["free", "pro", "enterprise"]
        if order.index(self.tier.value) < order.index(required_value):
            raise LocalizationBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of localization_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value localization_bot item."""
        self._usage_count += 1
        return max(self.MOCK_DATA, key=lambda x: x.get("score", 0))

    def analyze(self) -> Dict[str, Any]:
        """Run analysis and return summary statistics (PRO+)."""
        self._enforce_tier("pro")
        self._usage_count += 1
        values = [x.get("score", 0) for x in self.MOCK_DATA]
        return {
            "count": len(self.MOCK_DATA),
            "max_score": max(values),
            "min_score": min(values),
            "avg_score": round(sum(values) / len(values), 2),
        }

    def filter_by_score(self, min_score: float) -> List[Dict[str, Any]]:
        """Return items where score >= min_score (PRO+)."""
        self._enforce_tier("pro")
        self._usage_count += 1
        results = [x for x in self.MOCK_DATA if x.get("score", 0) >= min_score]
        return results[: self.RESULT_LIMITS[self.tier.value]]

    def export_report(self) -> Dict[str, Any]:
        """Generate a full report (ENTERPRISE only)."""
        self._enforce_tier("enterprise")
        self._usage_count += 1
        return {
            "bot": "LocalizationBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
