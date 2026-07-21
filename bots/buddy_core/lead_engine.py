"""
Lead Engine for the Buddy Core System.

Simulates lead scraping, scoring, and monetisation — no real network calls.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class LeadEngineError(Exception):
    """Raised when the lead engine encounters an error."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LeadSource(Enum):
    LINKEDIN = "linkedin"
    GOOGLE_BUSINESS = "google_business"
    YELP = "yelp"
    TWITTER = "twitter"
    REDDIT = "reddit"
    DIRECT = "direct"


class LeadStatus(Enum):
    RAW = "raw"
    VALIDATED = "validated"
    SCORED = "scored"
    SOLD = "sold"
    SUBSCRIBED = "subscribed"


class LeadTier(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class MonetizationStrategy(Enum):
    LEAD_SALE = "lead_sale"
    SUBSCRIPTION = "subscription"
    AFFILIATE = "affiliate"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Lead:
    lead_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    industry: Optional[str]
    source: LeadSource
    status: LeadStatus
    quality_score: float
    tier: LeadTier
    tags: list
    scraped_at: datetime
    metadata: dict = field(default_factory=dict)


@dataclass
class Revenue:
    revenue_id: str
    lead_id: str
    strategy: MonetizationStrategy
    amount_usd: float
    created_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

_FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry",
    "Iris", "Jack", "Karen", "Leo", "Maria", "Nick", "Olivia", "Paul",
    "Quinn", "Rachel", "Steve", "Tina",
]
_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson",
    "White", "Harris", "Martin", "Thompson", "Walker", "Young",
]
_COMPANIES = [
    "Apex Realty", "BlueWave Finance", "CloudNine Marketing",
    "Delta Logistics", "Echo Health", "FreeFlow Freelance",
    "GreenPath Consulting", "HorizonTech", "InnoVentures", "JetSet Travel",
]
_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "company.io", "biz.net"]


def _fake_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _fake_email(name: str) -> str:
    parts = name.lower().split()
    return f"{parts[0]}.{parts[1]}@{random.choice(_DOMAINS)}"


def _fake_phone() -> str:
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"


def _fake_company() -> str:
    return random.choice(_COMPANIES)


# ---------------------------------------------------------------------------
# Lead Scraper
# ---------------------------------------------------------------------------

class LeadScraper:
    """Generates synthetic leads (no real network calls)."""

    def scrape(
        self,
        source: LeadSource,
        industry: str = "",
        count: int = 10,
    ) -> list[Lead]:
        if count < 1:
            raise LeadEngineError("count must be >= 1")
        leads: list[Lead] = []
        for _ in range(count):
            name = _fake_name()
            lead = Lead(
                lead_id=str(uuid.uuid4()),
                name=name,
                email=_fake_email(name) if random.random() > 0.1 else None,
                phone=_fake_phone() if random.random() > 0.3 else None,
                company=_fake_company() if random.random() > 0.2 else None,
                industry=industry or "general",
                source=source,
                status=LeadStatus.RAW,
                quality_score=0.0,
                tier=LeadTier.COLD,
                tags=[source.value, industry] if industry else [source.value],
                scraped_at=datetime.utcnow(),
            )
            leads.append(lead)
        return leads

    def validate(self, lead: Lead) -> Lead:
        """Mark lead as validated if it has at least an email or phone."""
        if lead.email or lead.phone:
            lead.status = LeadStatus.VALIDATED
        return lead

    def enrich(self, lead: Lead) -> Lead:
        """Add supplementary metadata."""
        lead.metadata["enriched"] = True
        lead.metadata["source_platform"] = lead.source.value
        if not lead.company:
            lead.company = _fake_company()
        return lead


# ---------------------------------------------------------------------------
# Lead Scorer
# ---------------------------------------------------------------------------

class LeadScorer:
    """Scores and tiers leads based on data completeness and signals."""

    def score(self, lead: Lead) -> Lead:
        score = 0.0
        if lead.email:
            score += 30.0
        if lead.phone:
            score += 20.0
        if lead.company:
            score += 20.0
        if lead.status == LeadStatus.VALIDATED:
            score += 15.0
        if lead.metadata.get("enriched"):
            score += 15.0
        # Normalise to 0–1
        lead.quality_score = round(min(score / 100.0, 1.0), 4)
        if lead.quality_score >= 0.7:
            lead.tier = LeadTier.HOT
        elif lead.quality_score >= 0.4:
            lead.tier = LeadTier.WARM
        else:
            lead.tier = LeadTier.COLD
        lead.status = LeadStatus.SCORED
        return lead

    def rank(self, leads: list[Lead]) -> list[Lead]:
        return sorted(leads, key=lambda l: l.quality_score, reverse=True)

    def get_hot_leads(self, leads: list[Lead]) -> list[Lead]:
        return [l for l in leads if l.tier == LeadTier.HOT]


