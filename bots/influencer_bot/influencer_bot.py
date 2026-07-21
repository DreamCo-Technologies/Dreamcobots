"""
DreamCo Influencer Bot — Main Entry Point.

Composes all Influencer Bot sub-systems into a single platform:

  • Influencer Database   — 22+ influencers/celebrities across 10 categories
  • Brand Partnership     — co-branded bot creation and revenue projection
  • Virality Engine       — campaign management and viral content generation

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── influencer_bot
    │     ├── influencer_database
    │     ├── brand_partnership
    │     └── virality_engine
    │
    └── ai_level_up_bot

Usage
-----
    from bots.influencer_bot import InfluencerBot, Tier

    bot = InfluencerBot(tier=Tier.PRO)
    influencers = bot.browse_influencers()
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.influencer_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_INFLUENCER_CATALOG,
    FEATURE_COBRAND_TEMPLATE,
    FEATURE_BASIC_ANALYTICS,
    FEATURE_FULL_DATABASE,
    FEATURE_VIRALITY_ENGINE,
    FEATURE_CAMPAIGN_MANAGER,
    FEATURE_AUDIENCE_ANALYTICS,
    FEATURE_CELEBRITY_PARTNERSHIPS,
    FEATURE_CUSTOM_COBRAND,
    FEATURE_REVENUE_SHARING,
)
from bots.influencer_bot.influencer_database import InfluencerDatabase, PARTNERSHIP_CELEBRITY
from bots.influencer_bot.brand_partnership import BrandPartnership
from bots.influencer_bot.virality_engine import ViralityEngine

from framework import GlobalAISourcesFlow  # noqa: F401


class InfluencerBotError(Exception):
    """Base exception for Influencer Bot errors."""


class InfluencerBotTierError(InfluencerBotError):
    """Raised when accessing a feature unavailable on the current tier."""


class InfluencerBot:
    """DreamCo Influencer Bot orchestrator.

    Combines the Influencer Database, Brand Partnership engine, and
    Virality Engine into a unified platform for celebrity & influencer
    co-branded bots.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    user_id : str
        Identifier for the current user session.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user") -> None:
        self.bot_name = "Influencer Bot"
        self.version = "1.0"
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        self.database = InfluencerDatabase()
        self.partnership = BrandPartnership()
        self.virality = ViralityEngine()

    # ------------------------------------------------------------------
    # Influencer discovery
    # ------------------------------------------------------------------

    def browse_influencers(self, category: str = None) -> list:
        """Return influencers from the catalog.

        FREE tier returns all influencers (read-only catalog access).
        PRO/ENTERPRISE return full database including all metadata.

        Parameters
        ----------
        category : str, optional
            Filter by category (e.g. 'FITNESS', 'MUSIC').

        Returns
        -------
        list of dict
        """
        self._require_feature(FEATURE_INFLUENCER_CATALOG)
        influencers = self.database.list_influencers(category=category)
        if not self.config.has_feature(FEATURE_FULL_DATABASE):
            # FREE tier limited to non-celebrity influencers only
            influencers = [i for i in influencers if i.partnership_tier != PARTNERSHIP_CELEBRITY]
        return [i.to_dict() for i in influencers]

    def get_influencer(self, influencer_id: str) -> dict:
        """Return details for a single influencer.

        Parameters
        ----------
        influencer_id : str

        Returns
        -------
        dict or error dict
        """
        self._require_feature(FEATURE_INFLUENCER_CATALOG)
        inf = self.database.get_influencer(influencer_id)
        if inf is None:
            return {"error": f"Influencer '{influencer_id}' not found."}
        return inf.to_dict()

    # ------------------------------------------------------------------
    # Partnerships & co-branded bots
    # ------------------------------------------------------------------

    def create_partnership(
        self,
        influencer_id: str,
        brand_name: str,
        bot_name: str,
        bot_description: str,
        category: str,
        revenue_share_pct: float = 0.15,
    ) -> dict:
        """Create a brand-influencer partnership.

        Requires PRO tier or higher. ENTERPRISE required for CELEBRITY
        influencer partnerships.
        """
        self._require_feature(FEATURE_COBRAND_TEMPLATE)

        inf = self.database.get_influencer(influencer_id)
        if inf and inf.partnership_tier == PARTNERSHIP_CELEBRITY:
            self._require_feature(FEATURE_CELEBRITY_PARTNERSHIPS)

        if revenue_share_pct > 0 and not self.config.has_feature(FEATURE_REVENUE_SHARING):
            # Non-enterprise tiers get a fixed default revenue share
            revenue_share_pct = 0.10

        return self.partnership.create_partnership(
            influencer_id=influencer_id,
            brand_name=brand_name,
            bot_name=bot_name,
            bot_description=bot_description,
            category=category,
            revenue_share_pct=revenue_share_pct,
        )

    def create_cobranded_bot(
        self,
        partnership_id: str,
        target_audience: str,
        bot_capabilities: list,
    ) -> dict:
        """Create a co-branded bot from an existing partnership.

        Requires PRO tier or higher.
        """
        self._require_feature(FEATURE_COBRAND_TEMPLATE)
        self._check_bot_limit()
        return self.partnership.create_cobranded_bot(
            partnership_id=partnership_id,
            target_audience=target_audience,
            bot_capabilities=bot_capabilities,
        )

    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------

    def launch_campaign(
        self,
        partnership_id: str,
        campaign_type: str,
        title: str,
        description: str,
        duration_days: int,
    ) -> dict:
        """Create and immediately launch a viral campaign.

        Requires PRO tier or higher.
        """
        self._require_feature(FEATURE_VIRALITY_ENGINE)
        campaign = self.virality.create_campaign(
            partnership_id=partnership_id,
            campaign_type=campaign_type,
            title=title,
            description=description,
            duration_days=duration_days,
        )
        return self.virality.launch_campaign(campaign["campaign_id"])

    def track_campaign(self, campaign_id: str) -> dict:
        """Return metrics for an active campaign.

        Requires PRO tier or higher.
        """
        self._require_feature(FEATURE_CAMPAIGN_MANAGER)
        return self.virality.track_campaign(campaign_id)

    def generate_viral_content(self, partnership_id: str, content_type: str) -> dict:
        """Generate viral content ideas for a partnership.

        Requires PRO tier or higher.
        """
        self._require_feature(FEATURE_VIRALITY_ENGINE)
        return self.virality.generate_viral_content(
            partnership_id=partnership_id,
            content_type=content_type,
        )

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
            "max_cobranded_bots": cfg.max_cobranded_bots,
            "features": cfg.features,
            "support_level": cfg.support_level,
        }

    def get_upgrade_info(self) -> dict:
        """Return information about the next available tier."""
        upgrade = get_upgrade_path(self.tier)
        if upgrade is None:
            return {"message": "You are already on the highest tier.", "upgrade_available": False}
        return {
            "upgrade_available": True,
            "upgrade_to": upgrade.name,
            "price_usd_monthly": upgrade.price_usd_monthly,
            "additional_features": [
                f for f in upgrade.features if f not in self.config.features
            ],
        }

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Handle a plain-text chat message and return a response.

        Parameters
        ----------
        message : str
            User message.

        Returns
        -------
        str
            Bot response string.
        """
        msg = message.lower().strip()

        if "influencer" in msg or "browse" in msg or "catalog" in msg:
            count = self.database.count()
            return (
                f"I have {count} influencers across 10 categories in my catalog. "
                "Use browse_influencers() to explore them!"
            )
        if "partnership" in msg or "brand" in msg:
            return (
                "I can help you create co-branded bot partnerships with influencers. "
                "Try create_partnership() to get started."
            )
        if "campaign" in msg or "viral" in msg:
            return (
                "Launch viral campaigns and track performance with my virality engine. "
                "Use launch_campaign() and track_campaign()."
            )
        if "tier" in msg or "upgrade" in msg or "plan" in msg:
            info = self.get_upgrade_info()
            if info.get("upgrade_available"):
                return (
                    f"You're on the {self.tier.value.upper()} plan. "
                    f"Upgrade to {info['upgrade_to']} for ${info['price_usd_monthly']}/month "
                    f"and unlock: {', '.join(info['additional_features'])}."
                )
            return f"You're on the {self.tier.value.upper()} plan — the highest tier. Enjoy!"
        if "celebrity" in msg:
            celebs = self.database.get_celebrities()
            names = ", ".join(c.name for c in celebs[:3])
            return f"Celebrity partners include: {names} and more. Upgrade to ENTERPRISE to unlock."

        return (
            f"Hi! I'm {self.bot_name} v{self.version} on the {self.tier.value.upper()} tier. "
            "I help you create co-branded bots with influencers and celebrities. "
            "Ask me about influencers, partnerships, or campaigns!"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise InfluencerBotTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier. "
                "Please upgrade your subscription."
            )

    def _check_bot_limit(self) -> None:
        """Raise if the tier's co-branded bot limit would be exceeded."""
        limit = self.config.max_cobranded_bots
        if limit is None:
            return
        total_bots = sum(
            len(p["cobranded_bots"]) for p in self.partnership.list_partnerships()
        )
        if total_bots >= limit:
            raise InfluencerBotTierError(
                f"Co-branded bot limit of {limit} reached for the {self.tier.value} tier. "
                "Please upgrade your subscription."
            )
