"""
Buddy Bot — Offer Generator Engine

Auto-crafts tailored service offers for business leads.  Outputs include:
  • Ad campaign packages   — social/search ad management
  • Marketing funnel kits  — landing page + email sequence + CRM
  • Lead generation systems — multi-channel outbound pipelines
  • Brand identity packages — logo, copy, positioning
  • Business automation packs — booking, CRM, invoicing, support bots

Offer pricing adapts to the lead's estimated value and the urgency of their
digital gap.  ENTERPRISE tier unlocks performance-based pricing and
multi-service bundles.

Tier access
-----------
  FREE:       3 offer templates, fixed pricing.
  PRO:        All templates, dynamic pricing by vertical, urgency scoring.
  ENTERPRISE: Custom bundles, performance-based deals, white-label offers.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# Minimum lead value (USD/month) to qualify for performance-based pricing
PERFORMANCE_PRICING_THRESHOLD_USD: float = 3000.0


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ServiceType(Enum):
    AD_CAMPAIGN = "ad_campaign"
    MARKETING_FUNNEL = "marketing_funnel"
    LEAD_GENERATION = "lead_generation"
    BRAND_IDENTITY = "brand_identity"
    BUSINESS_AUTOMATION = "business_automation"
    WEBSITE_AND_SEO = "website_and_seo"
    SOCIAL_MEDIA_MANAGEMENT = "social_media_management"
    EMAIL_MARKETING = "email_marketing"
    FULL_AI_OPERATOR = "full_ai_operator"


class PricingModel(Enum):
    FIXED_SETUP = "fixed_setup"
    MONTHLY_RETAINER = "monthly_retainer"
    PERFORMANCE_BASED = "performance_based"
    CUSTOM_BUNDLE = "custom_bundle"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ServiceOffer:
    """A crafted service offer for a specific business lead."""

    offer_id: str
    target_business: str
    service_type: ServiceType
    headline: str
    description: str
    deliverables: list
    pricing_model: PricingModel
    setup_fee_usd: float
    monthly_fee_usd: float
    guarantee: str
    platforms: list
    timeline_days: int
    upsell_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "offer_id": self.offer_id,
            "target_business": self.target_business,
            "service_type": self.service_type.value,
            "headline": self.headline,
            "description": self.description,
            "deliverables": self.deliverables,
            "pricing_model": self.pricing_model.value,
            "setup_fee_usd": self.setup_fee_usd,
            "monthly_fee_usd": self.monthly_fee_usd,
            "guarantee": self.guarantee,
            "platforms": self.platforms,
            "timeline_days": self.timeline_days,
            "upsell_path": self.upsell_path,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class OfferGeneratorError(Exception):
    """Base exception for OfferGeneratorEngine errors."""


class OfferGeneratorTierError(OfferGeneratorError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Offer templates
# ---------------------------------------------------------------------------

_FREE_SERVICE_TYPES = [
    ServiceType.AD_CAMPAIGN,
    ServiceType.MARKETING_FUNNEL,
    ServiceType.LEAD_GENERATION,
]

_ALL_SERVICE_TYPES = list(ServiceType)

_SERVICE_METADATA: dict[ServiceType, dict] = {
    ServiceType.AD_CAMPAIGN: {
        "headline_tpl": "Launch high-converting ads for {business} and reach 10,000+ new customers",
        "description": "We design, launch, and optimise paid ad campaigns across major platforms.",
        "deliverables": [
            "Campaign strategy document",
            "3 ad creatives (static + video)",
            "A/B split testing setup",
            "Monthly performance report",
            "Conversion tracking integration",
        ],
        "platforms": ["Facebook", "Instagram", "Google", "TikTok"],
        "timeline_days": 7,
        "setup_fee": 500,
        "monthly_fee_range": (500, 1500),
        "guarantee": "We guarantee a minimum 2x ROAS in 60 days or your money back.",
        "upsell": ServiceType.MARKETING_FUNNEL.value,
    },
    ServiceType.MARKETING_FUNNEL: {
        "headline_tpl": "Build a fully automated sales funnel for {business} — capture and close leads 24/7",
        "description": "End-to-end funnel: landing page, email sequences, CRM, and retargeting.",
        "deliverables": [
            "Custom landing page design",
            "7-email drip sequence",
            "CRM setup (leads automatically added)",
            "Lead magnet creation",
            "Retargeting pixel installation",
            "Monthly funnel analytics report",
        ],
        "platforms": ["Email", "SMS", "Facebook Pixel", "Google Tag Manager"],
        "timeline_days": 14,
        "setup_fee": 1000,
        "monthly_fee_range": (750, 2000),
        "guarantee": "Funnel live in 14 days or we extend free for 30 days.",
        "upsell": ServiceType.LEAD_GENERATION.value,
    },
    ServiceType.LEAD_GENERATION: {
        "headline_tpl": "Generate 30–100 qualified leads/month for {business}",
        "description": "Multi-channel lead engine: outbound outreach + inbound content + paid ads.",
        "deliverables": [
            "Prospect database build (500+ contacts)",
            "Cold outreach sequences (email + SMS)",
            "Weekly new-lead pipeline report",
            "Lead scoring and qualification",
            "Booked-call automation",
        ],
        "platforms": ["Email", "SMS", "LinkedIn", "Google"],
        "timeline_days": 10,
        "setup_fee": 750,
        "monthly_fee_range": (1000, 3000),
        "guarantee": "Minimum 30 qualified leads in 30 days or we continue at no charge.",
        "upsell": ServiceType.BUSINESS_AUTOMATION.value,
    },
    ServiceType.BRAND_IDENTITY: {
        "headline_tpl": "Give {business} a standout brand that commands premium prices",
        "description": "Complete brand identity: logo, colour palette, voice, positioning.",
        "deliverables": [
            "Professional logo (3 concepts)",
            "Brand colour palette + typography",
            "Brand voice & messaging guide",
            "Business card + letterhead templates",
            "Social media profile kit",
        ],
        "platforms": ["All platforms"],
        "timeline_days": 10,
        "setup_fee": 800,
        "monthly_fee_range": (0, 300),
        "guarantee": "Unlimited revisions until 100% satisfied.",
        "upsell": ServiceType.SOCIAL_MEDIA_MANAGEMENT.value,
    },
    ServiceType.BUSINESS_AUTOMATION: {
        "headline_tpl": "Automate {business} ops — booking, invoicing, and customer support on autopilot",
        "description": "AI-powered business automation: scheduling, CRM, invoicing, and chat support.",
        "deliverables": [
            "Online booking integration",
            "Automated invoice + payment collection",
            "Customer support chatbot",
            "Appointment reminder sequences",
            "Payroll summary automation",
        ],
        "platforms": ["Calendly", "Stripe", "Twilio", "Zapier"],
        "timeline_days": 14,
        "setup_fee": 1200,
        "monthly_fee_range": (800, 2500),
        "guarantee": "Full automation live in 2 weeks or extended free support.",
        "upsell": ServiceType.FULL_AI_OPERATOR.value,
    },
    ServiceType.WEBSITE_AND_SEO: {
        "headline_tpl": "Build a high-converting website for {business} and dominate local search",
        "description": "Professional website + on-page SEO + Google Business optimisation.",
        "deliverables": [
            "5-page professional website",
            "Mobile-responsive design",
            "On-page SEO setup",
            "Google Business profile optimisation",
            "Site speed optimisation",
            "Monthly ranking report",
        ],
        "platforms": ["Google", "Bing", "Maps"],
        "timeline_days": 14,
        "setup_fee": 1500,
        "monthly_fee_range": (300, 800),
        "guarantee": "Page-1 ranking for 3 local keywords in 90 days.",
        "upsell": ServiceType.AD_CAMPAIGN.value,
    },
    ServiceType.SOCIAL_MEDIA_MANAGEMENT: {
        "headline_tpl": "Grow {business} on social media with daily AI-powered content",
        "description": "Daily posts, story creation, community management, and follower growth.",
        "deliverables": [
            "30 posts/month (designed + copywritten)",
            "Daily story updates",
            "Hashtag research + strategy",
            "Community engagement (replies/DMs)",
            "Monthly growth report",
        ],
        "platforms": ["Instagram", "TikTok", "Facebook", "X (Twitter)"],
        "timeline_days": 3,
        "setup_fee": 300,
        "monthly_fee_range": (500, 1500),
        "guarantee": "Consistent posting guaranteed — miss a day, we refund that day.",
        "upsell": ServiceType.AD_CAMPAIGN.value,
    },
    ServiceType.EMAIL_MARKETING: {
        "headline_tpl": "Build {business} a profitable email list and automate revenue",
        "description": "List building, campaigns, automated sequences, and deliverability optimisation.",
        "deliverables": [
            "Email list building strategy",
            "Welcome + onboarding sequence (5 emails)",
            "Monthly newsletter (4 emails)",
            "Re-engagement campaign",
            "A/B subject-line testing",
            "Monthly open-rate & click report",
        ],
        "platforms": ["Klaviyo", "Mailchimp", "ActiveCampaign"],
        "timeline_days": 7,
        "setup_fee": 400,
        "monthly_fee_range": (400, 1200),
        "guarantee": "Minimum 25% open rate within 60 days.",
        "upsell": ServiceType.MARKETING_FUNNEL.value,
    },
    ServiceType.FULL_AI_OPERATOR: {
        "headline_tpl": "Deploy a full AI business operator for {business} — grow on autopilot",
        "description": "Complete AI workforce: ads, leads, sales, fulfilment, support, billing.",
        "deliverables": [
            "All services from every tier (ads, funnel, leads, SEO, social, email, automation)",
            "Dedicated AI account manager",
            "Real-time revenue dashboard",
            "Weekly strategy call",
            "Priority 24/7 support",
            "Quarterly growth roadmap",
        ],
        "platforms": ["All platforms"],
        "timeline_days": 21,
        "setup_fee": 2500,
        "monthly_fee_range": (3000, 7000),
        "guarantee": "ROI guarantee — if we don't deliver 3x your investment, we work free.",
        "upsell": None,
    },
}


# ---------------------------------------------------------------------------
# OfferGeneratorEngine
# ---------------------------------------------------------------------------

class OfferGeneratorEngine:
    """Generates tailored service offers for business leads.

    Parameters
    ----------
    available_service_types : list[ServiceType]
        Service types this tier can generate offers for.
    can_dynamic_pricing : bool
        Whether pricing adapts to lead value.
    can_performance_pricing : bool
        Whether performance-based pricing is available.
    can_custom_bundle : bool
        Whether multi-service bundles can be created.
    """

    def __init__(
        self,
        available_service_types: Optional[list] = None,
        can_dynamic_pricing: bool = False,
        can_performance_pricing: bool = False,
        can_custom_bundle: bool = False,
    ) -> None:
        self.available_service_types: list[ServiceType] = (
            available_service_types if available_service_types is not None
            else _FREE_SERVICE_TYPES
        )
        self.can_dynamic_pricing = can_dynamic_pricing
        self.can_performance_pricing = can_performance_pricing
        self.can_custom_bundle = can_custom_bundle
        self._offer_counter: int = 0
        self._offers: list[ServiceOffer] = []

    # ------------------------------------------------------------------
    # Core offer generation
    # ------------------------------------------------------------------

    def build_offer(
        self,
        business_name: str,
        service_type: Optional[ServiceType] = None,
        estimated_lead_value: float = 1000.0,
    ) -> ServiceOffer:
        """Build a single tailored service offer.

        Parameters
        ----------
        business_name : str
            Name of the target business.
        service_type : ServiceType | None
            Specific service to offer.  If None, the best-fit type is chosen.
        estimated_lead_value : float
            Lead's estimated monthly value (influences dynamic pricing).

        Returns
        -------
        ServiceOffer
            The generated offer.
        """
        if service_type is not None and service_type not in self.available_service_types:
            raise OfferGeneratorTierError(
                f"Service type '{service_type.value}' requires PRO tier or above."
            )

        chosen_type = service_type or self._best_fit_service(estimated_lead_value)
        meta = _SERVICE_METADATA[chosen_type]
        self._offer_counter += 1

        lo, hi = meta["monthly_fee_range"]
        if self.can_dynamic_pricing:
            scale = min(estimated_lead_value / 5000.0, 1.5)
            monthly = round(lo + (hi - lo) * scale, 2)
        else:
            monthly = round((lo + hi) / 2, 2)

        pricing_model = PricingModel.MONTHLY_RETAINER
        if self.can_performance_pricing and estimated_lead_value >= PERFORMANCE_PRICING_THRESHOLD_USD:
            pricing_model = PricingModel.PERFORMANCE_BASED

        offer = ServiceOffer(
            offer_id=f"offer_{self._offer_counter:04d}",
            target_business=business_name,
            service_type=chosen_type,
            headline=meta["headline_tpl"].format(business=business_name),
            description=meta["description"],
            deliverables=list(meta["deliverables"]),
            pricing_model=pricing_model,
            setup_fee_usd=meta["setup_fee"],
            monthly_fee_usd=monthly,
            guarantee=meta["guarantee"],
            platforms=list(meta["platforms"]),
            timeline_days=meta["timeline_days"],
            upsell_path=meta.get("upsell"),
        )
        self._offers.append(offer)
        return offer

    def build_bundle(
        self,
        business_name: str,
        service_types: list,
        estimated_lead_value: float = 2000.0,
    ) -> list:
        """Build a multi-service bundle offer (ENTERPRISE only).

        Parameters
        ----------
        business_name : str
            Name of the target business.
        service_types : list[ServiceType]
            List of service types to include in the bundle.
        estimated_lead_value : float
            Estimated monthly value for pricing.

        Returns
        -------
        list[ServiceOffer]
            One ServiceOffer per service type in the bundle.
        """
        if not self.can_custom_bundle:
            raise OfferGeneratorTierError(
                "Custom bundles require ENTERPRISE tier."
            )
        offers = []
        for stype in service_types:
            offer = self.build_offer(business_name, stype, estimated_lead_value)
            offers.append(offer)
        return offers

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _best_fit_service(self, lead_value: float) -> ServiceType:
        """Choose the highest-impact service type for the given lead value."""
        if lead_value >= 5000:
            return ServiceType.FULL_AI_OPERATOR
        if lead_value >= 3000:
            return ServiceType.LEAD_GENERATION
        if lead_value >= 1500:
            return ServiceType.MARKETING_FUNNEL
        return ServiceType.AD_CAMPAIGN

    def get_all_offers(self) -> list[ServiceOffer]:
        """Return all generated offers."""
        return list(self._offers)

    def list_available_services(self) -> list[str]:
        """Return names of service types available on this tier."""
        return [s.value for s in self.available_service_types]

    def to_dict(self) -> dict:
        """Return engine state as a serialisable dict."""
        return {
            "offer_count": self._offer_counter,
            "available_service_types": [s.value for s in self.available_service_types],
            "can_dynamic_pricing": self.can_dynamic_pricing,
            "can_performance_pricing": self.can_performance_pricing,
            "can_custom_bundle": self.can_custom_bundle,
        }
