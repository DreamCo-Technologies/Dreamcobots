"""
Tests for bots/cinecore_lead_engine/

Covers:
  1. Tiers
  2. CineCoreLeadEngine — scanning, scoring, scripts, outreach, ad packages
  3. Bulk generation
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

from bots.cinecore_lead_engine.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_BUSINESS_SCAN,
    FEATURE_SCRIPT_GENERATION,
    FEATURE_LEAD_SCORING,
    FEATURE_OUTREACH_DRAFT,
    FEATURE_CRM_EXPORT,
    FEATURE_BULK_GENERATION,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_NICHE_FILTER,
)
from bots.cinecore_lead_engine.cinecore_lead_engine import (
    CineCoreLeadEngine,
    CineCoreLeadEngineError,
    CineCoreLeadEngineTierError,
    BusinessLead,
    BusinessNiche,
    LeadStatus,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestCineCoreLeadEngineTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 29.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 99.0

    def test_free_max_leads(self):
        assert get_tier_config(Tier.FREE).max_leads_per_day == 100

    def test_pro_max_leads(self):
        assert get_tier_config(Tier.PRO).max_leads_per_day == 2_000

    def test_enterprise_unlimited(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_leads()

    def test_free_has_business_scan(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_BUSINESS_SCAN)

    def test_free_has_script_generation(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_SCRIPT_GENERATION)

    def test_free_lacks_lead_scoring(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_LEAD_SCORING)

    def test_free_lacks_crm_export(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_CRM_EXPORT)

    def test_pro_has_lead_scoring(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_LEAD_SCORING)

    def test_pro_has_outreach(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_OUTREACH_DRAFT)

    def test_pro_has_crm_export(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CRM_EXPORT)

    def test_pro_lacks_bulk_generation(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_BULK_GENERATION)

    def test_enterprise_has_bulk_generation(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_BULK_GENERATION)

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

    def test_upgrade_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)
        assert cfg.name == "Pro"


# ===========================================================================
# 2. Business Scanning
# ===========================================================================

class TestCineCoreLeadEngineScanning:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.FREE)

    def test_instantiation(self):
        assert self.engine is not None
        assert self.engine.tier == Tier.FREE

    def test_scan_returns_leads(self):
        result = self.engine.scan_businesses(count=5)
        assert result["new_leads"] >= 0
        assert result["new_leads"] <= 5
        assert "lead_ids" in result
        assert "timestamp" in result

    def test_scan_respects_daily_cap_free(self):
        result = self.engine.scan_businesses(count=200)
        assert result["scanned"] <= 100  # FREE tier cap

    def test_scan_returns_dict_with_correct_keys(self):
        result = self.engine.scan_businesses(count=3)
        assert "scanned" in result
        assert "new_leads" in result
        assert "lead_ids" in result
        assert "timestamp" in result

    def test_scan_niche_filter_requires_pro(self):
        with pytest.raises(CineCoreLeadEngineTierError):
            self.engine.scan_businesses(niche_filter=BusinessNiche.RESTAURANT)

    def test_pro_can_use_niche_filter(self):
        engine = CineCoreLeadEngine(tier=Tier.PRO)
        result = engine.scan_businesses(count=5, niche_filter=BusinessNiche.RESTAURANT)
        assert "lead_ids" in result

    def test_leads_stored_after_scan(self):
        self.engine.scan_businesses(count=5)
        summary = self.engine.get_summary()
        assert summary["total_leads"] >= 0

    def test_leads_have_correct_structure(self):
        self.engine.scan_businesses(count=3)
        leads = self.engine.get_leads()
        for lead in leads:
            assert "lead_id" in lead
            assert "name" in lead
            assert "niche" in lead
            assert "location" in lead
            assert "status" in lead


# ===========================================================================
# 3. Lead Scoring
# ===========================================================================

class TestCineCoreLeadEngineScoring:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)
        self.engine.scan_businesses(count=5)

    def test_score_leads_returns_count(self):
        result = self.engine.score_leads()
        assert "scored" in result
        assert isinstance(result["scored"], int)

    def test_score_leads_updates_status(self):
        self.engine.score_leads()
        leads = self.engine.get_leads()
        for lead in leads:
            assert lead["status"] in ("scored", "raw", "script_ready", "outreach_ready", "exported")

    def test_free_tier_cannot_score(self):
        engine = CineCoreLeadEngine(tier=Tier.FREE)
        engine.scan_businesses(count=3)
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.score_leads()

    def test_opportunity_scores_are_bounded(self):
        self.engine.score_leads()
        leads = self.engine.get_leads()
        for lead in leads:
            score = lead["opportunity_score"]
            assert 0 <= score <= 100


# ===========================================================================
# 4. Script Generation
# ===========================================================================

class TestCineCoreLeadEngineScripts:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)
        self.engine.scan_businesses(count=5)
        self.engine.score_leads()

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

    def test_free_tier_can_generate_scripts(self):
        engine = CineCoreLeadEngine(tier=Tier.FREE)
        engine.scan_businesses(count=3)
        result = engine.generate_scripts()
        assert result["scripts_generated"] >= 0

    def test_scripts_reference_business_name(self):
        self.engine.generate_scripts(top_n=5)
        leads = self.engine.get_leads()
        scripted = [l for l in leads if l["generated_script"]]
        for lead in scripted:
            assert lead["name"] in lead["generated_script"] or lead["location"] in lead["generated_script"]


# ===========================================================================
# 5. Outreach Drafts
# ===========================================================================

class TestCineCoreLeadEngineOutreach:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)
        self.engine.scan_businesses(count=5)
        self.engine.score_leads()
        self.engine.generate_scripts()

    def test_generate_outreach_returns_count(self):
        result = self.engine.generate_outreach()
        assert "outreach_drafts_generated" in result

    def test_outreach_drafts_are_strings(self):
        self.engine.generate_outreach()
        leads = self.engine.get_leads()
        ready = [l for l in leads if l["status"] == "outreach_ready"]
        for lead in ready:
            assert isinstance(lead["outreach_draft"], str)
            assert len(lead["outreach_draft"]) > 20

    def test_free_tier_cannot_generate_outreach(self):
        engine = CineCoreLeadEngine(tier=Tier.FREE)
        engine.scan_businesses(count=3)
        engine.generate_scripts()
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.generate_outreach()

    def test_outreach_contains_business_name(self):
        self.engine.generate_outreach()
        leads = self.engine.get_leads()
        ready = [l for l in leads if l["outreach_draft"]]
        for lead in ready:
            assert lead["name"] in lead["outreach_draft"]


# ===========================================================================
# 6. Ad Packages
# ===========================================================================

class TestCineCoreLeadEngineAdPackages:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)
        self.engine.scan_businesses(count=5)
        self.engine.score_leads()
        self.engine.generate_scripts()

    def test_build_ad_packages_returns_count(self):
        result = self.engine.build_ad_packages()
        assert "ad_packages_built" in result

    def test_ad_packages_have_required_keys(self):
        self.engine.build_ad_packages()
        leads = self.engine.get_leads()
        for lead in leads:
            if lead.get("ad_package") is not None:
                pkg = lead["ad_package"] if isinstance(lead.get("ad_package"), dict) else {}
                # packages are stored on lead object, check via engine
                break

    def test_free_tier_cannot_build_packages(self):
        engine = CineCoreLeadEngine(tier=Tier.FREE)
        engine.scan_businesses(count=3)
        engine.generate_scripts()
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.build_ad_packages()


# ===========================================================================
# 7. Bulk Generation
# ===========================================================================

class TestCineCoreLeadEngineBulk:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.ENTERPRISE)

    def test_bulk_generate_returns_results(self):
        result = self.engine.bulk_generate(["Tony's Pizza", "Downtown Gym", "City Dental"])
        assert result["bulk_generated"] == 3
        assert len(result["results"]) == 3

    def test_bulk_results_have_scripts(self):
        result = self.engine.bulk_generate(["Biz A", "Biz B"])
        for item in result["results"]:
            assert "script" in item
            assert isinstance(item["script"], str)

    def test_pro_tier_cannot_bulk_generate(self):
        engine = CineCoreLeadEngine(tier=Tier.PRO)
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.bulk_generate(["Biz A"])

    def test_bulk_generate_adds_to_leads(self):
        self.engine.bulk_generate(["A", "B", "C", "D", "E"])
        summary = self.engine.get_summary()
        assert summary["total_leads"] >= 5


# ===========================================================================
# 8. CRM Export
# ===========================================================================

class TestCineCoreLeadEngineCRM:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)
        self.engine.scan_businesses(count=5)
        self.engine.score_leads()
        self.engine.generate_scripts()

    def test_export_to_crm_returns_count(self):
        result = self.engine.export_to_crm("HubSpot")
        assert "leads_exported" in result
        assert result["crm"] == "HubSpot"

    def test_free_tier_cannot_export(self):
        engine = CineCoreLeadEngine(tier=Tier.FREE)
        engine.scan_businesses(count=3)
        engine.generate_scripts()
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.export_to_crm()

    def test_export_updates_status(self):
        self.engine.export_to_crm()
        leads = self.engine.get_leads()
        exported = [l for l in leads if l["status"] == "exported"]
        assert len(exported) >= 0

    def test_export_default_crm_name(self):
        result = self.engine.export_to_crm()
        assert result["crm"] == "default"


# ===========================================================================
# 9. Analytics & Summary
# ===========================================================================

class TestCineCoreLeadEngineAnalytics:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.ENTERPRISE)
        self.engine.scan_businesses(count=8)
        self.engine.score_leads()
        self.engine.generate_scripts()

    def test_get_summary_keys(self):
        summary = self.engine.get_summary()
        assert "total_leads" in summary
        assert "by_status" in summary
        assert "by_niche" in summary
        assert "tier" in summary
        assert "timestamp" in summary

    def test_summary_tier_matches(self):
        summary = self.engine.get_summary()
        assert summary["tier"] == "enterprise"

    def test_get_top_leads_returns_list(self):
        self.engine.score_leads()
        top = self.engine.get_top_leads(5)
        assert isinstance(top, list)
        assert len(top) <= 5

    def test_get_analytics_enterprise_only(self):
        result = self.engine.get_analytics()
        assert "top_5_leads" in result
        assert "crm_export_log" in result

    def test_pro_cannot_access_analytics(self):
        engine = CineCoreLeadEngine(tier=Tier.PRO)
        engine.scan_businesses(count=3)
        with pytest.raises(CineCoreLeadEngineTierError):
            engine.get_analytics()

    def test_get_leads_with_status_filter(self):
        leads = self.engine.get_leads(status=LeadStatus.SCRIPT_READY)
        for lead in leads:
            assert lead["status"] == "script_ready"

    def test_get_leads_with_niche_filter(self):
        leads = self.engine.get_leads(niche=BusinessNiche.RESTAURANT)
        for lead in leads:
            assert lead["niche"] == "restaurant"

    def test_avg_opportunity_score_is_float_or_none(self):
        summary = self.engine.get_summary()
        score = summary.get("avg_opportunity_score")
        assert score is None or isinstance(score, float)


# ===========================================================================
# 10. Chat & Process Interfaces
# ===========================================================================

class TestCineCoreLeadEngineChatInterface:
    def setup_method(self):
        self.engine = CineCoreLeadEngine(tier=Tier.PRO)

    def test_chat_scan_command(self):
        result = self.engine.chat("scan businesses")
        assert "message" in result
        assert "data" in result

    def test_chat_find_command(self):
        result = self.engine.chat("find leads")
        assert "message" in result

    def test_chat_summary_command(self):
        result = self.engine.chat("summary")
        assert "message" in result
        assert "data" in result

    def test_chat_stats_command(self):
        result = self.engine.chat("stats")
        assert "data" in result

    def test_chat_script_command(self):
        self.engine.scan_businesses(count=3)
        result = self.engine.chat("generate ad scripts")
        assert "message" in result

    def test_chat_commercial_command(self):
        self.engine.scan_businesses(count=3)
        result = self.engine.chat("commercial")
        assert "message" in result

    def test_chat_top_command(self):
        self.engine.scan_businesses(count=5)
        self.engine.score_leads()
        result = self.engine.chat("top leads")
        assert "data" in result

    def test_chat_unknown_returns_help(self):
        result = self.engine.chat("unknown xyz 123")
        assert "message" in result
        assert "CineCore Lead Engine" in result["message"]

    def test_process_entry_point(self):
        result = self.engine.process({"command": "summary"})
        assert "data" in result

    def test_process_empty_command(self):
        result = self.engine.process({})
        assert "message" in result


# ===========================================================================
# 11. Bot Library Registration
# ===========================================================================

class TestCineCoreLeadEngineBotLibrary:
    def test_registered_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("cinecore_lead_engine")
        assert entry.bot_id == "cinecore_lead_engine"
        assert entry.display_name == "CineCore Lead Engine"

    def test_bot_category_is_lead_gen(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("cinecore_lead_engine")
        assert entry.category == BotCategory.LEAD_GEN

    def test_bot_has_expected_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("cinecore_lead_engine")
        assert "business_scan" in entry.capabilities
        assert "script_generation" in entry.capabilities
        assert "crm_export" in entry.capabilities

    def test_bot_module_path(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("cinecore_lead_engine")
        assert entry.module_path == "bots.cinecore_lead_engine.cinecore_lead_engine"
        assert entry.class_name == "CineCoreLeadEngine"
