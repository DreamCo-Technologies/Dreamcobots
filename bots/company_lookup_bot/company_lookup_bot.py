"""
Company Lookup Bot — DreamCo autonomous company research system.

Looks up company information from external data sources and persists results
to ``data/companies.json``.  The bot can be triggered from GitHub Actions
workflow_dispatch events, making it easy to add companies from the Actions
page without writing code.

Sub-systems
-----------
  • CompanyDataFetcher     — queries external APIs (Crunchbase, Clearbit, custom)
  • CompanyDataEnricher    — adds funding, headcount, social links (PRO+)
  • RecommendationEngine   — suggests new platforms/integrations to explore (PRO+)
  • CompanyRepository      — reads / writes ``data/companies.json``

Tier access
-----------
  FREE:       5 lookups/day, basic fields (name, domain, description).
  PRO:        50 lookups/day, enriched fields, Slack notifications, CSV export.
  ENTERPRISE: Unlimited lookups, all fields, bulk import, webhooks, API access.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.company_lookup_bot import CompanyLookupBot, Tier

    bot = CompanyLookupBot(tier=Tier.PRO)
    result = bot.lookup("Stripe")
    print(bot.get_summary())
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from bots.company_lookup_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_LOOKUP,
    FEATURE_ENRICHED_FIELDS,
    FEATURE_SLACK_NOTIFY,
    FEATURE_EXPORT_CSV,
    FEATURE_BULK_IMPORT,
    FEATURE_API_ACCESS,
    FEATURE_WEBHOOK,
    FEATURE_RECOMMENDATIONS,
)

# ---------------------------------------------------------------------------
# Default data file path
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DEFAULT_DATA_PATH = os.path.join(_REPO_ROOT, "data", "companies.json")


# ---------------------------------------------------------------------------
# Mock company catalogue (used when external API is unavailable)
# ---------------------------------------------------------------------------

_MOCK_COMPANIES: Dict[str, Dict[str, Any]] = {
    "stripe": {
        "name": "Stripe",
        "domain": "stripe.com",
        "description": "Online payment processing for internet businesses.",
        "industry": "FinTech",
        "country": "United States",
        "founded_year": 2010,
        "employees": 8000,
        "funding_total_usd": 2200000000,
        "funding_rounds": 16,
        "linkedin_url": "https://www.linkedin.com/company/stripe",
        "crunchbase_url": "https://www.crunchbase.com/organization/stripe",
        "tags": ["payments", "api", "saas", "fintech"],
        "integration_suggestions": ["WordPress WooCommerce", "Shopify", "Streamlit billing"],
    },
    "shopify": {
        "name": "Shopify",
        "domain": "shopify.com",
        "description": "E-commerce platform for online stores and retail point-of-sale.",
        "industry": "E-Commerce",
        "country": "Canada",
        "founded_year": 2006,
        "employees": 11600,
        "funding_total_usd": 122000000,
        "funding_rounds": 4,
        "linkedin_url": "https://www.linkedin.com/company/shopify",
        "crunchbase_url": "https://www.crunchbase.com/organization/shopify",
        "tags": ["ecommerce", "saas", "retail"],
        "integration_suggestions": ["DreamCo payments", "Affiliate Bot", "God Mode Bot"],
    },
    "hubspot": {
        "name": "HubSpot",
        "domain": "hubspot.com",
        "description": "CRM platform for marketing, sales, and customer service.",
        "industry": "CRM / Marketing",
        "country": "United States",
        "founded_year": 2006,
        "employees": 7400,
        "funding_total_usd": 100500000,
        "funding_rounds": 5,
        "linkedin_url": "https://www.linkedin.com/company/hubspot",
        "crunchbase_url": "https://www.crunchbase.com/organization/hubspot",
        "tags": ["crm", "marketing", "saas"],
        "integration_suggestions": ["CRM Automation Bot", "Email Campaign Manager Bot"],
    },
    "twilio": {
        "name": "Twilio",
        "domain": "twilio.com",
        "description": "Cloud communications platform for SMS, voice, and messaging APIs.",
        "industry": "Communications",
        "country": "United States",
        "founded_year": 2008,
        "employees": 5900,
        "funding_total_usd": 235000000,
        "funding_rounds": 7,
        "linkedin_url": "https://www.linkedin.com/company/twilio",
        "crunchbase_url": "https://www.crunchbase.com/organization/twilio",
        "tags": ["sms", "api", "communications", "saas"],
        "integration_suggestions": ["SMS Sender", "Customer Support Bot", "Outreach Bot"],
    },
    "openai": {
        "name": "OpenAI",
        "domain": "openai.com",
        "description": "AI research and deployment company behind GPT and DALL-E.",
        "industry": "Artificial Intelligence",
        "country": "United States",
        "founded_year": 2015,
        "employees": 1500,
        "funding_total_usd": 11300000000,
        "funding_rounds": 7,
        "linkedin_url": "https://www.linkedin.com/company/openai",
        "crunchbase_url": "https://www.crunchbase.com/organization/openai",
        "tags": ["ai", "llm", "research", "api"],
        "integration_suggestions": ["Buddy Bot", "AI Models Integration", "AI Chatbot"],
    },
    "wordpress": {
        "name": "WordPress",
        "domain": "wordpress.org",
        "description": "Open-source CMS powering 43% of the web.",
        "industry": "CMS / Web",
        "country": "United States",
        "founded_year": 2003,
        "employees": 1900,
        "funding_total_usd": 0,
        "funding_rounds": 0,
        "linkedin_url": "https://www.linkedin.com/company/wordpress",
        "crunchbase_url": "https://www.crunchbase.com/organization/wordpress",
        "tags": ["cms", "open-source", "web", "plugins"],
        "integration_suggestions": ["WordPress plugin deployment", "WooCommerce payments"],
    },
    "slack": {
        "name": "Slack",
        "domain": "slack.com",
        "description": "Business communication platform with channels, DMs, and integrations.",
        "industry": "Collaboration",
        "country": "United States",
        "founded_year": 2013,
        "employees": 2500,
        "funding_total_usd": 1400000000,
        "funding_rounds": 9,
        "linkedin_url": "https://www.linkedin.com/company/slack-technologies",
        "crunchbase_url": "https://www.crunchbase.com/organization/slack",
        "tags": ["messaging", "collaboration", "saas"],
        "integration_suggestions": ["Slack notifications", "Integration Feedback Bot"],
    },
    "salesforce": {
        "name": "Salesforce",
        "domain": "salesforce.com",
        "description": "Enterprise CRM and cloud platform for sales, service, and marketing.",
        "industry": "CRM / Enterprise",
        "country": "United States",
        "founded_year": 1999,
        "employees": 73000,
        "funding_total_usd": 65000000,
        "funding_rounds": 3,
        "linkedin_url": "https://www.linkedin.com/company/salesforce",
        "crunchbase_url": "https://www.crunchbase.com/organization/salesforce",
        "tags": ["crm", "enterprise", "saas", "cloud"],
        "integration_suggestions": ["CRM Automation Bot", "Sales Bot", "Dream Sales Pro"],
    },
    "wix": {
        "name": "Wix",
        "domain": "wix.com",
        "description": "Cloud-based website builder with drag-and-drop functionality.",
        "industry": "Web / SaaS",
        "country": "Israel",
        "founded_year": 2006,
        "employees": 5500,
        "funding_total_usd": 615000000,
        "funding_rounds": 7,
        "linkedin_url": "https://www.linkedin.com/company/wix-com",
        "crunchbase_url": "https://www.crunchbase.com/organization/wix",
        "tags": ["website-builder", "saas", "ecommerce"],
        "integration_suggestions": ["Wix Velo API", "Shopify migration tools"],
    },
    "zapier": {
        "name": "Zapier",
        "domain": "zapier.com",
        "description": "Automation platform connecting 6,000+ apps via no-code workflows.",
        "industry": "Automation",
        "country": "United States",
        "founded_year": 2011,
        "employees": 600,
        "funding_total_usd": 1400000,
        "funding_rounds": 1,
        "linkedin_url": "https://www.linkedin.com/company/zapier",
        "crunchbase_url": "https://www.crunchbase.com/organization/zapier",
        "tags": ["automation", "no-code", "integration"],
        "integration_suggestions": ["Integration Feedback Bot", "God Mode Bot automations"],
    },
}

# ---------------------------------------------------------------------------
# Default platform recommendations
# ---------------------------------------------------------------------------

_DEFAULT_RECOMMENDATIONS: List[Dict[str, Any]] = [
    {
        "platform": "Streamlit Community Cloud",
        "reason": "Deploy Python dashboards directly from GitHub with zero-config CI/CD.",
        "category": "dashboard",
        "effort": "low",
        "priority": 1,
    },
    {
        "platform": "WordPress + WooCommerce",
        "reason": "Temporary dashboard and e-commerce layer for rapid revenue generation.",
        "category": "cms",
        "effort": "medium",
        "priority": 2,
    },
    {
        "platform": "Stripe Connect",
        "reason": "Multi-party payment processing for marketplace revenue flows.",
        "category": "payments",
        "effort": "medium",
        "priority": 3,
    },
    {
        "platform": "HubSpot CRM",
        "reason": "Free CRM to track all company lookups, leads, and outreach activity.",
        "category": "crm",
        "effort": "low",
        "priority": 4,
    },
    {
        "platform": "Twilio SMS / Voice",
        "reason": "Send real-time alerts and client follow-ups via SMS automation.",
        "category": "communications",
        "effort": "low",
        "priority": 5,
    },
    {
        "platform": "Zapier",
        "reason": "Bridge DreamCo bots to 6,000+ external apps via no-code zaps.",
        "category": "automation",
        "effort": "low",
        "priority": 6,
    },
    {
        "platform": "Shopify",
        "reason": "E-commerce storefront for selling digital products and SaaS subscriptions.",
        "category": "ecommerce",
        "effort": "medium",
        "priority": 7,
    },
    {
        "platform": "GitHub Actions (scheduled)",
        "reason": "Run company lookups on a cron schedule to keep data fresh autonomously.",
        "category": "automation",
        "effort": "low",
        "priority": 8,
    },
]


# ===========================================================================
# CompanyDataFetcher
# ===========================================================================


class CompanyDataFetcher:
    """
    Queries external company data sources.

    When a real API key (``CRUNCHBASE_API_KEY`` or ``CLEARBIT_API_KEY``) is
    present in the environment the fetcher attempts a live request; otherwise
    it falls back to the built-in mock catalogue.
    """

    def __init__(self) -> None:
        self._crunchbase_key = os.getenv("CRUNCHBASE_API_KEY", "")
        self._clearbit_key = os.getenv("CLEARBIT_API_KEY", "")

    def fetch(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Return raw company data for *company_name*.

        Priority order:
          1. Clearbit Enrichment API (if key present)
          2. Crunchbase Basic API   (if key present)
          3. Internal mock catalogue (always available)
        """
        key = company_name.lower().strip()

        if self._clearbit_key:
            result = self._fetch_clearbit(company_name)
            if result:
                return result

        if self._crunchbase_key:
            result = self._fetch_crunchbase(company_name)
            if result:
                return result

        return self._fetch_mock(key)

    # ------------------------------------------------------------------
    # Live API helpers (gracefully degrade to None on any error)
    # ------------------------------------------------------------------

    def _fetch_clearbit(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Attempt Clearbit Name-to-Domain API lookup."""
        try:
            import urllib.request
            url = (
                f"https://company.clearbit.com/v1/domains/find"
                f"?name={urllib.parse.quote(company_name)}"
            )
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self._clearbit_key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            return {
                "name": data.get("name", company_name),
                "domain": data.get("domain", ""),
                "description": data.get("description", ""),
                "industry": data.get("category", {}).get("industry", ""),
                "country": data.get("geo", {}).get("country", ""),
                "founded_year": data.get("foundedYear"),
                "employees": data.get("metrics", {}).get("employees"),
                "funding_total_usd": None,
                "funding_rounds": None,
                "linkedin_url": data.get("linkedin", {}).get("handle", ""),
                "crunchbase_url": data.get("crunchbase", {}).get("handle", ""),
                "tags": data.get("tags", []),
                "integration_suggestions": [],
                "source": "clearbit",
            }
        except Exception:
            return None

    def _fetch_crunchbase(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Attempt Crunchbase Basic API lookup."""
        try:
            import urllib.request
            import urllib.parse
            url = (
                "https://api.crunchbase.com/api/v4/searches/organizations"
                f"?user_key={self._crunchbase_key}"
            )
            payload = json.dumps({
                "field_ids": [
                    "identifier", "short_description", "website_url",
                    "founded_on", "num_employees_enum",
                ],
                "query": [{"type": "predicate", "field_id": "facet_ids",
                           "operator_id": "includes", "values": ["company"]}],
                "predicate": {"field_id": "identifier", "operator_id": "contains",
                              "values": [company_name]},
                "limit": 1,
            }).encode()
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            entities = data.get("entities", [])
            if not entities:
                return None
            props = entities[0].get("properties", {})
            return {
                "name": props.get("identifier", {}).get("value", company_name),
                "domain": props.get("website_url", ""),
                "description": props.get("short_description", ""),
                "industry": "",
                "country": "",
                "founded_year": (props.get("founded_on") or {}).get("value"),
                "employees": None,
                "funding_total_usd": None,
                "funding_rounds": None,
                "linkedin_url": "",
                "crunchbase_url": props.get("identifier", {}).get("permalink", ""),
                "tags": [],
                "integration_suggestions": [],
                "source": "crunchbase",
            }
        except Exception:
            return None

    def _fetch_mock(self, key: str) -> Optional[Dict[str, Any]]:
        """Return a record from the internal mock catalogue."""
        # Exact match first
        if key in _MOCK_COMPANIES:
            record = dict(_MOCK_COMPANIES[key])
            record["source"] = "mock"
            return record
        # Partial match
        for mock_key, company in _MOCK_COMPANIES.items():
            if key in mock_key or mock_key in key:
                record = dict(company)
                record["source"] = "mock"
                return record
        return None


# ===========================================================================
# CompanyDataEnricher  (PRO+)
# ===========================================================================


class CompanyDataEnricher:
    """Enriches basic company records with additional metadata (PRO+)."""

    def enrich(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add enriched fields to *record* in-place and return it.

        In production this would call LinkedIn, PitchBook, or Apollo APIs.
        For now it computes derived fields from whatever data is already
        present and flags the record as enriched.
        """
        record["enriched"] = True
        record["enriched_at"] = datetime.now(tz=timezone.utc).isoformat()

        # Derived insights
        employees = record.get("employees") or 0
        funding = record.get("funding_total_usd") or 0
        if employees > 10000:
            record["company_size"] = "enterprise"
        elif employees > 500:
            record["company_size"] = "mid-market"
        elif employees > 0:
            record["company_size"] = "smb"
        else:
            record["company_size"] = "unknown"

        if funding > 1_000_000_000:
            record["funding_stage"] = "unicorn+"
        elif funding > 100_000_000:
            record["funding_stage"] = "series_c+"
        elif funding > 10_000_000:
            record["funding_stage"] = "series_a_b"
        elif funding > 0:
            record["funding_stage"] = "seed_early"
        else:
            record["funding_stage"] = "bootstrapped_or_unknown"

        return record


# ===========================================================================
# RecommendationEngine  (PRO+)
# ===========================================================================


class RecommendationEngine:
    """
    Suggests new platforms and tools for integration based on company data.

    Returns a ranked list of platform suggestions derived from:
      - The company's industry tags
      - Existing integration gaps
      - Hard-coded DreamCo priority list
    """

    def recommend(
        self,
        company: Optional[Dict[str, Any]] = None,
        *,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Return up to *limit* integration recommendations.

        Parameters
        ----------
        company:
            Company record used to personalise recommendations.  When None,
            returns the default priority list.
        limit:
            Max number of recommendations to return.
        """
        recs = list(_DEFAULT_RECOMMENDATIONS)

        if company:
            tags = [t.lower() for t in (company.get("tags") or [])]
            company_recs = company.get("integration_suggestions") or []

            # Prepend company-specific suggestions at priority 0
            for i, sugg in enumerate(company_recs):
                recs.insert(0, {
                    "platform": sugg,
                    "reason": f"Suggested by {company.get('name', 'company')} integration data.",
                    "category": "company_specific",
                    "effort": "medium",
                    "priority": -i,
                })

            # Boost payment platforms for fintech companies
            if any(t in tags for t in ["fintech", "payments", "banking"]):
                for i, rec in enumerate(recs):
                    if rec.get("category") == "payments":
                        boosted = dict(rec)
                        boosted["priority"] = rec["priority"] - 10
                        recs[i] = boosted

        recs_sorted = sorted(recs, key=lambda r: r.get("priority", 99))
        return recs_sorted[:limit]


# ===========================================================================
# CompanyRepository
# ===========================================================================


class CompanyRepository:
    """Reads and writes the ``data/companies.json`` file."""

    def __init__(self, data_path: str = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def load(self) -> Dict[str, Any]:
        """Load the companies store from disk, creating it if absent."""
        if not os.path.exists(self.data_path):
            return {"last_updated": None, "total_companies": 0, "companies": []}
        with open(self.data_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, store: Dict[str, Any]) -> None:
        """Persist *store* to disk."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2)

    def add_or_update(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upsert *company* into the store by domain (or name if no domain).

        Returns the updated store.
        """
        store = self.load()
        companies: List[Dict[str, Any]] = store.get("companies", [])
        key = (company.get("domain") or company.get("name", "")).lower()

        existing_idx = None
        for i, c in enumerate(companies):
            c_key = (c.get("domain") or c.get("name", "")).lower()
            if c_key == key:
                existing_idx = i
                break

        if existing_idx is not None:
            companies[existing_idx] = company
        else:
            companies.append(company)

        store["companies"] = companies
        store["total_companies"] = len(companies)
        store["last_updated"] = datetime.now(tz=timezone.utc).isoformat()
        self.save(store)
        return store

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all stored companies."""
        return self.load().get("companies", [])

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a company by name (case-insensitive)."""
        for company in self.get_all():
            if company.get("name", "").lower() == name.lower():
                return company
        return None

    def export_csv(self, output_path: str) -> str:
        """Export all companies to *output_path* as CSV and return the path."""
        import csv
        companies = self.get_all()
        if not companies:
            return output_path
        fieldnames = list(companies[0].keys())
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(companies)
        return output_path


# ===========================================================================
# CompanyLookupBot  (main orchestrator)
# ===========================================================================


class CompanyLookupBot:
    """
    DreamCo Company Lookup Bot.

    Looks up company information, enriches it (PRO+), saves it to
    ``data/companies.json``, and optionally sends Slack notifications.

    Parameters
    ----------
    tier : Tier
        Subscription tier that governs feature access.
    data_path : str
        Path to the companies JSON store.  Defaults to ``data/companies.json``
        relative to the repository root.
    slack_webhook_url : str | None
        Slack incoming webhook URL.  When provided and the tier supports
        ``slack_notify``, a Slack message is sent on each successful lookup.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        data_path: str = DEFAULT_DATA_PATH,
        slack_webhook_url: Optional[str] = None,
    ) -> None:
        self.tier = tier
        self._config = get_tier_config(tier)
        self._fetcher = CompanyDataFetcher()
        self._enricher = CompanyDataEnricher()
        self._recommender = RecommendationEngine()
        self._repo = CompanyRepository(data_path)
        self._slack_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        self._lookup_count = 0
        self._results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Tier enforcement helpers
    # ------------------------------------------------------------------

    def _enforce_tier(self, required_feature: str) -> None:
        if not self._config.has_feature(required_feature):
            tier_name = self.tier.value.upper()
            upgrade = get_upgrade_path(self.tier)
            upgrade_hint = (
                f" Upgrade to {upgrade.name} for access."
                if upgrade else ""
            )
            raise PermissionError(
                f"Feature '{required_feature}' is not available on the {tier_name} tier."
                + upgrade_hint
            )

    def _check_daily_limit(self) -> None:
        limit = self._config.max_lookups_per_day
        if limit is not None and self._lookup_count >= limit:
            raise RuntimeError(
                f"Daily lookup limit ({limit}) reached on the "
                f"{self.tier.value.upper()} tier. Upgrade to increase your limit."
            )

    # ------------------------------------------------------------------
    # Core lookup
    # ------------------------------------------------------------------

    def lookup(self, company_name: str) -> Dict[str, Any]:
        """
        Look up *company_name* and save the result to the data store.

        Returns a dict with keys:
          - ``company``     : the raw/enriched company record
          - ``saved``       : True if persisted to companies.json
          - ``enriched``    : True if PRO+ enrichment was applied
          - ``recommendations`` : list of platform suggestions (PRO+ only)
          - ``slack_sent``  : True if a Slack notification was dispatched
          - ``timestamp``   : ISO-8601 UTC lookup time
        """
        self._enforce_tier(FEATURE_BASIC_LOOKUP)
        self._check_daily_limit()

        self._lookup_count += 1
        ts = datetime.now(tz=timezone.utc).isoformat()

        raw = self._fetcher.fetch(company_name)
        if raw is None:
            raw = {
                "name": company_name,
                "domain": "",
                "description": "No data found.",
                "source": "not_found",
            }

        raw["looked_up_at"] = ts

        enriched = False
        if self._config.has_feature(FEATURE_ENRICHED_FIELDS):
            raw = self._enricher.enrich(raw)
            enriched = True

        self._repo.add_or_update(raw)

        recommendations: List[Dict[str, Any]] = []
        if self._config.has_feature(FEATURE_RECOMMENDATIONS):
            recommendations = self._recommender.recommend(
                company=raw, limit=5
            )

        slack_sent = False
        if self._config.has_feature(FEATURE_SLACK_NOTIFY) and self._slack_url:
            slack_sent = self._send_slack_notification(raw, recommendations)

        result: Dict[str, Any] = {
            "company": raw,
            "saved": True,
            "enriched": enriched,
            "recommendations": recommendations,
            "slack_sent": slack_sent,
            "timestamp": ts,
        }
        self._results.append(result)
        return result

    def bulk_lookup(self, company_names: List[str]) -> List[Dict[str, Any]]:
        """
        Look up multiple companies at once (ENTERPRISE only).

        Parameters
        ----------
        company_names : list[str]
            Company names to look up.

        Returns
        -------
        list of lookup result dicts.
        """
        self._enforce_tier(FEATURE_BULK_IMPORT)
        return [self.lookup(name) for name in company_names]

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def get_companies(self) -> List[Dict[str, Any]]:
        """Return all stored companies."""
        return self._repo.get_all()

    def get_recommendations(self, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Return platform/integration recommendations (PRO+).

        Parameters
        ----------
        company_name : str | None
            When provided, personalise recommendations for that company.
        """
        self._enforce_tier(FEATURE_RECOMMENDATIONS)
        company = None
        if company_name:
            company = self._repo.get_by_name(company_name)
        return self._recommender.recommend(company=company)

    def export_csv(self, output_path: str = "data/companies_export.csv") -> str:
        """Export all companies to CSV (PRO+)."""
        self._enforce_tier(FEATURE_EXPORT_CSV)
        return self._repo.export_csv(output_path)

    # ------------------------------------------------------------------
    # Slack notifications
    # ------------------------------------------------------------------

    def _send_slack_notification(
        self,
        company: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
    ) -> bool:
        """
        Send a Slack message via incoming webhook.

        Returns True on success, False on any error.
        """
        try:
            import urllib.request

            name = company.get("name", "Unknown")
            domain = company.get("domain", "")
            description = company.get("description", "")[:120]
            industry = company.get("industry", "")
            rec_list = "\n".join(
                f"  • {r['platform']}: {r['reason']}"
                for r in recommendations[:3]
            )

            text = (
                f":mag: *Company Lookup Complete* — {name}\n"
                f"> Domain: {domain}\n"
                f"> Industry: {industry}\n"
                f"> {description}\n"
            )
            if rec_list:
                text += f"\n*Integration Suggestions:*\n{rec_list}"

            payload = json.dumps({"text": text}).encode()
            req = urllib.request.Request(
                self._slack_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of this session's lookup activity."""
        total_stored = len(self._repo.get_all())
        return {
            "bot": "CompanyLookupBot",
            "tier": self.tier.value,
            "lookups_this_session": self._lookup_count,
            "total_companies_stored": total_stored,
            "daily_limit": self._config.max_lookups_per_day,
            "features_enabled": list(self._config.features),
            "results": self._results,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }


__all__ = [
    "CompanyLookupBot",
    "CompanyDataFetcher",
    "CompanyDataEnricher",
    "RecommendationEngine",
    "CompanyRepository",
]
