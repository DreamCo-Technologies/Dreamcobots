"""
DreamCo Bot Marketplace — Main Entry Point.

Composes all Bot Marketplace sub-systems into a single platform:

  • MarketplaceCatalog   — listing, searching, rating bots
  • MonetizationEngine  — purchases, upsells, seller dashboards
  • IntegrationHub      — Fortune 500 partner integrations

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── ai_level_up_bot
    │
    └── bot_marketplace
          ├── marketplace_catalog
          ├── monetization_engine
          └── integration_hub

Usage
-----
    from bots.bot_marketplace import BotMarketplace, Tier

    mp = BotMarketplace(tier=Tier.PRO, user_id="seller123")
    listing = mp.list_bot("my_bot", "PRODUCTIVITY", "Automates tasks", 29.99)
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.bot_marketplace.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BROWSE,
    FEATURE_BUY_BOTS,
    FEATURE_SELL_BOTS,
    FEATURE_MONETIZE,
    FEATURE_UPSELL,
    FEATURE_ANALYTICS,
    FEATURE_CUSTOM_STOREFRONT,
    FEATURE_FORTUNE500_INTEGRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)
from bots.bot_marketplace.marketplace_catalog import MarketplaceCatalog
from bots.bot_marketplace.monetization_engine import MonetizationEngine
from bots.bot_marketplace.integration_hub import IntegrationHub

from framework import GlobalAISourcesFlow  # noqa: F401


class BotMarketplaceError(Exception):
    """Base exception for Bot Marketplace errors."""


class BotMarketplaceTierError(BotMarketplaceError):
    """Raised when accessing a feature unavailable on the current tier."""


class BotMarketplace:
    """DreamCo Bot Marketplace orchestrator.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    user_id : str
        Identifier for the current user/seller session.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user") -> None:
        self.bot_name = "Bot Marketplace"
        self.version = "1.0"
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        self.catalog = MarketplaceCatalog()
        self.monetization = MonetizationEngine(catalog=self.catalog)
        self.integration_hub = IntegrationHub()

        # Track how many listings this user has created
        self._user_listing_count: int = 0
        # Track how many purchases this user has made
        self._user_purchase_count: int = 0

    # ------------------------------------------------------------------
    # Browsing
    # ------------------------------------------------------------------

    def browse(
        self,
        category: str | None = None,
        max_price: float | None = None,
    ) -> list:
        """Browse active bot listings."""
        self._require_feature(FEATURE_BROWSE)
        return self.catalog.search_listings(category=category, max_price=max_price)

    def search(
        self,
        query: str | None = None,
        category: str | None = None,
        max_price: float | None = None,
    ) -> list:
        """Full-text search over active listings."""
        self._require_feature(FEATURE_BROWSE)
        return self.catalog.search_listings(query=query, category=category, max_price=max_price)

    # ------------------------------------------------------------------
    # Buying
    # ------------------------------------------------------------------

    def buy_bot(self, listing_id: str) -> dict:
        """Purchase a bot from the marketplace."""
        self._require_feature(FEATURE_BUY_BOTS)

        max_purchases = self.config.max_purchases
        if max_purchases is not None and self._user_purchase_count >= max_purchases:
            raise BotMarketplaceTierError(
                f"The {self.tier.value} tier allows a maximum of {max_purchases} purchases. "
                "Please upgrade to buy more bots."
            )

        txn = self.monetization.purchase_bot(
            listing_id=listing_id,
            buyer_id=self.user_id,
            platform_fee_pct=self.config.platform_fee_pct,
        )
        self._user_purchase_count += 1
        return txn

    # ------------------------------------------------------------------
    # Selling / listing
    # ------------------------------------------------------------------

    def list_bot(
        self,
        bot_name: str,
        category: str,
        description: str,
        price_usd: float,
        bot_type: str = "standard",
    ) -> dict:
        """Create a new bot listing in the marketplace."""
        self._require_feature(FEATURE_SELL_BOTS)

        max_listings = self.config.max_listings
        if max_listings is not None and self._user_listing_count >= max_listings:
            raise BotMarketplaceTierError(
                f"The {self.tier.value} tier allows a maximum of {max_listings} listing(s). "
                "Please upgrade to list more bots."
            )

        listing = self.catalog.list_bot(
            seller_id=self.user_id,
            bot_name=bot_name,
            category=category,
            description=description,
            price_usd=price_usd,
            bot_type=bot_type,
        )
        self._user_listing_count += 1
        return listing

    def sell_bot(
        self,
        bot_name: str,
        category: str,
        description: str,
        price_usd: float,
        bot_type: str = "standard",
    ) -> dict:
        """Alias for list_bot; requires FEATURE_SELL_BOTS."""
        return self.list_bot(
            bot_name=bot_name,
            category=category,
            description=description,
            price_usd=price_usd,
            bot_type=bot_type,
        )

    # ------------------------------------------------------------------
    # Monetization
    # ------------------------------------------------------------------

    def create_upsell(
        self,
        listing_id: str,
        upsell_type: str,
        name: str,
        description: str,
        price_usd: float,
    ) -> dict:
        """Create an upsell offer for a bot listing."""
        self._require_feature(FEATURE_UPSELL)
        return self.monetization.create_upsell(
            listing_id=listing_id,
            upsell_type=upsell_type,
            name=name,
            description=description,
            price_usd=price_usd,
        )

    def get_seller_dashboard(self) -> dict:
        """Return aggregated revenue metrics for the current user."""
        self._require_feature(FEATURE_ANALYTICS)
        return self.monetization.get_seller_dashboard(self.user_id)

    # ------------------------------------------------------------------
    # Integrations
    # ------------------------------------------------------------------

    def register_integration(self, listing_id: str, partner: str, config: dict | None = None) -> dict:
        """Register a Fortune 500 integration for a listing."""
        self._require_feature(FEATURE_FORTUNE500_INTEGRATION)
        return self.integration_hub.register_integration(listing_id, partner, config)

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_listings": cfg.max_listings,
            "max_purchases": cfg.max_purchases,
            "platform_fee_pct": cfg.platform_fee_pct,
            "features": cfg.features,
            "support_level": cfg.support_level,
        }

    def get_upgrade_info(self) -> dict | None:
        """Return information about the next available tier, or None if at top."""
        upgrade = get_upgrade_path(self.tier)
        if upgrade is None:
            return None
        return {
            "tier": upgrade.tier.value,
            "name": upgrade.name,
            "price_usd_monthly": upgrade.price_usd_monthly,
            "platform_fee_pct": upgrade.platform_fee_pct,
            "features": upgrade.features,
        }

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Handle a plain-text message and return a helpful response."""
        msg = message.lower()
        if "browse" in msg or "discover" in msg:
            listings = self.browse()
            return f"Found {len(listings)} active listings in the marketplace."
        if "upgrade" in msg:
            info = self.get_upgrade_info()
            if info:
                return f"Upgrade to {info['name']} for ${info['price_usd_monthly']}/mo."
            return "You are already on the highest tier."
        if "tier" in msg or "plan" in msg:
            info = self.get_tier_info()
            return f"You are on the {info['name']} tier (${info['price_usd_monthly']}/mo)."
        if "sell" in msg or "list" in msg:
            return "Use list_bot() to create a new listing in the marketplace."
        if "buy" in msg or "purchase" in msg:
            return "Use buy_bot(listing_id) to purchase a bot."
        return (
            f"Welcome to the {self.bot_name}! "
            "You can browse, buy, sell, and manage bots here."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise BotMarketplaceTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier. "
                "Please upgrade your subscription."
            )
