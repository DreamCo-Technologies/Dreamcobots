"""
Revenue & Monetization module for the CreatorEmpire bot.

Supports multiple revenue models: subscriptions (basic/premium), tips,
pay-per-view, merchandise, direct service fees, brand deals, and more.
Includes a lightweight revenue ledger for tracking earnings.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .tiers import (
    Tier,
    CREATOR_FEATURES_BY_TIER,
    MONETIZATION_MODELS_BY_TIER,
    FEATURE_MONETIZATION_BASIC,
    FEATURE_MONETIZATION_ADVANCED,
)


class MonetizationError(Exception):
    """Raised when a monetization operation cannot be completed."""


# ---------------------------------------------------------------------------
# Revenue model metadata
# ---------------------------------------------------------------------------

REVENUE_MODEL_INFO: dict[str, dict] = {
    "tip_jar": {
        "display_name": "Tip Jar",
        "description": "Accept one-time voluntary tips from fans.",
        "payment_types": ["one_time"],
        "platforms": ["streamlabs", "ko-fi", "buy_me_a_coffee", "paypal"],
    },
    "subscription_basic": {
        "display_name": "Basic Subscription",
        "description": "Monthly recurring subscription at an entry-level price.",
        "payment_types": ["recurring"],
        "platforms": ["patreon", "twitch", "youtube_membership"],
    },
    "subscription_premium": {
        "display_name": "Premium Subscription",
        "description": "Higher-tier monthly subscription with exclusive perks.",
        "payment_types": ["recurring"],
        "platforms": ["patreon", "substack", "memberful"],
    },
    "pay_per_view": {
        "display_name": "Pay-Per-View",
        "description": "Charge fans per individual piece of content or event.",
        "payment_types": ["one_time"],
        "platforms": ["youtube", "vimeo", "eventbrite", "gumroad"],
    },
    "merchandise": {
        "display_name": "Merchandise",
        "description": "Sell branded physical or digital products.",
        "payment_types": ["one_time"],
        "platforms": ["shopify", "printful", "teespring", "amazon_merch"],
    },
    "direct_service_fee": {
        "display_name": "Direct Service Fee",
        "description": "Charge for coaching, consulting, or custom content.",
        "payment_types": ["one_time", "recurring"],
        "platforms": ["stripe", "paypal", "calendly"],
    },
    "brand_deal": {
        "display_name": "Brand Deal / Sponsorship",
        "description": "Negotiate flat-fee or performance-based brand partnerships.",
        "payment_types": ["one_time", "recurring"],
        "platforms": ["direct_outreach", "aspire", "grin", "influencer_marketing_hub"],
    },
    "licensing": {
        "display_name": "Content Licensing",
        "description": "License your music, art, or content to third parties.",
        "payment_types": ["one_time", "royalty"],
        "platforms": ["distrokid", "musicbed", "artlist", "shutterstock"],
    },
    "revenue_share": {
        "display_name": "Revenue Share",
        "description": "Earn a percentage of revenue from platform ad programmes.",
        "payment_types": ["recurring"],
        "platforms": ["youtube_adsense", "twitch_bits", "spotify_podcasts"],
    },
    "nft": {
        "display_name": "NFT / Digital Collectibles",
        "description": "Mint and sell limited digital collectibles.",
        "payment_types": ["one_time", "royalty"],
        "platforms": ["opensea", "rarible", "foundation", "objkt"],
    },
}


@dataclass
class RevenueEntry:
    """A single revenue transaction entry.

    Attributes
    ----------
    entry_id : str
        Unique identifier.
    creator_name : str
        Creator who earned the revenue.
    model : str
        Revenue model (e.g. 'tip_jar').
    amount_usd : float
        Gross amount in USD.
    platform : str
        Platform through which revenue was earned.
    description : str
        Optional note.
    """

    entry_id: str
    creator_name: str
    model: str
    amount_usd: float
    platform: str
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "creator_name": self.creator_name,
            "model": self.model,
            "amount_usd": self.amount_usd,
            "platform": self.platform,
            "description": self.description,
        }


class MonetizationEngine:
    """
    Manages revenue model selection and a lightweight revenue ledger.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling available monetization features.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._active_models: dict[str, list[str]] = {}   # creator → [model_ids]
        self._ledger: list[RevenueEntry] = []
        self._entry_counter: int = 0

    # ------------------------------------------------------------------
    # Revenue model management
    # ------------------------------------------------------------------

    def enable_model(self, creator_name: str, model: str) -> dict:
        """
        Enable a revenue model for a creator.

        Parameters
        ----------
        creator_name : str
            The creator's name.
        model : str
            Revenue model ID (e.g. 'tip_jar', 'subscription_basic').

        Returns
        -------
        dict describing the enabled model.
        """
        self._check_model_available(model)
        if creator_name not in self._active_models:
            self._active_models[creator_name] = []
        if model not in self._active_models[creator_name]:
            self._active_models[creator_name].append(model)
        return self.get_model_info(model)

    def disable_model(self, creator_name: str, model: str) -> None:
        """Disable a revenue model for a creator."""
        if creator_name in self._active_models:
            self._active_models[creator_name] = [
                m for m in self._active_models[creator_name] if m != model
            ]

    def get_active_models(self, creator_name: str) -> list[dict]:
        """Return info dicts for all active revenue models of a creator."""
        models = self._active_models.get(creator_name, [])
        return [self.get_model_info(m) for m in models]

    def get_available_models(self) -> list[dict]:
        """Return info dicts for all revenue models available on this tier."""
        available = MONETIZATION_MODELS_BY_TIER[self.tier.value]
        return [self.get_model_info(m) for m in available]

    @staticmethod
    def get_model_info(model: str) -> dict:
        """Return metadata for a specific revenue model."""
        if model not in REVENUE_MODEL_INFO:
            raise MonetizationError(f"Unknown revenue model '{model}'.")
        return {"id": model, **REVENUE_MODEL_INFO[model]}

    # ------------------------------------------------------------------
    # Revenue ledger
    # ------------------------------------------------------------------

    def record_revenue(
        self,
        creator_name: str,
        model: str,
        amount_usd: float,
        platform: str,
        description: str = "",
    ) -> RevenueEntry:
        """
        Record a revenue transaction in the ledger.

        Parameters
        ----------
        creator_name : str
            Earning creator's name.
        model : str
            Revenue model used.
        amount_usd : float
            Gross amount in USD.
        platform : str
            Platform on which revenue was earned.
        description : str
            Optional note.

        Returns
        -------
        RevenueEntry
        """
        self._check_feature(FEATURE_MONETIZATION_BASIC)
        if amount_usd < 0:
            raise MonetizationError("Revenue amount cannot be negative.")

        self._entry_counter += 1
        entry = RevenueEntry(
            entry_id=f"rev_{self._entry_counter:06d}",
            creator_name=creator_name,
            model=model,
            amount_usd=amount_usd,
            platform=platform,
            description=description,
        )
        self._ledger.append(entry)
        return entry

    def get_total_revenue(self, creator_name: str) -> float:
        """Return the total gross revenue for a creator."""
        return sum(
            e.amount_usd for e in self._ledger if e.creator_name == creator_name
        )

    def get_revenue_by_model(self, creator_name: str) -> dict[str, float]:
        """Return a breakdown of gross revenue by model for a creator."""
        breakdown: dict[str, float] = {}
        for entry in self._ledger:
            if entry.creator_name == creator_name:
                breakdown[entry.model] = breakdown.get(entry.model, 0.0) + entry.amount_usd
        return breakdown

    def get_ledger(self, creator_name: Optional[str] = None) -> list[dict]:
        """Return all ledger entries, optionally filtered by creator."""
        entries = self._ledger
        if creator_name:
            entries = [e for e in entries if e.creator_name == creator_name]
        return [e.to_dict() for e in entries]

    def get_monetization_strategy(self, role: str) -> list[str]:
        """Return a recommended monetization strategy for a given creator role."""
        self._check_feature(FEATURE_MONETIZATION_BASIC)
        strategies: dict[str, list[str]] = {
            "streamer": [
                "Enable Twitch/YouTube subscriptions and bit/super-chat donations",
                "Set up a tip jar via Streamlabs or Ko-fi",
                "Launch a merchandise line once audience reaches 1k",
                "Pursue brand deals with gaming/lifestyle sponsors",
                "Offer coaching sessions as a direct service fee",
            ],
            "rapper": [
                "Distribute music via DistroKid to earn streaming royalties",
                "Sell beats and instrumentals on BeatStars",
                "Launch limited edition merchandise drops",
                "Seek brand deals aligned with your lifestyle niche",
                "Offer paid songwriting or feature collaborations",
            ],
            "athlete": [
                "Launch a training programme as a direct service fee",
                "Partner with sports equipment or apparel brands",
                "Sell access to exclusive training content via pay-per-view",
                "Enable audience donations during live Q&A streams",
                "Pursue licensing deals for highlight footage",
            ],
            "content_creator": [
                "Enable YouTube AdSense revenue share",
                "Launch a Patreon with tiered membership benefits",
                "Sell digital products (templates, presets, ebooks)",
                "Integrate affiliate marketing into content",
                "Pursue brand deals aligned with your content niche",
            ],
            "podcaster": [
                "Launch a listener-support subscription on Patreon/Supercast",
                "Seek podcast sponsorship deals (dynamic ad insertion)",
                "Sell premium ad-free episodes as pay-per-view",
                "Host paid live recording events",
                "Launch a paid community around your show",
            ],
        }
        role = role.lower().strip()
        return strategies.get(role, [
            "Set up a tip jar for one-time fan support",
            "Launch a basic subscription tier with exclusive content",
            "Explore brand deals once your audience reaches 1k",
            "Sell digital products related to your niche",
        ])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_model_available(self, model: str) -> None:
        available = MONETIZATION_MODELS_BY_TIER[self.tier.value]
        if model not in available:
            raise MonetizationError(
                f"Revenue model '{model}' is not available on the "
                f"{self.tier.value.capitalize()} tier."
            )

    def _check_feature(self, feature: str) -> None:
        available = CREATOR_FEATURES_BY_TIER[self.tier.value]
        if feature not in available:
            raise MonetizationError(
                f"Feature '{feature}' is not available on the "
                f"{self.tier.value.capitalize()} tier."
            )
