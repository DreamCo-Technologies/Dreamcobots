"""
Fiverr Automation Bot — Main Module

Automates Fiverr freelance operations: gig listings, order management,
inbox automation, review collection, analytics, AI-powered pricing,
freelancer/client matching, job postings, proposals, Stripe payments,
milestones, featured gigs, and admin dashboard.

Tier-aware:
  FREE:       5 gigs + 20 orders/month, 20% service fee.
  PRO ($49):  50 gigs + matching/proposals/Stripe, 10% service fee.
  ENTERPRISE ($199): Unlimited, AI pricing, admin dashboard, 5% fee.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

Stripe integration uses the STRIPE_SECRET_KEY environment variable.
No secret keys are hard-coded; mock mode is used when the variable is
not set so the bot remains fully functional in tests/development.
"""

from __future__ import annotations

import os
import random
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.fiverr_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_GIG_LISTING,
    FEATURE_ORDER_TRACKING,
    FEATURE_INBOX_AUTOMATION,
    FEATURE_REVIEW_COLLECTION,
    FEATURE_ANALYTICS,
    FEATURE_PRICING_OPTIMIZER,
    FEATURE_CRM_EXPORT,
    FEATURE_AI_PRICING,
    FEATURE_WHITE_LABEL,
    FEATURE_BULK_MESSAGING,
    FEATURE_FREELANCER_MATCHING,
    FEATURE_JOB_POSTINGS,
    FEATURE_PROPOSALS,
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_MILESTONES,
    FEATURE_ADMIN_DASHBOARD,
    FEATURE_FEATURED_GIGS,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FiverrBotError(Exception):
    """Base exception for Fiverr Bot errors."""


