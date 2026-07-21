"""
Public Lead Engine — Legal Public Business Search Bot

Uses public APIs (Google Places API / Yelp Fusion API) to legally discover
businesses, filter them by low star ratings and weak online marketing presence,
and generate commercial opportunities for the DreamCo CineCore™ system.

This bot is the **legal public search mode** of the DreamCo lead engine:
  - Queries only public business directories via their official APIs.
  - Filters for businesses with low ratings (≤ 3.5 stars) or minimal
    online presence — the highest-value commercial targets.
  - Scores each business for ad opportunity.
  - Generates targeted scripts and outreach drafts for human review.
  - Never sends unsolicited messages automatically — human approval required.

Tier-aware:
  FREE       — 50 searches/day, Google Places, rating filter.
  PRO ($39)  — 1,000/day, Yelp + Google, weak-marketing filter, scripts.
  ENTERPRISE ($149) — Unlimited, multi-API, AI scoring, full pipeline.
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.public_lead_engine.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_GOOGLE_PLACES_SEARCH,
    FEATURE_YELP_SEARCH,
    FEATURE_RATING_FILTER,
    FEATURE_WEAK_MARKETING_FILTER,
    FEATURE_AD_SCORE,
    FEATURE_SCRIPT_GENERATION,
    FEATURE_OUTREACH_DRAFT,
    FEATURE_CRM_EXPORT,
    FEATURE_MULTI_API,
    FEATURE_AI_OPPORTUNITY_SCORE,
    FEATURE_BULK_SEARCH,
    FEATURE_ANALYTICS,
)


# ---------------------------------------------------------------------------
# Enums & Data models
# ---------------------------------------------------------------------------

class DataSource(Enum):
    GOOGLE_PLACES = "google_places"
    YELP = "yelp"
    BING_LOCAL = "bing_local"
    FOURSQUARE = "foursquare"


class BusinessCategory(Enum):
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    AUTO_SERVICE = "auto_service"
    HOME_SERVICE = "home_service"
    HEALTH_BEAUTY = "health_beauty"
    FITNESS = "fitness"
    LEGAL = "legal"
    DENTAL = "dental"
    REAL_ESTATE = "real_estate"
    ECOMMERCE = "ecommerce"
    OTHER = "other"


class LeadStatus(Enum):
    RAW = "raw"
    FILTERED = "filtered"
    SCORED = "scored"
    SCRIPT_READY = "script_ready"
    OUTREACH_READY = "outreach_ready"
    EXPORTED = "exported"
    REJECTED = "rejected"


@dataclass
class PublicBusinessLead:
    """
    Represents a publicly discovered business lead from an official API.

    All data in this record was obtained from public, opt-in business listings.
    """
    lead_id: str
    source: DataSource
    name: str
    category: BusinessCategory
    location: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    star_rating: float = 0.0          # From API (e.g. 1.0–5.0)
    review_count: int = 0
    has_website: bool = False
    has_social_media: bool = False
    marketing_weakness_score: float = 50.0  # 0-100; higher = weaker marketing
    ad_opportunity_score: float = 0.0       # 0-100; higher = better opportunity
    status: LeadStatus = LeadStatus.RAW
    generated_script: Optional[str] = None
    outreach_draft: Optional[str] = None
    tags: list = field(default_factory=list)
    found_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PublicLeadEngineError(Exception):
    """Base exception for Public Lead Engine errors."""


class PublicLeadEngineTierError(PublicLeadEngineError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Simulated API helpers (replace with real API clients in production)
# ---------------------------------------------------------------------------

_SAMPLE_BUSINESSES = [
    ("The Corner Diner", BusinessCategory.RESTAURANT),
    ("Quick Cuts Barber Shop", BusinessCategory.HEALTH_BEAUTY),
    ("Valley Auto Repair", BusinessCategory.AUTO_SERVICE),
    ("Sunset Yoga Studio", BusinessCategory.FITNESS),
    ("Park Avenue Dental", BusinessCategory.DENTAL),
    ("Main St. Florist", BusinessCategory.RETAIL),
    ("HomeBase Contractors", BusinessCategory.HOME_SERVICE),
    ("Harbor View Realty", BusinessCategory.REAL_ESTATE),
    ("City Legal Aid", BusinessCategory.LEGAL),
    ("East Side Bakery", BusinessCategory.RESTAURANT),
    ("TechFix Repair Shop", BusinessCategory.RETAIL),
    ("River Run Spa", BusinessCategory.HEALTH_BEAUTY),
    ("Summit Roofing Co.", BusinessCategory.HOME_SERVICE),
    ("Crossfit 247", BusinessCategory.FITNESS),
    ("Coastal Dental Care", BusinessCategory.DENTAL),
]

_SAMPLE_LOCATIONS = [
    "Austin, TX", "Nashville, TN", "Portland, OR",
    "Charlotte, NC", "Las Vegas, NV", "San Diego, CA",
    "Columbus, OH", "Indianapolis, IN", "Jacksonville, FL", "San Antonio, TX",
]


def _simulate_api_search(
    source: DataSource,
    query: str,
    count: int,
    max_rating: Optional[float] = None,
) -> list[dict]:
    """
    Simulate a call to Google Places API or Yelp Fusion API.

    In production, replace this with real HTTP requests:
      - Google Places: https://maps.googleapis.com/maps/api/place/textsearch/json
      - Yelp Fusion:   https://api.yelp.com/v3/businesses/search
    """
    results = []
    for _ in range(count):
        name, category = random.choice(_SAMPLE_BUSINESSES)
        suffix = random.randint(1, 999)
        rating = round(random.uniform(1.5, 5.0), 1)
        review_count = random.randint(0, 500)
        has_website = random.random() > 0.4
        has_social = random.random() > 0.5

        if max_rating is not None and rating > max_rating:
            continue

        results.append({
            "name": f"{name} #{suffix}",
            "category": category,
            "location": random.choice(_SAMPLE_LOCATIONS),
            "address": f"{random.randint(100, 9999)} Main St",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "website": f"https://www.{name.lower().replace(' ', '')}{suffix}.com" if has_website else None,
            "star_rating": rating,
            "review_count": review_count,
            "has_website": has_website,
            "has_social_media": has_social,
            "source": source,
        })
    return results


def _compute_marketing_weakness(business: dict) -> float:
    """
    Compute a marketing weakness score (0–100) based on public signals.

    Higher score = weaker marketing = better commercial opportunity.
    """
    score = 0.0
    if business["star_rating"] <= 2.5:
        score += 35.0
    elif business["star_rating"] <= 3.5:
        score += 20.0
    if business["review_count"] < 10:
        score += 25.0
    elif business["review_count"] < 50:
        score += 10.0
    if not business["has_website"]:
        score += 25.0
    if not business["has_social_media"]:
        score += 15.0
    return min(100.0, round(score + random.uniform(-3, 3), 1))


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class PublicLeadEngine:
    """
    Public Lead Engine — legal business discovery via public APIs.

    Uses Google Places API and Yelp Fusion to find real businesses, then
    filters for those with low ratings and weak marketing — the highest-value
    commercial targets for the DreamCo CineCore™ system.

    All data is sourced from public, opt-in business directories only.
    Outreach messages are generated as *drafts* for human approval before
    sending — this engine is fully compliant with anti-spam regulations.

    Workflow:
        1. search_businesses()          — query Google Places / Yelp API
        2. filter_weak_marketing()      — keep only low-rating / low-presence businesses
        3. score_opportunities()        — rank by ad opportunity (ENTERPRISE)
        4. generate_scripts()           — create targeted commercial scripts (PRO+)
        5. generate_outreach()          — draft pitch messages for human review (PRO+)
        6. export_to_crm()              — push to CRM (PRO+)
    """

    SOURCE_TIERS = {
        Tier.FREE: [DataSource.GOOGLE_PLACES],
        Tier.PRO: [DataSource.GOOGLE_PLACES, DataSource.YELP],
        Tier.ENTERPRISE: list(DataSource),
    }

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._leads: dict[str, PublicBusinessLead] = {}
        self._counter: int = 0
        self._search_log: list = []
        self._crm_exports: list = []

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)." if upgrade else ""
            raise PublicLeadEngineTierError(
                f"Feature '{feature}' is not available on the {self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Business discovery
    # ------------------------------------------------------------------

    def search_businesses(
        self,
        query: str = "local business",
        count: int = 10,
        source: DataSource = DataSource.GOOGLE_PLACES,
        max_rating: Optional[float] = None,
    ) -> dict:
        """
        Search for businesses using public directory APIs.

        Parameters
        ----------
        query : str
            Search query (e.g. "restaurant Austin TX", "plumber near me").
        count : int
            Number of results to fetch (capped by tier daily limit).
        source : DataSource
            Which API to use (Yelp requires PRO+, others require ENTERPRISE).
        max_rating : float, optional
            Only return businesses at or below this star rating (PRO+).
            Useful for targeting businesses most in need of marketing help.
        """
        if source == DataSource.GOOGLE_PLACES:
            self._require(FEATURE_GOOGLE_PLACES_SEARCH)
        elif source == DataSource.YELP:
            self._require(FEATURE_YELP_SEARCH)
        else:
            self._require(FEATURE_MULTI_API)

        if max_rating is not None:
            self._require(FEATURE_RATING_FILTER)

        daily_cap = self._config.max_searches_per_day
        if daily_cap is not None:
            count = min(count, daily_cap)

        raw = _simulate_api_search(source, query, count, max_rating)
        new_leads = []

        for data in raw:
            self._counter += 1
            lead_id = f"pub_lead_{self._counter:08d}"
            lead = PublicBusinessLead(
                lead_id=lead_id,
                source=data["source"],
                name=data["name"],
                category=data["category"],
                location=data["location"],
                address=data.get("address"),
                phone=data.get("phone"),
                website=data.get("website"),
                star_rating=data["star_rating"],
                review_count=data["review_count"],
                has_website=data["has_website"],
                has_social_media=data["has_social_media"],
            )
            self._leads[lead_id] = lead
            new_leads.append(lead_id)

        log_entry = {
            "query": query,
            "source": source.value,
            "requested": count,
            "returned": len(raw),
            "new_leads": len(new_leads),
            "max_rating_filter": max_rating,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._search_log.append(log_entry)

        return {**log_entry, "lead_ids": new_leads}

    def search_all_sources(self, query: str = "local business", leads_per_source: int = 5) -> dict:
        """Search all available sources for this tier (PRO+)."""
        self._require(FEATURE_YELP_SEARCH)
        sources = self.SOURCE_TIERS.get(self.tier, [DataSource.GOOGLE_PLACES])
        results = []
        for source in sources:
            try:
                result = self.search_businesses(query, leads_per_source, source)
                results.append(result)
            except PublicLeadEngineTierError:
                pass
        return {
            "sources_searched": len(results),
            "total_new_leads": sum(r["new_leads"] for r in results),
            "results_by_source": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_weak_marketing(
        self,
        max_rating: float = 3.5,
        min_weakness_score: float = 30.0,
    ) -> dict:
        """
        Filter leads to keep only those with weak marketing signals (PRO+).

        Businesses with low ratings, few reviews, no website, or no social
        presence are the best candidates for commercial outreach.

        Parameters
        ----------
        max_rating : float
            Keep businesses with star rating at or below this value.
        min_weakness_score : float
            Minimum computed marketing weakness score to keep a lead.
        """
        self._require(FEATURE_WEAK_MARKETING_FILTER)
        kept = 0
        rejected = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.RAW:
                continue
            weakness = _compute_marketing_weakness({
                "star_rating": lead.star_rating,
                "review_count": lead.review_count,
                "has_website": lead.has_website,
                "has_social_media": lead.has_social_media,
            })
            lead.marketing_weakness_score = weakness
            if lead.star_rating <= max_rating and weakness >= min_weakness_score:
                lead.status = LeadStatus.FILTERED
                kept += 1
            else:
                lead.status = LeadStatus.REJECTED
                rejected += 1
        return {"kept": kept, "rejected": rejected}

    # ------------------------------------------------------------------
    # Opportunity scoring
    # ------------------------------------------------------------------

    def score_opportunities(self) -> dict:
        """AI-score filtered leads by commercial ad opportunity (ENTERPRISE+)."""
        self._require(FEATURE_AI_OPPORTUNITY_SCORE)
        scored = 0
        for lead in self._leads.values():
            if lead.status not in (LeadStatus.RAW, LeadStatus.FILTERED):
                continue
            score = lead.marketing_weakness_score
            category_bonus = {
                BusinessCategory.RESTAURANT: 15,
                BusinessCategory.REAL_ESTATE: 20,
                BusinessCategory.AUTO_SERVICE: 12,
                BusinessCategory.DENTAL: 18,
                BusinessCategory.HOME_SERVICE: 10,
            }.get(lead.category, 5)
            lead.ad_opportunity_score = min(100.0, round(score + category_bonus + random.uniform(-5, 5), 1))
            lead.status = LeadStatus.SCORED
            scored += 1
        return {"scored": scored}

    # ------------------------------------------------------------------
    # Ad score (PRO)
    # ------------------------------------------------------------------

    def compute_ad_scores(self) -> dict:
        """Compute ad opportunity scores for filtered leads (PRO+)."""
        self._require(FEATURE_AD_SCORE)
        scored = 0
        for lead in self._leads.values():
            if lead.status not in (LeadStatus.RAW, LeadStatus.FILTERED):
                continue
            lead.ad_opportunity_score = min(
                100.0,
                round(lead.marketing_weakness_score + random.uniform(0, 20), 1)
            )
            if lead.status == LeadStatus.RAW:
                lead.status = LeadStatus.FILTERED
            scored += 1
        return {"ad_scores_computed": scored}

    # ------------------------------------------------------------------
    # Script generation
    # ------------------------------------------------------------------

    def generate_scripts(self, top_n: int = 10) -> dict:
        """Generate ad scripts for the highest-opportunity leads (PRO+)."""
        self._require(FEATURE_SCRIPT_GENERATION)
        candidates = sorted(
            [l for l in self._leads.values() if l.status in (LeadStatus.FILTERED, LeadStatus.SCORED)],
            key=lambda l: l.ad_opportunity_score,
            reverse=True,
        )[:top_n]
        generated = 0
        for lead in candidates:
            lead.generated_script = self._build_script(lead)
            lead.status = LeadStatus.SCRIPT_READY
            generated += 1
        return {"scripts_generated": generated}

    def _build_script(self, lead: PublicBusinessLead) -> str:
        cat = lead.category.value.replace("_", " ")
        rating_note = f"Despite a {lead.star_rating}-star rating, " if lead.star_rating < 3.5 else ""
        templates = [
            (
                f"{rating_note}{lead.name} in {lead.location} deserves more customers. "
                f"Our AI commercial will show the world what makes your {cat} business special. "
                f"More customers. More revenue. Guaranteed results."
            ),
            (
                f"Are you a {cat} business in {lead.location} struggling to stand out? "
                f"{lead.name} — it's time the world knew your story. "
                f"We create high-converting commercials that bring real customers through your door."
            ),
            (
                f"Local {cat} businesses like {lead.name} deserve great marketing. "
                f"We craft commercials that convert viewers into loyal customers. "
                f"Serving {lead.location} — let's grow your business together."
            ),
        ]
        return random.choice(templates)

    # ------------------------------------------------------------------
    # Outreach drafts
    # ------------------------------------------------------------------

    def generate_outreach(self) -> dict:
        """
        Generate human-readable outreach drafts for script-ready leads (PRO+).

        IMPORTANT: These drafts require HUMAN REVIEW before sending.
        This engine does NOT send messages automatically to ensure full
        compliance with anti-spam regulations (CAN-SPAM, GDPR, etc.).
        """
        self._require(FEATURE_OUTREACH_DRAFT)
        generated = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.SCRIPT_READY:
                continue
            lead.outreach_draft = self._build_outreach(lead)
            lead.status = LeadStatus.OUTREACH_READY
            generated += 1
        return {
            "outreach_drafts_generated": generated,
            "requires_human_approval": True,
            "compliance_note": (
                "All outreach messages require human review before sending. "
                "Do not send bulk automated messages without consent."
            ),
        }

    def _build_outreach(self, lead: PublicBusinessLead) -> str:
        cat = lead.category.value.replace("_", " ")
        return (
            f"Hi {lead.name},\n\n"
            f"I came across your {cat} business in {lead.location} and wanted to reach out.\n\n"
            f"I've created a free AI commercial concept for your business that could help "
            f"attract more customers and boost your online presence.\n\n"
            f"Would you be interested in seeing it? There's no obligation — I just think "
            f"there's a great opportunity here.\n\n"
            f"Best regards,\nDreamCo CineCore Team\n\n"
            f"[HUMAN REVIEW REQUIRED BEFORE SENDING]"
        )

    # ------------------------------------------------------------------
    # Bulk search (ENTERPRISE)
    # ------------------------------------------------------------------

    def bulk_search(self, queries: list[str], leads_per_query: int = 10) -> dict:
        """Run multiple searches across all available sources (ENTERPRISE+)."""
        self._require(FEATURE_BULK_SEARCH)
        total_new = 0
        results = []
        for query in queries:
            result = self.search_businesses(query, leads_per_query)
            total_new += result["new_leads"]
            results.append(result)
        return {
            "queries_run": len(queries),
            "total_new_leads": total_new,
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # CRM export
    # ------------------------------------------------------------------

    def export_to_crm(self, crm_name: str = "default") -> dict:
        """Export outreach-ready leads to a CRM system (PRO+)."""
        self._require(FEATURE_CRM_EXPORT)
        exportable = [
            l for l in self._leads.values()
            if l.status in (LeadStatus.SCRIPT_READY, LeadStatus.OUTREACH_READY)
        ]
        for lead in exportable:
            lead.status = LeadStatus.EXPORTED
        entry = {
            "crm": crm_name,
            "leads_exported": len(exportable),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._crm_exports.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_leads(
        self,
        status: Optional[LeadStatus] = None,
        category: Optional[BusinessCategory] = None,
        limit: int = 50,
    ) -> list:
        """Return leads filtered by status and/or category."""
        leads = list(self._leads.values())
        if status:
            leads = [l for l in leads if l.status == status]
        if category:
            leads = [l for l in leads if l.category == category]
        return [_lead_to_dict(l) for l in leads[:limit]]

    def get_top_opportunities(self, n: int = 10) -> list:
        """Return top N leads by ad opportunity score."""
        ranked = sorted(self._leads.values(), key=lambda l: l.ad_opportunity_score, reverse=True)
        return [_lead_to_dict(l) for l in ranked[:n]]

    def get_low_rated_businesses(self, max_rating: float = 3.5) -> list:
        """Return all businesses at or below the specified star rating."""
        leads = [l for l in self._leads.values() if l.star_rating <= max_rating]
        leads.sort(key=lambda l: l.star_rating)
        return [_lead_to_dict(l) for l in leads]

    def get_summary(self) -> dict:
        """Return overall engine statistics."""
        leads = list(self._leads.values())
        by_status: dict[str, int] = {}
        by_source: dict[str, int] = {}
        by_category: dict[str, int] = {}
        for l in leads:
            by_status[l.status.value] = by_status.get(l.status.value, 0) + 1
            by_source[l.source.value] = by_source.get(l.source.value, 0) + 1
            by_category[l.category.value] = by_category.get(l.category.value, 0) + 1
        ratings = [l.star_rating for l in leads]
        return {
            "total_leads": len(leads),
            "by_status": by_status,
            "by_source": by_source,
            "by_category": by_category,
            "avg_star_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "total_searches": len(self._search_log),
            "total_crm_exports": sum(e["leads_exported"] for e in self._crm_exports),
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_analytics(self) -> dict:
        """Return extended analytics report (ENTERPRISE+)."""
        self._require(FEATURE_ANALYTICS)
        summary = self.get_summary()
        top = self.get_top_opportunities(5)
        return {
            **summary,
            "top_5_opportunities": top,
            "search_log": list(self._search_log),
            "crm_export_log": list(self._crm_exports),
        }

    # ------------------------------------------------------------------
    # Chat / GLOBAL AI SOURCES FLOW interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language interface for BuddyAI routing."""
        msg = message.lower()
        if "search" in msg or "find" in msg or "scan" in msg:
            result = self.search_businesses(query="local business", count=10)
            return {"message": f"Found {result['new_leads']} businesses via {result['source']}.", "data": result}
        if "filter" in msg or "weak" in msg or "low rating" in msg:
            result = self.filter_weak_marketing()
            return {"message": f"Filtered leads: {result['kept']} kept, {result['rejected']} rejected.", "data": result}
        if "script" in msg or "commercial" in msg:
            result = self.generate_scripts()
            return {"message": f"Generated {result['scripts_generated']} ad scripts.", "data": result}
        if "outreach" in msg or "pitch" in msg:
            result = self.generate_outreach()
            return {"message": f"Drafted {result['outreach_drafts_generated']} outreach messages (awaiting human approval).", "data": result}
        if "top" in msg or "best" in msg or "opportunity" in msg:
            return {"message": "Top business opportunities.", "data": self.get_top_opportunities()}
        if "summary" in msg or "stats" in msg or "status" in msg:
            return {"message": "Public Lead Engine summary.", "data": self.get_summary()}
        return {
            "message": (
                "Public Lead Engine online (legal mode). "
                f"Tier: {self.tier.value}. "
                "Commands: 'search businesses', 'filter weak marketing', 'generate scripts', "
                "'generate outreach', 'top opportunities', 'summary'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lead_to_dict(lead: PublicBusinessLead) -> dict:
    return {
        "lead_id": lead.lead_id,
        "source": lead.source.value,
        "name": lead.name,
        "category": lead.category.value,
        "location": lead.location,
        "address": lead.address,
        "phone": lead.phone,
        "website": lead.website,
        "star_rating": lead.star_rating,
        "review_count": lead.review_count,
        "has_website": lead.has_website,
        "has_social_media": lead.has_social_media,
        "marketing_weakness_score": lead.marketing_weakness_score,
        "ad_opportunity_score": lead.ad_opportunity_score,
        "status": lead.status.value,
        "generated_script": lead.generated_script,
        "outreach_draft": lead.outreach_draft,
        "tags": lead.tags,
        "found_at": lead.found_at,
    }


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Standalone entry point for the Public Lead Engine bot."""
    import json
    print("=== Public Lead Engine Bot ===")
    print("DreamCo CineCore™ — Legal Public Business Search Mode\n")

    engine = PublicLeadEngine(tier=Tier.PRO)

    print("Step 1: Searching businesses via Google Places API...")
    search = engine.search_businesses(query="restaurant near me", count=8, max_rating=4.0)
    print(f"  Found {search['new_leads']} leads (rating ≤ 4.0)\n")

    print("Step 2: Searching via Yelp API...")
    yelp_search = engine.search_businesses(
        query="local service", count=5, source=DataSource.YELP, max_rating=3.5
    )
    print(f"  Found {yelp_search['new_leads']} Yelp leads (rating ≤ 3.5)\n")

    print("Step 3: Filtering for weak marketing presence...")
    filtered = engine.filter_weak_marketing(max_rating=3.5, min_weakness_score=25.0)
    print(f"  Kept {filtered['kept']} high-opportunity leads\n")

    print("Step 4: Computing ad opportunity scores...")
    scored = engine.compute_ad_scores()
    print(f"  Scored {scored['ad_scores_computed']} leads\n")

    print("Step 5: Generating targeted ad scripts...")
    scripts = engine.generate_scripts(top_n=5)
    print(f"  Generated {scripts['scripts_generated']} scripts\n")

    print("Step 6: Drafting outreach messages (human approval required)...")
    outreach = engine.generate_outreach()
    print(f"  Drafted {outreach['outreach_drafts_generated']} messages\n")

    print("Summary:")
    summary = engine.get_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
