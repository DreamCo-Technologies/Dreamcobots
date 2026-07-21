"""
Multi-Layered Retail Intelligence Network — Discount Dominator interoperability module.

Orchestrates all five Discount Dominator setting groups (401–600) into a
unified retail intelligence layer:

* Advanced Analytics (401–450) for market insight
* In-Store Tactical Controls (451–500) for physical retail execution
* Online Platform Optimization (501–550) for e-commerce
* Enterprise-Grade Features (551–580) for scalability
* Behavioral Settings (581–600) for customer intelligence
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analytics import AdvancedAnalytics
from .behavioral_settings import BehavioralSettings
from .enterprise_features import EnterpriseFeatures
from .in_store_controls import InStoreTacticalControls
from .online_optimization import OnlinePlatformOptimization


class RetailIntelligenceNetwork:
    """Orchestrates all Discount Dominator modules for retail intelligence.

    This class is the primary integration point for the multi-layered retail
    intelligence network.  It configures every sub-module for retail use and
    exposes a unified API for analysis and action.

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` override dict.
    """

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        self.analytics = AdvancedAnalytics(overrides)
        self.in_store = InStoreTacticalControls(overrides)
        self.online = OnlinePlatformOptimization(overrides)
        self.enterprise = EnterpriseFeatures(overrides)
        self.behavioral = BehavioralSettings(overrides)

        # Apply retail-specific presets across all modules
        self.analytics.configure_for_retail_intelligence()
        self.in_store.configure_for_retail_intelligence()
        self.online.configure_for_marketplace()
        self.enterprise.configure_for_retail_network()
        self.behavioral.configure_for_retail_intelligence()

    # ------------------------------------------------------------------
    # Intelligence methods
    # ------------------------------------------------------------------

    def analyse_sku(self, sku_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a full intelligence analysis on a single SKU.

        Parameters
        ----------
        sku_data:
            Dict with keys such as ``sku``, ``price``, ``stock_pct``,
            ``sales_velocity``, ``competitor_price``.

        Returns
        -------
        dict
            Recommended actions and scores.
        """
        sku = sku_data.get("sku", "UNKNOWN")
        price = float(sku_data.get("price", 0))
        stock_pct = int(sku_data.get("stock_pct", 100))
        sales_velocity = float(sku_data.get("sales_velocity", 0))
        competitor_price = float(sku_data.get("competitor_price", price))

        actions: List[str] = []

        # Clearance decision
        clearance_candidates = self.in_store.get_clearance_candidates(
            {sku: stock_pct}
        )
        if clearance_candidates:
            actions.append("trigger_clearance_pricing")

        # Competitive pricing
        if competitor_price < price and self.online.dynamic_pricing_enabled:
            actions.append("lower_price_to_match_competitor")

        # Flash sale
        if sales_velocity < 0.1 and self.in_store.flash_sale_automation:
            actions.append("trigger_flash_sale")

        # Social proof
        if sales_velocity > 1.0 and self.behavioral.social_proof_injection:
            actions.append("inject_social_proof")

        return {
            "sku": sku,
            "price": price,
            "stock_pct": stock_pct,
            "sales_velocity": sales_velocity,
            "recommended_actions": actions,
            "competitor_gap": round(price - competitor_price, 2),
        }

    def analyse_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a full behavioural intelligence analysis on a customer."""
        return self.behavioral.score_customer(customer_data)

    def get_clearance_candidates(self, inventory: Dict[str, int]) -> List[str]:
        """Return SKUs eligible for clearance pricing."""
        return self.in_store.get_clearance_candidates(inventory)

    def generate_coupon(self, segment: str, discount_pct: int) -> Dict[str, Any]:
        """Generate a personalised coupon for a customer segment."""
        return self.online.generate_coupon(segment, discount_pct)

    def trigger_flash_sale(self, sku: str, discount_pct: int) -> Dict[str, Any]:
        """Trigger a flash sale for an SKU."""
        return self.in_store.trigger_flash_sale(sku, discount_pct)

    def list_active_features(self) -> Dict[str, List[str]]:
        """Return enabled features per module."""
        return {
            "analytics": self.analytics.get_enabled_features(),
            "in_store": self.in_store.get_enabled_features(),
            "online": self.online.get_enabled_features(),
            "enterprise": self.enterprise.get_enabled_features(),
            "behavioral": self.behavioral.get_enabled_features(),
        }

    def summary(self) -> Dict[str, Any]:
        """Return a combined summary of all active sub-module settings."""
        return {
            "module": "retail_intelligence_network",
            "analytics": self.analytics.summary(),
            "in_store": self.in_store.summary(),
            "online": self.online.summary(),
            "enterprise": self.enterprise.summary(),
            "behavioral": self.behavioral.summary(),
        }
