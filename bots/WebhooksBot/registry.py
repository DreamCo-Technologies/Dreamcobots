"""
WebhookBotRegistry — auto-discovers all DreamCo bots and registers webhooks.

Scans the bots/ directory, reads each bot's config.json / replit_profile.json,
and calls WebhooksBot.register() for every discovered bot.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from .webhook_bot import WebhooksBot, WebhookEventType, WebhookSubscription

logger = logging.getLogger(__name__)

BOTS_ROOT = Path(__file__).resolve().parents[2] / "bots"
DEFAULT_HOOK_BASE_URL = os.getenv(
    "DREAMCO_WEBHOOK_BASE_URL", "https://hooks.dreamco.io/bots/{bot_id}"
)


class WebhookBotRegistry:
    """
    Auto-discovers every bot under bots/ and bulk-registers webhooks.

    GLOBAL AI SOURCES FLOW
    """

    def __init__(self, webhooks_bot: Optional[WebhooksBot] = None) -> None:
        self.webhooks_bot = webhooks_bot or WebhooksBot()
        self._discovered: List[Dict] = []

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_bots(self) -> List[Dict]:
        """Walk bots/ and collect metadata for each discovered bot."""
        discovered = []
        for bot_dir in sorted(BOTS_ROOT.iterdir()):
            if not bot_dir.is_dir():
                continue
            bot_id = bot_dir.name.lower().replace("-", "_")
            meta = {"bot_id": bot_id, "path": str(bot_dir)}

            # Try config.json first, then replit_profile.json
            for cfg_name in ("config.json", "replit_profile.json"):
                cfg_path = bot_dir / cfg_name
                if cfg_path.exists():
                    try:
                        with cfg_path.open() as f:
                            meta.update(json.load(f))
                        meta["config_source"] = cfg_name
                        break
                    except (json.JSONDecodeError, OSError):
                        pass

            discovered.append(meta)

        self._discovered = discovered
        logger.info("Discovered %d bots for webhook registration", len(discovered))
        return discovered

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_all(
        self,
        base_url_template: str = DEFAULT_HOOK_BASE_URL,
        events: Optional[List[WebhookEventType]] = None,
        sandbox_validate: bool = False,
    ) -> List[WebhookSubscription]:
        """Register webhooks for every discovered bot."""
        if not self._discovered:
            self.discover_bots()

        all_events = events or list(WebhookEventType)
        subs = []

        for meta in self._discovered:
            bot_id = meta["bot_id"]
            url = base_url_template.replace("{bot_id}", bot_id)
            sub = self.webhooks_bot.register(bot_id, url, all_events)
            subs.append(sub)

            if sandbox_validate:
                try:
                    self.webhooks_bot.sandbox_validate(sub.subscription_id)
                except Exception as exc:
                    logger.warning(
                        "Sandbox validation failed for bot=%s: %s", bot_id, exc
                    )

        logger.info("Registered %d webhook subscriptions", len(subs))
        return subs

    def get_summary(self) -> Dict:
        return {
            "discovered_bots": len(self._discovered),
            **self.webhooks_bot.get_health_summary(),
        }
