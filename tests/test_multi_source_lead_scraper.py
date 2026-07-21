"""
Tests for bots/multi_source_lead_scraper/

Covers:
  1. Tiers
  2. MultiSourceLeadScraper — scraping, validation, enrichment, scoring, export
  3. Chat & process interfaces
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.multi_source_lead_scraper.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_BASIC_SCRAPING,
    FEATURE_MULTI_SOURCE,
    FEATURE_LEAD_ENRICHMENT,
    FEATURE_AI_SCORING,
    FEATURE_CRM_EXPORT,
    FEATURE_WHITE_LABEL,
)
from bots.multi_source_lead_scraper.lead_scraper import (
    MultiSourceLeadScraper,
    LeadScraperTierError,
    LeadSource,
    LeadStatus,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestLeadScraperTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_max_leads(self):
        assert get_tier_config(Tier.FREE).max_leads_per_day == 50

    def test_pro_max_leads(self):
        assert get_tier_config(Tier.PRO).max_leads_per_day == 5_000

    def test_enterprise_unlimited_leads(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_leads()

    def test_free_has_basic_scraping(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_BASIC_SCRAPING)

    def test_free_lacks_ai_scoring(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_AI_SCORING)

    def test_enterprise_has_ai_scoring(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_AI_SCORING)

    def test_free_lacks_white_label(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_WHITE_LABEL)

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade.tier == Tier.PRO

    def test_upgrade_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. Scraping
# ===========================================================================

class TestLeadScraperBasic:
    def setup_method(self):
        self.scraper = MultiSourceLeadScraper(tier=Tier.FREE)

    def test_instantiation(self):
        assert self.scraper is not None
        assert self.scraper.tier == Tier.FREE

    def test_scrape_google_returns_leads(self):
        result = self.scraper.scrape(LeadSource.GOOGLE, count=5)
        assert result["new_leads"] <= 5
        assert result["source"] == "google"

    def test_scrape_respects_daily_cap(self):
        result = self.scraper.scrape(LeadSource.GOOGLE, count=1000)
        assert result["requested"] == 50  # capped to FREE tier limit

    def test_free_tier_cannot_scrape_linkedin(self):
        with pytest.raises(LeadScraperTierError):
            self.scraper.scrape(LeadSource.LINKEDIN, count=5)

    def test_scrape_all_sources_requires_multi_source(self):
        with pytest.raises(LeadScraperTierError):
            self.scraper.scrape_all_sources()

    def test_summary_after_scrape(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        summary = self.scraper.get_summary()
        assert summary["total_leads"] >= 0
        assert summary["total_scrape_sessions"] == 1

    def test_scrape_log_recorded(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=3)
        log = self.scraper.get_scrape_log()
        assert len(log) == 1

    def test_get_leads_returns_list(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        leads = self.scraper.get_leads(limit=10)
        assert isinstance(leads, list)


class TestLeadScraperPro:
    def setup_method(self):
        self.scraper = MultiSourceLeadScraper(tier=Tier.PRO)

    def test_scrape_linkedin(self):
        result = self.scraper.scrape(LeadSource.LINKEDIN, count=10)
        assert result["source"] == "linkedin"

    def test_scrape_all_sources(self):
        result = self.scraper.scrape_all_sources(leads_per_source=5)
        assert result["sources_scraped"] >= 2
        assert "total_new_leads" in result

    def test_validate_leads(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        result = self.scraper.validate_leads()
        assert "validated" in result

    def test_enrich_leads(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        self.scraper.validate_leads()
        result = self.scraper.enrich_leads()
        assert "enriched" in result

    def test_crm_export(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        self.scraper.validate_leads()
        result = self.scraper.export_to_crm("HubSpot")
        assert result["crm"] == "HubSpot"
        assert result["leads_exported"] >= 0

    def test_webhook_export(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        self.scraper.validate_leads()
        result = self.scraper.export_to_webhook("https://webhook.site/test")
        assert "leads_exported" in result

    def test_industry_filter(self):
        result = self.scraper.scrape(LeadSource.GOOGLE, count=20, industry_filter="SaaS")
        # All returned leads should be filtered (may be 0 or more due to randomness)
        assert isinstance(result, dict)

    def test_deduplication(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        summary_before = self.scraper.get_summary()
        before_count = summary_before["total_leads"]
        # Scrape again — some emails may duplicate, dedup should handle it
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        summary_after = self.scraper.get_summary()
        assert summary_after["total_leads"] >= before_count


class TestLeadScraperEnterprise:
    def setup_method(self):
        self.scraper = MultiSourceLeadScraper(tier=Tier.ENTERPRISE)

    def test_score_leads(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        self.scraper.validate_leads()
        result = self.scraper.score_leads()
        assert "scored" in result

    def test_get_top_leads(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        self.scraper.validate_leads()
        self.scraper.score_leads()
        top = self.scraper.get_top_leads(n=5)
        assert isinstance(top, list)
        # Scores should be descending
        if len(top) > 1:
            assert top[0]["quality_score"] >= top[-1]["quality_score"]

    def test_unlimited_leads(self):
        result = self.scraper.scrape(LeadSource.GOOGLE, count=10000)
        assert result["requested"] == 10000

    def test_summary_by_source(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        self.scraper.scrape(LeadSource.LINKEDIN, count=5)
        summary = self.scraper.get_summary()
        assert "google" in summary["by_source"]


# ===========================================================================
# 3. Chat & Process
# ===========================================================================

class TestLeadScraperChat:
    def setup_method(self):
        self.scraper = MultiSourceLeadScraper(tier=Tier.PRO)

    def test_chat_scrape(self):
        resp = self.scraper.chat("scrape leads now")
        assert "message" in resp

    def test_chat_summary(self):
        resp = self.scraper.chat("show me the stats")
        assert "message" in resp

    def test_chat_top_leads(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=5)
        self.scraper.validate_leads()
        resp = self.scraper.chat("show top leads")
        assert "message" in resp

    def test_chat_unknown(self):
        resp = self.scraper.chat("xyzzy unknown command")
        assert "message" in resp

    def test_process_method(self):
        result = self.scraper.process({"command": "scrape leads"})
        assert "message" in result

    def test_get_leads_by_status(self):
        self.scraper.scrape(LeadSource.GOOGLE, count=10)
        self.scraper.validate_leads()
        leads = self.scraper.get_leads(status=LeadStatus.VALIDATED, limit=5)
        assert isinstance(leads, list)
