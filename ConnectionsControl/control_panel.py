"""
Control Panel — Unified control interface for all DreamCobots platforms.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ConnectionsControl.kill_switch import KillSwitch
from ConnectionsControl.telegram_integration import TelegramIntegration
from ConnectionsControl.slack_integration import SlackIntegration
from ConnectionsControl.discord_integration import DiscordIntegration
from ConnectionsControl.sms_kill_switch import SMSKillSwitch
from ConnectionsControl.webhook_manager import WebhookManager
from ConnectionsControl.rest_api import RestAPIManager
from ConnectionsControl.zoom_bot import ZoomBot
from ConnectionsControl.roku_dashboard import RokuDashboard
from ConnectionsControl.gaming_integration import GamingIntegration


@dataclass
class Platform:
    name: str
    type: str
    is_active: bool = False
    last_ping: Optional[datetime] = None


class ControlPanel:
    """Unified control interface aggregating all platform integrations."""

    PLATFORM_NAME_WIDTH = 20   # column width for platform name in control matrix

    def __init__(self) -> None:
        self._kill_switch = KillSwitch()
        self._platforms: Dict[str, Platform] = {}
        self._integrations: Dict[str, Any] = {}
        self._alert_log: List[dict] = []

        # Initialize default integrations
        self._telegram = TelegramIntegration()
        self._slack = SlackIntegration()
        self._discord = DiscordIntegration()
        self._sms = SMSKillSwitch()
        self._webhooks = WebhookManager()
        self._api = RestAPIManager()
        self._zoom = ZoomBot()
        self._roku = RokuDashboard()
        self._gaming = GamingIntegration()

        # Register platforms
        for name, integration in [
            ("telegram", self._telegram),
            ("slack", self._slack),
            ("discord", self._discord),
            ("sms", self._sms),
            ("webhooks", self._webhooks),
            ("rest_api", self._api),
            ("zoom", self._zoom),
            ("roku", self._roku),
            ("gaming", self._gaming),
        ]:
            self.register_platform(name, integration)

    def register_platform(self, name: str, integration: Any) -> Platform:
        """Register a platform integration under the given name."""
        platform = Platform(name=name, type=type(integration).__name__, is_active=True)
        self._platforms[name] = platform
        self._integrations[name] = integration
        return platform

    def get_platform_status(self) -> Dict[str, dict]:
        """Return a status dict for all registered platforms."""
        statuses = {}
        for name, platform in self._platforms.items():
            integration = self._integrations.get(name)
            is_active = False
            if hasattr(integration, "is_connected"):
                is_active = integration.is_connected
            elif hasattr(integration, "is_configured"):
                is_active = integration.is_configured
            else:
                is_active = platform.is_active
            statuses[name] = {
                "type": platform.type,
                "is_active": is_active,
                "last_ping": platform.last_ping.isoformat() if platform.last_ping else None,
            }
        return statuses

    def broadcast_alert(self, message: str, severity: str = "info") -> dict:
        """Send an alert to all active platforms."""
        results = {}
        if self._slack.is_connected:
            self._slack.send_alert(self._slack._default_channel or "#alerts", message, severity)
            results["slack"] = "sent"
        if self._telegram.is_connected:
            self._telegram.send_message(f"[{severity.upper()}] {message}")
            results["telegram"] = "sent"
        if self._discord.is_connected:
            self._discord.send_message("alerts", f"[{severity.upper()}] {message}")
            results["discord"] = "sent"
        self._webhooks.trigger_event("alert", {"message": message, "severity": severity})
        results["webhooks"] = "triggered"
        self._alert_log.append({
            "message": message,
            "severity": severity,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return results

    def activate_kill_switch(self, reason: str = "") -> dict:
        """Activate the kill switch and notify all platforms."""
        event = self._kill_switch.activate(reason)
        self.broadcast_alert(f"🚨 KILL SWITCH ACTIVATED: {reason}", severity="critical")
        return {"event_id": event.event_id, "reason": event.reason, "timestamp": event.timestamp.isoformat()}

    def deactivate_kill_switch(self) -> dict:
        """Deactivate the kill switch and notify all platforms."""
        event = self._kill_switch.deactivate()
        self.broadcast_alert("✅ Kill switch deactivated. Operations restored.", severity="info")
        return {"event_id": event.event_id, "timestamp": event.timestamp.isoformat()}

    def get_control_matrix(self) -> str:
        """Return a formatted string showing the bot-to-platform control mapping."""
        statuses = self.get_platform_status()
        # Compute column widths from actual data to avoid truncation/misalignment.
        name_w = max((len(n) for n in statuses), default=self.PLATFORM_NAME_WIDTH)
        name_w = max(name_w, self.PLATFORM_NAME_WIDTH)
        type_w = max((len(s["type"]) for s in statuses.values()), default=10)
        # icon (2) + 2 spaces + name + 1 space + brackets + type + 2 spaces = inner width
        inner = 2 + 2 + name_w + 1 + 1 + type_w + 1 + 2  # "✅  {name:<name_w} [{type}]  "
        border = "═" * (inner + 2)
        title = "DreamCobots Control Matrix"
        title_line = f"║ {title:^{inner}} ║"
        lines = [f"╔{border}╗", title_line, f"╠{border}╣"]
        for name, status in statuses.items():
            active_icon = "✅" if status["is_active"] else "⬜"
            row = f"{active_icon}  {name:<{name_w}} [{status['type']:<{type_w}}]"
            lines.append(f"║ {row} ║")
        lines.append(f"╚{border}╝")
        return "\n".join(lines)

    def ping_all_platforms(self) -> dict:
        """Ping all platforms to update last_ping timestamps."""
        now = datetime.utcnow()
        for platform in self._platforms.values():
            platform.last_ping = now
        return {"pinged": list(self._platforms.keys()), "timestamp": now.isoformat()}
