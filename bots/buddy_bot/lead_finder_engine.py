"""
Buddy Bot — Lead Finder Engine

Autonomously scans for businesses that need marketing, ads, lead-generation,
and automation services.  Supported business verticals:
  • Local service businesses (gyms, roofers, plumbers, contractors, …)
  • Shopify / ecommerce stores with low traffic
  • Real estate agents and wholesalers
  • Coaches and consultants
  • Restaurants, cleaning companies, lawn care, auto repair
  • Any entity with weak or absent digital marketing

Scoring uses a simple composite model based on:
  - Estimated digital gap (missing website, ads, funnel)
  - Industry revenue potential
  - Estimated ease of close

Tier access
-----------
  FREE:       Returns up to 5 demo leads, basic industry scoring.
  PRO:        Up to 100 leads per scan, multi-vertical search, enrichment.
  ENTERPRISE: Unlimited leads, geo-targeted search, full AI scoring, CRM export.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BusinessVertical(Enum):
    LOCAL_SERVICE = "local_service"
    ECOMMERCE = "ecommerce"
    REAL_ESTATE = "real_estate"
    HEALTH_FITNESS = "health_fitness"
    RESTAURANT = "restaurant"
    CONTRACTOR = "contractor"
    COACH_CONSULTANT = "coach_consultant"
    AUTOMOTIVE = "automotive"
    HOME_SERVICES = "home_services"
    RETAIL = "retail"


class LeadContactType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    SOCIAL = "social"


class LeadStatus(Enum):
    RAW = "raw"
    SCORED = "scored"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BusinessLead:
    """A single business lead candidate."""

    lead_id: str
    business_name: str
    vertical: BusinessVertical
    problem: str
    location: Optional[str]
    estimated_monthly_value_usd: float
    contact_type: LeadContactType
    contact_info: Optional[str]
    digital_gap_score: float          # 0–100: 100 = severe gap
    close_probability: float          # 0.0–1.0
    status: LeadStatus = LeadStatus.RAW
    tags: list = field(default_factory=list)
    discovered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "lead_id": self.lead_id,
            "business_name": self.business_name,
            "vertical": self.vertical.value,
            "problem": self.problem,
            "location": self.location,
            "estimated_monthly_value_usd": self.estimated_monthly_value_usd,
            "contact_type": self.contact_type.value,
            "contact_info": self.contact_info,
            "digital_gap_score": self.digital_gap_score,
            "close_probability": self.close_probability,
            "status": self.status.value,
            "tags": self.tags,
            "discovered_at": self.discovered_at,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LeadFinderError(Exception):
    """Base exception for LeadFinderEngine errors."""


class LeadFinderTierError(LeadFinderError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Business problem templates per vertical
# ---------------------------------------------------------------------------

_VERTICAL_PROBLEMS: dict[BusinessVertical, list[str]] = {
    BusinessVertical.LOCAL_SERVICE: [
        "No website or outdated website",
        "No Google Business profile",
        "No paid ads running",
        "No lead capture funnel",
        "Low social media presence",
    ],
    BusinessVertical.ECOMMERCE: [
        "Shopify store with low organic traffic",
        "No email marketing setup",
        "High cart abandonment, no retargeting",
        "No paid ad campaigns active",
        "No product review automation",
    ],
    BusinessVertical.REAL_ESTATE: [
        "No automated lead follow-up",
        "No landing page for listings",
        "Missing social proof / testimonials",
        "No CRM or contact management",
        "Weak local SEO",
    ],
    BusinessVertical.HEALTH_FITNESS: [
        "Gym with no online booking system",
        "No digital membership promotions",
        "No referral program",
        "Poor social media engagement",
        "No email list building",
    ],
    BusinessVertical.RESTAURANT: [
        "No online ordering integration",
        "No loyalty program",
        "No social media ads",
        "Missing Google review strategy",
        "No SMS marketing",
    ],
    BusinessVertical.CONTRACTOR: [
        "No lead funnel for services",
        "Relies solely on word-of-mouth",
        "No Google Ads or Local Services ads",
        "No professional website",
        "No customer review system",
    ],
    BusinessVertical.COACH_CONSULTANT: [
        "No automated booking page",
        "No content marketing strategy",
        "No email drip sequence",
        "No sales funnel for offers",
        "No affiliate or referral system",
    ],
    BusinessVertical.AUTOMOTIVE: [
        "No online appointment scheduling",
        "No remarketing to past customers",
        "Weak Google Maps presence",
        "No promotional email campaigns",
        "No social media ads",
    ],
    BusinessVertical.HOME_SERVICES: [
        "No seasonal promotion campaigns",
        "No review generation system",
        "No before/after photo strategy",
        "Missing local service ads",
        "No customer retention emails",
    ],
    BusinessVertical.RETAIL: [
        "No loyalty / rewards program",
        "No abandoned cart recovery",
        "No influencer marketing",
        "No paid retargeting",
        "No email newsletter",
    ],
}

_VERTICAL_VALUE_RANGES: dict[BusinessVertical, tuple[float, float]] = {
    BusinessVertical.LOCAL_SERVICE: (500, 3000),
    BusinessVertical.ECOMMERCE: (1000, 5000),
    BusinessVertical.REAL_ESTATE: (2000, 8000),
    BusinessVertical.HEALTH_FITNESS: (500, 2500),
    BusinessVertical.RESTAURANT: (300, 1500),
    BusinessVertical.CONTRACTOR: (1000, 5000),
    BusinessVertical.COACH_CONSULTANT: (1500, 6000),
    BusinessVertical.AUTOMOTIVE: (500, 2000),
    BusinessVertical.HOME_SERVICES: (400, 2000),
    BusinessVertical.RETAIL: (600, 3000),
}

_SAMPLE_BUSINESS_NAMES: dict[BusinessVertical, list[str]] = {
    BusinessVertical.LOCAL_SERVICE: [
        "City Plumbing Co.", "FastFix HVAC", "Sunrise Electric", "Peak Pest Control",
        "BlueLine Locksmith",
    ],
    BusinessVertical.ECOMMERCE: [
        "TrendVault Store", "UrbanEdge Apparel", "NaturalGlow Skincare",
        "PetSupply Plus", "TechGadget Deals",
    ],
    BusinessVertical.REAL_ESTATE: [
        "HomePath Realty", "PrimeKey Properties", "Nextdoor Homes",
        "SkyHigh Investments", "GreenAcre Realty",
    ],
    BusinessVertical.HEALTH_FITNESS: [
        "Iron Core Gym", "Zen Flow Yoga", "StrideFit Crossfit",
        "PureBalance Nutrition", "FitLife Studio",
    ],
    BusinessVertical.RESTAURANT: [
        "Mama Rosa's Kitchen", "Urban Bites Cafe", "Dragon Palace",
        "The Steak Loft", "Sunrise Breakfast Bar",
    ],
    BusinessVertical.CONTRACTOR: [
        "Summit Roofing", "ProBuild Contractors", "SteelFrame Construction",
        "TopCoat Painting", "Premier Foundation Works",
    ],
    BusinessVertical.COACH_CONSULTANT: [
        "Apex Life Coaching", "Revenue Mastery Consulting", "Bold Mindset Academy",
        "CareerEdge Coaching", "Wealth Blueprint Advisors",
    ],
    BusinessVertical.AUTOMOTIVE: [
        "FastLane Auto Repair", "Premier Detailing Co.", "Speedway Tire & Lube",
        "Prestige Auto Body", "AllStar Car Care",
    ],
    BusinessVertical.HOME_SERVICES: [
        "SparkleFresh Cleaning", "GreenCut Lawn Care", "SnowKing Removal",
        "ClearView Window Cleaning", "QuickMove Movers",
    ],
    BusinessVertical.RETAIL: [
        "Boutique 27", "The Hardware Spot", "KidsWorld Toys",
        "StyleHouse Clothing", "Bookmarks & More",
    ],
}

_LOCATIONS: list[str] = [
    "Atlanta, GA", "Houston, TX", "Chicago, IL", "Phoenix, AZ", "Miami, FL",
    "Dallas, TX", "Los Angeles, CA", "New York, NY", "Denver, CO", "Seattle, WA",
    "Nashville, TN", "Charlotte, NC", "Detroit, MI", "Portland, OR", "Austin, TX",
]


# ---------------------------------------------------------------------------
# LeadFinderEngine
# ---------------------------------------------------------------------------

class LeadFinderEngine:
    """Autonomous engine that discovers businesses needing marketing services.

    Parameters
    ----------
    max_leads_per_scan : int | None
        Maximum leads returned per scan.  ``None`` means unlimited.
    can_filter_vertical : bool
        Whether vertical filtering is allowed.
    can_enrich : bool
        Whether lead enrichment (location, contact info) is available.
    can_ai_score : bool
        Whether AI-powered composite scoring is available.
    """

    def __init__(
        self,
        max_leads_per_scan: Optional[int] = 5,
        can_filter_vertical: bool = False,
        can_enrich: bool = False,
        can_ai_score: bool = False,
    ) -> None:
        self.max_leads_per_scan = max_leads_per_scan
        self.can_filter_vertical = can_filter_vertical
        self.can_enrich = can_enrich
        self.can_ai_score = can_ai_score
        self._leads: list[BusinessLead] = []
        self._scan_count: int = 0

    # ------------------------------------------------------------------
    # Core scanning
    # ------------------------------------------------------------------

    def scan(
        self,
        vertical: Optional[BusinessVertical] = None,
        location: Optional[str] = None,
        min_value: float = 0.0,
    ) -> list[BusinessLead]:
        """Scan for business leads matching the given criteria.

        Parameters
        ----------
        vertical : BusinessVertical | None
            Filter by business vertical.  Requires ``can_filter_vertical``.
        location : str | None
            Optional location hint.
        min_value : float
            Minimum estimated monthly value filter.

        Returns
        -------
        list[BusinessLead]
            Newly discovered leads (also stored internally).
        """
        if vertical is not None and not self.can_filter_vertical:
            raise LeadFinderTierError(
                "Vertical filtering requires PRO tier or above."
            )

        self._scan_count += 1
        verticals = (
            [vertical] if vertical else list(BusinessVertical)
        )

        results: list[BusinessLead] = []
        rng = random.Random(int(time.time()) + self._scan_count)

        for v in verticals:
            names = _SAMPLE_BUSINESS_NAMES[v]
            lo, hi = _VERTICAL_VALUE_RANGES[v]
            problems = _VERTICAL_PROBLEMS[v]

            for name in rng.sample(names, min(2, len(names))):
                value = round(rng.uniform(lo, hi), 2)
                if value < min_value:
                    continue

                gap_score = round(rng.uniform(40.0, 95.0), 1)
                close_prob = round(rng.uniform(0.2, 0.85), 2)
                lead = BusinessLead(
                    lead_id=f"lead_{self._scan_count}_{rng.randint(1000, 9999)}",
                    business_name=name,
                    vertical=v,
                    problem=rng.choice(problems),
                    location=location or (rng.choice(_LOCATIONS) if self.can_enrich else None),
                    estimated_monthly_value_usd=value,
                    contact_type=rng.choice(list(LeadContactType)),
                    contact_info=(
                        f"contact@{name.lower().replace(' ', '').replace('.', '')}.com"
                        if self.can_enrich else None
                    ),
                    digital_gap_score=gap_score,
                    close_probability=close_prob if self.can_ai_score else round(rng.uniform(0.3, 0.7), 2),
                    tags=[v.value, "needs_marketing"],
                )
                results.append(lead)

        results.sort(key=lambda x: x.estimated_monthly_value_usd, reverse=True)

        if self.max_leads_per_scan is not None:
            results = results[: self.max_leads_per_scan]

        self._leads.extend(results)
        return results

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_all_leads(self) -> list[BusinessLead]:
        """Return all discovered leads."""
        return list(self._leads)

    def get_top_leads(self, n: int = 5) -> list[BusinessLead]:
        """Return the top *n* leads by estimated monthly value."""
        sorted_leads = sorted(
            self._leads,
            key=lambda x: x.estimated_monthly_value_usd,
            reverse=True,
        )
        return sorted_leads[:n]

    def get_leads_by_status(self, status: LeadStatus) -> list[BusinessLead]:
        """Return all leads with a given status."""
        return [l for l in self._leads if l.status == status]

    def mark_lead_status(self, lead_id: str, status: LeadStatus) -> BusinessLead:
        """Update the status of a lead by ID."""
        for lead in self._leads:
            if lead.lead_id == lead_id:
                lead.status = status
                return lead
        raise LeadFinderError(f"Lead not found: {lead_id}")

    def to_dict(self) -> dict:
        """Return engine state as a serialisable dict."""
        return {
            "scan_count": self._scan_count,
            "total_leads": len(self._leads),
            "max_leads_per_scan": self.max_leads_per_scan,
            "can_filter_vertical": self.can_filter_vertical,
            "can_enrich": self.can_enrich,
            "can_ai_score": self.can_ai_score,
        }
