"""
Car Flipping and Parts Arbitrage Bot — Discount Dominator interoperability module.

Wires together the Discount Dominator settings (401–600) for the vehicle
resale and auto-parts arbitrage use-case:

* Auto-parts market data feed (setting 411)
* Competitor price monitoring (setting 404)
* Price elasticity modelling (setting 418)
* Car buyer intent model (setting 593)
* Marketplace fee optimiser (setting 525)
* Dynamic pricing (setting 503)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analytics import AdvancedAnalytics
from .behavioral_settings import BehavioralSettings
from .enterprise_features import EnterpriseFeatures
from .online_optimization import OnlinePlatformOptimization


class CarFlippingBot:
    """Applies Discount Dominator settings to the car-flipping and parts arbitrage bot.

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` override dict.
    """

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        self.analytics = AdvancedAnalytics(overrides)
        self.behavioral = BehavioralSettings(overrides)
        self.enterprise = EnterpriseFeatures(overrides)
        self.online = OnlinePlatformOptimization(overrides)

        # Apply domain-specific presets
        self.analytics.configure_for_car_flipping()
        self.behavioral.configure_for_car_flipping()
        self.online.configure_for_car_flipping()

    # ------------------------------------------------------------------
    # Arbitrage helpers
    # ------------------------------------------------------------------

    def evaluate_vehicle(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a vehicle's arbitrage potential.

        Parameters
        ----------
        vehicle_data:
            Dict with keys such as ``purchase_price``, ``estimated_sale_price``,
            ``repair_cost``, ``days_to_flip``.

        Returns
        -------
        dict
            Profit estimate, ROI, and a buy/pass recommendation.
        """
        purchase_price = float(vehicle_data.get("purchase_price", 0))
        estimated_sale = float(vehicle_data.get("estimated_sale_price", 0))
        repair_cost = float(vehicle_data.get("repair_cost", 0))
        days_to_flip = int(vehicle_data.get("days_to_flip", 30))

        total_cost = purchase_price + repair_cost
        gross_profit = estimated_sale - total_cost
        roi_pct = (gross_profit / max(total_cost, 1)) * 100

        if roi_pct > 20 and days_to_flip <= 45:
            recommendation = "buy"
        elif roi_pct > 10:
            recommendation = "consider"
        else:
            recommendation = "pass"

        return {
            "gross_profit": round(gross_profit, 2),
            "roi_pct": round(roi_pct, 2),
            "days_to_flip": days_to_flip,
            "recommendation": recommendation,
            "competitor_monitoring": self.analytics.competitor_monitoring,
            "dynamic_pricing": self.online.dynamic_pricing_enabled,
        }

    def evaluate_part(self, part_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an auto-part's arbitrage potential.

        Parameters
        ----------
        part_data:
            Dict with keys such as ``buy_price``, ``sell_price``,
            ``platform_fee_pct``.

        Returns
        -------
        dict
            Net profit and a buy/pass recommendation.
        """
        buy_price = float(part_data.get("buy_price", 0))
        sell_price = float(part_data.get("sell_price", 0))
        fee_pct = float(part_data.get("platform_fee_pct", 10))

        fees = sell_price * (fee_pct / 100.0)
        net_profit = sell_price - buy_price - fees
        margin_pct = (net_profit / max(sell_price, 1)) * 100

        return {
            "net_profit": round(net_profit, 2),
            "margin_pct": round(margin_pct, 2),
            "recommendation": "buy" if net_profit > 0 else "pass",
            "auto_parts_feed_enabled": self.analytics.auto_parts_market_feed,
        }

    def score_buyer_intent(self, buyer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a potential buyer's purchase intent."""
        return self.behavioral.score_customer(buyer_data)

    def list_active_features(self) -> Dict[str, List[str]]:
        """Return enabled features per module for this bot."""
        return {
            "analytics": self.analytics.get_enabled_features(),
            "behavioral": self.behavioral.get_enabled_features(),
            "online": self.online.get_enabled_features(),
        }

    def summary(self) -> Dict[str, Any]:
        """Return a combined summary of all active sub-module settings."""
        return {
            "module": "car_flipping_bot",
            "analytics": self.analytics.summary(),
            "behavioral": self.behavioral.summary(),
            "online": self.online.summary(),
        }
