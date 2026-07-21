"""
CineCore Lead Engine — Original Lead Engine Bot

The classic DreamCo CineCore lead-generation engine. Scans businesses from
multiple sources, scores them for commercial opportunity, generates ad scripts,
builds outreach drafts, and exports qualified leads to CRM systems.

This is the *original* lead engine that powers the DreamCo CineCore™ system.
It operates independently as a standalone bot and integrates seamlessly with
the overall system for script generation, ad creation, and client outreach.

Tier-aware:
  FREE       — 100 leads/day, basic scan, script generation.
  PRO ($29)  — 2,000 leads/day, scoring, outreach drafts, CRM export.
  ENTERPRISE ($99) — Unlimited, bulk generation, analytics, white-label.
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

from bots.cinecore_lead_engine.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BUSINESS_SCAN,
    FEATURE_SCRIPT_GENERATION,
    FEATURE_LEAD_SCORING,
    FEATURE_OUTREACH_DRAFT,
    FEATURE_CRM_EXPORT,
    FEATURE_BULK_GENERATION,
    FEATURE_ANALYTICS,
    FEATURE_NICHE_FILTER,
    FEATURE_AD_PACKAGE,
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class BusinessNiche(Enum):
    RESTAURANT = "restaurant"
    REAL_ESTATE = "real_estate"
    AUTO_DEALER = "auto_dealer"
    ROOFING = "roofing"
    PLUMBING = "plumbing"
    ECOMMERCE = "ecommerce"
    RETAIL = "retail"
    HEALTH_WELLNESS = "health_wellness"
    FITNESS = "fitness"
    LEGAL = "legal"
    DENTAL = "dental"
    SALON = "salon"
    GENERAL = "general"


class LeadStatus(Enum):
    RAW = "raw"
    SCORED = "scored"
    SCRIPT_READY = "script_ready"
    OUTREACH_READY = "outreach_ready"
    EXPORTED = "exported"


@dataclass
class BusinessLead:
    """Represents a single business lead for CineCore outreach."""
    lead_id: str
    name: str
    niche: BusinessNiche
    location: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    marketing_score: float = 50.0      # 0-100; lower = weaker marketing
    opportunity_score: float = 50.0    # 0-100; higher = better opportunity
    status: LeadStatus = LeadStatus.RAW
    generated_script: Optional[str] = None
    outreach_draft: Optional[str] = None
    ad_package: Optional[dict] = None
    tags: list = field(default_factory=list)
    found_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CineCoreLeadEngineError(Exception):
    """Base exception for CineCore Lead Engine errors."""


class CineCoreLeadEngineTierError(CineCoreLeadEngineError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Internal simulation helpers
# ---------------------------------------------------------------------------

_SAMPLE_BUSINESSES = [
    ("Tony's Pizzeria", BusinessNiche.RESTAURANT),
    ("Downtown Auto Sales", BusinessNiche.AUTO_DEALER),
    ("Green Valley Roofing", BusinessNiche.ROOFING),
    ("FastFix Plumbing", BusinessNiche.PLUMBING),
    ("Style & Grace Salon", BusinessNiche.SALON),
    ("FitLife Gym", BusinessNiche.FITNESS),
    ("SmithLaw Associates", BusinessNiche.LEGAL),
    ("Bright Smile Dental", BusinessNiche.DENTAL),
    ("TrendShop Boutique", BusinessNiche.RETAIL),
    ("Premier Realty Group", BusinessNiche.REAL_ESTATE),
    ("NatureCare Wellness", BusinessNiche.HEALTH_WELLNESS),
    ("QuickShip Store", BusinessNiche.ECOMMERCE),
]

_SAMPLE_LOCATIONS = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL",
    "Houston, TX", "Phoenix, AZ", "Miami, FL",
    "Dallas, TX", "Atlanta, GA", "Seattle, WA", "Denver, CO",
]


def _simulate_business_scan(count: int, niche_filter: Optional[BusinessNiche] = None) -> list[dict]:
    """Simulate scanning public business directories for leads."""
    pool = _SAMPLE_BUSINESSES
    if niche_filter:
        pool = [(n, t) for n, t in pool if t == niche_filter]
    if not pool:
        pool = _SAMPLE_BUSINESSES

    results = []
    for i in range(count):
        name, niche = random.choice(pool)
        suffix = random.randint(1, 999)
        results.append({
            "name": f"{name} #{suffix}",
            "niche": niche,
            "location": random.choice(_SAMPLE_LOCATIONS),
            "website": f"https://www.{name.lower().replace(' ', '')}{suffix}.com",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "marketing_score": round(random.uniform(10.0, 60.0), 1),
        })
    return results


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class CineCoreLeadEngine:
    """
    CineCore Lead Engine — original DreamCo lead generation and commercial bot.

    Workflow:
        1. scan_businesses()      — find raw business leads
        2. score_leads()          — rank by commercial opportunity
        3. generate_scripts()     — create ad scripts for top leads
        4. generate_outreach()    — draft pitch messages
        5. build_ad_packages()    — full ad concept packages
        6. export_to_crm()        — push qualified leads to CRM
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._leads: dict[str, BusinessLead] = {}
        self._counter: int = 0
        self._crm_exports: list = []

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)." if upgrade else ""
            raise CineCoreLeadEngineTierError(
                f"Feature '{feature}' is not available on the {self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Lead discovery
    # ------------------------------------------------------------------

    def scan_businesses(
        self,
        count: int = 10,
        niche_filter: Optional[BusinessNiche] = None,
    ) -> dict:
        """
        Scan public business sources and collect raw leads.

        Parameters
        ----------
        count : int
            Number of businesses to scan (capped by tier daily limit).
        niche_filter : BusinessNiche, optional
            Restrict to a specific niche (PRO+ only).
        """
        self._require(FEATURE_BUSINESS_SCAN)

        if niche_filter is not None:
            self._require(FEATURE_NICHE_FILTER)

        daily_cap = self._config.max_leads_per_day
        if daily_cap is not None:
            count = min(count, daily_cap)

        raw = _simulate_business_scan(count, niche_filter)
        new_leads = []
        for data in raw:
            self._counter += 1
            lead_id = f"cinecore_lead_{self._counter:08d}"
            lead = BusinessLead(
                lead_id=lead_id,
                name=data["name"],
                niche=data["niche"],
                location=data["location"],
                website=data.get("website"),
                phone=data.get("phone"),
                marketing_score=data.get("marketing_score", 50.0),
            )
            self._leads[lead_id] = lead
            new_leads.append(lead_id)

        return {
            "scanned": count,
            "new_leads": len(new_leads),
            "lead_ids": new_leads,
            "niche_filter": niche_filter.value if niche_filter else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score_leads(self) -> dict:
        """Score raw leads by commercial opportunity (PRO+)."""
        self._require(FEATURE_LEAD_SCORING)
        scored = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.RAW:
                continue
            # Opportunity inversely proportional to marketing strength
            base = 100.0 - lead.marketing_score
            niche_bonus = {
                BusinessNiche.RESTAURANT: 15,
                BusinessNiche.REAL_ESTATE: 20,
                BusinessNiche.AUTO_DEALER: 18,
                BusinessNiche.DENTAL: 12,
                BusinessNiche.ROOFING: 10,
            }.get(lead.niche, 5)
            lead.opportunity_score = min(100.0, round(base + niche_bonus + random.uniform(-5, 5), 1))
            lead.status = LeadStatus.SCORED
            scored += 1
        return {"scored": scored}

    # ------------------------------------------------------------------
    # Script generation
    # ------------------------------------------------------------------

    def generate_scripts(self, top_n: int = 10) -> dict:
        """Generate ad scripts for the top-scored leads."""
        self._require(FEATURE_SCRIPT_GENERATION)

        candidates = sorted(
            [l for l in self._leads.values() if l.status in (LeadStatus.RAW, LeadStatus.SCORED)],
            key=lambda l: l.opportunity_score,
            reverse=True,
        )[:top_n]

        generated = 0
        for lead in candidates:
            lead.generated_script = self._build_script(lead)
            lead.status = LeadStatus.SCRIPT_READY
            generated += 1

        return {"scripts_generated": generated}

    def _build_script(self, lead: BusinessLead) -> str:
        templates = [
            (
                f"STOP losing customers to competitors. "
                f"{lead.name} is changing the game in {lead.location}. "
                f"Get the {lead.niche.value.replace('_', ' ')} experience you deserve. "
                f"Call now — limited spots available."
            ),
            (
                f"Imagine getting more {lead.niche.value.replace('_', ' ')} clients "
                f"without spending a fortune on ads. {lead.name} makes it happen. "
                f"Serving {lead.location}. Don't wait — act today."
            ),
            (
                f"Are you tired of {lead.niche.value.replace('_', ' ')} services "
                f"that over-promise and under-deliver? {lead.name} is different. "
                f"Real results. Real customers. In {lead.location}. Book your free demo."
            ),
        ]
        return random.choice(templates)

    # ------------------------------------------------------------------
    # Outreach drafts
    # ------------------------------------------------------------------

    def generate_outreach(self) -> dict:
        """Generate outreach pitch drafts for script-ready leads (PRO+)."""
        self._require(FEATURE_OUTREACH_DRAFT)
        generated = 0
        for lead in self._leads.values():
            if lead.status != LeadStatus.SCRIPT_READY:
                continue
            lead.outreach_draft = self._build_outreach(lead)
            lead.status = LeadStatus.OUTREACH_READY
            generated += 1
        return {"outreach_drafts_generated": generated}

    def _build_outreach(self, lead: BusinessLead) -> str:
        return (
            f"Hi {lead.name},\n\n"
            f"I created a free AI commercial for your {lead.niche.value.replace('_', ' ')} "
            f"business that could bring in 10–50 new customers monthly.\n\n"
            f"Would you like to see it? We specialize in turning low-visibility "
            f"businesses into high-converting ad systems.\n\n"
            f"No commitment — just results.\n\nBest,\nDreamCo CineCore Team"
        )

    # ------------------------------------------------------------------
    # Ad packages
    # ------------------------------------------------------------------

    def build_ad_packages(self) -> dict:
        """Build full ad concept packages for outreach-ready leads (PRO+)."""
        self._require(FEATURE_AD_PACKAGE)
        built = 0
        for lead in self._leads.values():
            if lead.status not in (LeadStatus.SCRIPT_READY, LeadStatus.OUTREACH_READY):
                continue
            lead.ad_package = {
                "script": lead.generated_script,
                "scenes": ["Problem hook", "Solution reveal", "Social proof", "CTA"],
                "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts", "Facebook Ads"],
                "voiceover_style": "energetic",
                "suggested_visuals": [
                    f"{lead.niche.value.replace('_', ' ')} interior shots",
                    "Customer testimonials",
                    "Before/after showcase",
                    "Product/service in action",
                ],
                "duration_seconds": 30,
                "pricing_tier": "Pro Commercial ($300–$1,000)",
            }
            built += 1
        return {"ad_packages_built": built}

    # ------------------------------------------------------------------
    # Bulk generation
    # ------------------------------------------------------------------

    def bulk_generate(self, business_list: list[str]) -> dict:
        """Mass-generate scripts and ad packages for a list of businesses (ENTERPRISE+)."""
        self._require(FEATURE_BULK_GENERATION)
        results = []
        for biz_name in business_list:
            self._counter += 1
            lead_id = f"cinecore_lead_{self._counter:08d}"
            lead = BusinessLead(
                lead_id=lead_id,
                name=biz_name,
                niche=BusinessNiche.GENERAL,
                location="Unknown",
                marketing_score=random.uniform(20.0, 50.0),
            )
            lead.generated_script = self._build_script(lead)
            lead.outreach_draft = self._build_outreach(lead)
            lead.status = LeadStatus.OUTREACH_READY
            self._leads[lead_id] = lead
            results.append({"lead_id": lead_id, "name": biz_name, "script": lead.generated_script})
        return {
            "bulk_generated": len(results),
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
        niche: Optional[BusinessNiche] = None,
        limit: int = 50,
    ) -> list:
        """Return leads filtered by status and/or niche."""
        leads = list(self._leads.values())
        if status:
            leads = [l for l in leads if l.status == status]
        if niche:
            leads = [l for l in leads if l.niche == niche]
        return [_lead_to_dict(l) for l in leads[:limit]]

    def get_top_leads(self, n: int = 10) -> list:
        """Return top N leads by opportunity score."""
        ranked = sorted(self._leads.values(), key=lambda l: l.opportunity_score, reverse=True)
        return [_lead_to_dict(l) for l in ranked[:n]]

    def get_summary(self) -> dict:
        """Return overall engine statistics."""
        leads = list(self._leads.values())
        by_status: dict[str, int] = {}
        by_niche: dict[str, int] = {}
        for l in leads:
            by_status[l.status.value] = by_status.get(l.status.value, 0) + 1
            by_niche[l.niche.value] = by_niche.get(l.niche.value, 0) + 1
        scores = [l.opportunity_score for l in leads]
        return {
            "total_leads": len(leads),
            "by_status": by_status,
            "by_niche": by_niche,
            "avg_opportunity_score": round(sum(scores) / len(scores), 1) if scores else None,
            "total_crm_exports": sum(e["leads_exported"] for e in self._crm_exports),
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_analytics(self) -> dict:
        """Return extended analytics (ENTERPRISE+)."""
        self._require(FEATURE_ANALYTICS)
        summary = self.get_summary()
        top = self.get_top_leads(5)
        return {
            **summary,
            "top_5_leads": top,
            "crm_export_log": list(self._crm_exports),
        }

    # ------------------------------------------------------------------
    # Chat / GLOBAL AI SOURCES FLOW interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language interface for BuddyAI routing."""
        msg = message.lower()
        if "scan" in msg or "find" in msg or "get leads" in msg:
            result = self.scan_businesses(count=10)
            return {"message": f"Scanned and found {result['new_leads']} new business leads.", "data": result}
        if "score" in msg:
            result = self.score_leads()
            return {"message": f"Scored {result['scored']} leads by opportunity.", "data": result}
        if "script" in msg or "commercial" in msg or "ad" in msg:
            result = self.generate_scripts()
            return {"message": f"Generated {result['scripts_generated']} ad scripts.", "data": result}
        if "outreach" in msg or "pitch" in msg or "message" in msg:
            result = self.generate_outreach()
            return {"message": f"Created {result['outreach_drafts_generated']} outreach drafts.", "data": result}
        if "summary" in msg or "stats" in msg or "status" in msg:
            return {"message": "CineCore Lead Engine summary retrieved.", "data": self.get_summary()}
        if "top" in msg or "best" in msg:
            return {"message": "Top leads by opportunity score.", "data": self.get_top_leads()}
        return {
            "message": (
                "CineCore Lead Engine online. "
                f"Tier: {self.tier.value}. "
                "Commands: 'scan businesses', 'score leads', 'generate scripts', "
                "'generate outreach', 'summary', 'top leads'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lead_to_dict(lead: BusinessLead) -> dict:
    return {
        "lead_id": lead.lead_id,
        "name": lead.name,
        "niche": lead.niche.value,
        "location": lead.location,
        "website": lead.website,
        "phone": lead.phone,
        "email": lead.email,
        "marketing_score": lead.marketing_score,
        "opportunity_score": lead.opportunity_score,
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
    """Standalone entry point for the CineCore Lead Engine bot."""
    import json
    print("=== CineCore Lead Engine Bot ===")
    print("DreamCo CineCore™ — Original Lead Engine\n")

    engine = CineCoreLeadEngine(tier=Tier.PRO)

    print("Step 1: Scanning businesses...")
    scan = engine.scan_businesses(count=5)
    print(f"  Found {scan['new_leads']} leads\n")

    print("Step 2: Scoring leads...")
    scored = engine.score_leads()
    print(f"  Scored {scored['scored']} leads\n")

    print("Step 3: Generating ad scripts...")
    scripts = engine.generate_scripts()
    print(f"  Generated {scripts['scripts_generated']} scripts\n")

    print("Step 4: Generating outreach drafts...")
    outreach = engine.generate_outreach()
    print(f"  Created {outreach['outreach_drafts_generated']} outreach drafts\n")

    print("Step 5: Summary")
    summary = engine.get_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
