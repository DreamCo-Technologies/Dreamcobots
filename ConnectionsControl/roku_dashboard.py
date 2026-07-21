"""
Roku Dashboard for DreamCobots ConnectionsControl.

Pushes KPI data to a Roku TV display for executive monitoring.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class KPIMetrics:
    revenue: float
    active_bots: int
    alerts: int
    throughput: float
    uptime: float   # percentage 0-100


class RokuDashboard:
    """Roku TV dashboard for KPI visualization (mock — no network calls)."""

    VALUE_COLUMN_WIDTH = 10   # right-aligned numeric value field width
    UPTIME_COLUMN_WIDTH = 9   # uptime field is one char narrower (holds the %)

    def __init__(self) -> None:
        self._device_ip: Optional[str] = None
        self._display_config: Dict = {
            "theme": "dark",
            "refresh_interval_sec": 30,
            "show_alerts": True,
            "font_size": "large",
        }
        self._push_log: List[dict] = []

    def configure(self, device_ip: str) -> None:
        """Configure the target Roku device IP address."""
        self._device_ip = device_ip

    def push_dashboard(self, metrics: KPIMetrics) -> dict:
        """Send KPI data to the Roku TV display (simulated)."""
        payload = {
            "device_ip": self._device_ip,
            "screen": self.render_kpi_screen(metrics),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pushed",
        }
        self._push_log.append(payload)
        return payload

    # Total inner width of the box (between the │ borders), excluding the leading space.
    _BOX_INNER = 37

    def _pad(self, content: str) -> str:
        """Right-pad *content* to fill the box inner width exactly."""
        return content.ljust(self._BOX_INNER)

    def render_kpi_screen(self, metrics: KPIMetrics) -> str:
        """Render a formatted KPI string suitable for TV display."""
        bar = "█" * int(metrics.uptime / 10) + "░" * (10 - int(metrics.uptime / 10))
        w = self.VALUE_COLUMN_WIDTH
        uw = self.UPTIME_COLUMN_WIDTH
        border = "─" * self._BOX_INNER
        rows = [
            f"  Revenue     : ${metrics.revenue:>{w},.2f}",
            f"  Active Bots : {metrics.active_bots:>{w}}",
            f"  Alerts      : {metrics.alerts:>{w}}",
            f"  Throughput  : {metrics.throughput:>{w}.1f} t/hr",
            f"  Uptime      : {metrics.uptime:>{uw}.2f}%",
            f"  [{bar}]",
        ]
        lines = [
            f"┌{border}┐",
            f"│{'DreamCobots Operations TV':^{self._BOX_INNER}}│",
            f"├{border}┤",
        ]
        for row in rows:
            lines.append(f"│{self._pad(row)}│")
        lines.append(f"└{border}┘")
        return "\n".join(lines)

    def get_display_config(self) -> dict:
        """Return the current display configuration."""
        return dict(self._display_config)

    def update_display_config(self, updates: dict) -> dict:
        """Apply configuration updates to the display."""
        self._display_config.update(updates)
        return self.get_display_config()

    def get_push_log(self) -> List[dict]:
        """Return the log of all dashboard pushes."""
        return list(self._push_log)

    def get_status(self) -> dict:
        """Return Roku dashboard status."""
        return {
            "device_ip": self._device_ip,
            "configured": bool(self._device_ip),
            "total_pushes": len(self._push_log),
            "config": self._display_config,
        }
