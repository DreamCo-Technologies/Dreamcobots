"""
Enterprise-Grade Features module for the Discount Dominator (settings 551–580).

Provides the :class:`EnterpriseFeatures` facade used by all bots that operate
at enterprise scale with multi-location, compliance, and integration needs.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_ENTERPRISE,
    get_setting,
    get_group_settings,
    as_dict,
)


class EnterpriseFeatures:
    """Facade for the Enterprise-Grade Features settings group (551–580).

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
    def multi_location_support(self) -> bool:
        return bool(get_setting(551).value)

    @property
    def api_rate_limit_per_min(self) -> int:
        return int(get_setting(552).value)

    @property
    def compliance_monitoring(self) -> bool:
        return bool(get_setting(554).value)

    @property
    def encryption_level(self) -> str:
        return str(get_setting(555).value)

    @property
    def sso_enabled(self) -> bool:
        return bool(get_setting(556).value)

    @property
    def rbac_enabled(self) -> bool:
        return bool(get_setting(557).value)

    @property
    def tenant_isolation(self) -> bool:
        return bool(get_setting(558).value)

    @property
    def sla_uptime_pct(self) -> float:
        return float(get_setting(560).value)

    @property
    def auto_scaling(self) -> bool:
        return bool(get_setting(563).value)

    @property
    def erp_integration(self) -> bool:
        return bool(get_setting(570).value)

    @property
    def crm_integration(self) -> bool:
        return bool(get_setting(571).value)

    @property
    def wms_integration(self) -> bool:
        return bool(get_setting(572).value)

    @property
    def oms_integration(self) -> bool:
        return bool(get_setting(573).value)

    @property
    def advanced_fraud_detection(self) -> bool:
        return bool(get_setting(574).value)

    @property
    def data_residency_region(self) -> str:
        return str(get_setting(567).value)

    @property
    def audit_trail_retention_years(self) -> int:
        return int(get_setting(566).value)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all enterprise settings as ``{id: value}``."""
        return as_dict(GROUP_ENTERPRISE)

    def get_enabled_features(self) -> List[str]:
        """Return names of enterprise settings that are currently ``True``."""
        return [
            s.name
            for s in get_group_settings(GROUP_ENTERPRISE)
            if s.value is True
        ]

    def configure_for_real_estate_enterprise(self) -> None:
        """Apply enterprise presets for large-scale real estate deployments."""
        DISCOUNT_DOMINATOR_SETTINGS[551].value = True   # multi_location
        DISCOUNT_DOMINATOR_SETTINGS[570].value = True   # erp_integration
        DISCOUNT_DOMINATOR_SETTINGS[571].value = True   # crm_integration
        DISCOUNT_DOMINATOR_SETTINGS[577].value = True   # custom_reporting
        DISCOUNT_DOMINATOR_SETTINGS[579].value = True   # multi_region_failover

    def configure_for_retail_network(self) -> None:
        """Apply enterprise presets for the retail intelligence network."""
        DISCOUNT_DOMINATOR_SETTINGS[551].value = True   # multi_location
        DISCOUNT_DOMINATOR_SETTINGS[572].value = True   # wms_integration
        DISCOUNT_DOMINATOR_SETTINGS[573].value = True   # oms_integration
        DISCOUNT_DOMINATOR_SETTINGS[563].value = True   # auto_scaling
        DISCOUNT_DOMINATOR_SETTINGS[574].value = True   # advanced_fraud_detection

    def is_compliant(self) -> bool:
        """Return True if all critical compliance settings are enabled."""
        return (
            self.compliance_monitoring
            and self.encryption_level == "AES256"
            and self.rbac_enabled
            and self.tenant_isolation
        )

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict of key enterprise settings."""
        return {
            "multi_location_support": self.multi_location_support,
            "sla_uptime_pct": self.sla_uptime_pct,
            "encryption_level": self.encryption_level,
            "sso_enabled": self.sso_enabled,
            "rbac_enabled": self.rbac_enabled,
            "auto_scaling": self.auto_scaling,
            "erp_integration": self.erp_integration,
            "crm_integration": self.crm_integration,
            "compliant": self.is_compliant(),
            "enabled_feature_count": len(self.get_enabled_features()),
        }
