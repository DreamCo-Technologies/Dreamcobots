"""
DreamCo OS — Notification Tool
================================

Unified Slack / Discord / log notification.

Usage::

    tool = NotificationTool()
    await tool.execute(channel="slack", message="Bot completed run", level="info")
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from python_bots.tools.base import BaseTool

logger = logging.getLogger(__name__)


class NotificationTool(BaseTool):

    @property
    def name(self) -> str:
        return "notification"

    @property
    def description(self) -> str:
        return "Send notifications via Slack, Discord, or structured log output."

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "enum": ["slack", "discord", "log"]},
                "message": {"type": "string"},
                "level": {"type": "string", "enum": ["info", "warning", "error"], "default": "info"},
            },
            "required": ["channel", "message"],
        }

    async def execute(
        self,
        channel: str,
        message: str,
        level: str = "info",
        **kwargs: Any,
    ) -> dict[str, Any]:
        if channel == "slack":
            return await self._slack(message, level)
        elif channel == "discord":
            return await self._discord(message, level)
        else:
            getattr(logger, level, logger.info)(message)
            return {"delivered": True, "channel": "log"}

    async def _slack(self, message: str, level: str) -> dict[str, Any]:
        webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        if not webhook:
            logger.info("[Slack (mock)] %s: %s", level.upper(), message)
            return {"delivered": False, "reason": "SLACK_WEBHOOK_URL not set"}
        emoji = {"error": "🔴", "warning": "🟡", "info": "🟢"}.get(level, "🔵")
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(webhook, json={"text": f"{emoji} *[DreamCo]* {message}"})
        return {"delivered": resp.status_code == 200, "status_code": resp.status_code}

    async def _discord(self, message: str, level: str) -> dict[str, Any]:
        webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
        if not webhook:
            logger.info("[Discord (mock)] %s: %s", level.upper(), message)
            return {"delivered": False, "reason": "DISCORD_WEBHOOK_URL not set"}
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(webhook, json={"content": f"**[DreamCo {level.upper()}]** {message}"})
        return {"delivered": resp.status_code in (200, 204), "status_code": resp.status_code}
