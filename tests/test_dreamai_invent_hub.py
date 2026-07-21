"""
Tests for bots/dreamai_invent_hub/

Covers:
  1. Tiers
  2. Matchmaking Engine
  3. Inventor Toolkit
     3a. DesignBot
     3b. FinancialProjectionBot
     3c. ManufacturingSimulator
     3d. PatentSupportAI
  4. R&D Marketplace
     4a. Directory
     4b. Forum
     4c. Prototyping Tools
  5. DreamAIInventHub main class (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.dreamai_invent_hub.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_MATCHMAKING,
    FEATURE_ADVANCED_MATCHMAKING,
    FEATURE_INVENTOR_TOOLKIT,
    FEATURE_DESIGN_BOT,
    FEATURE_FINANCIAL_PROJECTION,
    FEATURE_MANUFACTURING_SIMULATOR,
    FEATURE_PATENT_SUPPORT,
    FEATURE_FORUMS,
    FEATURE_MARKETPLACE_BROWSE,
    FEATURE_MARKETPLACE_LISTING,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_LICENSING_TEMPLATES,
    FEATURE_REVENUE_SHARING,
    FEATURE_IOT_LAB,
    FEATURE_PROTOTYPING_LAB,
)
from bots.dreamai_invent_hub.matchmaking import (
    MatchmakingEngine,
    Profile,
    ProfileType,
    CollaborationType,
    MatchStatus,
    Match,
)
from bots.dreamai_invent_hub.inventor_toolkit import (
    DesignBot,
    DesignDomain,
    DesignStage,
    FinancialProjectionBot,
    HardwareCostBreakdown,
    ManufacturingSimulator,
    ManufacturingMethod,
    PatentSupportAI,
    PatentType,
    PatentStatus,
    InventorToolkit,
)
from bots.dreamai_invent_hub.marketplace import (
    RDMarketplace,
    DirectoryCategory,
    DirectoryListing,
    ServiceType,
    ListingStatus,
    ForumCategory,
    ForumPost,
    PostType,
    PrototypingTool,
)
from bots.dreamai_invent_hub.dreamai_invent_hub import (
    DreamAIInventHub,
    DreamAIInventHubTierError,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_enterprise_unlimited_matches(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_matches()

    def test_free_tier_has_match_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_matches_per_month == 5

    def test_pro_tier_has_match_limit(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_matches_per_month == 100

    def test_free_has_basic_matchmaking(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_BASIC_MATCHMAKING)

    def test_free_lacks_advanced_matchmaking(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_ADVANCED_MATCHMAKING)

    def test_pro_has_advanced_matchmaking(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_ADVANCED_MATCHMAKING)

    def test_pro_has_forums(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_FORUMS)

    def test_pro_has_patent_support(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_PATENT_SUPPORT)

    def test_enterprise_has_api_access(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_iot_lab(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_IOT_LAB)

    def test_upgrade_from_free(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_from_pro(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_marketplace_listing_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_marketplace_listings == 0

    def test_tier_config_is_tier_config_instance(self):
        cfg = get_tier_config(Tier.FREE)
        assert isinstance(cfg, TierConfig)

    def test_all_tiers_have_support_level(self):
        for tier in Tier:
            cfg = get_tier_config(tier)
            assert cfg.support_level


# ===========================================================================
# 2. Matchmaking Engine
# ===========================================================================

class TestMatchmakingEngine:
    def _make_engine(self):
        return MatchmakingEngine()

    def test_seed_profiles_loaded(self):
        engine = self._make_engine()
        profiles = engine.list_profiles()
        assert len(profiles) >= 6

    def test_register_profile(self):
        engine = self._make_engine()
        profile = Profile(
            profile_id="TEST-001",
            name="Test AI Co",
            profile_type=ProfileType.AI_COMPANY,
            expertise=["computer vision", "nlp"],
            collaboration_types=[CollaborationType.CO_DEVELOPMENT],
        )
        returned_id = engine.register_profile(profile)
        assert returned_id == "TEST-001"
        assert engine.get_profile("TEST-001") is not None

    def test_get_nonexistent_profile(self):
        engine = self._make_engine()
        assert engine.get_profile("NONEXISTENT") is None

    def test_find_matches_returns_list(self):
        engine = self._make_engine()
        matches = engine.find_matches("SEED-INV-001")
        assert isinstance(matches, list)

    def test_find_matches_excludes_self(self):
        engine = self._make_engine()
        matches = engine.find_matches("SEED-AI-001")
        profile_ids = [m["profile"]["profile_id"] for m in matches]
        assert "SEED-AI-001" not in profile_ids

    def test_find_matches_score_between_0_and_1(self):
        engine = self._make_engine()
        matches = engine.find_matches("SEED-INV-001")
        for m in matches:
            assert 0.0 <= m["score"] <= 1.0

    def test_find_matches_sorted_by_score_descending(self):
        engine = self._make_engine()
        matches = engine.find_matches("SEED-INV-001")
        scores = [m["score"] for m in matches]
        assert scores == sorted(scores, reverse=True)

    def test_find_matches_filter_by_collaboration_type(self):
        engine = self._make_engine()
        matches = engine.find_matches(
            "SEED-INV-001",
            collaboration_type=CollaborationType.IOT_COLLABORATION,
        )
        for m in matches:
            assert CollaborationType.IOT_COLLABORATION.value in m["profile"]["collaboration_types"]

    def test_find_matches_empty_for_unknown_profile(self):
        engine = self._make_engine()
        assert engine.find_matches("UNKNOWN") == []

    def test_create_match(self):
        engine = self._make_engine()
        match = engine.create_match(
            requester_id="SEED-INV-001",
            partner_id="SEED-AI-001",
            collaboration_type=CollaborationType.CO_DEVELOPMENT,
            project_description="Develop AI-powered wearable sensor",
        )
        assert match.match_id.startswith("MATCH-")
        assert match.status == MatchStatus.PENDING
        assert match.compatibility_score >= 0.0

    def test_create_match_stored(self):
        engine = self._make_engine()
        match = engine.create_match(
            requester_id="SEED-INV-001",
            partner_id="SEED-AI-001",
            collaboration_type=CollaborationType.LICENSING,
            project_description="License IoT sensor technology",
        )
        retrieved = engine.get_match(match.match_id)
        assert retrieved is not None
        assert retrieved.match_id == match.match_id

    def test_update_match_status(self):
        engine = self._make_engine()
        match = engine.create_match(
            requester_id="SEED-INV-001",
            partner_id="SEED-ROB-001",
            collaboration_type=CollaborationType.CONTRACT_MANUFACTURING,
            project_description="Manufacture prototype batch",
        )
        result = engine.update_match_status(match.match_id, MatchStatus.ACCEPTED)
        assert result is True
        assert engine.get_match(match.match_id).status == MatchStatus.ACCEPTED

    def test_update_nonexistent_match_returns_false(self):
        engine = self._make_engine()
        assert engine.update_match_status("FAKE-9999", MatchStatus.ACCEPTED) is False

    def test_send_message(self):
        engine = self._make_engine()
        match = engine.create_match(
            "SEED-INV-001", "SEED-AI-001",
            CollaborationType.CO_DEVELOPMENT, "Joint dev project",
        )
        result = engine.send_message(match.match_id, "SEED-INV-001", "Hello!")
        assert result is True
        assert len(engine.get_match(match.match_id).messages) == 1

    def test_send_message_nonexistent_match(self):
        engine = self._make_engine()
        assert engine.send_message("FAKE", "USER", "msg") is False

    def test_list_matches_by_profile(self):
        engine = self._make_engine()
        engine.create_match(
            "SEED-INV-001", "SEED-AI-001",
            CollaborationType.CO_DEVELOPMENT, "Project A",
        )
        engine.create_match(
            "SEED-ROB-001", "SEED-ELEC-001",
            CollaborationType.CONTRACT_MANUFACTURING, "Project B",
        )
        inv_matches = engine.list_matches(profile_id="SEED-INV-001")
        assert all(
            m.requester_id == "SEED-INV-001" or m.partner_id == "SEED-INV-001"
            for m in inv_matches
        )

    def test_generate_licensing_terms_template(self):
        engine = self._make_engine()
        tmpl = engine.generate_terms_template(CollaborationType.LICENSING)
        assert tmpl["type"] == "licensing"
        assert "royalty_rate_pct" in tmpl

    def test_generate_revenue_sharing_template(self):
        engine = self._make_engine()
        tmpl = engine.generate_terms_template(CollaborationType.REVENUE_SHARING)
        assert tmpl["type"] == "revenue_sharing"
        assert "developer_share_pct" in tmpl

    def test_generate_iot_collaboration_template(self):
        engine = self._make_engine()
        tmpl = engine.generate_terms_template(CollaborationType.IOT_COLLABORATION)
        assert tmpl["type"] == "iot_collaboration"

    def test_generate_co_development_template(self):
        engine = self._make_engine()
        tmpl = engine.generate_terms_template(CollaborationType.CO_DEVELOPMENT)
        assert tmpl["type"] == "co_development"

    def test_profile_to_dict(self):
        profile = Profile(
            profile_id="P001",
            name="Test",
            profile_type=ProfileType.INVENTOR,
            expertise=["iot"],
            collaboration_types=[CollaborationType.LICENSING],
        )
        d = profile.to_dict()
        assert d["profile_type"] == "inventor"
        assert "licensing" in d["collaboration_types"]

    def test_match_to_dict(self):
        engine = self._make_engine()
        match = engine.create_match(
            "SEED-INV-001", "SEED-AI-001",
            CollaborationType.EQUITY_PARTNERSHIP, "Equity deal",
        )
        d = match.to_dict()
        assert d["collaboration_type"] == "equity_partnership"
        assert "status" in d

    def test_filter_profiles_by_type(self):
        engine = self._make_engine()
        ai_profiles = engine.list_profiles(profile_type=ProfileType.AI_COMPANY)
        assert all(p.profile_type == ProfileType.AI_COMPANY for p in ai_profiles)

    def test_match_with_proposed_terms(self):
        engine = self._make_engine()
        terms = {"royalty_rate_pct": 7.5, "license_duration_years": 5}
        match = engine.create_match(
            "SEED-INV-001", "SEED-AI-001",
            CollaborationType.LICENSING, "License deal",
            proposed_terms=terms,
        )
        assert match.proposed_terms["royalty_rate_pct"] == 7.5


# ===========================================================================
# 3a. DesignBot
# ===========================================================================

class TestDesignBot:
    def _bot(self):
        return DesignBot()

    def test_start_session_returns_session(self):
        bot = self._bot()
        session = bot.start_session("Smart Glove", DesignDomain.IOT, DesignStage.PROTOTYPE)
        assert session.session_id.startswith("DESIGN-")
        assert session.product_name == "Smart Glove"

    def test_session_has_suggestions(self):
        bot = self._bot()
        session = bot.start_session("Robot Arm", DesignDomain.ROBOTICS, DesignStage.CONCEPT)
        assert len(session.suggestions) > 0

    def test_session_has_components(self):
        bot = self._bot()
        session = bot.start_session("Wearable", DesignDomain.WEARABLES, DesignStage.MVP)
        assert len(session.components) > 0

    def test_iterate_increments_counter(self):
        bot = self._bot()
        session = bot.start_session("Device", DesignDomain.IOT, DesignStage.CONCEPT)
        bot.iterate(session.session_id, ["low power", "bluetooth"])
        updated = bot.get_session(session.session_id)
        assert updated.iterations == 1

    def test_iterate_adds_requirements(self):
        bot = self._bot()
        session = bot.start_session("Device", DesignDomain.IOT, DesignStage.CONCEPT)
        bot.iterate(session.session_id, ["waterproof"])
        updated = bot.get_session(session.session_id)
        assert "waterproof" in updated.requirements

    def test_iterate_nonexistent_returns_none(self):
        bot = self._bot()
        result = bot.iterate("FAKE-9999", ["req"])
        assert result is None

    def test_recommend_components_for_all_domains(self):
        bot = self._bot()
        for domain in DesignDomain:
            components = bot.recommend_components(domain)
            assert isinstance(components, list)
            assert len(components) > 0

    def test_session_to_dict(self):
        bot = self._bot()
        session = bot.start_session("Medical Patch", DesignDomain.MEDICAL_DEVICES, DesignStage.MVP)
        d = session.to_dict()
        assert d["domain"] == "medical_devices"
        assert d["stage"] == "mvp"

    def test_multiple_sessions_independent(self):
        bot = self._bot()
        s1 = bot.start_session("A", DesignDomain.IOT, DesignStage.CONCEPT)
        s2 = bot.start_session("B", DesignDomain.ROBOTICS, DesignStage.PROTOTYPE)
        assert s1.session_id != s2.session_id

    def test_get_nonexistent_session(self):
        bot = self._bot()
        assert bot.get_session("FAKE") is None

    def test_production_ready_stage(self):
        bot = self._bot()
        session = bot.start_session("Final", DesignDomain.AUTOMOTIVE, DesignStage.PRODUCTION_READY)
        assert len(session.suggestions) > 0

    def test_aerospace_components(self):
        bot = self._bot()
        components = bot.recommend_components(DesignDomain.AEROSPACE)
        assert any("fpga" in c.lower() or "radiation" in c.lower() for c in components)


# ===========================================================================
# 3b. FinancialProjectionBot
# ===========================================================================

class TestFinancialProjectionBot:
    def _bot(self):
        return FinancialProjectionBot()

    def test_project_revenue_returns_n_years(self):
        bot = self._bot()
        projections = bot.project_revenue(99.0, 500, years=5)
        assert len(projections) == 5

    def test_project_revenue_year1_correct(self):
        bot = self._bot()
        projections = bot.project_revenue(100.0, 100)
        assert projections[0]["revenue_usd"] == 10000.0
        assert projections[0]["year"] == 1

    def test_project_revenue_grows(self):
        bot = self._bot()
        projections = bot.project_revenue(50.0, 200, growth_rate_pct=100.0, years=3)
        assert projections[1]["units"] > projections[0]["units"]
        assert projections[2]["units"] > projections[1]["units"]

    def test_break_even_basic(self):
        bot = self._bot()
        result = bot.break_even_analysis(50000.0, 100.0, 40.0)
        assert result["break_even_units"] == 834
        assert result["break_even_revenue_usd"] == 83400.0

    def test_break_even_impossible(self):
        bot = self._bot()
        result = bot.break_even_analysis(50000.0, 30.0, 50.0)
        assert "error" in result

    def test_roi_analysis(self):
        bot = self._bot()
        result = bot.roi_analysis(100000.0, 25000.0)
        assert result["roi_pct"] == 25.0
        assert result["payback_months"] == 48.0

    def test_roi_zero_investment_error(self):
        bot = self._bot()
        result = bot.roi_analysis(0.0, 5000.0)
        assert "error" in result

    def test_hardware_cost_estimate(self):
        bot = self._bot()
        breakdown = bot.hardware_cost_estimate(
            bom_cost_usd=10.0,
            tooling_cost_usd=5000.0,
            certification_cost_usd=2000.0,
            overhead_pct=20.0,
            units=1000,
        )
        assert isinstance(breakdown, HardwareCostBreakdown)
        assert breakdown.unit_cost_usd == 12.0
        assert breakdown.total_investment_usd > 0

    def test_hardware_cost_to_dict(self):
        bot = self._bot()
        breakdown = bot.hardware_cost_estimate(5.0, 1000.0, 500.0, 10.0, 200)
        d = breakdown.to_dict()
        assert "unit_cost_usd" in d
        assert "total_investment_usd" in d

    def test_negative_profit_roi(self):
        bot = self._bot()
        result = bot.roi_analysis(100000.0, -5000.0)
        assert result["roi_pct"] < 0
        assert result["payback_months"] is None

    def test_project_revenue_custom_years(self):
        bot = self._bot()
        projections = bot.project_revenue(50.0, 100, years=3)
        assert len(projections) == 3


# ===========================================================================
# 3c. ManufacturingSimulator
# ===========================================================================

class TestManufacturingSimulator:
    def _sim(self):
        return ManufacturingSimulator()

    def test_simulate_pcb_assembly(self):
        sim = self._sim()
        result = sim.simulate(ManufacturingMethod.PCB_ASSEMBLY, 500)
        assert result.method == ManufacturingMethod.PCB_ASSEMBLY
        assert result.units == 500
        assert result.cost_per_unit_usd > 0

    def test_simulate_all_methods(self):
        sim = self._sim()
        for method in ManufacturingMethod:
            result = sim.simulate(method, 100)
            assert result.total_cost_usd > 0

    def test_higher_volume_lower_unit_cost(self):
        sim = self._sim()
        low_vol = sim.simulate(ManufacturingMethod.INJECTION_MOLDING, 100)
        high_vol = sim.simulate(ManufacturingMethod.INJECTION_MOLDING, 50000)
        assert high_vol.cost_per_unit_usd < low_vol.cost_per_unit_usd

    def test_simulation_result_to_dict(self):
        sim = self._sim()
        result = sim.simulate(ManufacturingMethod.CNC_MACHINING, 50)
        d = result.to_dict()
        assert d["method"] == "cnc_machining"
        assert "lead_time_days" in d

    def test_compare_methods_returns_all_methods(self):
        sim = self._sim()
        results = sim.compare_methods(units=1000)
        assert len(results) == len(ManufacturingMethod)

    def test_compare_methods_sorted_by_cost(self):
        sim = self._sim()
        results = sim.compare_methods(units=500)
        costs = [r["total_cost_usd"] for r in results]
        assert costs == sorted(costs)

    def test_low_volume_note(self):
        sim = self._sim()
        result = sim.simulate(ManufacturingMethod.ADDITIVE_3D_PRINT, 10)
        assert any("Low volume" in note for note in result.notes)

    def test_high_volume_note(self):
        sim = self._sim()
        result = sim.simulate(ManufacturingMethod.PCB_ASSEMBLY, 20000)
        assert any("High volume" in note for note in result.notes)

    def test_simulate_with_material_cost(self):
        sim = self._sim()
        no_material = sim.simulate(ManufacturingMethod.SHEET_METAL, 500, 0.0)
        with_material = sim.simulate(ManufacturingMethod.SHEET_METAL, 500, 5.0)
        assert with_material.cost_per_unit_usd > no_material.cost_per_unit_usd

    def test_lead_time_positive(self):
        sim = self._sim()
        for method in ManufacturingMethod:
            result = sim.simulate(method, 100)
            assert result.lead_time_days > 0


# ===========================================================================
# 3d. PatentSupportAI
# ===========================================================================

class TestPatentSupportAI:
    def _ai(self):
        return PatentSupportAI()

    def test_create_provisional_dossier(self):
        ai = self._ai()
        dossier = ai.create_dossier("Smart Sensor", "An IoT sensor array.", PatentType.PROVISIONAL)
        assert dossier.dossier_id.startswith("PAT-")
        assert dossier.patent_type == PatentType.PROVISIONAL
        assert dossier.status == PatentStatus.IDEA

    def test_create_utility_dossier(self):
        ai = self._ai()
        dossier = ai.create_dossier("Robot Arm", "Robotic arm mechanism.", PatentType.UTILITY)
        assert dossier.patent_type == PatentType.UTILITY

    def test_dossier_has_filing_guidance(self):
        ai = self._ai()
        dossier = ai.create_dossier("Wearable", "A wearable device.", PatentType.PROVISIONAL)
        assert len(dossier.filing_guidance) > 0

    def test_dossier_estimated_cost_positive(self):
        ai = self._ai()
        for patent_type in PatentType:
            dossier = ai.create_dossier("X", "desc", patent_type)
            assert dossier.estimated_cost_usd > 0

    def test_prior_art_search_updates_status(self):
        ai = self._ai()
        dossier = ai.create_dossier("Sensor", "desc", PatentType.UTILITY)
        refs = ai.search_prior_art(dossier.dossier_id, ["sensor array", "IoT"])
        assert len(refs) == 2
        updated = ai.get_dossier(dossier.dossier_id)
        assert updated.status == PatentStatus.PRIOR_ART_SEARCH

    def test_prior_art_nonexistent_dossier(self):
        ai = self._ai()
        result = ai.search_prior_art("FAKE", ["keyword"])
        assert result == []

    def test_draft_claims(self):
        ai = self._ai()
        dossier = ai.create_dossier("Invention", "desc", PatentType.UTILITY)
        claims = ai.draft_claims(dossier.dossier_id, ["a sensor module", "a wireless transmitter"])
        assert len(claims) == 2
        assert "Claim 1" in claims[0]
        assert "Claim 2" in claims[1]

    def test_draft_claims_updates_status(self):
        ai = self._ai()
        dossier = ai.create_dossier("Invention", "desc", PatentType.UTILITY)
        ai.draft_claims(dossier.dossier_id, ["element"])
        updated = ai.get_dossier(dossier.dossier_id)
        assert updated.status == PatentStatus.CLAIMS_DRAFTED

    def test_draft_claims_nonexistent(self):
        ai = self._ai()
        assert ai.draft_claims("FAKE", ["element"]) == []

    def test_get_filing_guidance(self):
        ai = self._ai()
        guidance = ai.get_filing_guidance(PatentType.UTILITY)
        assert len(guidance) > 0

    def test_estimate_cost_all_types(self):
        ai = self._ai()
        for patent_type in PatentType:
            cost = ai.estimate_cost(patent_type)
            assert "uspto_fee_usd" in cost
            assert "attorney_est_usd" in cost

    def test_dossier_to_dict(self):
        ai = self._ai()
        dossier = ai.create_dossier("Widget", "A widget.", PatentType.DESIGN)
        d = dossier.to_dict()
        assert d["patent_type"] == "design"
        assert "filing_guidance" in d

    def test_get_nonexistent_dossier(self):
        ai = self._ai()
        assert ai.get_dossier("NOPE") is None


# ===========================================================================
# 3e. InventorToolkit aggregator
# ===========================================================================

class TestInventorToolkit:
    def test_toolkit_has_all_four_tools(self):
        tk = InventorToolkit()
        assert hasattr(tk, "design_bot")
        assert hasattr(tk, "financial_projection")
        assert hasattr(tk, "manufacturing_simulator")
        assert hasattr(tk, "patent_support")

    def test_summary_returns_four_tools(self):
        tk = InventorToolkit()
        summary = tk.summary()
        assert len(summary["tools"]) == 4

    def test_summary_has_description(self):
        tk = InventorToolkit()
        summary = tk.summary()
        assert summary["description"]


# ===========================================================================
# 4a. Marketplace — Directory
# ===========================================================================

class TestMarketplaceDirectory:
    def _market(self):
        return RDMarketplace()

    def test_seed_listings_loaded(self):
        m = self._market()
        results = m.search_directory()
        assert len(results) >= 5

    def test_search_by_category(self):
        m = self._market()
        results = m.search_directory(category=DirectoryCategory.ELECTRONICS_FIRM)
        assert all(r["category"] == "electronics_firm" for r in results)

    def test_search_by_query(self):
        m = self._market()
        results = m.search_directory(query="robotics")
        assert len(results) > 0

    def test_search_verified_only(self):
        m = self._market()
        results = m.search_directory(verified_only=True)
        # All seed listings with verified=True should appear
        assert len(results) >= 4

    def test_search_min_rating(self):
        m = self._market()
        results = m.search_directory(min_rating=4.5)
        for r in results:
            listing = m.get_listing(r["listing_id"])
            assert listing.rating >= 4.5

    def test_create_listing(self):
        m = self._market()
        listing = m.create_listing(
            name="New AI Firm",
            category=DirectoryCategory.AI_SPECIALIST,
            services=[ServiceType.AI_INTEGRATION],
            description="Cutting-edge AI for embedded systems.",
        )
        assert listing.listing_id.startswith("LST-")
        assert m.get_listing(listing.listing_id) is not None

    def test_listing_to_dict(self):
        m = self._market()
        listing = m.create_listing(
            name="TestCo",
            category=DirectoryCategory.CIRCUIT_DESIGNER,
            services=[ServiceType.DESIGN],
            description="PCB design house",
        )
        d = listing.to_dict()
        assert d["category"] == "circuit_designer"
        assert "design" in d["services"]

    def test_list_categories(self):
        m = self._market()
        categories = m.list_categories()
        assert "electronics_firm" in categories
        assert "ai_specialist" in categories

    def test_featured_listings_appear_first(self):
        m = self._market()
        results = m.search_directory()
        # Featured listings should be at the top
        statuses = [
            m.get_listing(r["listing_id"]).status for r in results[:3]
        ]
        assert ListingStatus.FEATURED in statuses

    def test_search_no_results_for_nonexistent(self):
        m = self._market()
        results = m.search_directory(query="xyzzy_nonexistent_9999")
        assert results == []


# ===========================================================================
# 4b. Marketplace — Forum
# ===========================================================================

class TestMarketplaceForum:
    def _market(self):
        return RDMarketplace()

    def test_seed_posts_loaded(self):
        m = self._market()
        posts = m.list_posts()
        assert len(posts) >= 3

    def test_create_post(self):
        m = self._market()
        post = m.create_post(
            author_id="USER-001",
            title="My invention idea",
            content="Details about my invention.",
            category=ForumCategory.PROTOTYPING,
        )
        assert post.post_id.startswith("POST-")
        assert post.category == ForumCategory.PROTOTYPING

    def test_reply_to_post(self):
        m = self._market()
        post = m.create_post(
            author_id="USER-001",
            title="Question",
            content="How do I start?",
            category=ForumCategory.GENERAL,
        )
        result = m.reply_to_post(post.post_id, "USER-002", "Great idea!")
        assert result is True
        viewed = m.view_post(post.post_id)
        assert len(viewed.replies) == 1

    def test_reply_nonexistent_post(self):
        m = self._market()
        assert m.reply_to_post("FAKE", "USER", "msg") is False

    def test_upvote_post(self):
        m = self._market()
        post = m.create_post(
            author_id="USER-001",
            title="Cool idea",
            content="Content.",
            category=ForumCategory.AI_ROBOTICS,
        )
        m.upvote_post(post.post_id)
        m.upvote_post(post.post_id)
        viewed = m.view_post(post.post_id)
        assert viewed.upvotes == 2

    def test_upvote_nonexistent(self):
        m = self._market()
        assert m.upvote_post("FAKE") is False

    def test_view_increments_views(self):
        m = self._market()
        post = m.create_post(
            author_id="USER-001",
            title="Post",
            content="Content",
            category=ForumCategory.IOT,
        )
        m.view_post(post.post_id)
        m.view_post(post.post_id)
        viewed = m.view_post(post.post_id)
        assert viewed.views == 3

    def test_filter_posts_by_category(self):
        m = self._market()
        posts = m.list_posts(category=ForumCategory.AI_ROBOTICS)
        for p in posts:
            assert p["category"] == "ai_robotics"

    def test_filter_posts_by_type(self):
        m = self._market()
        posts = m.list_posts(post_type=PostType.TEST_OUTCOME)
        for p in posts:
            assert p["post_type"] == "test_outcome"

    def test_filter_posts_by_tag(self):
        m = self._market()
        posts = m.list_posts(tag="tinyml")
        assert len(posts) >= 1

    def test_pinned_posts_appear_first(self):
        m = self._market()
        posts = m.list_posts()
        if len(posts) > 1:
            assert posts[0]["pinned"] or posts[0]["upvotes"] >= posts[1]["upvotes"]

    def test_post_to_dict_has_required_keys(self):
        m = self._market()
        post = m.create_post(
            author_id="U",
            title="T",
            content="C",
            category=ForumCategory.PARTNERSHIPS,
            tags=["ai"],
        )
        d = post.to_dict()
        for key in ("post_id", "author_id", "title", "content", "category", "tags"):
            assert key in d

    def test_prototyping_showcase_post_type(self):
        m = self._market()
        post = m.create_post(
            author_id="INV-001",
            title="My Prototype",
            content="See my IoT sensor prototype.",
            category=ForumCategory.PROTOTYPING,
            post_type=PostType.PROTOTYPING_SHOWCASE,
            tags=["iot", "prototype"],
        )
        assert post.post_type == PostType.PROTOTYPING_SHOWCASE


# ===========================================================================
# 4c. Marketplace — Prototyping Tools
# ===========================================================================

class TestMarketplaceTools:
    def _market(self):
        return RDMarketplace()

    def test_submit_tool(self):
        m = self._market()
        tool = m.submit_tool(
            author_id="AI-001",
            name="Edge Inference Tester",
            description="Test TinyML models on embedded hardware.",
            tool_type="inference_tool",
            demo_url="https://demo.example.com",
            tags=["tinyml", "edge-ai"],
        )
        assert tool.tool_id.startswith("TOOL-")
        assert m.get_tool(tool.tool_id) is not None

    def test_upvote_tool(self):
        m = self._market()
        tool = m.submit_tool("U", "Tool", "desc", "type")
        m.upvote_tool(tool.tool_id)
        m.upvote_tool(tool.tool_id)
        retrieved = m.get_tool(tool.tool_id)
        assert retrieved.upvotes == 2

    def test_fork_tool(self):
        m = self._market()
        tool = m.submit_tool("U", "Tool", "desc", "type")
        m.fork_tool(tool.tool_id)
        retrieved = m.get_tool(tool.tool_id)
        assert retrieved.forks == 1

    def test_upvote_nonexistent_tool(self):
        m = self._market()
        assert m.upvote_tool("FAKE") is False

    def test_fork_nonexistent_tool(self):
        m = self._market()
        assert m.fork_tool("FAKE") is False

    def test_list_tools_by_tag(self):
        m = self._market()
        m.submit_tool("U", "IoT Tool", "desc", "type", tags=["iot"])
        m.submit_tool("U", "AI Tool", "desc", "type", tags=["ai"])
        iot_tools = m.list_tools(tag="iot")
        assert all("iot" in [t.lower() for t in tool["tags"]] for tool in iot_tools)

    def test_list_tools_sorted_by_upvotes(self):
        m = self._market()
        t1 = m.submit_tool("U", "T1", "d", "type")
        t2 = m.submit_tool("U", "T2", "d", "type")
        m.upvote_tool(t2.tool_id)
        m.upvote_tool(t2.tool_id)
        m.upvote_tool(t2.tool_id)
        tools = m.list_tools()
        upvotes = [t["upvotes"] for t in tools]
        assert upvotes == sorted(upvotes, reverse=True)

    def test_tool_to_dict(self):
        m = self._market()
        tool = m.submit_tool("U", "ProtoCad", "desc", "cad_tool", tags=["cad"])
        d = tool.to_dict()
        assert "tool_id" in d
        assert d["tool_type"] == "cad_tool"


# ===========================================================================
# 5. DreamAIInventHub — Integration Tests
# ===========================================================================

class TestDreamAIInventHubIntegration:
    def test_free_tier_initialises(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        assert hub.tier == Tier.FREE

    def test_pro_tier_initialises(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        assert hub.config.price_usd_monthly == 49.0

    def test_enterprise_tier_initialises(self):
        hub = DreamAIInventHub(tier=Tier.ENTERPRISE)
        assert hub.config.is_unlimited_matches()

    def test_global_ai_sources_flow_present(self):
        hub = DreamAIInventHub()
        assert hub.flow is not None

    def test_dashboard_returns_dict(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        d = hub.dashboard()
        assert isinstance(d, dict)
        assert d["bot"] == "DreamAIInvent Hub"

    def test_dashboard_has_all_sections(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        d = hub.dashboard()
        for key in ("profiles_registered", "matches", "marketplace", "toolkit"):
            assert key in d

    def test_find_matches_free_tier(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        matches = hub.find_matches("SEED-INV-001")
        assert isinstance(matches, list)

    def test_find_matches_respects_monthly_limit(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        # Free tier has 5 matches/month
        for _ in range(5):
            hub.find_matches("SEED-INV-001")
        with pytest.raises(DreamAIInventHubTierError):
            hub.find_matches("SEED-INV-001")

    def test_free_tier_terms_template_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.get_terms_template(CollaborationType.LICENSING)

    def test_pro_tier_terms_template_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        tmpl = hub.get_terms_template(CollaborationType.LICENSING)
        assert tmpl["type"] == "licensing"

    def test_start_design_session_free_tier(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        session = hub.start_design_session("Robot", "robotics", "concept")
        assert session is not None

    def test_design_session_toolkit_limit_free(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        for _ in range(3):
            hub.start_design_session("X", "iot", "concept")
        with pytest.raises(DreamAIInventHubTierError):
            hub.start_design_session("X", "iot", "concept")

    def test_financial_projection_free_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.project_revenue(50.0, 1000)

    def test_financial_projection_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        projections = hub.project_revenue(50.0, 1000, years=3)
        assert len(projections) == 3

    def test_break_even_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        result = hub.break_even_analysis(50000.0, 100.0, 40.0)
        assert "break_even_units" in result

    def test_manufacturing_simulator_free_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.simulate_manufacturing("pcb_assembly", 500)

    def test_manufacturing_simulator_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        result = hub.simulate_manufacturing("pcb_assembly", 500)
        assert result.total_cost_usd > 0

    def test_compare_manufacturing_methods_pro(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        results = hub.compare_manufacturing_methods(1000)
        assert len(results) == len(ManufacturingMethod)

    def test_patent_dossier_free_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.create_patent_dossier("Invention", "desc")

    def test_patent_dossier_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        dossier = hub.create_patent_dossier("Smart Widget", "An IoT widget.", "provisional")
        assert dossier.dossier_id.startswith("PAT-")

    def test_search_directory_free_allowed(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        results = hub.search_directory()
        assert len(results) >= 5

    def test_search_directory_with_filter(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        results = hub.search_directory(category="electronics_firm")
        assert all(r["category"] == "electronics_firm" for r in results)

    def test_create_forum_post_free_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.create_forum_post("USER", "Title", "Content")

    def test_create_forum_post_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        post = hub.create_forum_post(
            "USER-001", "My Invention", "Details here.", "prototyping"
        )
        assert post.post_id.startswith("POST-")

    def test_submit_prototyping_tool_free_blocked(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        with pytest.raises(DreamAIInventHubTierError):
            hub.submit_prototyping_tool("U", "Tool", "desc", "type")

    def test_submit_prototyping_tool_pro_allowed(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        tool = hub.submit_prototyping_tool(
            "USER-001", "PCB Sim", "PCB simulation tool", "simulation"
        )
        assert tool.tool_id.startswith("TOOL-")

    def test_upgrade_info_free(self):
        hub = DreamAIInventHub(tier=Tier.FREE)
        info = hub.upgrade_info()
        assert info["next_tier"] == "Pro"

    def test_upgrade_info_enterprise(self):
        hub = DreamAIInventHub(tier=Tier.ENTERPRISE)
        assert hub.upgrade_info() is None

    def test_create_match_returns_match(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        match = hub.create_match(
            "SEED-INV-001", "SEED-AI-001",
            CollaborationType.CO_DEVELOPMENT,
            "Build AI-powered wearable together",
        )
        assert match.match_id.startswith("MATCH-")

    def test_dashboard_updates_after_activity(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        hub.find_matches("SEED-INV-001")
        hub.start_design_session("Widget", "iot", "concept")
        d = hub.dashboard()
        assert d["match_usage_this_month"] == 1
        assert d["toolkit_usage_this_month"] == 1

    def test_register_and_match_new_profile(self):
        hub = DreamAIInventHub(tier=Tier.PRO)
        from bots.dreamai_invent_hub.matchmaking import Profile, ProfileType, CollaborationType
        profile = Profile(
            profile_id="NEW-001",
            name="My Startup",
            profile_type=ProfileType.AI_DEVELOPER,
            expertise=["machine learning", "robotics ai"],
            collaboration_types=[CollaborationType.CO_DEVELOPMENT],
        )
        hub.register_profile(profile)
        matches = hub.find_matches("NEW-001")
        assert isinstance(matches, list)
