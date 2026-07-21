"""
DreamCo Payments — Reporting Dashboard

Provides financial summaries, bot-performance tracking, Discount Dominator
settings management (IDs 401–600), and report export.

Discount Dominator setting groups:
  - analytics  : 401–450  (50 settings)
  - in_store   : 451–500  (50 settings)
  - online     : 501–550  (50 settings)
  - enterprise : 551–580  (30 settings)
  - behavioral : 581–600  (20 settings)

STARTER  : view settings only
GROWTH   : view + update settings, basic export
ENTERPRISE: all features including advanced export formats
"""

import datetime
import json
from typing import Any, Optional

from bots.dreamco_payments.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_ADVANCED_REPORTING,
    FEATURE_DISCOUNT_DOMINATOR,
)
from framework import GlobalAISourcesFlow  # noqa: F401


class DashboardTierError(Exception):
    """Raised when a dashboard feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Discount Dominator setting ranges
# ---------------------------------------------------------------------------

_DD_GROUPS: dict[str, tuple[int, int]] = {
    "analytics": (401, 450),
    "in_store":  (451, 500),
    "online":    (501, 550),
    "enterprise": (551, 580),
    "behavioral": (581, 600),
}

_ALL_EXPORT_FORMATS = {"json", "csv", "pdf"}


def _group_for_id(setting_id: int) -> Optional[str]:
    """Return the Discount Dominator group name for *setting_id*, or None."""
    for group, (lo, hi) in _DD_GROUPS.items():
        if lo <= setting_id <= hi:
            return group
    return None


def _default_setting_value(setting_id: int) -> Any:
    """Return a sensible mock default value for a setting."""
    group = _group_for_id(setting_id)
    defaults: dict[str, Any] = {
        "analytics": True,
        "in_store": 10,
        "online": "enabled",
        "enterprise": False,
        "behavioral": 0.5,
    }
    return defaults.get(group, None)


# Pre-populate the settings catalogue with mock defaults
_SETTINGS_CATALOGUE: dict[int, dict] = {}
for _group, (_lo, _hi) in _DD_GROUPS.items():
    for _sid in range(_lo, _hi + 1):
        _SETTINGS_CATALOGUE[_sid] = {
            "setting_id": _sid,
            "group": _group,
            "name": f"{_group}_setting_{_sid}",
            "value": _default_setting_value(_sid),
            "description": f"Discount Dominator {_group} setting #{_sid}",
        }


# ---------------------------------------------------------------------------
# DreamCo bot registry (mock performance data)
# ---------------------------------------------------------------------------

_BOT_REGISTRY: dict[str, dict] = {
    "ai_chatbot": {
        "bot_name": "ai_chatbot",
        "requests_today": 1_200,
        "requests_total": 450_000,
        "avg_response_ms": 320,
        "error_rate": 0.01,
        "uptime_pct": 99.9,
    },
    "ai_models_integration": {
        "bot_name": "ai_models_integration",
        "requests_today": 800,
        "requests_total": 210_000,
        "avg_response_ms": 580,
        "error_rate": 0.02,
        "uptime_pct": 99.7,
    },
    "dreamco_payments": {
        "bot_name": "dreamco_payments",
        "requests_today": 500,
        "requests_total": 95_000,
        "avg_response_ms": 210,
        "error_rate": 0.005,
        "uptime_pct": 99.95,
    },
    "government_contract_grant": {
        "bot_name": "government_contract_grant",
        "requests_today": 150,
        "requests_total": 30_000,
        "avg_response_ms": 750,
        "error_rate": 0.03,
        "uptime_pct": 99.5,
    },
}


class ReportingDashboard:
    """
    Tier-aware reporting dashboard for DreamCo Payments.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    """

    def __init__(self, tier: Tier = Tier.STARTER) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        # Local copy of settings so updates are instance-scoped
        self._settings: dict[int, dict] = {
            sid: dict(s) for sid, s in _SETTINGS_CATALOGUE.items()
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise DashboardTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier.  Please upgrade."
            )

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------
    # Financial summary  (GROWTH+)
    # ------------------------------------------------------------------

    def get_financial_summary(self, period: str = "monthly") -> dict:
        """
        Return a high-level financial summary for the given period.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        period : str
            One of 'daily', 'weekly', 'monthly', or 'yearly'.

        Returns
        -------
        dict
            total_revenue, total_transactions, average_transaction, etc.
        """
        self._require_feature(FEATURE_ANALYTICS_DASHBOARD)

        if period not in {"daily", "weekly", "monthly", "yearly"}:
            raise ValueError(f"Invalid period '{period}'.")

        multipliers = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
        m = multipliers[period]

        return {
            "period": period,
            "total_revenue": round(4_250.75 * m, 2),
            "total_transactions": 142 * m,
            "average_transaction": 29.93,
            "refunds_issued": 3 * m,
            "refund_amount": round(89.97 * m, 2),
            "new_subscriptions": 12 * m,
            "cancelled_subscriptions": 2 * m,
            "generated_at": ReportingDashboard._now_iso(),
        }

    # ------------------------------------------------------------------
    # Bot performance  (GROWTH+)
    # ------------------------------------------------------------------

    def get_bot_performance(self, bot_name: str) -> dict:
        """
        Return performance metrics for a specific DreamCo bot.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        bot_name : str
            Name of the bot (e.g. 'ai_chatbot').

        Returns
        -------
        dict
            Performance metrics for the bot.
        """
        self._require_feature(FEATURE_ANALYTICS_DASHBOARD)

        if bot_name not in _BOT_REGISTRY:
            raise KeyError(f"Bot '{bot_name}' not found in the DreamCo ecosystem.")

        return dict(_BOT_REGISTRY[bot_name])

    def get_all_bots_performance(self) -> dict:
        """
        Return performance metrics for all registered DreamCo bots.

        Requires GROWTH or ENTERPRISE tier.

        Returns
        -------
        dict
            Mapping of bot_name -> performance metrics.
        """
        self._require_feature(FEATURE_ANALYTICS_DASHBOARD)
        return {name: dict(data) for name, data in _BOT_REGISTRY.items()}

    # ------------------------------------------------------------------
    # Discount Dominator settings
    # ------------------------------------------------------------------

    def get_discount_dominator_settings(self, setting_id: int) -> dict:
        """
        Retrieve a single Discount Dominator setting (IDs 401–600).

        All tiers may read settings.

        Parameters
        ----------
        setting_id : int
            Setting identifier in range 401–600.

        Returns
        -------
        dict
            Setting record with id, group, name, value, description.
        """
        if setting_id not in self._settings:
            raise KeyError(
                f"Setting ID {setting_id} not found.  Valid range: 401–600."
            )
        return dict(self._settings[setting_id])

    def list_discount_dominator_settings(self, group: str) -> list:
        """
        List all Discount Dominator settings for a group.

        All tiers may list settings.

        Parameters
        ----------
        group : str
            One of 'analytics', 'in_store', 'online', 'enterprise', 'behavioral'.

        Returns
        -------
        list[dict]
            All settings belonging to the group, ordered by setting_id.
        """
        if group not in _DD_GROUPS:
            raise ValueError(
                f"Unknown group '{group}'.  Valid groups: {sorted(_DD_GROUPS)}"
            )
        lo, hi = _DD_GROUPS[group]
        return [dict(self._settings[sid]) for sid in range(lo, hi + 1)]

    def update_discount_dominator_setting(
        self, setting_id: int, value: Any
    ) -> dict:
        """
        Update the value of a Discount Dominator setting.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        setting_id : int
            Setting to update.
        value : Any
            New value for the setting.

        Returns
        -------
        dict
            Updated setting record.
        """
        self._require_feature(FEATURE_DISCOUNT_DOMINATOR)

        if setting_id not in self._settings:
            raise KeyError(
                f"Setting ID {setting_id} not found.  Valid range: 401–600."
            )

        self._settings[setting_id]["value"] = value
        self._settings[setting_id]["updated_at"] = self._now_iso()
        return dict(self._settings[setting_id])

    # ------------------------------------------------------------------
    # Report export  (ENTERPRISE gets all formats)
    # ------------------------------------------------------------------

    def export_report(self, format_type: str) -> dict:
        """
        Export a financial report in the requested format.

        - STARTER / GROWTH: json only
        - ENTERPRISE: json, csv, pdf

        Parameters
        ----------
        format_type : str
            One of 'json', 'csv', 'pdf'.

        Returns
        -------
        dict
            Mock export result with format, content, and generated_at.
        """
        fmt = format_type.lower()
        if fmt not in _ALL_EXPORT_FORMATS:
            raise ValueError(
                f"Unsupported format '{format_type}'.  "
                f"Supported: {sorted(_ALL_EXPORT_FORMATS)}"
            )

        if fmt in {"csv", "pdf"}:
            self._require_feature(FEATURE_ADVANCED_REPORTING)

        mock_content: dict[str, str] = {
            "json": '{"report": "mock_data", "total_revenue": 127522.50}',
            "csv": "date,revenue,transactions\n2024-01-01,4250.75,142",
            "pdf": "<mock PDF binary content — base64 encoded in production>",
        }

        return {
            "format": fmt,
            "content": mock_content[fmt],
            "generated_at": self._now_iso(),
            "tier": self.tier.value,
        }
