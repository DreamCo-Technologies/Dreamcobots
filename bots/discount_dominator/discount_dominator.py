"""
Discount Dominator — main bot class.

Integrates all Discount Dominator settings (401–600) and exposes a unified
entry-point for the three primary interoperability systems:

1. Real Estate Optimization System (:class:`~.real_estate_optimizer.RealEstateOptimizer`)
2. Car Flipping and Parts Arbitrage Bot (:class:`~.car_flipping_bot.CarFlippingBot`)
3. Multi-Layered Retail Intelligence Network (:class:`~.retail_intelligence.RetailIntelligenceNetwork`)

Usage
-----
    from bots.discount_dominator.discount_dominator import DiscountDominator

    bot = DiscountDominator()
    print(bot.summary())

    # Access domain modules
    score = bot.real_estate.score_property({"price": 350000, "sqft": 1200})
    deal  = bot.car_flipping.evaluate_vehicle({"purchase_price": 8000, ...})
    sku   = bot.retail.analyse_sku({"sku": "SKU-001", "price": 29.99, ...})
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    ALL_GROUPS,
    apply_settings,
    as_dict,
    reset_all,
)
from .analytics import AdvancedAnalytics
from .in_store_controls import InStoreTacticalControls
from .online_optimization import OnlinePlatformOptimization
from .enterprise_features import EnterpriseFeatures
from .behavioral_settings import BehavioralSettings
from .real_estate_optimizer import RealEstateOptimizer
from .car_flipping_bot import CarFlippingBot
from .retail_intelligence import RetailIntelligenceNetwork


class DiscountDominator:
    """Central orchestrator for Discount Dominator settings (401–600).

    Instantiating this class configures all five setting groups and makes
    the three interoperability domain modules available as attributes.

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` mapping to override defaults at
        construction time.  Applied before domain modules are created.
    """

    #: Total number of settings managed by this bot (401–600 inclusive).
    SETTINGS_COUNT = 200
    #: First setting ID.
    SETTINGS_START = 401
    #: Last setting ID.
    SETTINGS_END = 600

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        if overrides:
            apply_settings(overrides)

        # Core setting-group facades (shared state via module-level registry)
        self.analytics = AdvancedAnalytics()
        self.in_store = InStoreTacticalControls()
        self.online = OnlinePlatformOptimization()
        self.enterprise = EnterpriseFeatures()
        self.behavioral = BehavioralSettings()

        # Domain-specific interoperability modules
        self.real_estate = RealEstateOptimizer()
        self.car_flipping = CarFlippingBot()
        self.retail = RetailIntelligenceNetwork()

    # ------------------------------------------------------------------
    # Settings management
    # ------------------------------------------------------------------

    def configure(self, overrides: Dict[int, Any]) -> None:
        """Apply a partial settings override dictionary at runtime."""
        apply_settings(overrides)

    def reset(self) -> None:
        """Reset all settings to their default values."""
        reset_all()

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all 200 settings as ``{setting_id: current_value}``."""
        return as_dict()

    def get_settings_for_group(self, group: str) -> Dict[int, Any]:
        """Return settings for a specific group.

        Valid groups: ``advanced_analytics``, ``in_store_tactical_controls``,
        ``online_platform_optimization``, ``enterprise_grade_features``,
        ``behavioral_settings``.
        """
        return as_dict(group=group)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return a high-level summary of the Discount Dominator configuration."""
        return {
            "bot": "DiscountDominator",
            "settings_range": f"{self.SETTINGS_START}–{self.SETTINGS_END}",
            "total_settings": self.SETTINGS_COUNT,
            "groups": ALL_GROUPS,
            "analytics_summary": self.analytics.summary(),
            "in_store_summary": self.in_store.summary(),
            "online_summary": self.online.summary(),
            "enterprise_summary": self.enterprise.summary(),
            "behavioral_summary": self.behavioral.summary(),
        }

    def run(self) -> None:
        """Start the Discount Dominator bot (prints a diagnostics summary)."""
        print("Discount Dominator bot starting...")
        s = self.summary()
        print(f"  Settings range : {s['settings_range']}")
        print(f"  Total settings : {s['total_settings']}")
        print(f"  Groups         : {', '.join(s['groups'])}")
        print(
            f"  Analytics feats: "
            f"{s['analytics_summary']['enabled_feature_count']} enabled"
        )
        print(
            f"  In-store feats : "
            f"{s['in_store_summary']['enabled_feature_count']} enabled"
        )
        print(
            f"  Online feats   : "
            f"{s['online_summary']['enabled_feature_count']} enabled"
        )
        print(
            f"  Enterprise feats: "
            f"{s['enterprise_summary']['enabled_feature_count']} enabled"
        )
        print(
            f"  Behavioural feats: "
            f"{s['behavioral_summary']['enabled_feature_count']} enabled"
        )
        print("Discount Dominator bot ready.")


if __name__ == "__main__":
    DiscountDominator().run()
