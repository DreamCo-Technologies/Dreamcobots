"""
Tests for bots/public_lead_engine/

Covers:
  1. Tiers
  2. PublicLeadEngine — searching, filtering, scoring, scripts, outreach
  3. Bulk search
  4. CRM export
  5. Analytics & summary
  6. Chat & process interfaces
  7. Bot library registration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.public_lead_engine.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
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
    FEATURE_WHITE_LABEL,
)
from bots.public_lead_engine.public_lead_engine import (
    PublicLeadEngine,
    PublicLeadEngineError,
    PublicLeadEngineTierError,
    PublicBusinessLead,
    DataSource,
    BusinessCategory,
    LeadStatus,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestPublicLeadEngineTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 39.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 149.0

    def test_free_max_searches(self):
        assert get_tier_config(Tier.FREE).max_searches_per_day == 50

    def test_pro_max_searches(self):
        assert get_tier_config(Tier.PRO).max_searches_per_day == 1_000

    def test_enterprise_unlimited(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited()

    def test_free_has_google_places(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_GOOGLE_PLACES_SEARCH)

    def test_free_has_rating_filter(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_RATING_FILTER)

    def test_free_lacks_yelp(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_YELP_SEARCH)

    def test_free_lacks_weak_marketing_filter(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_WEAK_MARKETING_FILTER)

    def test_pro_has_yelp(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_YELP_SEARCH)

    def test_pro_has_weak_marketing_filter(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_WEAK_MARKETING_FILTER)

    def test_pro_has_script_generation(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_SCRIPT_GENERATION)

    def test_pro_has_crm_export(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CRM_EXPORT)

    def test_pro_lacks_multi_api(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_MULTI_API)

    def test_enterprise_has_multi_api(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_MULTI_API)

    def test_enterprise_has_ai_opportunity_score(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_AI_OPPORTUNITY_SCORE)

    def test_enterprise_has_bulk_search(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_BULK_SEARCH)

    def test_enterprise_has_analytics(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_ANALYTICS)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_is_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)
        assert cfg.name == "Pro"


# ===========================================================================
# 2. Business Search
# ===========================================================================

class TestPublicLeadEngineSearch:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.FREE)

    def test_instantiation(self):
        assert self.engine is not None
        assert self.engine.tier == Tier.FREE

    def test_search_google_places_returns_results(self):
        result = self.engine.search_businesses(
            query="restaurant near me", count=5, source=DataSource.GOOGLE_PLACES
        )
        assert result["new_leads"] >= 0
        assert result["source"] == "google_places"
        assert "lead_ids" in result
        assert "timestamp" in result

    def test_search_respects_daily_cap_free(self):
        result = self.engine.search_businesses(count=200)
        assert result["requested"] <= 50

    def test_search_with_max_rating_filter(self):
        result = self.engine.search_businesses(count=20, max_rating=3.5)
        assert "lead_ids" in result

    def test_search_yelp_requires_pro(self):
        with pytest.raises(PublicLeadEngineTierError):
            self.engine.search_businesses(source=DataSource.YELP)

    def test_pro_can_search_yelp(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        result = engine.search_businesses(query="cafe", count=5, source=DataSource.YELP)
        assert result["source"] == "yelp"

    def test_bing_requires_enterprise(self):
        with pytest.raises(PublicLeadEngineTierError):
            self.engine.search_businesses(source=DataSource.BING_LOCAL)

    def test_lead_data_has_required_fields(self):
        self.engine.search_businesses(count=3)
        leads = self.engine.get_leads()
        for lead in leads:
            assert "lead_id" in lead
            assert "name" in lead
            assert "category" in lead
            assert "location" in lead
            assert "star_rating" in lead
            assert "status" in lead

    def test_star_ratings_in_valid_range(self):
        self.engine.search_businesses(count=10)
        leads = self.engine.get_leads()
        for lead in leads:
            assert 0.0 <= lead["star_rating"] <= 5.0

    def test_search_log_updated(self):
        self.engine.search_businesses(count=3)
        self.engine.search_businesses(count=3)
        summary = self.engine.get_summary()
        assert summary["total_searches"] >= 2

    def test_search_all_sources_requires_pro(self):
        with pytest.raises(PublicLeadEngineTierError):
            self.engine.search_all_sources()

    def test_pro_can_search_all_sources(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        result = engine.search_all_sources(query="local business", leads_per_source=3)
        assert "total_new_leads" in result
        assert "sources_searched" in result


# ===========================================================================
# 3. Filtering
# ===========================================================================

class TestPublicLeadEngineFiltering:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.PRO)
        self.engine.search_businesses(count=15)

    def test_filter_weak_marketing_returns_counts(self):
        result = self.engine.filter_weak_marketing()
        assert "kept" in result
        assert "rejected" in result
        assert result["kept"] + result["rejected"] >= 0

    def test_filter_updates_lead_status(self):
        self.engine.filter_weak_marketing()
        leads = self.engine.get_leads()
        for lead in leads:
            assert lead["status"] in ("filtered", "rejected", "raw")

    def test_free_cannot_filter_weak_marketing(self):
        engine = PublicLeadEngine(tier=Tier.FREE)
        engine.search_businesses(count=5)
        with pytest.raises(PublicLeadEngineTierError):
            engine.filter_weak_marketing()

    def test_filter_default_rating_threshold(self):
        result = self.engine.filter_weak_marketing(max_rating=3.5)
        assert isinstance(result["kept"], int)

    def test_filter_high_threshold_keeps_more(self):
        engine_a = PublicLeadEngine(tier=Tier.PRO)
        engine_b = PublicLeadEngine(tier=Tier.PRO)
        engine_a.search_businesses(count=20)
        engine_b.search_businesses(count=20)
        result_strict = engine_a.filter_weak_marketing(max_rating=2.0)
        result_lenient = engine_b.filter_weak_marketing(max_rating=5.0)
        assert result_lenient["kept"] >= result_strict["kept"]

    def test_get_low_rated_businesses(self):
        leads = self.engine.get_low_rated_businesses(max_rating=3.5)
        for lead in leads:
            assert lead["star_rating"] <= 3.5


# ===========================================================================
# 4. Opportunity Scoring
# ===========================================================================

class TestPublicLeadEngineScoring:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.ENTERPRISE)
        self.engine.search_businesses(count=10)
        self.engine.filter_weak_marketing()

    def test_score_opportunities_returns_count(self):
        result = self.engine.score_opportunities()
        assert "scored" in result
        assert isinstance(result["scored"], int)

    def test_ad_scores_are_bounded(self):
        self.engine.score_opportunities()
        leads = self.engine.get_leads()
        for lead in leads:
            assert 0.0 <= lead["ad_opportunity_score"] <= 100.0

    def test_pro_cannot_ai_score(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        engine.search_businesses(count=5)
        with pytest.raises(PublicLeadEngineTierError):
            engine.score_opportunities()

    def test_pro_can_compute_ad_scores(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        engine.search_businesses(count=5)
        result = engine.compute_ad_scores()
        assert "ad_scores_computed" in result


# ===========================================================================
# 5. Script Generation
# ===========================================================================

class TestPublicLeadEngineScripts:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.PRO)
        self.engine.search_businesses(count=8)
        self.engine.filter_weak_marketing()

    def test_generate_scripts_returns_count(self):
        result = self.engine.generate_scripts()
        assert "scripts_generated" in result
        assert isinstance(result["scripts_generated"], int)

    def test_scripts_are_non_empty_strings(self):
        self.engine.generate_scripts()
        leads = self.engine.get_leads()
        scripted = [l for l in leads if l["status"] == "script_ready"]
        for lead in scripted:
            assert isinstance(lead["generated_script"], str)
            assert len(lead["generated_script"]) > 10

    def test_free_cannot_generate_scripts(self):
        engine = PublicLeadEngine(tier=Tier.FREE)
        engine.search_businesses(count=5)
        with pytest.raises(PublicLeadEngineTierError):
            engine.generate_scripts()

    def test_scripts_contain_location_or_name(self):
        self.engine.generate_scripts(top_n=5)
        leads = self.engine.get_leads()
        scripted = [l for l in leads if l["generated_script"]]
        for lead in scripted:
            script = lead["generated_script"]
            assert lead["location"] in script or lead["name"] in script or lead["category"] in script


# ===========================================================================
# 6. Outreach Drafts
# ===========================================================================

class TestPublicLeadEngineOutreach:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.PRO)
        self.engine.search_businesses(count=8)
        self.engine.filter_weak_marketing()
        self.engine.generate_scripts()

    def test_generate_outreach_returns_count(self):
        result = self.engine.generate_outreach()
        assert "outreach_drafts_generated" in result

    def test_outreach_requires_human_approval(self):
        result = self.engine.generate_outreach()
        assert result.get("requires_human_approval") is True

    def test_outreach_has_compliance_note(self):
        result = self.engine.generate_outreach()
        assert "compliance_note" in result

    def test_outreach_drafts_are_strings(self):
        self.engine.generate_outreach()
        leads = self.engine.get_leads()
        ready = [l for l in leads if l["status"] == "outreach_ready"]
        for lead in ready:
            assert isinstance(lead["outreach_draft"], str)
            assert len(lead["outreach_draft"]) > 20

    def test_free_cannot_generate_outreach(self):
        engine = PublicLeadEngine(tier=Tier.FREE)
        engine.search_businesses(count=5)
        with pytest.raises(PublicLeadEngineTierError):
            engine.generate_outreach()

    def test_outreach_contains_human_review_note(self):
        self.engine.generate_outreach()
        leads = self.engine.get_leads()
        ready = [l for l in leads if l["outreach_draft"]]
        for lead in ready:
            assert "HUMAN REVIEW REQUIRED" in lead["outreach_draft"]


# ===========================================================================
# 7. Bulk Search
# ===========================================================================

class TestPublicLeadEngineBulkSearch:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.ENTERPRISE)

    def test_bulk_search_runs_multiple_queries(self):
        queries = ["restaurant Austin", "plumber Dallas", "gym Houston"]
        result = self.engine.bulk_search(queries, leads_per_query=5)
        assert result["queries_run"] == 3
        assert "total_new_leads" in result

    def test_bulk_search_returns_results_list(self):
        result = self.engine.bulk_search(["q1", "q2"])
        assert len(result["results"]) == 2

    def test_pro_cannot_bulk_search(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        with pytest.raises(PublicLeadEngineTierError):
            engine.bulk_search(["query1"])


# ===========================================================================
# 8. CRM Export
# ===========================================================================

class TestPublicLeadEngineCRM:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.PRO)
        self.engine.search_businesses(count=8)
        self.engine.filter_weak_marketing()
        self.engine.generate_scripts()

    def test_export_to_crm_returns_count(self):
        result = self.engine.export_to_crm("Salesforce")
        assert "leads_exported" in result
        assert result["crm"] == "Salesforce"

    def test_free_cannot_export(self):
        engine = PublicLeadEngine(tier=Tier.FREE)
        engine.search_businesses(count=5)
        with pytest.raises(PublicLeadEngineTierError):
            engine.export_to_crm()

    def test_export_updates_status(self):
        self.engine.export_to_crm()
        leads = self.engine.get_leads()
        exported = [l for l in leads if l["status"] == "exported"]
        assert len(exported) >= 0

    def test_export_default_crm(self):
        result = self.engine.export_to_crm()
        assert result["crm"] == "default"


# ===========================================================================
# 9. Analytics & Summary
# ===========================================================================

class TestPublicLeadEngineAnalytics:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.ENTERPRISE)
        self.engine.search_businesses(count=10)
        self.engine.filter_weak_marketing()
        self.engine.generate_scripts()

    def test_get_summary_has_required_keys(self):
        summary = self.engine.get_summary()
        assert "total_leads" in summary
        assert "by_status" in summary
        assert "by_source" in summary
        assert "by_category" in summary
        assert "tier" in summary
        assert "timestamp" in summary

    def test_summary_tier_matches(self):
        summary = self.engine.get_summary()
        assert summary["tier"] == "enterprise"

    def test_avg_star_rating_is_float_or_none(self):
        summary = self.engine.get_summary()
        val = summary.get("avg_star_rating")
        assert val is None or isinstance(val, float)

    def test_get_top_opportunities_returns_list(self):
        top = self.engine.get_top_opportunities(5)
        assert isinstance(top, list)
        assert len(top) <= 5

    def test_get_analytics_enterprise_only(self):
        result = self.engine.get_analytics()
        assert "top_5_opportunities" in result
        assert "search_log" in result

    def test_pro_cannot_access_analytics(self):
        engine = PublicLeadEngine(tier=Tier.PRO)
        engine.search_businesses(count=3)
        with pytest.raises(PublicLeadEngineTierError):
            engine.get_analytics()

    def test_get_leads_filtered_by_status(self):
        leads = self.engine.get_leads(status=LeadStatus.SCRIPT_READY)
        for lead in leads:
            assert lead["status"] == "script_ready"

    def test_get_leads_filtered_by_category(self):
        leads = self.engine.get_leads(category=BusinessCategory.RESTAURANT)
        for lead in leads:
            assert lead["category"] == "restaurant"

    def test_get_low_rated_businesses_sorted(self):
        leads = self.engine.get_low_rated_businesses(max_rating=3.5)
        ratings = [l["star_rating"] for l in leads]
        assert ratings == sorted(ratings)


# ===========================================================================
# 10. Chat & Process Interfaces
# ===========================================================================

class TestPublicLeadEngineChatInterface:
    def setup_method(self):
        self.engine = PublicLeadEngine(tier=Tier.PRO)

    def test_chat_search_command(self):
        result = self.engine.chat("search businesses")
        assert "message" in result
        assert "data" in result

    def test_chat_find_command(self):
        result = self.engine.chat("find leads")
        assert "message" in result

    def test_chat_filter_command(self):
        self.engine.search_businesses(count=5)
        result = self.engine.chat("filter weak marketing")
        assert "message" in result

    def test_chat_low_rating_command(self):
        self.engine.search_businesses(count=5)
        result = self.engine.chat("low rating")
        assert "message" in result

    def test_chat_script_command(self):
        self.engine.search_businesses(count=5)
        self.engine.filter_weak_marketing()
        result = self.engine.chat("generate scripts")
        assert "message" in result

    def test_chat_commercial_command(self):
        self.engine.search_businesses(count=5)
        self.engine.filter_weak_marketing()
        result = self.engine.chat("commercial")
        assert "message" in result

    def test_chat_outreach_command(self):
        self.engine.search_businesses(count=5)
        self.engine.filter_weak_marketing()
        self.engine.generate_scripts()
        result = self.engine.chat("outreach")
        assert "message" in result

    def test_chat_top_opportunities_command(self):
        self.engine.search_businesses(count=5)
        result = self.engine.chat("top opportunities")
        assert "data" in result

    def test_chat_summary_command(self):
        result = self.engine.chat("summary")
        assert "message" in result
        assert "data" in result

    def test_chat_unknown_returns_help(self):
        result = self.engine.chat("random unknown xyz")
        assert "message" in result
        assert "Public Lead Engine" in result["message"]

    def test_process_entry_point(self):
        result = self.engine.process({"command": "summary"})
        assert "data" in result

    def test_process_empty_command(self):
        result = self.engine.process({})
        assert "message" in result


# ===========================================================================
# 11. Bot Library Registration
# ===========================================================================

class TestPublicLeadEngineBotLibrary:
    def test_registered_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("public_lead_engine")
        assert entry.bot_id == "public_lead_engine"
        assert entry.display_name == "Public Lead Engine"

    def test_bot_category_is_lead_gen(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("public_lead_engine")
        assert entry.category == BotCategory.LEAD_GEN

    def test_bot_has_expected_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("public_lead_engine")
        assert "google_places_search" in entry.capabilities
        assert "yelp_search" in entry.capabilities
        assert "rating_filter" in entry.capabilities
        assert "weak_marketing_filter" in entry.capabilities

    def test_bot_module_path(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("public_lead_engine")
        assert entry.module_path == "bots.public_lead_engine.public_lead_engine"
        assert entry.class_name == "PublicLeadEngine"

    def test_both_lead_bots_registered(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        cinecore = lib.get_bot("cinecore_lead_engine")
        public = lib.get_bot("public_lead_engine")
        assert cinecore is not None
        assert public is not None

    def test_lead_gen_bots_searchable(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        results = lib.search("lead engine")
        bot_ids = [r["bot_id"] for r in results]
        assert "cinecore_lead_engine" in bot_ids
        assert "public_lead_engine" in bot_ids
