"""
In-Store Tactical Controls module for the Discount Dominator (settings 451–500).

Provides the :class:`InStoreTacticalControls` facade used by all bots that
have an in-store physical presence component.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_INSTORE,
    get_setting,
    get_group_settings,
    as_dict,
)


class InStoreTacticalControls:
    """Facade for the In-Store Tactical Controls settings group (451–500).

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
    def display_optimisation(self) -> bool:
        return bool(get_setting(451).value)

    @property
    def shelf_placement_strategy(self) -> str:
        return str(get_setting(452).value)

    @property
    def bundle_discount_rules(self) -> bool:
        return bool(get_setting(453).value)

    @property
    def flash_sale_automation(self) -> bool:
        return bool(get_setting(454).value)

    @property
    def loss_leader_strategy(self) -> bool:
        return bool(get_setting(455).value)

    @property
    def endcap_rotation_days(self) -> int:
        return int(get_setting(456).value)

    @property
    def price_tag_sync(self) -> bool:
        return bool(get_setting(457).value)

    @property
    def clearance_threshold_pct(self) -> int:
        return int(get_setting(463).value)

    @property
    def pos_integration(self) -> bool:
        return bool(get_setting(467).value)

    @property
    def real_time_stock_visibility(self) -> bool:
        return bool(get_setting(472).value)

    @property
    def bopis_enabled(self) -> bool:
        return bool(get_setting(492).value)

    @property
    def price_match_automation(self) -> bool:
        return bool(get_setting(494).value)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all in-store settings as ``{id: value}``."""
        return as_dict(GROUP_INSTORE)

    def get_enabled_features(self) -> List[str]:
        """Return names of in-store settings that are currently ``True``."""
        return [
            s.name
            for s in get_group_settings(GROUP_INSTORE)
            if s.value is True
        ]

    def configure_for_retail_intelligence(self) -> None:
        """Apply in-store presets for the multi-layered retail intelligence network."""
        DISCOUNT_DOMINATOR_SETTINGS[451].value = True   # display_optimisation
        DISCOUNT_DOMINATOR_SETTINGS[453].value = True   # bundle_discount_rules
        DISCOUNT_DOMINATOR_SETTINGS[467].value = True   # pos_integration
        DISCOUNT_DOMINATOR_SETTINGS[472].value = True   # real_time_stock_visibility
        DISCOUNT_DOMINATOR_SETTINGS[486].value = True   # aisle_traffic_analysis

    def trigger_flash_sale(self, sku: str, discount_pct: int) -> Dict[str, Any]:
        """Simulate triggering a flash sale for a given SKU.

        Returns a dict describing the triggered flash sale event.
        """
        if not self.flash_sale_automation:
            return {"status": "disabled", "sku": sku}
        return {
            "status": "triggered",
            "sku": sku,
            "discount_pct": discount_pct,
            "source": "flash_sale_automation",
        }

    def get_clearance_candidates(self, inventory_levels: Dict[str, int]) -> List[str]:
        """Return SKUs whose inventory is at or below the clearance threshold.

        Parameters
        ----------
        inventory_levels:
            ``{sku: stock_level_pct}`` mapping where values are 0–100.
        """
        threshold = self.clearance_threshold_pct
        return [
            sku for sku, level in inventory_levels.items()
            if level <= threshold
        ]

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict of key in-store settings."""
        return {
            "display_optimisation": self.display_optimisation,
            "shelf_placement_strategy": self.shelf_placement_strategy,
            "bundle_discount_rules": self.bundle_discount_rules,
            "flash_sale_automation": self.flash_sale_automation,
            "clearance_threshold_pct": self.clearance_threshold_pct,
            "pos_integration": self.pos_integration,
            "bopis_enabled": self.bopis_enabled,
            "enabled_feature_count": len(self.get_enabled_features()),
        }
