"""
ContractorRateBot — contractor rate optimizer.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class ContractorRateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class ContractorRateBot:
    """Tier-aware contractor rate optimizer."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'JOB001', 'title': 'Role 1', 'company': 'Co 1', 'location': 'NYC', 'salary_usd': 50000, 'match_pct': 57.1, 'score': 52.2, 'industry': 'Finance'}, {'id': 'JOB002', 'title': 'Role 2', 'company': 'Co 2', 'location': 'SF', 'salary_usd': 55000, 'match_pct': 59.2, 'score': 54.4, 'industry': 'Healthcare'}, {'id': 'JOB003', 'title': 'Role 3', 'company': 'Co 3', 'location': 'Austin', 'salary_usd': 60000, 'match_pct': 61.3, 'score': 56.6, 'industry': 'Education'}, {'id': 'JOB004', 'title': 'Role 4', 'company': 'Co 4', 'location': 'Chicago', 'salary_usd': 65000, 'match_pct': 63.4, 'score': 58.8, 'industry': 'Retail'}, {'id': 'JOB005', 'title': 'Role 5', 'company': 'Co 5', 'location': 'Remote', 'salary_usd': 70000, 'match_pct': 65.5, 'score': 61.0, 'industry': 'Tech'}, {'id': 'JOB006', 'title': 'Role 6', 'company': 'Co 6', 'location': 'NYC', 'salary_usd': 75000, 'match_pct': 67.6, 'score': 63.2, 'industry': 'Finance'}, {'id': 'JOB007', 'title': 'Role 7', 'company': 'Co 7', 'location': 'SF', 'salary_usd': 80000, 'match_pct': 69.7, 'score': 65.4, 'industry': 'Healthcare'}, {'id': 'JOB008', 'title': 'Role 8', 'company': 'Co 8', 'location': 'Austin', 'salary_usd': 85000, 'match_pct': 71.8, 'score': 67.6, 'industry': 'Education'}, {'id': 'JOB009', 'title': 'Role 9', 'company': 'Co 9', 'location': 'Chicago', 'salary_usd': 90000, 'match_pct': 73.9, 'score': 69.8, 'industry': 'Retail'}, {'id': 'JOB010', 'title': 'Role 10', 'company': 'Co 10', 'location': 'Remote', 'salary_usd': 95000, 'match_pct': 76.0, 'score': 72.0, 'industry': 'Tech'}, {'id': 'JOB011', 'title': 'Role 11', 'company': 'Co 11', 'location': 'NYC', 'salary_usd': 100000, 'match_pct': 78.1, 'score': 74.2, 'industry': 'Finance'}, {'id': 'JOB012', 'title': 'Role 12', 'company': 'Co 12', 'location': 'SF', 'salary_usd': 105000, 'match_pct': 80.2, 'score': 76.4, 'industry': 'Healthcare'}, {'id': 'JOB013', 'title': 'Role 13', 'company': 'Co 13', 'location': 'Austin', 'salary_usd': 110000, 'match_pct': 82.3, 'score': 78.6, 'industry': 'Education'}, {'id': 'JOB014', 'title': 'Role 14', 'company': 'Co 14', 'location': 'Chicago', 'salary_usd': 115000, 'match_pct': 84.4, 'score': 80.8, 'industry': 'Retail'}, {'id': 'JOB015', 'title': 'Role 15', 'company': 'Co 15', 'location': 'Remote', 'salary_usd': 120000, 'match_pct': 86.5, 'score': 83.0, 'industry': 'Tech'}, {'id': 'JOB016', 'title': 'Role 16', 'company': 'Co 16', 'location': 'NYC', 'salary_usd': 125000, 'match_pct': 88.6, 'score': 85.2, 'industry': 'Finance'}, {'id': 'JOB017', 'title': 'Role 17', 'company': 'Co 17', 'location': 'SF', 'salary_usd': 130000, 'match_pct': 90.7, 'score': 87.4, 'industry': 'Healthcare'}, {'id': 'JOB018', 'title': 'Role 18', 'company': 'Co 18', 'location': 'Austin', 'salary_usd': 135000, 'match_pct': 92.8, 'score': 89.6, 'industry': 'Education'}, {'id': 'JOB019', 'title': 'Role 19', 'company': 'Co 19', 'location': 'Chicago', 'salary_usd': 140000, 'match_pct': 94.9, 'score': 91.8, 'industry': 'Retail'}, {'id': 'JOB020', 'title': 'Role 20', 'company': 'Co 20', 'location': 'Remote', 'salary_usd': 145000, 'match_pct': 97.0, 'score': 94.0, 'industry': 'Tech'}]

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
            raise ContractorRateBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of contractor_rate_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value contractor_rate_bot item."""
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
            "bot": "ContractorRateBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
