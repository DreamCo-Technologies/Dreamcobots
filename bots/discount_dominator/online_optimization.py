"""
Online Platform Optimization module for the Discount Dominator (settings 501–550).

Provides the :class:`OnlinePlatformOptimization` facade used by all bots that
operate on e-commerce and marketplace channels.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_ONLINE,
    get_setting,
    get_group_settings,
    as_dict,
)


class OnlinePlatformOptimization:
    """Facade for the Online Platform Optimization settings group (501–550).

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
    # Property helpers
    # ------------------------------------------------------------------

    @property
    def seo_level(self) -> str:
        return str(get_setting(501).value)

    @property
    def product_listing_enhancement(self) -> bool:
        return bool(get_setting(502).value)

    @property
    def dynamic_pricing_enabled(self) -> bool:
        return bool(get_setting(503).value)

    @property
    def cross_platform_syndication(self) -> bool:
        return bool(get_setting(504).value)

    @property
    def sponsored_ad_automation(self) -> bool:
        return bool(get_setting(506).value)

    @property
    def cart_recovery_emails(self) -> bool:
        return bool(get_setting(507).value)

    @property
    def recommendation_engine(self) -> bool:
        return bool(get_setting(509).value)

    @property
    def site_speed_target_ms(self) -> int:
        return int(get_setting(513).value)

    @property
    def buy_box_strategy(self) -> str:
        return str(get_setting(526).value)

    @property
    def dynamic_coupon_generation(self) -> bool:
        return bool(get_setting(549).value)

    @property
    def gdpr_consent_management(self) -> bool:
        return bool(get_setting(539).value)

    @property
    def accessibility_level(self) -> str:
        return str(get_setting(540).value)

    @property
    def fraud_scoring_at_checkout(self) -> bool:
        return bool(get_setting(542).value)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all online optimisation settings as ``{id: value}``."""
        return as_dict(GROUP_ONLINE)

    def get_enabled_features(self) -> List[str]:
        """Return names of online settings that are currently ``True``."""
        return [
            s.name
            for s in get_group_settings(GROUP_ONLINE)
            if s.value is True
        ]

    def configure_for_marketplace(self) -> None:
        """Apply presets optimised for marketplace (Amazon/eBay) selling."""
        DISCOUNT_DOMINATOR_SETTINGS[501].value = "aggressive"  # seo
        DISCOUNT_DOMINATOR_SETTINGS[503].value = True    # dynamic_pricing
        DISCOUNT_DOMINATOR_SETTINGS[504].value = True    # cross_platform_syndication
        DISCOUNT_DOMINATOR_SETTINGS[506].value = True    # sponsored_ads
        DISCOUNT_DOMINATOR_SETTINGS[526].value = "mixed" # buy_box_strategy

    def configure_for_car_flipping(self) -> None:
        """Apply online presets for the car-flipping and parts arbitrage bot."""
        DISCOUNT_DOMINATOR_SETTINGS[503].value = True    # dynamic_pricing
        DISCOUNT_DOMINATOR_SETTINGS[504].value = True    # cross_platform_syndication
        DISCOUNT_DOMINATOR_SETTINGS[525].value = True    # marketplace_fee_optimiser
        DISCOUNT_DOMINATOR_SETTINGS[542].value = True    # fraud_scoring_at_checkout

    def configure_for_real_estate(self) -> None:
        """Apply online presets for the real estate optimisation system."""
        DISCOUNT_DOMINATOR_SETTINGS[502].value = True    # listing enhancement
        DISCOUNT_DOMINATOR_SETTINGS[509].value = True    # recommendation engine
        DISCOUNT_DOMINATOR_SETTINGS[515].value = True    # social_commerce
        DISCOUNT_DOMINATOR_SETTINGS[536].value = True    # delivery_promise_engine

    def generate_coupon(self, segment: str, discount_pct: int) -> Dict[str, Any]:
        """Simulate generating a personalised coupon for a customer segment."""
        if not self.dynamic_coupon_generation:
            return {"status": "disabled", "segment": segment}
        return {
            "status": "generated",
            "segment": segment,
            "discount_pct": discount_pct,
            "source": "dynamic_coupon_generation",
        }

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict of key online settings."""
        return {
            "seo_level": self.seo_level,
            "dynamic_pricing_enabled": self.dynamic_pricing_enabled,
            "cross_platform_syndication": self.cross_platform_syndication,
            "recommendation_engine": self.recommendation_engine,
            "buy_box_strategy": self.buy_box_strategy,
            "site_speed_target_ms": self.site_speed_target_ms,
            "gdpr_consent_management": self.gdpr_consent_management,
            "accessibility_level": self.accessibility_level,
            "enabled_feature_count": len(self.get_enabled_features()),
        }
