"""
Big Bro AI — Master Dashboard

Aggregates data from all Big Bro AI sub-systems into a single,
unified view.  Shows tasks, errors, revenue, compound growth,
readiness scores, franchise health, and study progress.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Dashboard panel types
# ---------------------------------------------------------------------------

PANEL_NAMES: tuple[str, ...] = (
    "overview",
    "memory_system",
    "bot_factory",
    "continuous_study",
    "prospectus_system",
    "courses_system",
    "route_gps",
    "sales_monetization",
    "catalog_franchise",
    "mentor_engine",
)


# ---------------------------------------------------------------------------
# Alert levels
# ---------------------------------------------------------------------------

class AlertLevel:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Dashboard alert
# ---------------------------------------------------------------------------

@dataclass
class DashboardAlert:
    """A system-generated alert surfaced in the dashboard."""
    level: str
    source: str
    message: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Master Dashboard
# ---------------------------------------------------------------------------

class MasterDashboard:
    """
    Unified command-and-control panel for Big Bro AI.

    Accepts summary data from each sub-system and presents it as a
    coherent snapshot.

    Parameters
    ----------
    big_bro_name : str
        The custom name given to this Big Bro instance.
    tier : str
        Active subscription tier.
    """

    def __init__(self, big_bro_name: str = "Big Bro", tier: str = "free") -> None:
        self.big_bro_name = big_bro_name
        self.tier = tier
        self._panels: dict[str, dict] = {name: {} for name in PANEL_NAMES}
        self._alerts: list[DashboardAlert] = []
        self._initialized_at: str = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Panel updates
    # ------------------------------------------------------------------

    def update_panel(self, panel_name: str, data: dict) -> None:
        """
        Update a named panel with fresh data from a sub-system.

        Parameters
        ----------
        panel_name : str
            One of the panel names defined in PANEL_NAMES.
        data : dict
            Summary data from the sub-system.
        """
        if panel_name not in self._panels:
            self._panels[panel_name] = {}
        self._panels[panel_name] = {
            **data,
            "_last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def get_panel(self, panel_name: str) -> dict:
        """Return the current data for a named panel."""
        return self._panels.get(panel_name, {})

    # ------------------------------------------------------------------
    # Alert management
    # ------------------------------------------------------------------

    def add_alert(
        self, level: str, source: str, message: str
    ) -> DashboardAlert:
        """Add a system alert to the dashboard."""
        alert = DashboardAlert(level=level, source=source, message=message)
        self._alerts.append(alert)
        return alert

    def get_alerts(
        self, level: Optional[str] = None, limit: int = 50
    ) -> list[DashboardAlert]:
        """Return recent alerts, optionally filtered by level."""
        alerts = self._alerts
        if level is not None:
            alerts = [a for a in alerts if a.level == level]
        return alerts[-limit:]

    def clear_alerts(self) -> int:
        """Clear all alerts.  Returns count cleared."""
        count = len(self._alerts)
        self._alerts = []
        return count

    # ------------------------------------------------------------------
    # Full dashboard snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """
        Return the complete dashboard snapshot.

        Returns a structured dict suitable for JSON serialisation or
        display in a web interface / Xbox browser.
        """
        recent_alerts = self.get_alerts(limit=10)
        return {
            "big_bro_name": self.big_bro_name,
            "tier": self.tier,
            "initialized_at": self._initialized_at,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
            "panels": {
                name: self._panels.get(name, {}) for name in PANEL_NAMES
            },
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "alert_count": len(self._alerts),
        }

    # ------------------------------------------------------------------
    # KPI summary (high-level numbers for the overview panel)
    # ------------------------------------------------------------------

    def kpi_summary(self) -> dict:
        """
        Return the key performance indicators for the overview panel.

        Pulls from already-updated panels so no sub-system references
        are needed here.
        """
        money = self._panels.get("sales_monetization", {})
        factory = self._panels.get("bot_factory", {})
        catalog = self._panels.get("catalog_franchise", {})
        study = self._panels.get("continuous_study", {})
        memory = self._panels.get("memory_system", {})

        return {
            "total_revenue_usd": money.get("total_revenue_usd", 0),
            "mrr_usd": money.get("monthly_recurring_revenue_usd", 0),
            "total_bots_created": factory.get("total_bots", 0),
            "avg_bot_readiness": factory.get("average_readiness_score", 0),
            "catalog_orders": catalog.get("total_orders", 0),
            "active_franchises": catalog.get("active_franchises", 0),
            "knowledge_patterns": study.get("total_patterns", 0),
            "user_profiles": memory.get("profile_count", 0),
        }

    # ------------------------------------------------------------------
    # Multi-device export
    # ------------------------------------------------------------------

    def export_for_device(self, device: str = "browser") -> dict:
        """
        Return a device-optimised snapshot.

        Supported devices: browser, tablet, mobile, xbox.
        All devices receive the same JSON data — the client renders it.
        """
        supported = {"browser", "tablet", "mobile", "xbox"}
        return {
            "device": device if device in supported else "browser",
            "supported_devices": sorted(supported),
            "no_download_required": True,
            "data": self.snapshot(),
        }