# ---------------------------------------------------------------------------
# Monetization Engine
# ---------------------------------------------------------------------------

class MonetizationEngine:
    """Sells leads, manages subscriptions, and tracks affiliate revenue."""

    def __init__(self) -> None:
        self._revenues: list[Revenue] = []
        self._subscriptions: list[dict] = []

    def sell_lead(self, lead: Lead, price_usd: float) -> Revenue:
        if price_usd <= 0:
            raise LeadEngineError("price_usd must be positive.")
        rev = Revenue(
            revenue_id=str(uuid.uuid4()),
            lead_id=lead.lead_id,
            strategy=MonetizationStrategy.LEAD_SALE,
            amount_usd=price_usd,
        )
        lead.status = LeadStatus.SOLD
        self._revenues.append(rev)
        return rev

    def create_subscription(
        self, user_id: str, plan: str, amount_usd: float
    ) -> dict:
        sub = {
            "subscription_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan": plan,
            "amount_usd": amount_usd,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        rev = Revenue(
            revenue_id=str(uuid.uuid4()),
            lead_id="subscription",
            strategy=MonetizationStrategy.SUBSCRIPTION,
            amount_usd=amount_usd,
        )
        self._subscriptions.append(sub)
        self._revenues.append(rev)
        return sub

    def add_affiliate_revenue(self, source: str, amount_usd: float) -> Revenue:
        rev = Revenue(
            revenue_id=str(uuid.uuid4()),
            lead_id=f"affiliate:{source}",
            strategy=MonetizationStrategy.AFFILIATE,
            amount_usd=amount_usd,
        )
        self._revenues.append(rev)
        return rev

    def get_total_revenue(self) -> float:
        return sum(r.amount_usd for r in self._revenues)

    def get_summary(self) -> dict:
        by_strategy: dict[str, float] = {s.value: 0.0 for s in MonetizationStrategy}
        for r in self._revenues:
            by_strategy[r.strategy.value] += r.amount_usd
        return {
            "total_revenue": self.get_total_revenue(),
            "total_transactions": len(self._revenues),
            "subscriptions": len(self._subscriptions),
            "by_strategy": by_strategy,
        }


# ---------------------------------------------------------------------------
# LeadEngine (facade)
# ---------------------------------------------------------------------------

class LeadEngine:
    """Composes LeadScraper, LeadScorer, and MonetizationEngine."""

    def __init__(self) -> None:
        self.scraper = LeadScraper()
        self.scorer = LeadScorer()
        self.monetization = MonetizationEngine()
        self._campaigns: list[dict] = []

    def run_campaign(
        self,
        industry: str,
        source: LeadSource,
        count: int = 20,
    ) -> dict:
        """Scrape, validate, enrich, score, and summarise a lead campaign."""
        raw = self.scraper.scrape(source, industry, count)
        validated = [self.scraper.validate(l) for l in raw]
        enriched = [self.scraper.enrich(l) for l in validated]
        scored = [self.scorer.score(l) for l in enriched]
        ranked = self.scorer.rank(scored)
        hot = self.scorer.get_hot_leads(ranked)

        campaign = {
            "campaign_id": str(uuid.uuid4()),
            "industry": industry,
            "source": source.value,
            "total_leads": len(ranked),
            "hot_leads": len(hot),
            "warm_leads": sum(1 for l in ranked if l.tier == LeadTier.WARM),
            "cold_leads": sum(1 for l in ranked if l.tier == LeadTier.COLD),
            "avg_quality_score": round(
                sum(l.quality_score for l in ranked) / len(ranked), 4
            ) if ranked else 0.0,
            "leads": [
                {
                    "lead_id": l.lead_id,
                    "name": l.name,
                    "tier": l.tier.value,
                    "score": l.quality_score,
                }
                for l in ranked[:10]
            ],
        }
        self._campaigns.append(campaign)
        return campaign

    def get_stats(self) -> dict:
        return {
            "total_campaigns": len(self._campaigns),
            "monetization": self.monetization.get_summary(),
        }
