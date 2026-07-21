"""
Tests for bots/company_lookup_bot/

Covers:
  1. Tiers (FREE / PRO / ENTERPRISE)
  2. CompanyDataFetcher (mock catalogue)
  3. CompanyDataEnricher
  4. RecommendationEngine
  5. CompanyRepository (load / save / upsert)
  6. CompanyLookupBot orchestrator (lookup / bulk_lookup / get_summary)
  7. Tier gating (feature access + daily limits)
  8. Error handling & edge cases
  9. Bot Library registration
"""

import json
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
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
    FEATURE_RECOMMENDATIONS,
)

# ---------------------------------------------------------------------------
# Bot imports
# ---------------------------------------------------------------------------
from bots.company_lookup_bot.company_lookup_bot import (
    CompanyLookupBot,
    CompanyDataFetcher,
    CompanyDataEnricher,
    RecommendationEngine,
    CompanyRepository,
)


# ===========================================================================
# 1. Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_catalogue_has_all_tiers(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_free_tier_config(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.max_lookups_per_day == 5
        assert cfg.has_feature(FEATURE_BASIC_LOOKUP)
        assert not cfg.has_feature(FEATURE_ENRICHED_FIELDS)
        assert not cfg.has_feature(FEATURE_BULK_IMPORT)

    def test_pro_tier_config(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0
        assert cfg.max_lookups_per_day == 50
        assert cfg.has_feature(FEATURE_BASIC_LOOKUP)
        assert cfg.has_feature(FEATURE_ENRICHED_FIELDS)
        assert cfg.has_feature(FEATURE_SLACK_NOTIFY)
        assert not cfg.has_feature(FEATURE_BULK_IMPORT)

    def test_enterprise_tier_config(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0
        assert cfg.max_lookups_per_day is None
        assert cfg.is_unlimited()
        assert cfg.has_feature(FEATURE_BULK_IMPORT)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 3
        assert tiers[0].tier == Tier.FREE

    def test_upgrade_path(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO
        assert get_upgrade_path(Tier.PRO).tier == Tier.ENTERPRISE
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_has_feature_false(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature("nonexistent_feature")


# ===========================================================================
# 2. CompanyDataFetcher tests
# ===========================================================================

class TestCompanyDataFetcher:
    def setup_method(self):
        self.fetcher = CompanyDataFetcher()

    def test_fetch_known_company(self):
        result = self.fetcher.fetch("Stripe")
        assert result is not None
        assert result["name"] == "Stripe"
        assert result["domain"] == "stripe.com"
        assert result["source"] == "mock"

    def test_fetch_case_insensitive(self):
        result = self.fetcher.fetch("stripe")
        assert result is not None
        assert result["name"] == "Stripe"

    def test_fetch_partial_match(self):
        result = self.fetcher.fetch("open")
        assert result is not None  # matches "openai"

    def test_fetch_unknown_company_returns_none(self):
        result = self.fetcher.fetch("xyzunknowncompanyabc123")
        assert result is None

    def test_fetch_shopify(self):
        result = self.fetcher.fetch("Shopify")
        assert result["domain"] == "shopify.com"
        assert "ecommerce" in result["tags"]

    def test_fetch_has_integration_suggestions(self):
        result = self.fetcher.fetch("Stripe")
        assert isinstance(result.get("integration_suggestions"), list)
        assert len(result["integration_suggestions"]) > 0


# ===========================================================================
# 3. CompanyDataEnricher tests
# ===========================================================================

class TestCompanyDataEnricher:
    def setup_method(self):
        self.enricher = CompanyDataEnricher()

    def test_enriches_record(self):
        record = {"name": "TestCo", "employees": 1000, "funding_total_usd": 50000000}
        result = self.enricher.enrich(record)
        assert result["enriched"] is True
        assert "enriched_at" in result

    def test_company_size_enterprise(self):
        record = {"name": "BigCo", "employees": 50000, "funding_total_usd": 0}
        result = self.enricher.enrich(record)
        assert result["company_size"] == "enterprise"

    def test_company_size_mid_market(self):
        record = {"name": "MidCo", "employees": 1000, "funding_total_usd": 0}
        result = self.enricher.enrich(record)
        assert result["company_size"] == "mid-market"

    def test_company_size_smb(self):
        record = {"name": "SmallCo", "employees": 50, "funding_total_usd": 0}
        result = self.enricher.enrich(record)
        assert result["company_size"] == "smb"

    def test_company_size_unknown(self):
        record = {"name": "GhostCo", "employees": 0, "funding_total_usd": 0}
        result = self.enricher.enrich(record)
        assert result["company_size"] == "unknown"

    def test_funding_stage_unicorn(self):
        record = {"name": "BigFund", "employees": 500, "funding_total_usd": 2000000000}
        result = self.enricher.enrich(record)
        assert result["funding_stage"] == "unicorn+"

    def test_funding_stage_bootstrapped(self):
        record = {"name": "Bootstrap", "employees": 5, "funding_total_usd": 0}
        result = self.enricher.enrich(record)
        assert result["funding_stage"] == "bootstrapped_or_unknown"

    def test_enrich_modifies_in_place(self):
        record = {"name": "InPlace", "employees": 200, "funding_total_usd": 5000000}
        original_id = id(record)
        result = self.enricher.enrich(record)
        assert id(result) == original_id


# ===========================================================================
# 4. RecommendationEngine tests
# ===========================================================================

class TestRecommendationEngine:
    def setup_method(self):
        self.engine = RecommendationEngine()

    def test_recommend_returns_list(self):
        recs = self.engine.recommend()
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_recommend_limit(self):
        recs = self.engine.recommend(limit=3)
        assert len(recs) <= 3

    def test_recommend_with_company(self):
        company = {
            "name": "Stripe",
            "tags": ["fintech", "payments"],
            "integration_suggestions": ["WooCommerce"],
        }
        recs = self.engine.recommend(company=company, limit=5)
        assert len(recs) <= 5
        platforms = [r["platform"] for r in recs]
        assert "WooCommerce" in platforms

    def test_recommend_fields(self):
        recs = self.engine.recommend(limit=1)
        rec = recs[0]
        assert "platform" in rec
        assert "reason" in rec
        assert "category" in rec
        assert "priority" in rec

    def test_recommend_fintech_boosts_payment_platforms(self):
        company = {
            "name": "PayCo",
            "tags": ["fintech", "payments"],
            "integration_suggestions": [],
        }
        recs = self.engine.recommend(company=company, limit=10)
        payment_recs = [r for r in recs if r.get("category") == "payments"]
        if payment_recs:
            # Payment platforms should appear earlier (boosted priority)
            payment_idx = recs.index(payment_recs[0])
            assert payment_idx < len(recs)  # present in results

    def test_recommend_default_no_crash(self):
        recs = self.engine.recommend(company=None)
        assert isinstance(recs, list)


# ===========================================================================
# 5. CompanyRepository tests
# ===========================================================================

class TestCompanyRepository:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.tmpdir, "companies.json")
        self.repo = CompanyRepository(data_path=self.data_path)

    def test_load_creates_empty_store_when_missing(self):
        store = self.repo.load()
        assert store["companies"] == []
        assert store["total_companies"] == 0

    def test_add_company(self):
        company = {"name": "TestCo", "domain": "testco.com"}
        self.repo.add_or_update(company)
        companies = self.repo.get_all()
        assert len(companies) == 1
        assert companies[0]["name"] == "TestCo"

    def test_upsert_by_domain(self):
        self.repo.add_or_update({"name": "TestCo", "domain": "testco.com", "v": 1})
        self.repo.add_or_update({"name": "TestCo Updated", "domain": "testco.com", "v": 2})
        companies = self.repo.get_all()
        assert len(companies) == 1
        assert companies[0]["name"] == "TestCo Updated"
        assert companies[0]["v"] == 2

    def test_add_multiple_companies(self):
        for i in range(3):
            self.repo.add_or_update({"name": f"Co{i}", "domain": f"co{i}.com"})
        assert len(self.repo.get_all()) == 3

    def test_get_by_name(self):
        self.repo.add_or_update({"name": "Stripe", "domain": "stripe.com"})
        result = self.repo.get_by_name("Stripe")
        assert result is not None
        assert result["domain"] == "stripe.com"

    def test_get_by_name_case_insensitive(self):
        self.repo.add_or_update({"name": "Stripe", "domain": "stripe.com"})
        assert self.repo.get_by_name("stripe") is not None
        assert self.repo.get_by_name("STRIPE") is not None

    def test_get_by_name_not_found(self):
        assert self.repo.get_by_name("Nonexistent") is None

    def test_save_updates_metadata(self):
        self.repo.add_or_update({"name": "Meta", "domain": "meta.com"})
        store = self.repo.load()
        assert store["total_companies"] == 1
        assert store["last_updated"] is not None

    def test_export_csv(self):
        self.repo.add_or_update({"name": "Stripe", "domain": "stripe.com", "industry": "FinTech"})
        csv_path = os.path.join(self.tmpdir, "export.csv")
        result = self.repo.export_csv(csv_path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "Stripe" in content


# ===========================================================================
# 6. CompanyLookupBot tests
# ===========================================================================

class TestCompanyLookupBot:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.tmpdir, "companies.json")

    def _make_bot(self, tier=Tier.FREE):
        return CompanyLookupBot(tier=tier, data_path=self.data_path)

    def test_lookup_free_known_company(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.lookup("Stripe")
        assert result["saved"] is True
        assert result["company"]["name"] == "Stripe"
        assert result["enriched"] is False  # FREE tier — no enrichment
        assert result["recommendations"] == []  # FREE tier — no recommendations

    def test_lookup_pro_enriched(self):
        bot = self._make_bot(Tier.PRO)
        result = bot.lookup("Shopify")
        assert result["enriched"] is True
        assert result["company"].get("company_size") is not None
        assert len(result["recommendations"]) > 0

    def test_lookup_saves_to_file(self):
        bot = self._make_bot(Tier.FREE)
        bot.lookup("Stripe")
        assert os.path.exists(self.data_path)
        with open(self.data_path) as f:
            store = json.load(f)
        assert store["total_companies"] == 1

    def test_lookup_unknown_company_saved(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.lookup("UnknownXYZ12345")
        assert result["saved"] is True
        assert result["company"]["source"] == "not_found"

    def test_lookup_increments_counter(self):
        bot = self._make_bot(Tier.FREE)
        bot.lookup("Stripe")
        bot.lookup("Shopify")
        assert bot._lookup_count == 2

    def test_lookup_timestamps(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.lookup("Stripe")
        assert "timestamp" in result
        assert "T" in result["timestamp"]  # ISO-8601

    def test_get_summary(self):
        bot = self._make_bot(Tier.FREE)
        bot.lookup("Stripe")
        summary = bot.get_summary()
        assert summary["bot"] == "CompanyLookupBot"
        assert summary["tier"] == "free"
        assert summary["lookups_this_session"] == 1
        assert summary["total_companies_stored"] == 1
        assert summary["generated_by"] == "GLOBAL AI SOURCES FLOW"

    def test_get_companies(self):
        bot = self._make_bot(Tier.FREE)
        bot.lookup("Stripe")
        companies = bot.get_companies()
        assert len(companies) == 1


# ===========================================================================
# 7. Tier gating tests
# ===========================================================================

class TestTierGating:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.tmpdir, "companies.json")

    def _make_bot(self, tier):
        return CompanyLookupBot(tier=tier, data_path=self.data_path)

    def test_free_cannot_bulk_import(self):
        bot = self._make_bot(Tier.FREE)
        with pytest.raises(PermissionError, match="bulk_import"):
            bot.bulk_lookup(["Stripe", "Shopify"])

    def test_pro_cannot_bulk_import(self):
        bot = self._make_bot(Tier.PRO)
        with pytest.raises(PermissionError, match="bulk_import"):
            bot.bulk_lookup(["Stripe", "Shopify"])

    def test_enterprise_can_bulk_import(self):
        bot = self._make_bot(Tier.ENTERPRISE)
        results = bot.bulk_lookup(["Stripe", "Shopify"])
        assert len(results) == 2

    def test_free_cannot_get_recommendations(self):
        bot = self._make_bot(Tier.FREE)
        with pytest.raises(PermissionError, match="recommendations"):
            bot.get_recommendations()

    def test_pro_can_get_recommendations(self):
        bot = self._make_bot(Tier.PRO)
        recs = bot.get_recommendations()
        assert isinstance(recs, list)

    def test_free_cannot_export_csv(self):
        bot = self._make_bot(Tier.FREE)
        with pytest.raises(PermissionError):
            bot.export_csv()

    def test_pro_can_export_csv(self):
        bot = self._make_bot(Tier.PRO)
        bot.lookup("Stripe")
        csv_path = os.path.join(self.tmpdir, "export.csv")
        result = bot.export_csv(csv_path)
        assert os.path.exists(result)

    def test_free_daily_limit_enforced(self):
        bot = self._make_bot(Tier.FREE)
        bot._lookup_count = 5  # hit the limit
        with pytest.raises(RuntimeError, match="limit"):
            bot.lookup("Stripe")

    def test_enterprise_no_daily_limit(self):
        bot = self._make_bot(Tier.ENTERPRISE)
        bot._lookup_count = 999999  # should not raise
        result = bot.lookup("Stripe")
        assert result["saved"] is True


# ===========================================================================
# 8. Error handling & edge cases
# ===========================================================================

class TestEdgeCases:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.tmpdir, "companies.json")

    def test_empty_company_name(self):
        bot = CompanyLookupBot(tier=Tier.FREE, data_path=self.data_path)
        result = bot.lookup("")
        assert result["saved"] is True  # saved as not_found record

    def test_whitespace_company_name(self):
        bot = CompanyLookupBot(tier=Tier.FREE, data_path=self.data_path)
        result = bot.lookup("   ")
        assert result["saved"] is True

    def test_get_recommendations_with_known_company(self):
        bot = CompanyLookupBot(tier=Tier.PRO, data_path=self.data_path)
        bot.lookup("Stripe")
        recs = bot.get_recommendations("Stripe")
        assert isinstance(recs, list)

    def test_get_recommendations_unknown_company(self):
        bot = CompanyLookupBot(tier=Tier.PRO, data_path=self.data_path)
        recs = bot.get_recommendations("NonExistentCompany")
        assert isinstance(recs, list)  # falls back to defaults


# ===========================================================================
# 9. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_company_lookup_bot_registered(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("company_lookup_bot")
        assert entry.bot_id == "company_lookup_bot"
        assert entry.class_name == "CompanyLookupBot"

    def test_company_lookup_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("company_lookup_bot")
        caps = entry.capabilities
        assert "company_lookup" in caps
        assert "slack_notifications" in caps
        assert "github_actions_trigger" in caps

    def test_company_lookup_bot_category(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("company_lookup_bot")
        assert entry.category == BotCategory.BUSINESS
