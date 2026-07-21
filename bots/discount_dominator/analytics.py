"""
Advanced Analytics module for the Discount Dominator (settings 401–450).

This module exposes a high-level :class:`AdvancedAnalytics` facade that reads
its behaviour from the Discount Dominator settings registry and provides
methods used by other bot modules and interoperability consumers such as
the real estate optimisation system, the car-flipping bot, and the
multi-layered retail intelligence network.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_ANALYTICS,
    get_setting,
    get_group_settings,
    as_dict,
)


class AdvancedAnalytics:
    """Facade for the Advanced Analytics settings group (401–450).

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` mapping to override defaults.
    """

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        if overrides:
            for sid, val in overrides.items():
                if sid in DISCOUNT_DOMINATOR_SETTINGS:
                    DISCOUNT_DOMINATOR_SETTINGS[sid].value = val

    # ------------------------------------------------------------------
    # Property helpers — each wraps a specific setting for easy access
    # ------------------------------------------------------------------

    @property
    def realtime_enabled(self) -> bool:
        return bool(get_setting(401).value)

    @property
    def retention_days(self) -> int:
        return int(get_setting(402).value)

    @property
    def competitor_monitoring(self) -> bool:
        return bool(get_setting(404).value)

    @property
    def demand_forecasting(self) -> bool:
        return bool(get_setting(406).value)

    @property
    def revenue_attribution_model(self) -> str:
        return str(get_setting(409).value)

    @property
    def real_estate_price_index(self) -> bool:
        return bool(get_setting(410).value)

    @property
    def auto_parts_market_feed(self) -> bool:
        return bool(get_setting(411).value)

    @property
    def retail_basket_analysis(self) -> bool:
        return bool(get_setting(412).value)

    @property
    def anomaly_detection(self) -> bool:
        return bool(get_setting(414).value)

    @property
    def cross_bot_data_sharing(self) -> bool:
        return bool(get_setting(427).value)

    @property
    def export_format(self) -> str:
        return str(get_setting(428).value)

    @property
    def alert_threshold_pct(self) -> int:
        return int(get_setting(429).value)

    @property
    def dashboard_refresh_sec(self) -> int:
        return int(get_setting(430).value)

    @property
    def base_currency(self) -> str:
        return str(get_setting(432).value)

    @property
    def analytics_api_enabled(self) -> bool:
        return bool(get_setting(449).value)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all analytics settings as ``{id: value}``."""
        return as_dict(GROUP_ANALYTICS)

    def get_enabled_features(self) -> List[str]:
        """Return names of analytics settings that are currently ``True``."""
        return [
            s.name
            for s in get_group_settings(GROUP_ANALYTICS)
            if s.value is True
        ]

    def configure_for_real_estate(self) -> None:
        """Apply analytics presets optimised for the real estate system."""
        DISCOUNT_DOMINATOR_SETTINGS[410].value = True   # real_estate_price_index
        DISCOUNT_DOMINATOR_SETTINGS[419].value = True   # geo_heatmap_analytics
        DISCOUNT_DOMINATOR_SETTINGS[407].value = True   # cohort_analysis_enabled
        DISCOUNT_DOMINATOR_SETTINGS[417].value = "rfm_ml"  # clv model

    def configure_for_car_flipping(self) -> None:
        """Apply analytics presets optimised for the car-flipping bot."""
        DISCOUNT_DOMINATOR_SETTINGS[411].value = True   # auto_parts_market_feed
        DISCOUNT_DOMINATOR_SETTINGS[404].value = True   # competitor_price_monitoring
        DISCOUNT_DOMINATOR_SETTINGS[418].value = True   # price_elasticity_modelling
        DISCOUNT_DOMINATOR_SETTINGS[415].value = True   # inventory_turnover_tracking

    def configure_for_retail_intelligence(self) -> None:
        """Apply analytics presets for the retail intelligence network."""
        DISCOUNT_DOMINATOR_SETTINGS[412].value = True   # retail_basket_analysis
        DISCOUNT_DOMINATOR_SETTINGS[413].value = True   # cross_channel_attribution
        DISCOUNT_DOMINATOR_SETTINGS[425].value = True   # social_sentiment_feed
        DISCOUNT_DOMINATOR_SETTINGS[427].value = True   # cross_bot_data_sharing

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict of key analytics settings."""
        return {
            "realtime_enabled": self.realtime_enabled,
            "retention_days": self.retention_days,
            "competitor_monitoring": self.competitor_monitoring,
            "demand_forecasting": self.demand_forecasting,
            "attribution_model": self.revenue_attribution_model,
            "export_format": self.export_format,
            "base_currency": self.base_currency,
            "alert_threshold_pct": self.alert_threshold_pct,
            "enabled_feature_count": len(self.get_enabled_features()),
        }