class FiverrBotTierError(FiverrBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class GigCategory(Enum):
    DATA_ENTRY = "data_entry"
    RESEARCH = "research"
    CONTENT_WRITING = "content_writing"
    ANALYTICS = "analytics"
    GRAPHIC_DESIGN = "graphic_design"
    VIDEO_EDITING = "video_editing"
    SEO = "seo"
    SOCIAL_MEDIA = "social_media"
    WEB_DEVELOPMENT = "web_development"
    VIRTUAL_ASSISTANT = "virtual_assistant"


class OrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REVISION_REQUESTED = "revision_requested"


class ProposalStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class MilestoneStatus(Enum):
    PENDING = "pending"
    FUNDED = "funded"
    RELEASED = "released"
    REFUNDED = "refunded"


@dataclass
class Gig:
    gig_id: str
    title: str
    category: GigCategory
    description: str
    price_usd: float
    delivery_days: int
    tags: list = field(default_factory=list)
    active: bool = True
    featured: bool = False
    featured_until: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    orders_total: int = 0
    rating: float = 0.0
    review_count: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Order:
    order_id: str
    gig_id: str
    buyer_username: str
    amount_usd: float
    status: OrderStatus
    requirements: str = ""
    deliverable: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    delivered_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Review:
    review_id: str
    order_id: str
    gig_id: str
    buyer_username: str
    rating: float          # 1.0 – 5.0
    comment: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class FreelancerProfile:
    username: str
    skills: list            # e.g. ["python", "web_development", "SEO"]
    bio: str
    hourly_rate_usd: float
    rating: float = 0.0
    review_count: int = 0
    joined_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class ClientProfile:
    username: str
    company_name: str
    bio: str
    joined_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class JobPosting:
    job_id: str
    client_username: str
    title: str
    description: str
    category: GigCategory
    budget_usd: float
    skills_required: list   # skills the client is looking for
    status: str = "open"    # open | closed | in_progress
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Proposal:
    proposal_id: str
    job_id: str
    freelancer_username: str
    cover_letter: str
    rate_usd: float
    delivery_days: int
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Milestone:
    milestone_id: str
    order_id: str
    title: str
    amount_usd: float
    status: MilestoneStatus = MilestoneStatus.PENDING
    payment_intent_id: Optional[str] = None
    funded_at: Optional[str] = None
    released_at: Optional[str] = None


# ---------------------------------------------------------------------------
# GIG_TEMPLATES — realistic starting-point gig definitions
# ---------------------------------------------------------------------------

GIG_TEMPLATES = {
    GigCategory.DATA_ENTRY: {
        "title": "Professional Data Entry & Spreadsheet Management",
        "description": (
            "I will perform accurate, fast data entry into Excel, Google Sheets, "
            "CRM systems, or any database you use. Includes deduplication and "
            "formatting cleanup."
        ),
        "base_price_usd": 15.0,
        "delivery_days": 1,
        "tags": ["data entry", "spreadsheet", "excel", "google sheets", "database"],
    },
    GigCategory.RESEARCH: {
        "title": "In-Depth Market Research & Competitor Analysis",
        "description": (
            "I will research your industry, competitors, or target audience and "
            "deliver a structured report with actionable insights."
        ),
        "base_price_usd": 25.0,
        "delivery_days": 2,
        "tags": ["research", "market analysis", "competitor research", "report"],
    },
    GigCategory.CONTENT_WRITING: {
        "title": "SEO-Optimized Blog Posts & Article Writing",
        "description": (
            "I will write engaging, SEO-friendly articles (500–2,000 words) on "
            "any topic, including keyword research and meta descriptions."
        ),
        "base_price_usd": 20.0,
        "delivery_days": 2,
        "tags": ["blog writing", "SEO", "articles", "content", "copywriting"],
    },
    GigCategory.ANALYTICS: {
        "title": "Business Analytics Dashboard & KPI Reporting",
        "description": (
            "I will build analytics dashboards in Google Data Studio, Tableau, or "
            "Excel, and produce monthly KPI reports tailored to your business goals."
        ),
        "base_price_usd": 50.0,
        "delivery_days": 3,
        "tags": ["analytics", "dashboard", "KPI", "data visualization", "reporting"],
    },
    GigCategory.SEO: {
        "title": "Complete SEO Audit & Optimization Strategy",
        "description": (
            "I will audit your website, identify SEO issues, and provide a "
            "prioritized action plan to improve search rankings."
        ),
        "base_price_usd": 35.0,
        "delivery_days": 2,
        "tags": ["SEO", "audit", "keyword research", "on-page SEO", "backlinks"],
    },
    GigCategory.SOCIAL_MEDIA: {
        "title": "Social Media Management & Content Calendar",
        "description": (
            "I will create and schedule 30 days of social media content for "
            "Instagram, Facebook, Twitter/X, or LinkedIn."
        ),
        "base_price_usd": 40.0,
        "delivery_days": 3,
        "tags": ["social media", "content calendar", "Instagram", "Facebook", "scheduling"],
    },
    GigCategory.VIRTUAL_ASSISTANT: {
        "title": "Professional Virtual Assistant for Business Tasks",
        "description": (
            "I will handle emails, scheduling, research, data management, and "
            "any administrative tasks to free up your time."
        ),
        "base_price_usd": 10.0,
        "delivery_days": 1,
        "tags": ["virtual assistant", "admin", "scheduling", "email management"],
    },
    GigCategory.GRAPHIC_DESIGN: {
        "title": "Modern Logo & Brand Identity Design",
        "description": (
            "I will design a professional logo with full brand identity package "
            "including color palette, typography, and usage guidelines."
        ),
        "base_price_usd": 45.0,
        "delivery_days": 3,
        "tags": ["logo design", "branding", "graphic design", "identity", "Canva"],
    },
    GigCategory.VIDEO_EDITING: {
        "title": "Professional Video Editing for YouTube & Social Media",
        "description": (
            "I will edit your raw footage into a polished video with captions, "
            "transitions, music, and color grading."
        ),
        "base_price_usd": 30.0,
        "delivery_days": 2,
        "tags": ["video editing", "YouTube", "reels", "TikTok", "color grading"],
    },
    GigCategory.WEB_DEVELOPMENT: {
        "title": "Responsive Website Design with WordPress or HTML/CSS",
        "description": (
            "I will build a clean, mobile-responsive website with SEO best "
            "practices, contact forms, and fast loading times."
        ),
        "base_price_usd": 75.0,
        "delivery_days": 5,
        "tags": ["web design", "WordPress", "HTML", "CSS", "responsive"],
    },
}


# ---------------------------------------------------------------------------
# Stripe integration helper (mock when STRIPE_SECRET_KEY not set)
# ---------------------------------------------------------------------------

class _StripeClient:
    """
    Thin wrapper around Stripe API calls.

    Uses the real Stripe library when STRIPE_SECRET_KEY is set as an
    environment variable.  Falls back to mock mode (no network calls,
    no real money) when the variable is absent, which is the default in
    tests and development.

    Never hard-code the secret key — always supply it via environment:
        export STRIPE_SECRET_KEY=sk_live_...   # or sk_test_...
    """

    def __init__(self) -> None:
        self._key = os.environ.get("STRIPE_SECRET_KEY", "")
        self._mock = not bool(self._key)

    @property
    def mock_mode(self) -> bool:
        return self._mock

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str = "usd",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create a Stripe PaymentIntent (real or mock)."""
        if self._mock:
            return {
                "id": f"pi_mock_{uuid.uuid4().hex[:16]}",
                "amount": amount_cents,
                "currency": currency,
                "status": "requires_payment_method",
                "metadata": metadata or {},
                "mock": True,
            }
        try:
            import stripe  # type: ignore
            stripe.api_key = self._key
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
            )
            return dict(intent)
        except Exception as exc:  # pragma: no cover
            raise FiverrBotError(f"Stripe error: {exc}") from exc

    def transfer_payout(
        self,
        amount_cents: int,
        destination: str,
        currency: str = "usd",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create a Stripe Transfer (real or mock)."""
        if self._mock:
            return {
                "id": f"tr_mock_{uuid.uuid4().hex[:16]}",
                "amount": amount_cents,
                "currency": currency,
                "destination": destination,
                "metadata": metadata or {},
                "mock": True,
            }
        try:
            import stripe  # type: ignore
            stripe.api_key = self._key
            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency=currency,
                destination=destination,
                metadata=metadata or {},
            )
            return dict(transfer)
        except Exception as exc:  # pragma: no cover
            raise FiverrBotError(f"Stripe transfer error: {exc}") from exc


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class FiverrBot:
    """
    Fiverr Automation Bot — empire-grade freelance automation engine.

    Automates service listing, order management, inbox automation,
    review collection, analytics, freelancer/client matching, job
    postings, proposals, Stripe payments, milestones, featured gigs,
    and admin dashboard.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and limits.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._gigs: dict[str, Gig] = {}
        self._orders: dict[str, Order] = {}
        self._reviews: dict[str, Review] = {}
        self._inbox: list[dict] = []
        self._revenue_log: list[dict] = []
        self._gig_counter: int = 0
        self._order_counter: int = 0
        self._review_counter: int = 0
        # New collections
        self._freelancers: dict[str, FreelancerProfile] = {}
        self._clients: dict[str, ClientProfile] = {}
        self._job_postings: dict[str, JobPosting] = {}
        self._proposals: dict[str, Proposal] = {}
        self._milestones: dict[str, Milestone] = {}
        self._service_fee_log: list[dict] = []
        self._job_counter: int = 0
        self._proposal_counter: int = 0
        self._milestone_counter: int = 0
        self._stripe = _StripeClient()

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Feature '{feature}' is not available on the "
                f"{self._config.name} tier.{suggestion}"
            )

    def _check_gig_limit(self) -> None:
        limit = self._config.max_gigs
        if limit is not None and len(self._gigs) >= limit:
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Gig limit of {limit} reached on the {self._config.name} tier.{suggestion}"
            )

    def _check_order_limit(self) -> None:
        limit = self._config.max_orders_per_month
        if limit is not None and len(self._orders) >= limit:
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Order limit of {limit} reached on the {self._config.name} tier.{suggestion}"
            )

    # ------------------------------------------------------------------
    # Gig management
    # ------------------------------------------------------------------

    def create_gig(
        self,
        category: GigCategory,
        title: Optional[str] = None,
        price_usd: Optional[float] = None,
        delivery_days: Optional[int] = None,
        description: Optional[str] = None,
    ) -> dict:
        """Create a new gig listing from a category template or custom values."""
        self._require(FEATURE_GIG_LISTING)
        self._check_gig_limit()

        template = GIG_TEMPLATES.get(category, GIG_TEMPLATES[GigCategory.DATA_ENTRY])
        self._gig_counter += 1
        gig_id = f"gig_{self._gig_counter:04d}"

        gig = Gig(
            gig_id=gig_id,
            title=title or template["title"],
            category=category,
            description=description or template["description"],
            price_usd=price_usd or template["base_price_usd"],
            delivery_days=delivery_days or template["delivery_days"],
            tags=list(template.get("tags", [])),
        )
        self._gigs[gig_id] = gig
        return _gig_to_dict(gig)

    def update_gig_price(self, gig_id: str, new_price_usd: float) -> dict:
        """Update the price of an existing gig."""
        gig = self._get_gig(gig_id)
        gig.price_usd = round(new_price_usd, 2)
        return _gig_to_dict(gig)

    def deactivate_gig(self, gig_id: str) -> dict:
        """Deactivate a gig so it no longer appears in listings."""
        gig = self._get_gig(gig_id)
        gig.active = False
        return {"gig_id": gig_id, "active": False, "status": "deactivated"}

    def get_gigs(self, active_only: bool = False) -> list:
        """Return all (or only active) gigs."""
        gigs = list(self._gigs.values())
        if active_only:
            gigs = [g for g in gigs if g.active]
        return [_gig_to_dict(g) for g in gigs]

    def _get_gig(self, gig_id: str) -> Gig:
        if gig_id not in self._gigs:
            raise FiverrBotError(f"Gig '{gig_id}' not found.")
        return self._gigs[gig_id]

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def receive_order(
        self,
        gig_id: str,
        buyer_username: str,
        requirements: str = "",
    ) -> dict:
        """Record a new incoming order for a gig."""
        self._require(FEATURE_ORDER_TRACKING)
        self._check_order_limit()
        gig = self._get_gig(gig_id)

        self._order_counter += 1
        order_id = f"ord_{self._order_counter:04d}"
        order = Order(
            order_id=order_id,
            gig_id=gig_id,
            buyer_username=buyer_username,
            amount_usd=gig.price_usd,
            status=OrderStatus.PENDING,
            requirements=requirements,
        )
        self._orders[order_id] = order
        gig.orders_total += 1
        return _order_to_dict(order)

    def start_order(self, order_id: str) -> dict:
        """Mark an order as in-progress."""
        order = self._get_order(order_id)
        order.status = OrderStatus.IN_PROGRESS
        return _order_to_dict(order)

    def deliver_order(self, order_id: str, deliverable: str) -> dict:
        """Mark an order as delivered with the provided deliverable content."""
        order = self._get_order(order_id)
        order.status = OrderStatus.DELIVERED
        order.deliverable = deliverable
        order.delivered_at = datetime.now(timezone.utc).isoformat()
        return _order_to_dict(order)

    def complete_order(self, order_id: str) -> dict:
        """Mark an order as completed, record revenue, and deduct service fee."""
        order = self._get_order(order_id)
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now(timezone.utc).isoformat()
        fee_pct = self._config.service_fee_pct
        fee_usd = round(order.amount_usd * fee_pct / 100.0, 2)
        net_usd = round(order.amount_usd - fee_usd, 2)
        self._revenue_log.append({
            "order_id": order_id,
            "gig_id": order.gig_id,
            "amount_usd": order.amount_usd,
            "buyer": order.buyer_username,
            "completed_at": order.completed_at,
        })
        self._service_fee_log.append({
            "order_id": order_id,
            "gross_usd": order.amount_usd,
            "fee_pct": fee_pct,
            "fee_usd": fee_usd,
            "net_usd": net_usd,
            "recorded_at": order.completed_at,
        })
        return _order_to_dict(order)

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        order = self._get_order(order_id)
        order.status = OrderStatus.CANCELLED
        return _order_to_dict(order)

    def get_orders(self, status: Optional[OrderStatus] = None) -> list:
        """Return all orders, optionally filtered by status."""
        orders = list(self._orders.values())
        if status:
            orders = [o for o in orders if o.status == status]
        return [_order_to_dict(o) for o in orders]

    def _get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise FiverrBotError(f"Order '{order_id}' not found.")
        return self._orders[order_id]

    # ------------------------------------------------------------------
    # Inbox automation
    # ------------------------------------------------------------------

    def send_message(self, buyer_username: str, message: str) -> dict:
        """Send an automated inbox message to a buyer."""
        self._require(FEATURE_INBOX_AUTOMATION)
        entry = {
            "to": buyer_username,
            "message": message,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
        }
        self._inbox.append(entry)
        return entry

    def bulk_message(self, buyer_usernames: list, message: str) -> dict:
        """Send a bulk message to multiple buyers."""
        self._require(FEATURE_BULK_MESSAGING)
        sent = []
        for username in buyer_usernames:
            sent.append(self.send_message(username, message))
        return {"recipients": len(sent), "status": "sent", "messages": sent}

    def auto_respond_inquiry(self, buyer_username: str, inquiry: str) -> dict:
        """Generate and send an automated response to a buyer inquiry."""
        self._require(FEATURE_INBOX_AUTOMATION)
        response = (
            f"Hi {buyer_username}, thanks for your message! "
            "I'd be happy to help. Could you share more details about your project? "
            "I'll get back to you within 24 hours with a custom quote. — DreamCo Bot"
        )
        return self.send_message(buyer_username, response)

    def get_inbox(self) -> list:
        """Return all inbox messages sent."""
        return list(self._inbox)

    # ------------------------------------------------------------------
    # Review collection
    # ------------------------------------------------------------------

    def request_review(self, order_id: str) -> dict:
        """Send a review request message after order completion."""
        self._require(FEATURE_REVIEW_COLLECTION)
        order = self._get_order(order_id)
        if order.status != OrderStatus.COMPLETED:
            raise FiverrBotError(
                f"Order '{order_id}' must be completed before requesting a review."
            )
        message = (
            f"Hi {order.buyer_username}, thank you for your order! "
            "If you're happy with the delivery, I'd really appreciate a 5-star review. "
            "It helps my profile grow. 🙏"
        )
        return self.send_message(order.buyer_username, message)

    def record_review(
        self,
        order_id: str,
        rating: float,
        comment: str = "",
    ) -> dict:
        """Record a buyer review for a completed order."""
        self._require(FEATURE_REVIEW_COLLECTION)
        order = self._get_order(order_id)
        if not (1.0 <= rating <= 5.0):
            raise FiverrBotError("Rating must be between 1.0 and 5.0.")

        self._review_counter += 1
        review_id = f"rev_{self._review_counter:04d}"
        review = Review(
            review_id=review_id,
            order_id=order_id,
            gig_id=order.gig_id,
            buyer_username=order.buyer_username,
            rating=round(rating, 1),
            comment=comment,
        )
        self._reviews[review_id] = review

        # Update gig rating
        gig = self._gigs.get(order.gig_id)
        if gig:
            total_rating = gig.rating * gig.review_count + rating
            gig.review_count += 1
            gig.rating = round(total_rating / gig.review_count, 2)

        return _review_to_dict(review)

    def get_reviews(self, gig_id: Optional[str] = None) -> list:
        """Return all reviews, optionally filtered by gig."""
        reviews = list(self._reviews.values())
        if gig_id:
            reviews = [r for r in reviews if r.gig_id == gig_id]
        return [_review_to_dict(r) for r in reviews]

    # ------------------------------------------------------------------
    # Pricing optimizer
    # ------------------------------------------------------------------

    def optimize_price(self, gig_id: str) -> dict:
        """Suggest an optimized price for a gig based on category benchmarks."""
        self._require(FEATURE_PRICING_OPTIMIZER)
        gig = self._get_gig(gig_id)
        template = GIG_TEMPLATES.get(gig.category, GIG_TEMPLATES[GigCategory.DATA_ENTRY])
        base = template["base_price_usd"]

        # AI pricing uses additional signals
        if self._config.has_feature(FEATURE_AI_PRICING):
            demand_factor = random.uniform(1.05, 1.40)
            optimized = round(base * demand_factor, 2)
            method = "AI demand modeling"
        else:
            # Simple rules-based optimization
            if gig.rating >= 4.8 and gig.review_count >= 10:
                optimized = round(base * 1.20, 2)
            elif gig.orders_total >= 50:
                optimized = round(base * 1.10, 2)
            else:
                optimized = base
            method = "rules-based"

        return {
            "gig_id": gig_id,
            "current_price_usd": gig.price_usd,
            "optimized_price_usd": optimized,
            "optimization_method": method,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_analytics(self) -> dict:
        """Return performance analytics across all gigs and orders."""
        self._require(FEATURE_ANALYTICS)
        total_revenue = sum(e["amount_usd"] for e in self._revenue_log)
        completed = [o for o in self._orders.values() if o.status == OrderStatus.COMPLETED]
        avg_rating = (
            round(sum(r.rating for r in self._reviews.values()) / len(self._reviews), 2)
            if self._reviews else 0.0
        )
        conversion_rate = (
            round(len(completed) / len(self._orders) * 100, 1)
            if self._orders else 0.0
        )

        by_category: dict = {}
        for gig in self._gigs.values():
            cat = gig.category.value
            rev = sum(
                o.amount_usd
                for o in self._orders.values()
                if o.gig_id == gig.gig_id and o.status == OrderStatus.COMPLETED
            )
            by_category[cat] = by_category.get(cat, 0.0) + rev

        return {
            "total_gigs": len(self._gigs),
            "active_gigs": sum(1 for g in self._gigs.values() if g.active),
            "total_orders": len(self._orders),
            "completed_orders": len(completed),
            "total_revenue_usd": round(total_revenue, 2),
            "average_order_value_usd": (
                round(total_revenue / len(completed), 2) if completed else 0.0
            ),
            "avg_rating": avg_rating,
            "review_count": len(self._reviews),
            "conversion_rate_pct": conversion_rate,
            "revenue_by_category": {k: round(v, 2) for k, v in by_category.items()},
            "tier": self.tier.value,
        }

    def get_revenue_summary(self) -> dict:
        """Return a summary of revenue earned."""
        total = sum(e["amount_usd"] for e in self._revenue_log)
        by_gig: dict = {}
        for entry in self._revenue_log:
            gid = entry["gig_id"]
            by_gig[gid] = round(by_gig.get(gid, 0.0) + entry["amount_usd"], 2)
        return {
            "total_revenue_usd": round(total, 2),
            "completed_orders": len(self._revenue_log),
            "by_gig": by_gig,
            "revenue_log": list(self._revenue_log),
        }

    # ------------------------------------------------------------------
    # CRM export
    # ------------------------------------------------------------------

    def export_to_crm(self, crm_name: str = "default") -> dict:
        """Export completed order data to an external CRM."""
        self._require(FEATURE_CRM_EXPORT)
        records = [
            {
                "order_id": e["order_id"],
                "buyer": e["buyer"],
                "amount_usd": e["amount_usd"],
                "gig_id": e["gig_id"],
                "completed_at": e["completed_at"],
            }
            for e in self._revenue_log
        ]
        return {
            "crm": crm_name,
            "records_exported": len(records),
            "records": records,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }

    # ------------------------------------------------------------------
    # Freelancer & client registration
    # ------------------------------------------------------------------

    def register_freelancer(
        self,
        username: str,
        skills: list,
        bio: str = "",
        hourly_rate_usd: float = 25.0,
    ) -> dict:
        """Register a freelancer profile."""
        self._require(FEATURE_FREELANCER_MATCHING)
        if username in self._freelancers:
            raise FiverrBotError(f"Freelancer '{username}' is already registered.")
        profile = FreelancerProfile(
            username=username,
            skills=[s.lower() for s in skills],
            bio=bio,
            hourly_rate_usd=round(hourly_rate_usd, 2),
        )
        self._freelancers[username] = profile
        return _freelancer_to_dict(profile)

    def get_freelancer(self, username: str) -> dict:
        """Return a freelancer profile."""
        self._require(FEATURE_FREELANCER_MATCHING)
        if username not in self._freelancers:
            raise FiverrBotError(f"Freelancer '{username}' not found.")
        return _freelancer_to_dict(self._freelancers[username])

    def register_client(
        self,
        username: str,
        company_name: str = "",
        bio: str = "",
    ) -> dict:
        """Register a client profile."""
        self._require(FEATURE_JOB_POSTINGS)
        if username in self._clients:
            raise FiverrBotError(f"Client '{username}' is already registered.")
        profile = ClientProfile(
            username=username,
            company_name=company_name,
            bio=bio,
        )
        self._clients[username] = profile
        return _client_to_dict(profile)

    # ------------------------------------------------------------------
    # Job postings
    # ------------------------------------------------------------------

    def post_job(
        self,
        client_username: str,
        title: str,
        description: str,
        category: GigCategory,
        budget_usd: float,
        skills_required: Optional[list] = None,
    ) -> dict:
        """Client posts a new job listing."""
        self._require(FEATURE_JOB_POSTINGS)
        if client_username not in self._clients:
            raise FiverrBotError(
                f"Client '{client_username}' is not registered. "
                "Call register_client() first."
            )
        self._job_counter += 1
        job_id = f"job_{self._job_counter:04d}"
        job = JobPosting(
            job_id=job_id,
            client_username=client_username,
            title=title,
            description=description,
            category=category,
            budget_usd=round(budget_usd, 2),
            skills_required=[s.lower() for s in (skills_required or [])],
        )
        self._job_postings[job_id] = job
        return _job_to_dict(job)

    def get_jobs(
        self,
        category: Optional[GigCategory] = None,
        skills: Optional[list] = None,
        status: str = "open",
    ) -> list:
        """Return job postings, optionally filtered by category, skills, or status."""
        self._require(FEATURE_JOB_POSTINGS)
        jobs = list(self._job_postings.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if category:
            jobs = [j for j in jobs if j.category == category]
        if skills:
            needle = {s.lower() for s in skills}
            jobs = [j for j in jobs if needle & set(j.skills_required)]
        return [_job_to_dict(j) for j in jobs]

    # ------------------------------------------------------------------
    # Freelancer–client matching
    # ------------------------------------------------------------------

    def match_freelancers(self, job_id: str) -> list:
        """
        Return a ranked list of freelancer profiles that match a job posting
        by skill overlap.  Higher overlap = higher rank.
        """
        self._require(FEATURE_FREELANCER_MATCHING)
        if job_id not in self._job_postings:
            raise FiverrBotError(f"Job '{job_id}' not found.")
        job = self._job_postings[job_id]
        required = set(job.skills_required)
        matches = []
        for fl in self._freelancers.values():
            fl_skills = set(fl.skills)
            overlap = required & fl_skills
            if overlap:
                matches.append({
                    **_freelancer_to_dict(fl),
                    "matched_skills": sorted(overlap),
                    "match_score": round(len(overlap) / max(len(required), 1) * 100, 1),
                })
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    # ------------------------------------------------------------------
    # Proposals
    # ------------------------------------------------------------------

    def submit_proposal(
        self,
        job_id: str,
        freelancer_username: str,
        cover_letter: str,
        rate_usd: float,
        delivery_days: int,
    ) -> dict:
        """Freelancer submits a proposal for a job."""
        self._require(FEATURE_PROPOSALS)
        if job_id not in self._job_postings:
            raise FiverrBotError(f"Job '{job_id}' not found.")
        if freelancer_username not in self._freelancers:
            raise FiverrBotError(
                f"Freelancer '{freelancer_username}' not registered."
            )
        self._proposal_counter += 1
        proposal_id = f"prop_{self._proposal_counter:04d}"
        proposal = Proposal(
            proposal_id=proposal_id,
            job_id=job_id,
            freelancer_username=freelancer_username,
            cover_letter=cover_letter,
            rate_usd=round(rate_usd, 2),
            delivery_days=delivery_days,
        )
        self._proposals[proposal_id] = proposal
        return _proposal_to_dict(proposal)

    def get_proposals(self, job_id: str) -> list:
        """Return all proposals for a job."""
        self._require(FEATURE_PROPOSALS)
        return [
            _proposal_to_dict(p)
            for p in self._proposals.values()
            if p.job_id == job_id
        ]

    def accept_proposal(self, proposal_id: str) -> dict:
        """Client accepts a proposal, closing the job to further proposals."""
        self._require(FEATURE_PROPOSALS)
        if proposal_id not in self._proposals:
            raise FiverrBotError(f"Proposal '{proposal_id}' not found.")
        proposal = self._proposals[proposal_id]
        proposal.status = ProposalStatus.ACCEPTED
        # Reject all other proposals for the same job
        for pid, p in self._proposals.items():
            if p.job_id == proposal.job_id and pid != proposal_id:
                if p.status == ProposalStatus.PENDING:
                    p.status = ProposalStatus.REJECTED
        # Mark the job as in_progress
        job = self._job_postings.get(proposal.job_id)
        if job:
            job.status = "in_progress"
        return _proposal_to_dict(proposal)

    # ------------------------------------------------------------------
    # Stripe payment integration
    # ------------------------------------------------------------------

    def create_payment_intent(
        self,
        order_id: str,
        amount_usd: Optional[float] = None,
    ) -> dict:
        """
        Create a Stripe PaymentIntent for an order.

        The Stripe secret key is read from the STRIPE_SECRET_KEY environment
        variable.  When the variable is not set the call runs in mock mode
        (no real charge is made).
        """
        self._require(FEATURE_STRIPE_PAYMENTS)
        order = self._get_order(order_id)
        charge_usd = amount_usd if amount_usd is not None else order.amount_usd
        amount_cents = int(round(charge_usd * 100))
        result = self._stripe.create_payment_intent(
            amount_cents=amount_cents,
            currency="usd",
            metadata={"order_id": order_id, "buyer": order.buyer_username},
        )
        result["order_id"] = order_id
        return result

    # ------------------------------------------------------------------
    # Milestones
    # ------------------------------------------------------------------

    def add_milestone(
        self,
        order_id: str,
        title: str,
        amount_usd: float,
    ) -> dict:
        """Add a payment milestone to an order."""
        self._require(FEATURE_MILESTONES)
        self._get_order(order_id)  # validates order exists
        self._milestone_counter += 1
        milestone_id = f"ms_{self._milestone_counter:04d}"
        milestone = Milestone(
            milestone_id=milestone_id,
            order_id=order_id,
            title=title,
            amount_usd=round(amount_usd, 2),
        )
        self._milestones[milestone_id] = milestone
        return _milestone_to_dict(milestone)

    def fund_milestone(self, milestone_id: str) -> dict:
        """Fund a milestone via Stripe (creates a PaymentIntent)."""
        self._require(FEATURE_MILESTONES)
        if milestone_id not in self._milestones:
            raise FiverrBotError(f"Milestone '{milestone_id}' not found.")
        ms = self._milestones[milestone_id]
        if ms.status != MilestoneStatus.PENDING:
            raise FiverrBotError(
                f"Milestone '{milestone_id}' cannot be funded "
                f"(current status: {ms.status.value})."
            )
        amount_cents = int(round(ms.amount_usd * 100))
        pi = self._stripe.create_payment_intent(
            amount_cents=amount_cents,
            currency="usd",
            metadata={"milestone_id": milestone_id, "order_id": ms.order_id},
        )
        ms.status = MilestoneStatus.FUNDED
        ms.payment_intent_id = pi["id"]
        ms.funded_at = datetime.now(timezone.utc).isoformat()
        return _milestone_to_dict(ms)

    def release_milestone(self, milestone_id: str, destination: str = "freelancer") -> dict:
        """
        Release a funded milestone to the freelancer.

        In live mode this creates a Stripe Transfer; in mock mode a
        mock transfer is recorded.
        """
        self._require(FEATURE_MILESTONES)
        if milestone_id not in self._milestones:
            raise FiverrBotError(f"Milestone '{milestone_id}' not found.")
        ms = self._milestones[milestone_id]
        if ms.status != MilestoneStatus.FUNDED:
            raise FiverrBotError(
                f"Milestone '{milestone_id}' must be funded before release "
                f"(current status: {ms.status.value})."
            )
        fee_pct = self._config.service_fee_pct
        fee_usd = round(ms.amount_usd * fee_pct / 100.0, 2)
        payout_usd = round(ms.amount_usd - fee_usd, 2)
        payout_cents = int(round(payout_usd * 100))
        transfer = self._stripe.transfer_payout(
            amount_cents=payout_cents,
            destination=destination,
            metadata={
                "milestone_id": milestone_id,
                "order_id": ms.order_id,
                "fee_pct": str(fee_pct),
            },
        )
        ms.status = MilestoneStatus.RELEASED
        ms.released_at = datetime.now(timezone.utc).isoformat()
        self._service_fee_log.append({
            "milestone_id": milestone_id,
            "order_id": ms.order_id,
            "gross_usd": ms.amount_usd,
            "fee_pct": fee_pct,
            "fee_usd": fee_usd,
            "net_usd": payout_usd,
            "recorded_at": ms.released_at,
        })
        return {**_milestone_to_dict(ms), "transfer": transfer}

    def get_milestones(self, order_id: Optional[str] = None) -> list:
        """Return milestones, optionally filtered by order."""
        milestones = list(self._milestones.values())
        if order_id:
            milestones = [m for m in milestones if m.order_id == order_id]
        return [_milestone_to_dict(m) for m in milestones]

    # ------------------------------------------------------------------
    # Featured gigs
    # ------------------------------------------------------------------

    def feature_gig(self, gig_id: str, days: int = 7) -> dict:
        """
        Mark a gig as featured for a given number of days.

        Featured gigs receive priority placement in listings.
        Requires ENTERPRISE tier.
        """
        self._require(FEATURE_FEATURED_GIGS)
        gig = self._get_gig(gig_id)
        if days < 1:
            raise FiverrBotError("Featured duration must be at least 1 day.")
        until = (
            datetime.now(timezone.utc) + timedelta(days=days)
        ).isoformat()
        gig.featured = True
        gig.featured_until = until
        return {
            "gig_id": gig_id,
            "featured": True,
            "featured_until": until,
            "days": days,
            "status": "featured",
        }

    def get_featured_gigs(self) -> list:
        """Return all currently featured gigs."""
        self._require(FEATURE_FEATURED_GIGS)
        return [_gig_to_dict(g) for g in self._gigs.values() if g.featured]

    # ------------------------------------------------------------------
    # Admin dashboard
    # ------------------------------------------------------------------

    def get_admin_dashboard(self) -> dict:
        """
        Return a comprehensive admin analytics snapshot covering
        transactions, user activity, project statuses, and service fees.
        """
        self._require(FEATURE_ADMIN_DASHBOARD)
        total_gross = sum(e["amount_usd"] for e in self._revenue_log)
        total_fees = sum(e["fee_usd"] for e in self._service_fee_log)
        total_net = round(total_gross - total_fees, 2)

        order_status_breakdown: dict = {}
        for o in self._orders.values():
            key = o.status.value
            order_status_breakdown[key] = order_status_breakdown.get(key, 0) + 1

        proposal_status_breakdown: dict = {}
        for p in self._proposals.values():
            key = p.status.value
            proposal_status_breakdown[key] = proposal_status_breakdown.get(key, 0) + 1

        milestone_status_breakdown: dict = {}
        for m in self._milestones.values():
            key = m.status.value
            milestone_status_breakdown[key] = milestone_status_breakdown.get(key, 0) + 1

        return {
            "tier": self.tier.value,
            "users": {
                "freelancers": len(self._freelancers),
                "clients": len(self._clients),
            },
            "gigs": {
                "total": len(self._gigs),
                "active": sum(1 for g in self._gigs.values() if g.active),
                "featured": sum(1 for g in self._gigs.values() if g.featured),
            },
            "orders": {
                "total": len(self._orders),
                "by_status": order_status_breakdown,
            },
            "job_postings": {
                "total": len(self._job_postings),
                "open": sum(
                    1 for j in self._job_postings.values() if j.status == "open"
                ),
                "in_progress": sum(
                    1 for j in self._job_postings.values() if j.status == "in_progress"
                ),
            },
            "proposals": {
                "total": len(self._proposals),
                "by_status": proposal_status_breakdown,
            },
            "milestones": {
                "total": len(self._milestones),
                "by_status": milestone_status_breakdown,
            },
            "revenue": {
                "gross_usd": round(total_gross, 2),
                "service_fees_usd": round(total_fees, 2),
                "net_usd": total_net,
                "service_fee_pct": self._config.service_fee_pct,
            },
            "reviews": {
                "total": len(self._reviews),
                "avg_rating": (
                    round(
                        sum(r.rating for r in self._reviews.values()) / len(self._reviews), 2
                    )
                    if self._reviews else 0.0
                ),
            },
            "inbox_messages_sent": len(self._inbox),
        }

    # ------------------------------------------------------------------
    # Summary & chat interfaces
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return overall bot statistics."""
        total_revenue = sum(e["amount_usd"] for e in self._revenue_log)
        total_fees = sum(e["fee_usd"] for e in self._service_fee_log)
        return {
            "tier": self.tier.value,
            "total_gigs": len(self._gigs),
            "total_orders": len(self._orders),
            "total_reviews": len(self._reviews),
            "total_revenue_usd": round(total_revenue, 2),
            "total_service_fees_usd": round(total_fees, 2),
            "total_job_postings": len(self._job_postings),
            "total_proposals": len(self._proposals),
            "registered_freelancers": len(self._freelancers),
            "registered_clients": len(self._clients),
            "inbox_messages_sent": len(self._inbox),
        }

    def run(self) -> str:
        """Return a one-line status string (used by ControlCenter)."""
        summary = self.get_summary()
        return (
            f"FiverrBot [{self.tier.value}]: "
            f"{summary['total_gigs']} gigs, "
            f"{summary['total_orders']} orders, "
            f"${summary['total_revenue_usd']:.2f} revenue"
        )

    def chat(self, message: str) -> dict:
        """Natural-language interface for BuddyAI routing."""
        msg = message.lower()
        if "summary" in msg or "stats" in msg or "status" in msg:
            return {"message": "Fiverr Bot summary retrieved.", "data": self.get_summary()}
        if "gigs" in msg or "listings" in msg:
            return {"message": "Gig listings retrieved.", "data": self.get_gigs()}
        if "orders" in msg:
            return {"message": "Orders retrieved.", "data": self.get_orders()}
        if "revenue" in msg or "earnings" in msg:
            return {"message": "Revenue summary retrieved.", "data": self.get_revenue_summary()}
        if "jobs" in msg or "postings" in msg:
            return {"message": "Job postings retrieved.", "data": self.get_jobs()}
        if "proposals" in msg:
            return {"message": "Proposals retrieved.", "data": list(self._proposals.values())}
        if "dashboard" in msg or "admin" in msg:
            if self._config.has_feature(FEATURE_ADMIN_DASHBOARD):
                return {"message": "Admin dashboard retrieved.", "data": self.get_admin_dashboard()}
        return {
            "message": (
                f"Fiverr Automation Bot online. Tier: {self.tier.value}. "
                "Try: 'summary', 'gigs', 'orders', 'revenue', 'jobs', "
                "'proposals', or 'dashboard'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        action = payload.get("action", "summary")
        if action == "create_gig":
            category_str = payload.get("category", "data_entry")
            category = GigCategory(category_str)
            return self.create_gig(
                category=category,
                title=payload.get("title"),
                price_usd=payload.get("price_usd"),
                delivery_days=payload.get("delivery_days"),
                description=payload.get("description"),
            )
        if action == "receive_order":
            return self.receive_order(
                gig_id=payload["gig_id"],
                buyer_username=payload["buyer_username"],
                requirements=payload.get("requirements", ""),
            )
        if action == "post_job":
            return self.post_job(
                client_username=payload["client_username"],
                title=payload["title"],
                description=payload.get("description", ""),
                category=GigCategory(payload.get("category", "data_entry")),
                budget_usd=payload.get("budget_usd", 0.0),
                skills_required=payload.get("skills_required"),
            )
        if action == "submit_proposal":
            return self.submit_proposal(
                job_id=payload["job_id"],
                freelancer_username=payload["freelancer_username"],
                cover_letter=payload.get("cover_letter", ""),
                rate_usd=payload.get("rate_usd", 0.0),
                delivery_days=payload.get("delivery_days", 7),
            )
        if action == "match_freelancers":
            return {"matches": self.match_freelancers(payload["job_id"])}
        if action == "get_analytics":
            return self.get_analytics()
        if action == "get_admin_dashboard":
            return self.get_admin_dashboard()
        return self.get_summary()

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self._config
        gig_limit = "Unlimited" if cfg.is_unlimited_gigs() else str(cfg.max_gigs)
        order_limit = (
            "Unlimited" if cfg.max_orders_per_month is None
            else str(cfg.max_orders_per_month)
        )
        lines = [
            f"=== {cfg.name} Fiverr Automation Bot Tier ===",
            f"Price         : ${cfg.price_usd_monthly:.2f}/month",
            f"Max Gigs      : {gig_limit}",
            f"Max Orders/mo : {order_limit}",
            f"Service Fee   : {cfg.service_fee_pct:.0f}% per transaction",
            f"Support       : {cfg.support_level}",
            "",
            "Features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output


# ---------------------------------------------------------------------------
# Helper serializers
# ---------------------------------------------------------------------------

def _gig_to_dict(g: Gig) -> dict:
    return {
        "gig_id": g.gig_id,
        "title": g.title,
        "category": g.category.value,
        "description": g.description,
        "price_usd": g.price_usd,
        "delivery_days": g.delivery_days,
        "tags": g.tags,
        "active": g.active,
        "featured": g.featured,
        "featured_until": g.featured_until,
        "impressions": g.impressions,
        "clicks": g.clicks,
        "orders_total": g.orders_total,
        "rating": g.rating,
        "review_count": g.review_count,
        "created_at": g.created_at,
    }


def _order_to_dict(o: Order) -> dict:
    return {
        "order_id": o.order_id,
        "gig_id": o.gig_id,
        "buyer_username": o.buyer_username,
        "amount_usd": o.amount_usd,
        "status": o.status.value,
        "requirements": o.requirements,
        "deliverable": o.deliverable,
        "created_at": o.created_at,
        "delivered_at": o.delivered_at,
        "completed_at": o.completed_at,
    }


def _review_to_dict(r: Review) -> dict:
    return {
        "review_id": r.review_id,
        "order_id": r.order_id,
        "gig_id": r.gig_id,
        "buyer_username": r.buyer_username,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at,
    }


def _freelancer_to_dict(fl: FreelancerProfile) -> dict:
    return {
        "username": fl.username,
        "skills": fl.skills,
        "bio": fl.bio,
        "hourly_rate_usd": fl.hourly_rate_usd,
        "rating": fl.rating,
        "review_count": fl.review_count,
        "joined_at": fl.joined_at,
    }


def _client_to_dict(c: ClientProfile) -> dict:
    return {
        "username": c.username,
        "company_name": c.company_name,
        "bio": c.bio,
        "joined_at": c.joined_at,
    }


def _job_to_dict(j: JobPosting) -> dict:
    return {
        "job_id": j.job_id,
        "client_username": j.client_username,
        "title": j.title,
        "description": j.description,
        "category": j.category.value,
        "budget_usd": j.budget_usd,
        "skills_required": j.skills_required,
        "status": j.status,
        "created_at": j.created_at,
    }


def _proposal_to_dict(p: Proposal) -> dict:
    return {
        "proposal_id": p.proposal_id,
        "job_id": p.job_id,
        "freelancer_username": p.freelancer_username,
        "cover_letter": p.cover_letter,
        "rate_usd": p.rate_usd,
        "delivery_days": p.delivery_days,
        "status": p.status.value,
        "created_at": p.created_at,
    }


def _milestone_to_dict(m: Milestone) -> dict:
    return {
        "milestone_id": m.milestone_id,
        "order_id": m.order_id,
        "title": m.title,
        "amount_usd": m.amount_usd,
        "status": m.status.value,
        "payment_intent_id": m.payment_intent_id,
        "funded_at": m.funded_at,
        "released_at": m.released_at,
    }


__all__ = [
    "FiverrBot",
    "FiverrBotError",
    "FiverrBotTierError",
    "GigCategory",
    "OrderStatus",
    "ProposalStatus",
    "MilestoneStatus",
    "Gig",
    "Order",
    "Review",
    "FreelancerProfile",
    "ClientProfile",
    "JobPosting",
    "Proposal",
    "Milestone",
]
