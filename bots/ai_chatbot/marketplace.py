"""
marketplace.py – SaaS sales preparation, subscription management, and
marketing documentation manager for the Dreamcobots AI Chatbot platform.

This module handles:
* Subscription creation and upgrades
* Checkout-session preparation (Stripe-compatible payload structure)
* Marketing Documentation Manager – layout templates, asset management,
  and co-branded collateral generation
* White-label configuration (Premium only)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .tiers import Tier, TierConfig, TIER_CONFIGS, require_feature, tier_summary


# ---------------------------------------------------------------------------
# Subscription models
# ---------------------------------------------------------------------------

@dataclass
class Subscription:
    subscription_id: str = field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:12]}")
    user_id: str = ""
    tier: Tier = Tier.FREE
    status: str = "active"          # active | cancelled | past_due | trialing
    started_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    renews_at: str = ""
    payment_method: str = ""


@dataclass
class CheckoutSession:
    """Stripe-compatible checkout session payload for the storefront."""

    session_id: str = field(default_factory=lambda: f"cs_{uuid.uuid4().hex[:16]}")
    user_id: str = ""
    tier: Tier = Tier.FREE
    amount_usd: float = 0.0
    currency: str = "usd"
    success_url: str = "https://dreamcobots.io/checkout/success"
    cancel_url: str = "https://dreamcobots.io/checkout/cancel"
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Marketing Documentation Manager models
# ---------------------------------------------------------------------------

LAYOUT_TEMPLATES = {
    "b2b_landing": {
        "name": "B2B Landing Page",
        "sections": ["Hero", "Value Propositions", "Tier Comparison", "Social Proof", "CTA"],
        "target_audience": "enterprise decision-makers",
        "description": "High-conversion landing page targeting business buyers.",
    },
    "developer_portal": {
        "name": "Developer Portal",
        "sections": ["Quickstart", "API Reference", "SDKs & Libraries", "Tutorials", "Community"],
        "target_audience": "software developers",
        "description": "Documentation-first layout for onboarding technical users.",
    },
    "partner_brief": {
        "name": "Partner Brief",
        "sections": ["Executive Summary", "Mutual Benefits", "Integration Overview",
                     "Go-to-Market Plan", "Next Steps"],
        "target_audience": "potential AI ecosystem partners",
        "description": "One-pager designed for outreach to strategic partners.",
    },
    "enterprise_pitch": {
        "name": "Enterprise Pitch Deck",
        "sections": ["Problem", "Solution", "Platform Overview", "Tier Pricing",
                     "Case Studies", "Security & Compliance", "Roadmap"],
        "target_audience": "enterprise CXOs and procurement teams",
        "description": "Sales deck for enterprise accounts.",
    },
    "product_hunt": {
        "name": "Product Hunt Launch",
        "sections": ["Tagline", "Gallery", "Feature Highlights", "Maker Story", "Offer Code"],
        "target_audience": "early adopters and indie hackers",
        "description": "Launch materials optimised for Product Hunt.",
    },
}


@dataclass
class MarketingDocument:
    doc_id: str = field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:10]}")
    template_key: str = "b2b_landing"
    title: str = ""
    content: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    last_modified: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    export_formats: List[str] = field(default_factory=lambda: ["pdf", "notion", "confluence"])


# ---------------------------------------------------------------------------
# Marketplace class
# ---------------------------------------------------------------------------

class Marketplace:
    """
    Handles subscriptions, online sales, and marketing documentation
    for the Dreamcobots AI Chatbot platform.
    """

    def __init__(self) -> None:
        self._subscriptions: Dict[str, Subscription] = {}
        self._documents: Dict[str, MarketingDocument] = {}

    # ------------------------------------------------------------------
    # Tier / pricing catalogue
    # ------------------------------------------------------------------

    def get_pricing_catalogue(self) -> str:
        """Return a human-readable pricing catalogue."""
        return tier_summary()

    def get_tier_details(self, tier: Tier) -> Dict:
        """Return structured pricing and feature details for a tier."""
        cfg: TierConfig = TIER_CONFIGS[tier]
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "monthly_price_usd": cfg.monthly_price_usd,
            "max_messages_per_day": (
                "Unlimited" if cfg.max_messages_per_day == -1
                else cfg.max_messages_per_day
            ),
            "ai_models": cfg.ai_models,
            "features": cfg.features,
            "description": cfg.description,
        }

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        user_id: str,
        tier: Tier,
        payment_method: str = "card",
    ) -> Subscription:
        """Create or upgrade a user's subscription."""
        renewal_days = 30
        renews_at = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=renewal_days)
        ).isoformat()

        sub = Subscription(
            user_id=user_id,
            tier=tier,
            status="trialing" if tier != Tier.FREE else "active",
            renews_at=renews_at,
            payment_method=payment_method,
        )
        self._subscriptions[user_id] = sub
        return sub

    def cancel_subscription(self, user_id: str) -> Subscription:
        """Cancel a user's subscription (downgrades to Free at period end)."""
        sub = self._subscriptions.get(user_id)
        if not sub:
            raise KeyError(f"No subscription found for user '{user_id}'.")
        sub.status = "cancelled"
        return sub

    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Retrieve the subscription record for a user."""
        return self._subscriptions.get(user_id)

    # ------------------------------------------------------------------
    # Checkout (Stripe-compatible payload)
    # ------------------------------------------------------------------

    def create_checkout_session(
        self,
        user_id: str,
        tier: Tier,
        success_url: str = "",
        cancel_url: str = "",
    ) -> CheckoutSession:
        """
        Prepare a checkout session payload ready to pass to Stripe's API.

        In production, forward ``CheckoutSession.__dict__`` to
        ``stripe.checkout.Session.create(**payload)``.
        """
        cfg = TIER_CONFIGS[tier]
        session = CheckoutSession(
            user_id=user_id,
            tier=tier,
            amount_usd=cfg.monthly_price_usd,
            success_url=success_url or "https://dreamcobots.io/checkout/success",
            cancel_url=cancel_url or "https://dreamcobots.io/checkout/cancel",
            metadata={
                "tier": tier.value,
                "features": cfg.features,
                "ai_models": cfg.ai_models,
            },
        )
        return session

    # ------------------------------------------------------------------
    # Marketing Documentation Manager (Premium)
    # ------------------------------------------------------------------

    def list_templates(self, tier: Tier) -> Dict:
        """List available marketing layout templates (Premium only)."""
        require_feature(tier, "marketing_doc_manager")
        return {key: tmpl["name"] for key, tmpl in LAYOUT_TEMPLATES.items()}

    def create_marketing_document(
        self,
        tier: Tier,
        template_key: str,
        title: str,
        brand_name: str = "Dreamcobots",
        value_propositions: Optional[List[str]] = None,
    ) -> MarketingDocument:
        """
        Generate a pre-populated marketing document from a template.

        Parameters
        ----------
        tier             : User's subscription tier (must be Premium).
        template_key     : One of the keys in ``LAYOUT_TEMPLATES``.
        title            : Document title / campaign name.
        brand_name       : Company or product name to embed in content.
        value_propositions : List of key selling points.
        """
        require_feature(tier, "marketing_doc_manager")

        if template_key not in LAYOUT_TEMPLATES:
            raise ValueError(
                f"Unknown template '{template_key}'. "
                f"Choose from: {', '.join(LAYOUT_TEMPLATES)}"
            )

        template = LAYOUT_TEMPLATES[template_key]
        vps = value_propositions or [
            f"Tiered AI chatbot platform built for scale",
            f"KimiK AI integration for extended reasoning",
            f"Partner recruitment and AI ecosystem directory",
        ]

        content: Dict = {
            "title": title,
            "brand": brand_name,
            "template": template["name"],
            "target_audience": template["target_audience"],
            "sections": {},
        }

        for section in template["sections"]:
            content["sections"][section] = _generate_section_content(
                section, brand_name, vps
            )

        doc = MarketingDocument(
            template_key=template_key,
            title=title,
            content=content,
        )
        self._documents[doc.doc_id] = doc
        return doc

    def get_document(self, doc_id: str) -> Optional[MarketingDocument]:
        """Retrieve a marketing document by ID."""
        return self._documents.get(doc_id)

    def list_documents(self) -> List[Dict]:
        """Return a summary list of all generated marketing documents."""
        return [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "template": doc.template_key,
                "created_at": doc.created_at,
            }
            for doc in self._documents.values()
        ]

    # ------------------------------------------------------------------
    # White-label (Premium)
    # ------------------------------------------------------------------

    def configure_white_label(
        self,
        tier: Tier,
        brand_name: str,
        primary_color: str = "#4F46E5",
        logo_url: str = "",
        custom_domain: str = "",
    ) -> Dict:
        """
        Configure white-label settings for the chatbot UI (Premium only).
        """
        require_feature(tier, "white_label")
        return {
            "brand_name": brand_name,
            "primary_color": primary_color,
            "logo_url": logo_url or f"https://assets.dreamcobots.io/{brand_name.lower()}/logo.png",
            "custom_domain": custom_domain or f"{brand_name.lower().replace(' ', '-')}.dreamcobots.io",
            "powered_by": "Dreamcobots AI Platform",
            "configured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_section_content(
    section: str, brand_name: str, vps: List[str]
) -> str:
    """Generate placeholder content for a marketing document section."""
    section_lower = section.lower()
    if "hero" in section_lower or "tagline" in section_lower:
        return f"{brand_name} – The AI Chatbot Platform Built for Every Business"
    if "value" in section_lower or "feature" in section_lower or "highlight" in section_lower:
        return "\n".join(f"• {vp}" for vp in vps)
    if "tier" in section_lower or "pricing" in section_lower or "offer" in section_lower:
        return tier_summary()
    if "cta" in section_lower or "next step" in section_lower:
        return f"Get started with {brand_name} today – Free tier, no credit card required."
    if "problem" in section_lower:
        return "Businesses waste hours on repetitive support tasks with no scalable AI solution."
    if "solution" in section_lower:
        return (
            f"{brand_name} provides tiered AI chatbots powered by KimiK and leading LLMs, "
            "deployable in minutes."
        )
    if "social proof" in section_lower or "case stud" in section_lower:
        return "Trusted by 500+ businesses. 98% customer satisfaction. 4.9★ on G2."
    if "security" in section_lower or "compliance" in section_lower:
        return "SOC 2 Type II certified. GDPR compliant. End-to-end encryption."
    if "roadmap" in section_lower:
        return "Near-term: Multimodal support · 6 months: Voice interface · 9 months: Agent orchestration"
    return f"[{section} content for {brand_name} – customise before publishing]"
