"""
Gaming Integration for DreamCobots ConnectionsControl.

Enables dashboard access via gaming console browsers (Xbox, PlayStation, Switch).

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConsoleType(Enum):
    XBOX = "xbox"
    PLAYSTATION = "playstation"
    SWITCH = "switch"
    GENERIC = "generic"


class GamingIntegration:
    """Gaming console browser integration for DreamCobots dashboards."""

    CONSOLE_BROWSER_URLS: dict = {
        ConsoleType.XBOX: "https://edge.microsoft.com",
        ConsoleType.PLAYSTATION: "https://browser.playstation.com",
        ConsoleType.SWITCH: "https://internet.nintendo.net",
        ConsoleType.GENERIC: "http://localhost:8080",
    }

    def __init__(self) -> None:
        self._console_type: ConsoleType = ConsoleType.GENERIC
        self._browser_url: Optional[str] = None
        self._configured: bool = False

    def configure(self, console_type: ConsoleType, browser_url: Optional[str] = None) -> None:
        """Configure the console type and optional custom browser URL."""
        self._console_type = console_type
        self._browser_url = browser_url or self.CONSOLE_BROWSER_URLS.get(console_type, "")
        self._configured = True

    def generate_dashboard_url(self) -> str:
        """Return the URL for accessing the DreamCobots dashboard on the console browser."""
        base = self._browser_url or "http://localhost:8080"
        return f"{base}/dreamcobots/dashboard"

    def render_console_view(self, metrics: dict) -> str:
        """Render a simplified HTML string for console browser viewing."""
        revenue = metrics.get("revenue", 0)
        bots = metrics.get("active_bots", 0)
        alerts = metrics.get("alerts", 0)
        uptime = metrics.get("uptime", 100)
        return (
            "<!DOCTYPE html><html><head>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<style>body{background:#111;color:#eee;font-family:sans-serif;padding:20px}"
            "h1{color:#0af}table{width:100%;border-collapse:collapse}"
            "td,th{padding:10px;border:1px solid #333;text-align:left}"
            "th{background:#222}.alert{color:#f44}</style></head><body>"
            "<h1>DreamCobots Dashboard</h1>"
            f"<p>Console: <b>{self._console_type.value.upper()}</b></p>"
            "<table><tr><th>Metric</th><th>Value</th></tr>"
            f"<tr><td>Revenue</td><td>${revenue:,.2f}</td></tr>"
            f"<tr><td>Active Bots</td><td>{bots}</td></tr>"
            f"<tr class='alert'><td>Alerts</td><td>{alerts}</td></tr>"
            f"<tr><td>Uptime</td><td>{uptime:.2f}%</td></tr>"
            "</table></body></html>"
        )

    def get_supported_consoles(self) -> list:
        """Return list of supported console types."""
        return [c.value for c in ConsoleType]

    def get_status(self) -> dict:
        """Return gaming integration status."""
        return {
            "configured": self._configured,
            "console_type": self._console_type.value,
            "dashboard_url": self.generate_dashboard_url(),
        }
