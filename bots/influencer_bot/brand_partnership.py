"""
Brand Partnership — co-branding engine for the DreamCo Influencer Bot.

Handles creating partnerships between brands and influencers, generating
co-branded bot definitions, and projecting revenue.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class BrandPartnership:
    """Manages brand-influencer partnerships and co-branded bot creation."""

    # Base monthly subscription revenue per user (USD)
    _BASE_SUB_REVENUE_PER_USER = 9.99
    # Base ad revenue per monthly active user (USD)
    _BASE_AD_REVENUE_PER_USER = 0.50

    def __init__(self) -> None:
        self._partnerships: dict = {}
        self._cobranded_bots: dict = {}

    # ------------------------------------------------------------------
    # Partnership management
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
        """Create a new brand-influencer partnership.

        Parameters
        ----------
        influencer_id : str
            ID of the influencer from InfluencerDatabase.
        brand_name : str
            Name of the brand entering the partnership.
        bot_name : str
            Display name for the co-branded bot.
        bot_description : str
            Short description of the bot's purpose.
        category : str
            Content category (e.g. FITNESS, MUSIC).
        revenue_share_pct : float
            Fraction of net revenue shared with the influencer (default 15%).

        Returns
        -------
        dict
            Partnership record including generated partnership_id.
        """
        partnership_id = f"prt_{uuid.uuid4().hex[:10]}"
        record = {
            "partnership_id": partnership_id,
            "influencer_id": influencer_id,
            "brand_name": brand_name,
            "bot_name": bot_name,
            "bot_description": bot_description,
            "category": category,
            "revenue_share_pct": revenue_share_pct,
            "status": "ACTIVE",
            "cobranded_bots": [],
        }
        self._partnerships[partnership_id] = record
        return record

    def get_partnership(self, partnership_id: str) -> Optional[dict]:
        """Return a partnership record by ID, or None if not found."""
        return self._partnerships.get(partnership_id)

    def list_partnerships(self, influencer_id: Optional[str] = None) -> List[dict]:
        """Return all partnerships, optionally filtered by influencer_id."""
        all_p = list(self._partnerships.values())
        if influencer_id:
            all_p = [p for p in all_p if p["influencer_id"] == influencer_id]
        return all_p

    # ------------------------------------------------------------------
    # Co-branded bot creation
    # ------------------------------------------------------------------

    def create_cobranded_bot(
        self,
        partnership_id: str,
        target_audience: str,
        bot_capabilities: list,
    ) -> dict:
        """Generate a co-branded bot definition from a partnership.

        Parameters
        ----------
        partnership_id : str
            ID of an existing partnership.
        target_audience : str
            Description of the intended audience.
        bot_capabilities : list
            List of capability strings for the bot.

        Returns
        -------
        dict
            Bot definition with influencer branding applied.

        Raises
        ------
        ValueError
            If the partnership_id does not exist.
        """
        partnership = self._partnerships.get(partnership_id)
        if partnership is None:
            raise ValueError(f"Partnership '{partnership_id}' not found.")

        bot_id = f"bot_{uuid.uuid4().hex[:10]}"
        bot_def = {
            "bot_id": bot_id,
            "partnership_id": partnership_id,
            "bot_name": partnership["bot_name"],
            "brand_name": partnership["brand_name"],
            "influencer_id": partnership["influencer_id"],
            "category": partnership["category"],
            "target_audience": target_audience,
            "capabilities": bot_capabilities,
            "branding": {
                "co_brand_label": f"{partnership['brand_name']} × Influencer Bot",
                "description": partnership["bot_description"],
                "revenue_share_pct": partnership["revenue_share_pct"],
            },
            "status": "READY",
        }
        self._cobranded_bots[bot_id] = bot_def
        partnership["cobranded_bots"].append(bot_id)
        return bot_def

    # ------------------------------------------------------------------
    # Revenue projection
    # ------------------------------------------------------------------

    def calculate_projected_revenue(
        self, partnership_id: str, monthly_users: int
    ) -> dict:
        """Project monthly revenue for a partnership.

        Parameters
        ----------
        partnership_id : str
            ID of an existing partnership.
        monthly_users : int
            Estimated number of monthly active users.

        Returns
        -------
        dict
            Breakdown of subscription, ads, influencer share, and total revenue.

        Raises
        ------
        ValueError
            If the partnership_id does not exist.
        """
        partnership = self._partnerships.get(partnership_id)
        if partnership is None:
            raise ValueError(f"Partnership '{partnership_id}' not found.")

        subscription_revenue = monthly_users * self._BASE_SUB_REVENUE_PER_USER
        ad_revenue = monthly_users * self._BASE_AD_REVENUE_PER_USER
        gross_revenue = subscription_revenue + ad_revenue
        influencer_share = gross_revenue * partnership["revenue_share_pct"]
        net_revenue = gross_revenue - influencer_share

        return {
            "partnership_id": partnership_id,
            "monthly_users": monthly_users,
            "subscription_revenue_usd": round(subscription_revenue, 2),
            "ad_revenue_usd": round(ad_revenue, 2),
            "gross_revenue_usd": round(gross_revenue, 2),
            "influencer_share_usd": round(influencer_share, 2),
            "net_revenue_usd": round(net_revenue, 2),
            "revenue_share_pct": partnership["revenue_share_pct"],
        }
