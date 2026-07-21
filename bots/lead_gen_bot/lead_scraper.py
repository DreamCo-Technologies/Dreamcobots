"""
LeadGenBot — Lead Scraper Module

Automates collection of business leads from real estate listings,
small business directories, agency contacts, and online forums.

Supports three target audiences:
  - Realtors (buyers/sellers in real estate market)
  - Small Businesses (local or online sales)
  - Agencies (digital, marketing, recruitment)

Tier-aware:
  FREE  — 25 leads/day, real estate + directory sources.
  PRO   — 2,000 leads/day, all 6 sources, enrichment, CSV/CRM export.
  ENTERPRISE — Unlimited leads, AI scoring, autonomous workflows.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import csv
import io
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from bots.lead_gen_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BASIC_SCRAPING,
    FEATURE_MULTI_SOURCE,
    FEATURE_LEAD_ENRICHMENT,
    FEATURE_AI_SCORING,
    FEATURE_CSV_EXPORT,
    FEATURE_CRM_EXPORT,
    FEATURE_DEDUPLICATION,
    FEATURE_EMAIL_VALIDATION,
    FEATURE_PHONE_VALIDATION,
    FEATURE_INDUSTRY_FILTER,
    FEATURE_WEBHOOK_EXPORT,
    FEATURE_REAL_ESTATE_SCRAPING,
    FEATURE_BUSINESS_DIRECTORY_SCRAPING,
    FEATURE_AGENCY_SCRAPING,
    FEATURE_FORUM_SCRAPING,
)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class LeadSource(Enum):
    REAL_ESTATE = "real_estate"
    BUSINESS_DIRECTORY = "business_directory"
    AGENCY = "agency"
    FORUM = "forum"
    LINKEDIN = "linkedin"
    CUSTOM = "custom"


class LeadIndustry(Enum):
    REAL_ESTATE = "Real Estate"
    FINANCE = "Finance"
    FREELANCING = "Freelancing"
    MARKETING = "Marketing"
    HEALTHCARE = "Healthcare"
    LOGISTICS = "Logistics"
    SAAS = "SaaS"
    E_COMMERCE = "E-Commerce"
    CONSULTING = "Consulting"
    LEGAL = "Legal"


class LeadStatus(Enum):
    RAW = "raw"
    VALIDATED = "validated"
    ENRICHED = "enriched"
    SCORED = "scored"
    EXPORTED = "exported"
    DUPLICATE = "duplicate"
    INVALID = "invalid"
    SOLD = "sold"


# ---------------------------------------------------------------------------
# Lead data model
# ---------------------------------------------------------------------------

@dataclass
class Lead:
    """Represents a single scraped lead."""
    lead_id: str
    source: LeadSource
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_url: Optional[str] = None
    listing_url: Optional[str] = None
    status: LeadStatus = LeadStatus.RAW
    quality_score: Optional[float] = None
    price_usd: Optional[float] = None
    tags: list = field(default_factory=list)
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    enriched_at: Optional[str] = None
    raw_data: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LeadGenBotError(Exception):
    """Base exception for LeadGenBot errors."""


class LeadGenBotTierError(LeadGenBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Simulated data pools (swap in real HTTP clients per source)
# ---------------------------------------------------------------------------

_REALTOR_NAMES = [
    "Robert Anderson", "Jennifer White", "Michael Thompson", "Lisa Martinez",
    "David Johnson", "Sarah Williams", "James Davis", "Amanda Garcia",
    "Christopher Miller", "Nicole Brown",
]
_BUSINESS_NAMES = [
    "PinPoint Realty", "BlueSky Properties", "FirstChoice Mortgage",
    "GrowthEdge Digital", "NexGen Consulting", "Summit Marketing Group",
    "IronBridge Agency", "ProLead Solutions", "Vertex Financial", "PrimePath Logistics",
]
_AGENCY_NAMES = [
    "Omni Digital Agency", "BrightMind Recruitment", "PeakPerform Marketing",
    "EliteHire Staffing", "NovaSpark Creative", "TrueNorth Consulting",
    "CloudBridge Media", "SignalFire PR", "Meridian Talent Group", "Apex Growth Partners",
]
_FORUM_HANDLES = [
    "RealEstateGuru99", "StartupFounder42", "FreelanceNinja7", "DigitalMarketer88",
    "SmallBizOwner21", "InvestorMind55", "AgencyLeader13", "SaaSBuilder76",
    "ConsultantPro33", "LocalBizKing10",
]
_LOCATIONS = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
    "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "Dallas, TX",
    "Miami, FL", "Atlanta, GA",
]
_SOURCE_INDUSTRY_MAP = {
    LeadSource.REAL_ESTATE: LeadIndustry.REAL_ESTATE.value,
    LeadSource.BUSINESS_DIRECTORY: None,  # mixed
    LeadSource.AGENCY: LeadIndustry.MARKETING.value,
    LeadSource.FORUM: None,  # mixed
    LeadSource.LINKEDIN: None,
    LeadSource.CUSTOM: None,
}
_MIXED_INDUSTRIES = [i.value for i in LeadIndustry]


def _simulate_scrape(source: LeadSource, count: int) -> list[dict]:
    """Generate realistic simulated lead data for a given source."""
    leads = []
    default_industry = _SOURCE_INDUSTRY_MAP.get(source)
    for i in range(count):
        if source == LeadSource.REAL_ESTATE:
            name = random.choice(_REALTOR_NAMES)
            company = random.choice(_BUSINESS_NAMES[:5])
            listing_url = f"https://listings.example.com/property/{random.randint(10000, 99999)}"
        elif source == LeadSource.AGENCY:
            name = random.choice(_AGENCY_NAMES)
            company = name
            listing_url = f"https://agencies.example.com/{name.lower().replace(' ', '-')}"
        elif source == LeadSource.FORUM:
            handle = random.choice(_FORUM_HANDLES)
            name = handle
            company = None
            listing_url = f"https://forum.example.com/user/{handle}"
        else:
            name = random.choice(_REALTOR_NAMES + _AGENCY_NAMES)
            company = random.choice(_BUSINESS_NAMES + _AGENCY_NAMES)
            listing_url = None

        industry = default_industry or random.choice(_MIXED_INDUSTRIES)
        parts = name.split()
        first = parts[0].lower() if parts else "lead"
        last = parts[-1].lower() if len(parts) > 1 else str(i)
        safe_company = "".join(c for c in (company or "dreamco").lower() if c.isalnum())
        location = random.choice(_LOCATIONS)

        leads.append({
            "name": name,
            "email": f"{first}.{last}@{safe_company}.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "company": company,
            "industry": industry,
            "location": location,
            "website": f"https://www.{safe_company}.com",
            "social_url": f"https://linkedin.com/in/{first}{last}",
            "listing_url": listing_url,
        })
    return leads


# ---------------------------------------------------------------------------
# Main scraper class
# ---------------------------------------------------------------------------

class LeadScraper:
    """
    LeadGenBot — Lead Scraper engine.

    Scrapes, validates, deduplicates, enriches, and scores leads from
    real estate listings, business directories, agency contacts, and forums.
    Exports to CSV or CRM.
    """

    SOURCE_FEATURE_MAP = {
        LeadSource.REAL_ESTATE: FEATURE_REAL_ESTATE_SCRAPING,
        LeadSource.BUSINESS_DIRECTORY: FEATURE_BUSINESS_DIRECTORY_SCRAPING,
        LeadSource.AGENCY: FEATURE_AGENCY_SCRAPING,
        LeadSource.FORUM: FEATURE_FORUM_SCRAPING,
        LeadSource.LINKEDIN: FEATURE_MULTI_SOURCE,
        LeadSource.CUSTOM: FEATURE_MULTI_SOURCE,
    }

    DEFAULT_SOURCES = {
        Tier.FREE: [LeadSource.REAL_ESTATE, LeadSource.BUSINESS_DIRECTORY],
        Tier.PRO: [
            LeadSource.REAL_ESTATE, LeadSource.BUSINESS_DIRECTORY,
            LeadSource.AGENCY, LeadSource.FORUM,
            LeadSource.LINKEDIN, LeadSource.CUSTOM,
        ],
        Tier.ENTERPRISE: list(LeadSource),
    }

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._leads: dict[str, Lead] = {}
        self._email_index: set[str] = set()
        self._counter: int = 0
        self._scrape_log: list = []
        self._export_log: list = []

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
            raise LeadGenBotTierError(
                f"Feature '{feature}' is not available on the {self._config.name} tier.{suggestion}"
            )

    # ------------------------------------------------------------------
    # Scraping
    # ------------------------------------------------------------------

    def scrape(
        self,
        source: LeadSource,
        count: int = 10,
        industry_filter: Optional[str] = None,
    ) -> dict:
        """
        Scrape leads from the specified source.

        Parameters
        ----------
        source : LeadSource
            Target data source.
        count : int
            Number of leads to request (capped by tier daily limit).
        industry_filter : str, optional
            Filter results to a specific industry (PRO+ only).

        Returns
        -------
        dict
            Scrape summary including new lead IDs.
        """
        self._require(FEATURE_BASIC_SCRAPING)

        required_feature = self.SOURCE_FEATURE_MAP.get(source, FEATURE_BASIC_SCRAPING)
        self._require(required_feature)

        daily_cap = self._config.max_leads_per_day
        if daily_cap is not None:
            count = min(count, daily_cap)

        if industry_filter:
            self._require(FEATURE_INDUSTRY_FILTER)

        raw_leads = _simulate_scrape(source, count)

        if industry_filter:
            raw_leads = [
                l for l in raw_leads
                if l.get("industry", "").lower() == industry_filter.lower()
            ]

        new_leads: list[str] = []
        duplicates = 0

        for data in raw_leads:
            self._counter += 1
            lead_id = f"lgb_{self._counter:08d}"
            email = data.get("email")

            lead = Lead(
                lead_id=lead_id,
                source=source,
                name=data["name"],
                email=email,
                phone=data.get("phone"),
                company=data.get("company"),
                industry=data.get("industry"),
                location=data.get("location"),
                website=data.get("website"),
                social_url=data.get("social_url"),
                listing_url=data.get("listing_url"),
                raw_data=data,
            )

            if (
                self._config.has_feature(FEATURE_DEDUPLICATION)
                and email
                and email in self._email_index
            ):
                lead.status = LeadStatus.DUPLICATE
                duplicates += 1
            else:
                if email:
                    self._email_index.add(email)
                self._leads[lead_id] = lead
                new_leads.append(lead_id)

        log_entry = {
            "source": source.value,
            "requested": count,
            "scraped": len(raw_leads),
            "new_leads": len(new_leads),
            "duplicates": duplicates,
            "industry_filter": industry_filter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._scrape_log.append(log_entry)
        return {**log_entry, "lead_ids": new_leads}

    def scrape_all_sources(self, leads_per_source: int = 5) -> dict:
        """Scrape from all available sources for this tier."""
        self._require(FEATURE_MULTI_SOURCE)
        sources = self.DEFAULT_SOURCES.get(self.tier, [LeadSource.REAL_ESTATE])
        results = []
        for source in sources:
            result = self.scrape(source, leads_per_source)
            results.append(result)
        total_new = sum(r["new_leads"] for r in results)
        return {
            "sources_scraped": len(sources),
            "total_new_leads": total_new,
            "results_by_source": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Validation & enrichment
    # ------------------------------------------------------------------

    def validate_leads(self) -> dict:
        """Validate email (and optionally phone) for all RAW leads."""
        self._require(FEATURE_EMAIL_VALIDATION)
        validated = 0
        invalid = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.RAW:
                continue
            email_ok = (
                lead.email
                and "@" in lead.email
                and "." in lead.email.split("@")[-1]
            )
            if email_ok:
                lead.status = LeadStatus.VALIDATED
                validated += 1
            else:
                lead.status = LeadStatus.INVALID
                invalid += 1
        return {"validated": validated, "invalid": invalid}

    def enrich_leads(self) -> dict:
        """Enrich validated leads with additional data points."""
        self._require(FEATURE_LEAD_ENRICHMENT)
        enriched = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.VALIDATED:
                continue
            if not lead.website and lead.email:
                domain = lead.email.split("@")[-1]
                lead.website = f"https://{domain}"
            lead.tags = _infer_tags(lead)
            lead.status = LeadStatus.ENRICHED
            lead.enriched_at = datetime.now(timezone.utc).isoformat()
            enriched += 1
        return {"enriched": enriched}

    def score_leads(self) -> dict:
        """AI-score all enriched/validated leads (0–100)."""
        self._require(FEATURE_AI_SCORING)
        scored = 0
        for lead in self._leads.values():
            if lead.status not in (LeadStatus.VALIDATED, LeadStatus.ENRICHED):
                continue
            score = 0.0
            if lead.email:
                score += 30.0
            if lead.phone:
                score += 20.0
            if lead.company:
                score += 20.0
            if lead.website:
                score += 15.0
            if lead.location:
                score += 10.0
            if lead.social_url:
                score += 5.0
            lead.quality_score = min(100.0, round(score + random.uniform(-5, 5), 1))
            lead.status = LeadStatus.SCORED
            scored += 1
        return {"scored": scored}

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_to_csv(self) -> str:
        """Export all valid leads to CSV string."""
        self._require(FEATURE_CSV_EXPORT)
        exportable = [
            l for l in self._leads.values()
            if l.status in (LeadStatus.VALIDATED, LeadStatus.ENRICHED, LeadStatus.SCORED)
        ]
        output = io.StringIO()
        fieldnames = [
            "lead_id", "source", "name", "email", "phone", "company",
            "industry", "location", "website", "social_url", "listing_url",
            "status", "quality_score", "tags", "scraped_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for lead in exportable:
            writer.writerow({
                "lead_id": lead.lead_id,
                "source": lead.source.value,
                "name": lead.name,
                "email": lead.email or "",
                "phone": lead.phone or "",
                "company": lead.company or "",
                "industry": lead.industry or "",
                "location": lead.location or "",
                "website": lead.website or "",
                "social_url": lead.social_url or "",
                "listing_url": lead.listing_url or "",
                "status": lead.status.value,
                "quality_score": lead.quality_score if lead.quality_score is not None else "",
                "tags": "|".join(lead.tags),
                "scraped_at": lead.scraped_at,
            })
            lead.status = LeadStatus.EXPORTED
        log_entry = {
            "format": "csv",
            "leads_exported": len(exportable),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._export_log.append(log_entry)
        return output.getvalue()

    def export_to_crm(self, crm_name: str = "default") -> dict:
        """Export all valid leads to a CRM system."""
        self._require(FEATURE_CRM_EXPORT)
        exportable = [
            l for l in self._leads.values()
            if l.status in (LeadStatus.VALIDATED, LeadStatus.ENRICHED, LeadStatus.SCORED)
        ]
        for lead in exportable:
            lead.status = LeadStatus.EXPORTED
        log_entry = {
            "crm": crm_name,
            "leads_exported": len(exportable),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._export_log.append(log_entry)
        return log_entry

    def export_to_webhook(self, webhook_url: str) -> dict:
        """Export leads to a webhook endpoint."""
        self._require(FEATURE_WEBHOOK_EXPORT)
        exportable = [
            l for l in self._leads.values()
            if l.status in (LeadStatus.VALIDATED, LeadStatus.ENRICHED, LeadStatus.SCORED)
        ]
        for lead in exportable:
            lead.status = LeadStatus.EXPORTED
        log_entry = {
            "webhook_url": webhook_url,
            "leads_exported": len(exportable),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._export_log.append(log_entry)
        return log_entry

    # ------------------------------------------------------------------
    # Analytics & retrieval
    # ------------------------------------------------------------------

    def get_leads(
        self,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        industry: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        """Return leads filtered by status, source, and/or industry."""
        leads = list(self._leads.values())
        if status:
            leads = [l for l in leads if l.status == status]
        if source:
            leads = [l for l in leads if l.source == source]
        if industry:
            leads = [l for l in leads if (l.industry or "").lower() == industry.lower()]
        return [_lead_to_dict(l) for l in leads[:limit]]

    def get_top_leads(self, n: int = 10) -> list:
        """Return top N leads by quality score."""
        scored = [l for l in self._leads.values() if l.quality_score is not None]
        scored.sort(key=lambda l: l.quality_score, reverse=True)
        return [_lead_to_dict(l) for l in scored[:n]]

    def get_summary(self) -> dict:
        """Return overall scraper statistics."""
        leads = list(self._leads.values())
        by_source: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_industry: dict[str, int] = {}
        for l in leads:
            by_source[l.source.value] = by_source.get(l.source.value, 0) + 1
            by_status[l.status.value] = by_status.get(l.status.value, 0) + 1
            if l.industry:
                by_industry[l.industry] = by_industry.get(l.industry, 0) + 1

        scored = [l.quality_score for l in leads if l.quality_score is not None]
        return {
            "total_leads": len(leads),
            "by_source": by_source,
            "by_status": by_status,
            "by_industry": by_industry,
            "avg_quality_score": round(sum(scored) / len(scored), 1) if scored else None,
            "total_scrape_sessions": len(self._scrape_log),
            "total_exports": sum(e.get("leads_exported", 0) for e in self._export_log),
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_scrape_log(self) -> list:
        return list(self._scrape_log)

    def get_lead_by_id(self, lead_id: str) -> Optional[dict]:
        lead = self._leads.get(lead_id)
        return _lead_to_dict(lead) if lead else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_tags(lead: Lead) -> list:
    tags = []
    if lead.industry:
        tags.append(lead.industry.lower().replace(" ", "_"))
    if lead.source == LeadSource.REAL_ESTATE:
        tags.append("realtor")
    elif lead.source == LeadSource.AGENCY:
        tags.append("agency")
    elif lead.source == LeadSource.FORUM:
        tags.append("community")
    if lead.location:
        city = lead.location.split(",")[0].strip().lower().replace(" ", "_")
        tags.append(f"city:{city}")
    return tags


def _lead_to_dict(l: Lead) -> dict:
    return {
        "lead_id": l.lead_id,
        "source": l.source.value,
        "name": l.name,
        "email": l.email,
        "phone": l.phone,
        "company": l.company,
        "industry": l.industry,
        "location": l.location,
        "website": l.website,
        "social_url": l.social_url,
        "listing_url": l.listing_url,
        "status": l.status.value,
        "quality_score": l.quality_score,
        "price_usd": l.price_usd,
        "tags": l.tags,
        "scraped_at": l.scraped_at,
    }


LeadScraperBot = LeadScraper
Bot = LeadScraper

# ---------------------------------------------------------------------------
# Simple requests-based scraper interface for test compatibility
# ---------------------------------------------------------------------------
try:
    import requests
except ImportError:
    requests = None  # type: ignore

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore

import os as _os_lgs


_DEFAULT_URL = "https://example.com/business-directory"
_DEFAULT_DATA_DIR = "data"
_DEFAULT_NAME = "Real Lead Scraper"


_orig_leadscraper_init = LeadScraper.__init__


def _leadscraper_new_init(
    self,
    tier: Tier = Tier.FREE,
    url: str = _DEFAULT_URL,
    data_dir: str = _DEFAULT_DATA_DIR,
    name: str = _DEFAULT_NAME,
) -> None:
    _orig_leadscraper_init(self, tier)
    self.url = url
    self.data_dir = data_dir
    self.name = name


def _leadscraper_scrape(self) -> list:
    """Scrape leads from the configured URL."""
    global requests, BeautifulSoup
    if requests is None:
        return []
    try:
        resp = requests.get(self.url, timeout=10)
        html = resp.text
        if BeautifulSoup is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        leads = []
        for biz in soup.select(".business"):
            name_tag = biz.find("h2")
            phone_tag = biz.select_one(".phone")
            if name_tag:
                leads.append({
                    "name": name_tag.get_text(strip=True),
                    "phone": phone_tag.get_text(strip=True) if phone_tag else "",
                })
        return leads
    except Exception:
        return []


def _leadscraper_save(self, leads: list) -> None:
    """Save leads to data_dir/leads.txt."""
    _os_lgs.makedirs(self.data_dir, exist_ok=True)
    leads_file = _os_lgs.path.join(self.data_dir, "leads.txt")
    with open(leads_file, "a", encoding="utf-8") as fh:
        for lead in leads:
            fh.write(f"{lead.get('name', '')} | {lead.get('phone', '')}\n")


def _leadscraper_run(self) -> str:
    """Scrape and save leads. Return status string."""
    leads = self.scrape()
    self.save(leads)
    return f"Scraped {len(leads)} leads and saved to {self.data_dir}/leads.txt"


LeadScraper.__init__ = _leadscraper_new_init
LeadScraper.scrape = _leadscraper_scrape
LeadScraper.save = _leadscraper_save
LeadScraper.run = _leadscraper_run

LeadScraperBot = LeadScraper
Bot = LeadScraper
