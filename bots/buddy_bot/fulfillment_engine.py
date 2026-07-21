"""
Buddy Bot — Fulfillment Engine

Automatically delivers services to clients after a deal is closed:
  • Ad campaign creation   — generates campaign structure, ad copy, targeting
  • Landing page builder   — creates high-converting page layouts + copy
  • Content generation     — social posts, blog articles, email sequences
  • Funnel assembly        — connects lead magnet → opt-in → email → sale
  • Business automation    — booking pages, invoicing templates, CRM setup
  • Brand kit generation   — logo briefs, colour palettes, brand voice docs

All deliverable outputs are structured data objects ready for downstream
publishing or human review before deployment.

Tier access
-----------
  FREE:       Ad copy generation only.
  PRO:        Ad campaigns, landing pages, content, email sequences.
  ENTERPRISE: Full fulfillment suite — funnels, automation, brand kits,
              bulk generation.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# Email sequence length limits
MIN_EMAIL_SEQUENCE_LENGTH: int = 3
MAX_EMAIL_SEQUENCE_LENGTH: int = 10


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DeliverableType(Enum):
    AD_COPY = "ad_copy"
    AD_CAMPAIGN = "ad_campaign"
    LANDING_PAGE = "landing_page"
    SOCIAL_POSTS = "social_posts"
    BLOG_ARTICLE = "blog_article"
    EMAIL_SEQUENCE = "email_sequence"
    SALES_FUNNEL = "sales_funnel"
    AUTOMATION_SETUP = "automation_setup"
    BRAND_KIT = "brand_kit"


class DeliverableStatus(Enum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    DEPLOYED = "deployed"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Deliverable:
    """A completed service deliverable."""

    deliverable_id: str
    client_name: str
    deliverable_type: DeliverableType
    title: str
    content: dict
    status: DeliverableStatus = DeliverableStatus.DRAFT
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    approved_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "deliverable_id": self.deliverable_id,
            "client_name": self.client_name,
            "deliverable_type": self.deliverable_type.value,
            "title": self.title,
            "content": self.content,
            "status": self.status.value,
            "created_at": self.created_at,
            "approved_at": self.approved_at,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FulfillmentEngineError(Exception):
    """Base exception for FulfillmentEngine errors."""


class FulfillmentEngineTierError(FulfillmentEngineError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Content templates
# ---------------------------------------------------------------------------

_AD_HOOKS = [
    "Tired of slow business growth? Here's the fix.",
    "Local businesses are seeing 3x customers with this one system.",
    "Stop wasting ad budget — here's what actually works.",
    "The #1 reason your competitors are outranking you (and how to fix it today).",
    "We helped {client} get 47 new leads in 30 days — here's how.",
]

_CTA_PHRASES = [
    "Get your free growth audit →",
    "Book a strategy call →",
    "See your growth plan →",
    "Start your free trial →",
    "Claim your spot →",
]

_EMAIL_SUBJECTS = [
    "Quick question about {client}'s marketing",
    "We found 3 quick wins for {client}",
    "{client}: your growth report is ready",
    "How {client} can get 30 more customers this month",
    "Your competitor is doing this — are you?",
]

_PLATFORMS = ["Facebook", "Instagram", "Google", "TikTok", "LinkedIn", "X (Twitter)"]


# ---------------------------------------------------------------------------
# FulfillmentEngine
# ---------------------------------------------------------------------------

class FulfillmentEngine:
    """Delivers services automatically after a deal is closed.

    Parameters
    ----------
    can_landing_pages : bool
        Whether landing page generation is available.
    can_email_sequences : bool
        Whether email sequence generation is available.
    can_funnels : bool
        Whether sales funnel assembly is available.
    can_automation_setup : bool
        Whether business automation setup is available.
    can_brand_kit : bool
        Whether brand kit generation is available.
    can_bulk_generate : bool
        Whether bulk content generation is available.
    """

    def __init__(
        self,
        can_landing_pages: bool = False,
        can_email_sequences: bool = False,
        can_funnels: bool = False,
        can_automation_setup: bool = False,
        can_brand_kit: bool = False,
        can_bulk_generate: bool = False,
    ) -> None:
        self.can_landing_pages = can_landing_pages
        self.can_email_sequences = can_email_sequences
        self.can_funnels = can_funnels
        self.can_automation_setup = can_automation_setup
        self.can_brand_kit = can_brand_kit
        self.can_bulk_generate = can_bulk_generate
        self._deliverables: list[Deliverable] = []
        self._counter: int = 0

    # ------------------------------------------------------------------
    # Core delivery methods
    # ------------------------------------------------------------------

    def generate_ad_copy(
        self,
        client_name: str,
        industry: str = "local business",
        platforms: Optional[list] = None,
    ) -> Deliverable:
        """Generate ad copy for a client.

        Parameters
        ----------
        client_name : str
            Client business name.
        industry : str
            Business industry/vertical.
        platforms : list | None
            Target ad platforms.  Defaults to top 3.

        Returns
        -------
        Deliverable
            Ad copy deliverable (DRAFT status).
        """
        rng = random.Random(self._counter + hash(client_name) % 1000)
        chosen_platforms = platforms or rng.sample(_PLATFORMS, 3)

        ads = []
        for platform in chosen_platforms:
            ads.append({
                "platform": platform,
                "headline": rng.choice(_AD_HOOKS).replace("{client}", client_name),
                "body": (
                    f"Attention {industry} owners — "
                    f"DreamCo Buddy AI has helped businesses just like {client_name} "
                    f"grow their customer base by 3x in 60 days using automated "
                    f"marketing systems. No guesswork. No wasted budget. "
                    f"Just results."
                ),
                "cta": rng.choice(_CTA_PHRASES),
                "estimated_reach": rng.randint(5000, 80000),
            })

        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.AD_COPY,
            title=f"Ad Copy Package for {client_name}",
            content={"ads": ads, "platforms": chosen_platforms},
        )

    def generate_ad_campaign(
        self,
        client_name: str,
        budget_usd: float = 1000.0,
        duration_days: int = 30,
    ) -> Deliverable:
        """Generate a full ad campaign structure.

        Parameters
        ----------
        client_name : str
            Client business name.
        budget_usd : float
            Total campaign budget.
        duration_days : int
            Campaign run duration.

        Returns
        -------
        Deliverable
        """
        rng = random.Random(self._counter + hash(client_name) % 999)
        daily_budget = round(budget_usd / duration_days, 2)

        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.AD_CAMPAIGN,
            title=f"Ad Campaign for {client_name} — {duration_days}-Day Run",
            content={
                "campaign_name": f"{client_name} Growth Campaign",
                "total_budget_usd": budget_usd,
                "daily_budget_usd": daily_budget,
                "duration_days": duration_days,
                "platforms": rng.sample(_PLATFORMS, 3),
                "objective": "Lead generation + brand awareness",
                "audiences": [
                    f"Local {client_name.split()[0]} lookalike audience",
                    "Retargeting — website visitors 30 days",
                    "Interest-based — competitors' page fans",
                ],
                "ad_sets": [
                    {"name": "Awareness", "budget_pct": 30},
                    {"name": "Consideration", "budget_pct": 40},
                    {"name": "Conversion", "budget_pct": 30},
                ],
                "kpis": {
                    "target_cpl_usd": round(budget_usd / rng.randint(30, 100), 2),
                    "target_roas": round(rng.uniform(2.0, 4.5), 1),
                    "estimated_reach": rng.randint(20000, 150000),
                },
            },
        )

    def build_landing_page(
        self,
        client_name: str,
        headline: str,
        offer_summary: str,
    ) -> Deliverable:
        """Generate a high-converting landing page layout.

        Parameters
        ----------
        client_name : str
            Client business name.
        headline : str
            Primary page headline.
        offer_summary : str
            Brief description of the offer.

        Returns
        -------
        Deliverable
        """
        if not self.can_landing_pages:
            raise FulfillmentEngineTierError(
                "Landing page generation requires PRO tier or above."
            )
        rng = random.Random(self._counter + hash(client_name) % 777)
        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.LANDING_PAGE,
            title=f"Landing Page for {client_name}",
            content={
                "headline": headline,
                "sub_headline": f"Join hundreds of {client_name.split()[0]} customers who have already made the switch.",
                "offer": offer_summary,
                "social_proof": [
                    f"⭐⭐⭐⭐⭐ '{client_name} helped us 3x our bookings in 30 days.' — Happy Client",
                    f"⭐⭐⭐⭐⭐ 'Best investment we made this year.' — Verified Customer",
                ],
                "form_fields": ["First name", "Email address", "Phone number"],
                "cta_button": rng.choice(_CTA_PHRASES),
                "trust_badges": ["SSL Secured", "No Spam", "Cancel Anytime"],
                "sections": ["Hero", "Pain Points", "Solution", "Social Proof", "CTA", "FAQ"],
            },
        )

    def generate_email_sequence(
        self,
        client_name: str,
        sequence_length: int = 5,
        goal: str = "onboarding",
    ) -> Deliverable:
        """Generate an email drip sequence.

        Parameters
        ----------
        client_name : str
            Client business name.
        sequence_length : int
            Number of emails (3–10).
        goal : str
            Sequence goal (onboarding, sales, re-engagement).

        Returns
        -------
        Deliverable
        """
        if not self.can_email_sequences:
            raise FulfillmentEngineTierError(
                "Email sequence generation requires PRO tier or above."
            )
        sequence_length = max(MIN_EMAIL_SEQUENCE_LENGTH, min(sequence_length, MAX_EMAIL_SEQUENCE_LENGTH))
        rng = random.Random(self._counter + hash(client_name) % 555)

        emails = []
        for i in range(sequence_length):
            day = [0, 2, 4, 7, 10, 14, 21, 28, 35, 42][i]
            emails.append({
                "email_number": i + 1,
                "send_day": day,
                "subject": _EMAIL_SUBJECTS[i % len(_EMAIL_SUBJECTS)].format(client=client_name),
                "preview_text": f"Quick update for {client_name} — Day {day}",
                "body_summary": (
                    f"Email {i + 1} ({goal}): "
                    + [
                        f"Welcome to DreamCo! Here's what happens next for {client_name}.",
                        f"Your first quick win — here's the easiest thing to improve.",
                        f"Case study: how a business like {client_name} grew 40% in 30 days.",
                        f"Frequently asked questions — answered.",
                        f"Your progress report — what we've done so far.",
                        f"Introducing our most powerful feature for {client_name}.",
                        f"Special offer — upgrade and save 30% this month only.",
                        f"Success story: {client_name} spotlight.",
                        f"What's coming next for your account.",
                        f"Thank you — and here's your bonus resource.",
                    ][i % 10]
                ),
                "cta": rng.choice(_CTA_PHRASES),
            })

        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.EMAIL_SEQUENCE,
            title=f"{sequence_length}-Email {goal.title()} Sequence for {client_name}",
            content={"goal": goal, "emails": emails},
        )

    def assemble_funnel(
        self,
        client_name: str,
        lead_magnet: str,
        offer: str,
    ) -> Deliverable:
        """Assemble a complete sales funnel.

        Parameters
        ----------
        client_name : str
            Client business name.
        lead_magnet : str
            Free resource used to capture leads.
        offer : str
            Main paid offer at the bottom of the funnel.

        Returns
        -------
        Deliverable
        """
        if not self.can_funnels:
            raise FulfillmentEngineTierError(
                "Funnel assembly requires ENTERPRISE tier."
            )
        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.SALES_FUNNEL,
            title=f"Full Sales Funnel for {client_name}",
            content={
                "stages": [
                    {
                        "stage": 1,
                        "name": "Awareness",
                        "tactic": "Paid ads + organic social → landing page",
                        "goal": "500+ monthly visitors",
                    },
                    {
                        "stage": 2,
                        "name": "Lead Capture",
                        "tactic": f"Lead magnet: {lead_magnet}",
                        "goal": "25% opt-in conversion",
                    },
                    {
                        "stage": 3,
                        "name": "Nurture",
                        "tactic": "7-email drip sequence",
                        "goal": "30% email open rate",
                    },
                    {
                        "stage": 4,
                        "name": "Conversion",
                        "tactic": f"Sales page for: {offer}",
                        "goal": "5–10% conversion",
                    },
                    {
                        "stage": 5,
                        "name": "Retention",
                        "tactic": "Onboarding + upsell sequence",
                        "goal": "60% retention at 90 days",
                    },
                ],
                "tools": ["Landing page builder", "Email platform", "CRM", "Stripe"],
                "estimated_monthly_revenue_usd": "Varies by traffic & offer price",
            },
        )

    def setup_automation(self, client_name: str) -> Deliverable:
        """Generate a business automation setup plan.

        Parameters
        ----------
        client_name : str
            Client business name.

        Returns
        -------
        Deliverable
        """
        if not self.can_automation_setup:
            raise FulfillmentEngineTierError(
                "Automation setup requires ENTERPRISE tier."
            )
        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.AUTOMATION_SETUP,
            title=f"Business Automation Setup for {client_name}",
            content={
                "systems": [
                    {
                        "name": "Appointment Booking",
                        "tool": "Calendly / Cal.com",
                        "setup_steps": ["Embed booking widget on website", "Configure availability", "Enable reminders"],
                    },
                    {
                        "name": "Invoice & Payments",
                        "tool": "Stripe",
                        "setup_steps": ["Create product catalog", "Set up recurring billing", "Configure automatic receipts"],
                    },
                    {
                        "name": "Customer Support Bot",
                        "tool": "DreamCo Buddy AI Chat",
                        "setup_steps": ["Configure FAQ responses", "Set escalation rules", "Enable 24/7 auto-reply"],
                    },
                    {
                        "name": "CRM & Lead Tracking",
                        "tool": "HubSpot / Pipedrive",
                        "setup_steps": ["Import existing contacts", "Set up pipeline stages", "Configure auto-follow-ups"],
                    },
                    {
                        "name": "Review Generation",
                        "tool": "Automated email after service delivery",
                        "setup_steps": ["Set trigger: 48 hours post-service", "Draft review request email", "Track response rate"],
                    },
                ],
                "estimated_time_savings_hrs_per_week": 15,
            },
        )

    def generate_brand_kit(self, client_name: str, industry: str = "general") -> Deliverable:
        """Generate a brand identity kit brief.

        Parameters
        ----------
        client_name : str
            Client business name.
        industry : str
            Business industry for context.

        Returns
        -------
        Deliverable
        """
        if not self.can_brand_kit:
            raise FulfillmentEngineTierError(
                "Brand kit generation requires ENTERPRISE tier."
            )
        rng = random.Random(hash(client_name) % 10000)
        palettes = [
            ["#1A1A2E", "#16213E", "#0F3460", "#E94560"],
            ["#2C3E50", "#E74C3C", "#ECF0F1", "#3498DB"],
            ["#1B1B2F", "#162447", "#1F4068", "#1B262C"],
            ["#FFFFFF", "#000000", "#FF6B6B", "#4ECDC4"],
            ["#2D2D2D", "#F5A623", "#FFFFFF", "#1A73E8"],
        ]
        return self._create_deliverable(
            client_name=client_name,
            deliverable_type=DeliverableType.BRAND_KIT,
            title=f"Brand Identity Kit for {client_name}",
            content={
                "brand_name": client_name,
                "industry": industry,
                "brand_voice": rng.choice([
                    "Bold, confident, results-driven",
                    "Warm, approachable, community-focused",
                    "Professional, trustworthy, expert",
                    "Energetic, innovative, forward-thinking",
                    "Premium, exclusive, sophisticated",
                ]),
                "colour_palette": rng.choice(palettes),
                "typography": {
                    "heading": rng.choice(["Montserrat Bold", "Playfair Display", "Raleway ExtraBold", "Bebas Neue"]),
                    "body": rng.choice(["Open Sans", "Lato", "Source Sans Pro", "Nunito"]),
                },
                "logo_brief": {
                    "style": rng.choice(["Wordmark", "Icon + Wordmark", "Monogram", "Abstract Icon"]),
                    "feeling": "Trustworthy, modern, memorable",
                    "avoid": "Clip art, overly complex designs, dated fonts",
                },
                "tagline_options": [
                    f"Powering {industry} forward.",
                    f"Your {industry} partner, elevated.",
                    f"Results. Every time.",
                ],
                "social_media_templates": ["Profile picture", "Cover photo", "Post template", "Story template"],
            },
        )

    def bulk_generate(
        self,
        client_name: str,
        deliverable_types: list,
        **kwargs,
    ) -> list:
        """Generate multiple deliverables in one call (ENTERPRISE only).

        Parameters
        ----------
        client_name : str
            Client business name.
        deliverable_types : list[DeliverableType]
            Deliverable types to generate.
        **kwargs
            Extra keyword arguments forwarded to individual generators.

        Returns
        -------
        list[Deliverable]
        """
        if not self.can_bulk_generate:
            raise FulfillmentEngineTierError(
                "Bulk generation requires ENTERPRISE tier."
            )
        results = []
        for dtype in deliverable_types:
            if dtype == DeliverableType.AD_COPY:
                results.append(self.generate_ad_copy(client_name))
            elif dtype == DeliverableType.AD_CAMPAIGN:
                results.append(self.generate_ad_campaign(client_name))
            elif dtype == DeliverableType.LANDING_PAGE:
                results.append(self.build_landing_page(
                    client_name,
                    headline=kwargs.get("headline", f"Grow {client_name} with AI Marketing"),
                    offer_summary=kwargs.get("offer_summary", "Full AI marketing system"),
                ))
            elif dtype == DeliverableType.EMAIL_SEQUENCE:
                results.append(self.generate_email_sequence(client_name))
            elif dtype == DeliverableType.SALES_FUNNEL:
                results.append(self.assemble_funnel(
                    client_name,
                    lead_magnet=kwargs.get("lead_magnet", "Free marketing audit"),
                    offer=kwargs.get("offer", "Full AI marketing package"),
                ))
            elif dtype == DeliverableType.AUTOMATION_SETUP:
                results.append(self.setup_automation(client_name))
            elif dtype == DeliverableType.BRAND_KIT:
                results.append(self.generate_brand_kit(client_name))
        return results

    # ------------------------------------------------------------------
    # Approval workflow
    # ------------------------------------------------------------------

    def approve_deliverable(self, deliverable_id: str) -> Deliverable:
        """Mark a deliverable as approved.

        Parameters
        ----------
        deliverable_id : str
            The ID of the deliverable to approve.

        Returns
        -------
        Deliverable
        """
        for d in self._deliverables:
            if d.deliverable_id == deliverable_id:
                d.status = DeliverableStatus.APPROVED
                d.approved_at = datetime.now(timezone.utc).isoformat()
                return d
        raise FulfillmentEngineError(f"Deliverable not found: {deliverable_id}")

    def deploy_deliverable(self, deliverable_id: str) -> Deliverable:
        """Mark a deliverable as deployed.

        Parameters
        ----------
        deliverable_id : str
            The ID of the deliverable to deploy.

        Returns
        -------
        Deliverable
        """
        for d in self._deliverables:
            if d.deliverable_id == deliverable_id:
                if d.status != DeliverableStatus.APPROVED:
                    raise FulfillmentEngineError(
                        "Deliverable must be approved before deployment."
                    )
                d.status = DeliverableStatus.DEPLOYED
                return d
        raise FulfillmentEngineError(f"Deliverable not found: {deliverable_id}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_deliverable(
        self,
        client_name: str,
        deliverable_type: DeliverableType,
        title: str,
        content: dict,
    ) -> Deliverable:
        self._counter += 1
        deliverable = Deliverable(
            deliverable_id=f"del_{self._counter:04d}",
            client_name=client_name,
            deliverable_type=deliverable_type,
            title=title,
            content=content,
            status=DeliverableStatus.DRAFT,
        )
        self._deliverables.append(deliverable)
        return deliverable

    def get_all_deliverables(self) -> list[Deliverable]:
        """Return all deliverables."""
        return list(self._deliverables)

    def get_deliverables_for_client(self, client_name: str) -> list[Deliverable]:
        """Return all deliverables for a specific client."""
        return [d for d in self._deliverables if d.client_name == client_name]

    def to_dict(self) -> dict:
        """Return engine state as a serialisable dict."""
        return {
            "total_deliverables": len(self._deliverables),
            "can_landing_pages": self.can_landing_pages,
            "can_email_sequences": self.can_email_sequences,
            "can_funnels": self.can_funnels,
            "can_automation_setup": self.can_automation_setup,
            "can_brand_kit": self.can_brand_kit,
            "can_bulk_generate": self.can_bulk_generate,
        }
