"""
Dreamcobots RealEstateBot — tier-aware property search and investment analysis.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.real_estate_bot.tiers import REAL_ESTATE_FEATURES, get_real_estate_tier_info
import uuid
from datetime import datetime


class RealEstateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RealEstateBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class RealEstateBot:
    """Tier-aware property search and investment analysis bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise RealEstateBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = REAL_ESTATE_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise RealEstateBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _make_deal(self, idx: int, location: str, budget: float, property_type: str, include_score: bool = False, full_analytics: bool = False) -> dict:
        base_price = 250000 + idx * 50000
        if budget:
            base_price = min(base_price, budget)
        deal = {
            "property_id": f"PROP-{str(uuid.uuid4())[:8].upper()}",
            "address": f"{100 + idx * 10} Main St, {location}",
            "price": float(base_price),
            "type": property_type or "residential",
        }
        if include_score:
            deal["score"] = round(0.5 + idx * 0.05, 2)
        if full_analytics:
            deal["predicted_appreciation"] = f"{3 + idx}%"
            deal["rental_yield"] = f"{4 + idx * 0.5:.1f}%"
            deal["neighborhood_score"] = round(7.0 + idx * 0.2, 1)
        return deal

    def find_deals(self, criteria: dict) -> dict:
        """
        Search for property deals matching the criteria.

        Args:
            criteria: {"location": str, "budget": float optional, "type": str optional}

        Returns:
            {"deals": list, "count": int, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        location = criteria.get("location", "Unknown")
        budget = criteria.get("budget", 0.0)
        property_type = criteria.get("type", "residential")

        if self.tier == Tier.FREE:
            deals = [self._make_deal(i, location, budget, property_type) for i in range(2)]
        elif self.tier == Tier.PRO:
            deals = [self._make_deal(i, location, budget, property_type, include_score=True) for i in range(5)]
        else:  # ENTERPRISE
            deals = [self._make_deal(i, location, budget, property_type, include_score=True, full_analytics=True) for i in range(10)]

        return {
            "deals": deals,
            "count": len(deals),
            "tier": self.tier.value,
        }

    def analyze_property(self, property_id: str) -> dict:
        """
        Analyze a specific property for investment potential.

        Args:
            property_id: The property identifier.

        Returns:
            {"property_id": str, "estimated_value": float, "roi_estimate": float,
             "risk_score": float, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError(
                "Property analysis is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        if self.tier == Tier.PRO:
            estimated_value = 320000.0
            roi_estimate = 0.07
            risk_score = 0.35
        else:  # ENTERPRISE
            estimated_value = 315000.0
            roi_estimate = 0.085
            risk_score = 0.25

        return {
            "property_id": property_id,
            "estimated_value": estimated_value,
            "roi_estimate": roi_estimate,
            "risk_score": risk_score,
            "tier": self.tier.value,
        }

    def calculate_roi(self, property: dict) -> dict:
        """
        Calculate the return on investment for a property.

        Args:
            property: {"price": float, "rent": float, "expenses": float optional}

        Returns:
            {"property": dict, "annual_roi": float, "monthly_cashflow": float, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError(
                "ROI calculation is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        price = property.get("price", 0.0)
        rent = property.get("rent", 0.0)
        expenses = property.get("expenses", 0.0)

        monthly_cashflow = rent - expenses
        annual_income = monthly_cashflow * 12
        annual_roi = (annual_income / price) if price > 0 else 0.0

        return {
            "property": property,
            "annual_roi": round(annual_roi, 4),
            "monthly_cashflow": round(monthly_cashflow, 2),
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "buddy_integration": True,
        }
