"""
API Gateway — DreamCo Global Bot Communication Network.

Connects DreamCo bots to external platforms and services through a unified
routing interface.  Supported integrations (mock / stub implementations):

  - Slack
  - Discord
  - OpenAI
  - Trello
  - Notion

All integrations are designed to be swapped for real HTTP clients by
injecting a custom *adapter* callable.  In tests and offline environments the
built-in mock adapters return realistic stub responses without network calls.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums & constants
# ---------------------------------------------------------------------------

class IntegrationType(Enum):
    SLACK = "slack"
    DISCORD = "discord"
    OPENAI = "openai"
    TRELLO = "trello"
    NOTION = "notion"
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class APIGatewayError(Exception):
    """Base exception for the API Gateway."""


class IntegrationNotFound(APIGatewayError):
    """Raised when referencing an integration that has not been registered."""


class IntegrationDisabled(APIGatewayError):
    """Raised when calling a disabled integration."""


# ---------------------------------------------------------------------------
# Integration registration
# ---------------------------------------------------------------------------

@dataclass
class Integration:
    """
    Describes a registered external integration.

    Parameters
    ----------
    name : str
        Human-readable label (e.g. "Slack", "Discord").
    integration_type : IntegrationType
        Canonical type enum.
    adapter : callable
        ``adapter(action: str, payload: dict) -> dict`` — handles all calls
        to this integration.  Replace with a real HTTP client in production.
    enabled : bool
        Toggle without de-registering.
    config : dict
        Integration-specific config (tokens, channel IDs, etc.).
    """

    name: str
    integration_type: IntegrationType
    adapter: Callable[[str, dict], dict]
    enabled: bool = True
    config: dict = field(default_factory=dict)
    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def call(self, action: str, payload: dict) -> dict:
        if not self.enabled:
            raise IntegrationDisabled(f"Integration '{self.name}' is disabled.")
        return self.adapter(action, payload)


# ---------------------------------------------------------------------------
# Built-in mock adapters
# ---------------------------------------------------------------------------

def _slack_adapter(action: str, payload: dict) -> dict:
    """Mock Slack adapter — returns stub responses."""
    if action == "send_message":
        return {
            "ok": True,
            "channel": payload.get("channel", "#general"),
            "ts": "1717000000.000000",
            "message": {"text": payload.get("text", "")},
        }
    if action == "fetch_channel":
        return {"ok": True, "channel": {"id": "C01234", "name": "general"}}
    if action == "list_users":
        return {"ok": True, "members": []}
    return {"ok": False, "error": f"unknown_action:{action}"}


def _discord_adapter(action: str, payload: dict) -> dict:
    """Mock Discord adapter."""
    if action == "send_message":
        return {
            "id": "1234567890",
            "channel_id": payload.get("channel_id", "0"),
            "content": payload.get("content", ""),
        }
    if action == "get_guild":
        return {"id": payload.get("guild_id", "0"), "name": "DreamCo Server"}
    if action == "list_channels":
        return {"channels": []}
    return {"error": f"unknown_action:{action}"}


def _openai_adapter(action: str, payload: dict) -> dict:
    """Mock OpenAI adapter."""
    if action == "chat_completion":
        return {
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"[Mock OpenAI response to: {payload.get('user_message', '')}]",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
    if action == "embedding":
        return {"embedding": [0.1, 0.2, 0.3], "model": "text-embedding-ada-002"}
    return {"error": f"unknown_action:{action}"}


def _trello_adapter(action: str, payload: dict) -> dict:
    """Mock Trello adapter."""
    if action == "create_card":
        return {"id": "trello_card_001", "name": payload.get("name", ""), "idList": payload.get("list_id", "")}
    if action == "get_board":
        return {"id": payload.get("board_id", ""), "name": "DreamCo Board"}
    if action == "move_card":
        return {"id": payload.get("card_id", ""), "idList": payload.get("list_id", "")}
    return {"error": f"unknown_action:{action}"}


def _notion_adapter(action: str, payload: dict) -> dict:
    """Mock Notion adapter."""
    if action == "create_page":
        return {"id": "notion_page_001", "title": payload.get("title", ""), "url": "https://notion.so/mock"}
    if action == "query_database":
        return {"results": [], "next_cursor": None}
    if action == "update_page":
        return {"id": payload.get("page_id", ""), "updated": True}
    return {"error": f"unknown_action:{action}"}


_DEFAULT_ADAPTERS: dict[IntegrationType, Callable] = {
    IntegrationType.SLACK: _slack_adapter,
    IntegrationType.DISCORD: _discord_adapter,
    IntegrationType.OPENAI: _openai_adapter,
    IntegrationType.TRELLO: _trello_adapter,
    IntegrationType.NOTION: _notion_adapter,
}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

@dataclass
class GatewayRequest:
    """A task request routed through the API Gateway."""

    integration_name: str
    action: str
    payload: dict = field(default_factory=dict)
    bot_id: str = ""
    request_id: str = field(
        default_factory=lambda: f"req_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    )


@dataclass
class GatewayResponse:
    """Result of a Gateway request."""

    request_id: str
    integration_name: str
    action: str
    result: dict = field(default_factory=dict)
    success: bool = True
    error: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "integration": self.integration_name,
            "action": self.action,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# API Gateway
# ---------------------------------------------------------------------------

class APIGateway:
    """
    Routes external task requests to registered integrations.

    Usage::

        gateway = APIGateway()
        gateway.register_default_integrations()
        resp = gateway.route("Slack", "send_message", {"channel": "#general", "text": "Hello"})
    """

    def __init__(self) -> None:
        self._integrations: dict[str, Integration] = {}
        self._request_log: list[GatewayResponse] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        integration_type: IntegrationType,
        adapter: Optional[Callable] = None,
        config: Optional[dict] = None,
        enabled: bool = True,
    ) -> Integration:
        """
        Register an external integration.

        Parameters
        ----------
        name : str
            Unique name (e.g. ``"Slack"``).
        integration_type : IntegrationType
            Canonical type.
        adapter : callable, optional
            Custom adapter.  Defaults to the built-in mock for the type.
        config : dict, optional
            Integration configuration (API keys, channels, etc.).
        enabled : bool
            Whether the integration is active immediately.

        Returns
        -------
        Integration
            The registered integration object.
        """
        if adapter is None:
            adapter = _DEFAULT_ADAPTERS.get(integration_type, lambda a, p: {"error": "no_adapter"})
        integration = Integration(
            name=name,
            integration_type=integration_type,
            adapter=adapter,
            enabled=enabled,
            config=config or {},
        )
        self._integrations[name] = integration
        return integration

    def register_default_integrations(self) -> None:
        """Register all built-in mock integrations (Slack, Discord, OpenAI, Trello, Notion)."""
        self.register("Slack", IntegrationType.SLACK)
        self.register("Discord", IntegrationType.DISCORD)
        self.register("OpenAI", IntegrationType.OPENAI)
        self.register("Trello", IntegrationType.TRELLO)
        self.register("Notion", IntegrationType.NOTION)

    def unregister(self, name: str) -> None:
        """Remove an integration by name."""
        self._integrations.pop(name, None)

    def enable(self, name: str) -> None:
        """Enable a registered integration."""
        self._get(name).enabled = True

    def disable(self, name: str) -> None:
        """Disable a registered integration (calls will raise IntegrationDisabled)."""
        self._get(name).enabled = False

    def list_integrations(self) -> list[dict]:
        """Return metadata for all registered integrations."""
        return [
            {
                "name": i.name,
                "type": i.integration_type.value,
                "enabled": i.enabled,
                "registered_at": i.registered_at,
            }
            for i in self._integrations.values()
        ]

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def route(
        self,
        integration_name: str,
        action: str,
        payload: Optional[dict] = None,
        bot_id: str = "",
    ) -> GatewayResponse:
        """
        Execute *action* on *integration_name* with *payload*.

        Parameters
        ----------
        integration_name : str
            Name of a registered integration.
        action : str
            Integration-specific action string (e.g. ``"send_message"``).
        payload : dict, optional
            Action parameters.
        bot_id : str, optional
            Identifier of the requesting bot (for logging).

        Returns
        -------
        GatewayResponse
        """
        req = GatewayRequest(
            integration_name=integration_name,
            action=action,
            payload=payload or {},
            bot_id=bot_id,
        )
        try:
            integration = self._get(integration_name)
            result = integration.call(action, req.payload)
            resp = GatewayResponse(
                request_id=req.request_id,
                integration_name=integration_name,
                action=action,
                result=result,
                success=True,
            )
        except (IntegrationNotFound, IntegrationDisabled) as exc:
            resp = GatewayResponse(
                request_id=req.request_id,
                integration_name=integration_name,
                action=action,
                success=False,
                error=str(exc),
            )
        self._request_log.append(resp)
        return resp

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    def get_request_log(self, integration_name: Optional[str] = None) -> list[dict]:
        """Return the request log, optionally filtered by integration."""
        log = self._request_log
        if integration_name:
            log = [r for r in log if r.integration_name == integration_name]
        return [r.to_dict() for r in log]

    def get_stats(self) -> dict:
        """Return gateway statistics."""
        total = len(self._request_log)
        failed = sum(1 for r in self._request_log if not r.success)
        return {
            "registered_integrations": len(self._integrations),
            "total_requests": total,
            "successful_requests": total - failed,
            "failed_requests": failed,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, name: str) -> Integration:
        if name not in self._integrations:
            raise IntegrationNotFound(f"Integration '{name}' is not registered.")
        return self._integrations[name]
