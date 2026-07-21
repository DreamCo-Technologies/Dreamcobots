"""
ServiceExpansionBot — service expansion advisor.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class ServiceExpansionBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class ServiceExpansionBot:
    """Tier-aware service expansion advisor."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'GIG001', 'title': 'Service 1', 'price_usd': 40, 'rating': 4.04, 'reviews': 22, 'score': 52.3, 'category': 'Writing'}, {'id': 'GIG002', 'title': 'Service 2', 'price_usd': 55, 'rating': 4.08, 'reviews': 34, 'score': 54.6, 'category': 'SEO'}, {'id': 'GIG003', 'title': 'Service 3', 'price_usd': 70, 'rating': 4.12, 'reviews': 46, 'score': 56.9, 'category': 'Video'}, {'id': 'GIG004', 'title': 'Service 4', 'price_usd': 85, 'rating': 4.16, 'reviews': 58, 'score': 59.2, 'category': 'Tech'}, {'id': 'GIG005', 'title': 'Service 5', 'price_usd': 100, 'rating': 4.2, 'reviews': 70, 'score': 61.5, 'category': 'Design'}, {'id': 'GIG006', 'title': 'Service 6', 'price_usd': 115, 'rating': 4.24, 'reviews': 82, 'score': 63.8, 'category': 'Writing'}, {'id': 'GIG007', 'title': 'Service 7', 'price_usd': 130, 'rating': 4.28, 'reviews': 94, 'score': 66.1, 'category': 'SEO'}, {'id': 'GIG008', 'title': 'Service 8', 'price_usd': 145, 'rating': 4.32, 'reviews': 106, 'score': 68.4, 'category': 'Video'}, {'id': 'GIG009', 'title': 'Service 9', 'price_usd': 160, 'rating': 4.36, 'reviews': 118, 'score': 70.7, 'category': 'Tech'}, {'id': 'GIG010', 'title': 'Service 10', 'price_usd': 175, 'rating': 4.4, 'reviews': 130, 'score': 73.0, 'category': 'Design'}, {'id': 'GIG011', 'title': 'Service 11', 'price_usd': 190, 'rating': 4.44, 'reviews': 142, 'score': 75.3, 'category': 'Writing'}, {'id': 'GIG012', 'title': 'Service 12', 'price_usd': 205, 'rating': 4.48, 'reviews': 154, 'score': 77.6, 'category': 'SEO'}, {'id': 'GIG013', 'title': 'Service 13', 'price_usd': 220, 'rating': 4.52, 'reviews': 166, 'score': 79.9, 'category': 'Video'}, {'id': 'GIG014', 'title': 'Service 14', 'price_usd': 235, 'rating': 4.56, 'reviews': 178, 'score': 82.2, 'category': 'Tech'}, {'id': 'GIG015', 'title': 'Service 15', 'price_usd': 250, 'rating': 4.6, 'reviews': 190, 'score': 84.5, 'category': 'Design'}, {'id': 'GIG016', 'title': 'Service 16', 'price_usd': 265, 'rating': 4.64, 'reviews': 202, 'score': 86.8, 'category': 'Writing'}, {'id': 'GIG017', 'title': 'Service 17', 'price_usd': 280, 'rating': 4.68, 'reviews': 214, 'score': 89.1, 'category': 'SEO'}, {'id': 'GIG018', 'title': 'Service 18', 'price_usd': 295, 'rating': 4.72, 'reviews': 226, 'score': 91.4, 'category': 'Video'}, {'id': 'GIG019', 'title': 'Service 19', 'price_usd': 310, 'rating': 4.76, 'reviews': 238, 'score': 93.7, 'category': 'Tech'}, {'id': 'GIG020', 'title': 'Service 20', 'price_usd': 325, 'rating': 4.8, 'reviews': 250, 'score': 96.0, 'category': 'Design'}]

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
            raise ServiceExpansionBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of service_expansion_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value service_expansion_bot item."""
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
            "bot": "ServiceExpansionBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
