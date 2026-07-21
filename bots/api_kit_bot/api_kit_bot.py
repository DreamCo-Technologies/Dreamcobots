"""
DreamCo API Kit Bot — Main Entry Point.

Composes the API Kit Catalog, Sandbox Manager, and One-Click Deploy systems
into a unified developer-adoption platform:

  • API Kit Catalog    — 20+ pre-made AI-as-a-Service bot kits
  • Sandbox Manager   — secure isolated testing environments with secret keys
  • One-Click Deploy  — deploy kits to AWS, GCP, Azure, Vercel, and more

Architecture:
    DreamCoBots
    │
    ├── ai_level_up_bot
    │
    ├── api_kit_bot
    │     ├── api_kit_catalog
    │     ├── sandbox_manager
    │     └── one_click_deploy
    │
    └── …

Usage
-----
    from bots.api_kit_bot import APIKitBot, Tier

    bot = APIKitBot(owner_id="dev_001", tier=Tier.PRO)
    kits = bot.browse_kits()
    sandbox = bot.create_sandbox("My Test Sandbox")
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.api_kit_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_API_KIT_BASIC,
    FEATURE_SANDBOX_BASIC,
    FEATURE_SECRET_KEY_MANAGEMENT,
    FEATURE_ONE_CLICK_DEPLOY,
    FEATURE_ANALYTICS,
    FEATURE_ADVANCED_SANDBOX,
    FEATURE_AUTO_KEY_EXPIRATION,
)
from bots.api_kit_bot.api_kit_catalog import APIKitCatalog
from bots.api_kit_bot.sandbox_manager import SandboxManager
from bots.api_kit_bot.one_click_deploy import OneClickDeploy

from framework import GlobalAISourcesFlow  # noqa: F401


class APIKitBotError(Exception):
    """Base exception for API Kit Bot errors."""


class APIKitTierError(APIKitBotError):
    """Raised when accessing a feature unavailable on the current tier."""


class APIKitBot:
    """DreamCo API Kit Bot orchestrator.

    Combines the API Kit Catalog, Sandbox Manager, and One-Click Deploy
    into a unified platform for developer adoption.

    Parameters
    ----------
    owner_id : str
        Identifier for the current user/owner session.
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    """

    def __init__(
        self,
        owner_id: str = "user",
        tier: Tier = Tier.FREE,
    ) -> None:
        self.bot_name = "API Kit Bot"
        self.version = "1.0"
        self.owner_id = owner_id
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        self._catalog = APIKitCatalog()
        self._sandbox_manager = SandboxManager()
        self._deployer = OneClickDeploy()

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    def browse_kits(self, category: str | None = None) -> list:
        """List available API kits, optionally filtered by category."""
        self._require_feature(FEATURE_API_KIT_BASIC)
        return [k.to_dict() for k in self._catalog.list_kits(category)]

    def get_kit(self, kit_id: str) -> dict:
        """Retrieve details for a specific kit by ID."""
        self._require_feature(FEATURE_API_KIT_BASIC)
        kit = self._catalog.get_kit(kit_id)
        if kit is None:
            return {"error": f"Kit '{kit_id}' not found."}
        return kit.to_dict()

    # ------------------------------------------------------------------
    # Sandbox
    # ------------------------------------------------------------------

    def create_sandbox(
        self,
        name: str,
        kit_id: str | None = None,
    ) -> dict:
        """Create a new sandbox environment for the current owner."""
        self._require_feature(FEATURE_SANDBOX_BASIC)
        existing = self._sandbox_manager.list_sandboxes(self.owner_id)
        active = [s for s in existing if s.get("status") == "ACTIVE"]
        max_sb = self.config.max_sandboxes
        if max_sb is not None and len(active) >= max_sb:
            raise APIKitTierError(
                f"Sandbox limit reached ({max_sb}) for the {self.tier.value} tier. "
                f"Please upgrade to create more sandboxes."
            )
        return self._sandbox_manager.create_sandbox(self.owner_id, name, kit_id)

    def validate_key(self, sandbox_id: str, secret_key: str) -> bool:
        """Validate a secret key against a sandbox."""
        self._require_feature(FEATURE_SANDBOX_BASIC)
        return self._sandbox_manager.validate_secret_key(sandbox_id, secret_key)

    def rotate_key(self, sandbox_id: str) -> dict:
        """Rotate the secret key for a sandbox (PRO+ only)."""
        self._require_feature(FEATURE_SECRET_KEY_MANAGEMENT)
        return self._sandbox_manager.rotate_secret_key(sandbox_id)

    def get_sandbox_analytics(self, sandbox_id: str) -> dict:
        """Retrieve analytics for a sandbox (PRO+ only)."""
        self._require_feature(FEATURE_ANALYTICS)
        return self._sandbox_manager.get_sandbox_analytics(sandbox_id)

    # ------------------------------------------------------------------
    # Deploy
    # ------------------------------------------------------------------

    def deploy_kit(
        self,
        kit_id: str,
        target: str,
        config: dict | None = None,
    ) -> dict:
        """Deploy a kit to a cloud target (PRO+ only)."""
        self._require_feature(FEATURE_ONE_CLICK_DEPLOY)
        return self._deployer.deploy_kit(kit_id, self.owner_id, target, config)

    def get_deployment(self, deployment_id: str) -> dict:
        """Get deployment details."""
        self._require_feature(FEATURE_ONE_CLICK_DEPLOY)
        return self._deployer.get_deployment(deployment_id)

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_api_kits": cfg.max_api_kits,
            "max_sandboxes": cfg.max_sandboxes,
            "max_api_calls_per_day": cfg.max_api_calls_per_day,
            "features": cfg.features,
            "support_level": cfg.support_level,
        }

    def get_upgrade_info(self) -> dict:
        """Return information about the next available tier upgrade."""
        upgrade = get_upgrade_path(self.tier)
        if upgrade is None:
            return {"message": "You are already on the highest tier (Enterprise)."}
        return {
            "current_tier": self.tier.value,
            "upgrade_to": upgrade.tier.value,
            "upgrade_name": upgrade.name,
            "upgrade_price_usd_monthly": upgrade.price_usd_monthly,
            "new_features": [f for f in upgrade.features if f not in self.config.features],
        }

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Simple conversational interface for the API Kit Bot."""
        msg = message.lower().strip()

        if "kit" in msg and ("list" in msg or "browse" in msg or "show" in msg):
            kits = self._catalog.list_kits()
            names = ", ".join(k.name for k in kits[:5])
            return f"Here are some popular kits: {names} — and {len(kits) - 5} more!"

        if "sandbox" in msg and ("create" in msg or "new" in msg):
            return (
                "To create a sandbox, call bot.create_sandbox('My Sandbox'). "
                "You'll receive a sandbox_id and a secret key prefixed with 'sk_sandbox_'."
            )

        if "deploy" in msg:
            return (
                "One-Click Deploy supports: AWS Lambda, Google Cloud Run, Azure Functions, "
                "Heroku, Vercel, Railway, and Docker. Use bot.deploy_kit(kit_id, target)."
            )

        if "tier" in msg or "pricing" in msg or "upgrade" in msg:
            info = self.get_upgrade_info()
            if "message" in info:
                return info["message"]
            return (
                f"You're on {self.tier.value.upper()}. "
                f"Upgrade to {info['upgrade_name']} for ${info['upgrade_price_usd_monthly']}/mo "
                f"and unlock: {', '.join(info['new_features'])}."
            )

        return (
            f"Hi! I'm the {self.bot_name} v{self.version}. "
            "I can help you browse API kits, manage sandboxes, and deploy your AI services. "
            "Ask me about kits, sandboxes, deployments, or pricing!"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise APIKitTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier. "
                f"Please upgrade your subscription."
            )
