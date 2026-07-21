"""
Real Estate Optimization System — Discount Dominator interoperability module.

This module wires together the relevant Discount Dominator settings (401–600)
to drive the real estate optimisation use-case:

* Property-price index analytics (setting 410)
* Geo heat-map analytics (setting 419)
* Real estate buyer scoring (setting 592)
* Enterprise multi-location and CRM/ERP integrations (settings 551, 571, 570)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analytics import AdvancedAnalytics
from .behavioral_settings import BehavioralSettings
from .enterprise_features import EnterpriseFeatures
from .online_optimization import OnlinePlatformOptimization


class RealEstateOptimizer:
    """Applies Discount Dominator settings to the real estate optimisation system.

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` override dict passed through to all
        sub-modules so callers can customise behaviour without touching defaults.
    """

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        self.analytics = AdvancedAnalytics(overrides)
        self.behavioral = BehavioralSettings(overrides)
        self.enterprise = EnterpriseFeatures(overrides)
        self.online = OnlinePlatformOptimization(overrides)

        # Apply domain-specific presets
        self.analytics.configure_for_real_estate()
        self.behavioral.configure_for_real_estate()
        self.enterprise.configure_for_real_estate_enterprise()
        self.online.configure_for_real_estate()

    # ------------------------------------------------------------------
    # Property search & scoring
    # ------------------------------------------------------------------

    def score_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a property listing against current market analytics.

        Parameters
        ----------
        property_data:
            Dict with keys such as ``price``, ``sqft``, ``location``,
            ``days_on_market``.

        Returns
        -------
        dict
            Investment score between 0.0 (poor) and 1.0 (excellent) with a
            recommendation label.
        """
        price = float(property_data.get("price", 0))
        sqft = float(property_data.get("sqft", 1))
        days_on_market = int(property_data.get("days_on_market", 30))

        price_per_sqft = price / max(sqft, 1)
        freshness_score = max(0.0, 1.0 - days_on_market / 180.0)
        value_score = max(0.0, 1.0 - price_per_sqft / 1000.0)

        investment_score = round((freshness_score + value_score) / 2.0, 4)

        if investment_score > 0.7:
            recommendation = "strong_buy"
        elif investment_score > 0.4:
            recommendation = "consider"
        else:
            recommendation = "pass"

        return {
            "investment_score": investment_score,
            "recommendation": recommendation,
            "price_per_sqft": round(price_per_sqft, 2),
            "days_on_market": days_on_market,
            "analytics_enabled": self.analytics.real_estate_price_index,
        }

    def score_buyer(self, buyer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a potential property buyer using behavioral settings."""
        return self.behavioral.score_customer(buyer_data)

    def list_active_features(self) -> Dict[str, List[str]]:
        """Return enabled features per module for this optimizer."""
        return {
            "analytics": self.analytics.get_enabled_features(),
            "behavioral": self.behavioral.get_enabled_features(),
            "enterprise": self.enterprise.get_enabled_features(),
            "online": self.online.get_enabled_features(),
        }

    def summary(self) -> Dict[str, Any]:
        """Return a combined summary of all active sub-module settings."""
        return {
            "module": "real_estate_optimizer",
            "analytics": self.analytics.summary(),
            "behavioral": self.behavioral.summary(),
            "enterprise": self.enterprise.summary(),
            "online": self.online.summary(),
        }
