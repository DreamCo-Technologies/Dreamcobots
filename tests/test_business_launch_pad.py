import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.business_launch_pad.tiers import (
    Tier, TierConfig, get_tier_config, list_tiers, TIER_CATALOGUE,
    FEATURE_PLAN_GENERATOR, FEATURE_MARKET_RESEARCH, FEATURE_LEGAL_FORMATION,
    FEATURE_BRAND_IDENTITY, FEATURE_WEBSITE_SETUP, FEATURE_FINANCIAL_PROJECTIONS,
    FEATURE_PITCH_DECK, FEATURE_TAM_ANALYSIS, FEATURE_SWOT_ANALYSIS,
    FEATURE_COMPLIANCE_MONITORING, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS,
    BOT_FEATURES,
)
from bots.business_launch_pad.plan_generator import PlanGenerator, BusinessPlan
from bots.business_launch_pad.market_research import MarketResearch, Competitor, CustomerPersona, MarketReport
from bots.business_launch_pad.legal_formation import LegalFormation, LegalEntity, EntityType, FormationStatus
from bots.business_launch_pad.brand_identity import BrandIdentity, BrandKit, ColorPalette
from bots.business_launch_pad.website_setup import WebsiteSetup, WebsiteProject, WebsiteTemplate, DomainStatus
from bots.business_launch_pad.business_launch_pad import (
    BusinessLaunchPad, BusinessLaunchPadError, BusinessLaunchPadTierError,
)


# ===========================================================================
# Tiers
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_catalogue_has_all_tiers(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_plans(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_plans_per_month == 3

    def test_pro_max_plans(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_plans_per_month == 50

    def test_enterprise_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_plans_per_month is None
        assert cfg.is_unlimited()

    def test_free_has_plan_generator(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_PLAN_GENERATOR)

    def test_free_lacks_market_research(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_MARKET_RESEARCH)

    def test_pro_has_all_main_features(self):
        cfg = get_tier_config(Tier.PRO)
        for feat in [FEATURE_PLAN_GENERATOR, FEATURE_MARKET_RESEARCH, FEATURE_LEGAL_FORMATION,
                     FEATURE_BRAND_IDENTITY, FEATURE_WEBSITE_SETUP, FEATURE_FINANCIAL_PROJECTIONS,
                     FEATURE_PITCH_DECK, FEATURE_TAM_ANALYSIS, FEATURE_SWOT_ANALYSIS]:
            assert cfg.has_feature(feat), f"PRO missing {feat}"

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_enterprise_has_compliance_monitoring(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_COMPLIANCE_MONITORING)

    def test_list_tiers_returns_three(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_list_tiers_ordered_by_price(self):
        tiers = list_tiers()
        prices = [t.price_usd_monthly for t in tiers]
        assert prices == sorted(prices)

    def test_bot_features_dict_keys(self):
        for tier in Tier:
            assert tier.value in BOT_FEATURES

    def test_tier_config_dataclass_fields(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg.name, str)
        assert isinstance(cfg.features, list)


# ===========================================================================
# PlanGenerator
# ===========================================================================

class TestPlanGenerator:
    def setup_method(self):
        self.pg = PlanGenerator()

    def test_generate_plan_returns_business_plan(self):
        plan = self.pg.generate_plan("AcmeCo", "technology", "A SaaS product")
        assert isinstance(plan, BusinessPlan)

    def test_plan_has_correct_name(self):
        plan = self.pg.generate_plan("BetaCo", "retail", "Online store")
        assert plan.business_name == "BetaCo"

    def test_plan_has_correct_industry(self):
        plan = self.pg.generate_plan("GammaCo", "healthcare", "Telemedicine")
        assert plan.industry == "healthcare"

    def test_plan_id_is_unique(self):
        p1 = self.pg.generate_plan("Co1", "tech", "desc")
        p2 = self.pg.generate_plan("Co2", "tech", "desc")
        assert p1.plan_id != p2.plan_id

    def test_financial_projections_five_years(self):
        proj = self.pg.generate_financial_projections(100_000, 0.3)
        assert set(proj.keys()) == {"year1", "year2", "year3", "year4", "year5"}

    def test_financial_projections_growth(self):
        proj = self.pg.generate_financial_projections(100_000, 0.5)
        assert proj["year2"] > proj["year1"]
        assert proj["year5"] > proj["year4"]

    def test_financial_projections_base_revenue(self):
        proj = self.pg.generate_financial_projections(50_000, 0.0)
        assert proj["year1"] == 50_000.0

    def test_calculate_tam_technology(self):
        tam = self.pg.calculate_tam("technology")
        assert tam > 0

    def test_calculate_tam_unknown_industry(self):
        tam = self.pg.calculate_tam("underwater basket weaving")
        assert tam == 1_000_000_000_000.0

    def test_executive_summary_contains_name(self):
        summary = self.pg.generate_executive_summary("FooCo", "finance", "We do finance")
        assert "FooCo" in summary

    def test_executive_summary_contains_industry(self):
        summary = self.pg.generate_executive_summary("BarCo", "education", "We teach")
        assert "education" in summary

    def test_export_pitch_deck_keys(self):
        plan = self.pg.generate_plan("PitchCo", "technology", "A pitch")
        deck = self.pg.export_pitch_deck(plan)
        for key in ["title_slide", "problem", "solution", "market_opportunity", "business_model", "financials", "team", "ask"]:
            assert key in deck, f"Missing key: {key}"

    def test_list_plans_initially_empty(self):
        pg = PlanGenerator()
        assert pg.list_plans() == []

    def test_list_plans_after_generate(self):
        self.pg.generate_plan("Co", "tech", "desc")
        assert len(self.pg.list_plans()) == 1

    def test_get_plan_by_id(self):
        plan = self.pg.generate_plan("GetCo", "tech", "desc")
        retrieved = self.pg.get_plan(plan.plan_id)
        assert retrieved.plan_id == plan.plan_id

    def test_get_plan_raises_for_unknown_id(self):
        with pytest.raises(KeyError):
            self.pg.get_plan("nonexistent-id")


# ===========================================================================
# MarketResearch
# ===========================================================================

class TestMarketResearch:
    def setup_method(self):
        self.mr = MarketResearch()

    def test_generate_report_returns_market_report(self):
        report = self.mr.generate_report("technology")
        assert isinstance(report, MarketReport)

    def test_report_has_industry(self):
        report = self.mr.generate_report("retail")
        assert report.industry == "retail"

    def test_report_has_competitors(self):
        report = self.mr.generate_report("technology")
        assert len(report.competitors) > 0

    def test_report_has_personas(self):
        report = self.mr.generate_report("healthcare")
        assert len(report.personas) >= 3

    def test_report_has_swot(self):
        report = self.mr.generate_report("finance")
        assert "strengths" in report.swot
        assert "weaknesses" in report.swot
        assert "opportunities" in report.swot
        assert "threats" in report.swot

    def test_report_has_trends(self):
        report = self.mr.generate_report("education")
        assert len(report.trends) >= 5

    def test_map_competitors_known_industry(self):
        comps = self.mr.map_competitors("technology")
        assert all(isinstance(c, Competitor) for c in comps)

    def test_map_competitors_unknown_industry(self):
        comps = self.mr.map_competitors("astrology consulting")
        assert len(comps) > 0

    def test_build_personas_returns_list(self):
        personas = self.mr.build_personas("retail")
        assert isinstance(personas, list)
        assert all(isinstance(p, CustomerPersona) for p in personas)

    def test_generate_swot_structure(self):
        swot = self.mr.generate_swot("TestCo", "healthcare")
        for key in ["strengths", "weaknesses", "opportunities", "threats"]:
            assert key in swot
            assert len(swot[key]) >= 3

    def test_get_trends_known_industry(self):
        trends = self.mr.get_trends("technology")
        assert len(trends) >= 5

    def test_get_trends_unknown_industry(self):
        trends = self.mr.get_trends("beekeeping")
        assert len(trends) >= 5

    def test_list_reports_initially_empty(self):
        mr = MarketResearch()
        assert mr.list_reports() == []

    def test_list_reports_after_generate(self):
        self.mr.generate_report("technology")
        assert len(self.mr.list_reports()) == 1


# ===========================================================================
# LegalFormation
# ===========================================================================

class TestLegalFormation:
    def setup_method(self):
        self.lf = LegalFormation()

    def test_form_entity_returns_legal_entity(self):
        entity = self.lf.form_entity("TestCo", EntityType.LLC, "CA")
        assert isinstance(entity, LegalEntity)

    def test_form_entity_starts_in_draft(self):
        entity = self.lf.form_entity("DraftCo", EntityType.LLC, "TX")
        assert entity.status == FormationStatus.DRAFT

    def test_form_entity_stores_name(self):
        entity = self.lf.form_entity("NamedCo", EntityType.CORPORATION, "DE")
        assert entity.business_name == "NamedCo"

    def test_form_entity_normalizes_state(self):
        entity = self.lf.form_entity("StateCo", EntityType.LLC, "ca")
        assert entity.state == "CA"

    def test_file_entity_transitions_to_filed(self):
        entity = self.lf.form_entity("FileCo", EntityType.LLC, "NY")
        filed = self.lf.file_entity(entity.entity_id)
        assert filed.status == FormationStatus.FILED

    def test_approve_entity_transitions_to_active(self):
        entity = self.lf.form_entity("ApproveCo", EntityType.LLC, "FL")
        self.lf.file_entity(entity.entity_id)
        approved = self.lf.approve_entity(entity.entity_id)
        assert approved.status == FormationStatus.ACTIVE

    def test_register_ein_format(self):
        entity = self.lf.form_entity("EINCo", EntityType.CORPORATION, "TX")
        ein = self.lf.register_ein(entity.entity_id)
        assert "-" in ein
        parts = ein.split("-")
        assert len(parts) == 2
        assert len(parts[0]) == 2
        assert len(parts[1]) == 7

    def test_register_ein_stored_on_entity(self):
        entity = self.lf.form_entity("EINStoreCo", EntityType.LLC, "DE")
        ein = self.lf.register_ein(entity.entity_id)
        assert entity.ein == ein

    def test_compliance_checklist_has_items(self):
        items = self.lf.get_compliance_checklist(EntityType.LLC, "CA")
        assert len(items) > 0

    def test_compliance_checklist_llc_includes_articles(self):
        items = self.lf.get_compliance_checklist(EntityType.LLC, "TX")
        assert any("Articles" in item for item in items)

    def test_compliance_checklist_corporation_includes_bylaws(self):
        items = self.lf.get_compliance_checklist(EntityType.CORPORATION, "DE")
        assert any("Bylaws" in item for item in items)

    def test_list_entities_initially_empty(self):
        lf = LegalFormation()
        assert lf.list_entities() == []

    def test_list_entities_after_form(self):
        self.lf.form_entity("ListCo", EntityType.LLC, "WA")
        assert len(self.lf.list_entities()) == 1

    def test_get_entity_by_id(self):
        entity = self.lf.form_entity("GetCo", EntityType.LLC, "NV")
        retrieved = self.lf.get_entity(entity.entity_id)
        assert retrieved.entity_id == entity.entity_id

    def test_get_entity_raises_for_unknown(self):
        with pytest.raises(KeyError):
            self.lf.get_entity("bad-id")

    def test_get_filing_requirements_known_state(self):
        reqs = self.lf.get_filing_requirements("CA")
        assert "filing_fee" in reqs
        assert reqs["state"] == "CA"

    def test_get_filing_requirements_unknown_state(self):
        reqs = self.lf.get_filing_requirements("ZZ")
        assert "filing_fee" in reqs


# ===========================================================================
# BrandIdentity
# ===========================================================================

class TestBrandIdentity:
    def setup_method(self):
        self.bi = BrandIdentity()

    def test_create_brand_returns_brand_kit(self):
        kit = self.bi.create_brand("BrandCo", "technology")
        assert isinstance(kit, BrandKit)

    def test_create_brand_stores_name(self):
        kit = self.bi.create_brand("NameBrand", "retail")
        assert kit.business_name == "NameBrand"

    def test_create_brand_has_logo_concepts(self):
        kit = self.bi.create_brand("LogoCo", "healthcare")
        assert len(kit.logo_concepts) == 5

    def test_create_brand_has_color_palette(self):
        kit = self.bi.create_brand("ColorCo", "finance")
        assert isinstance(kit.color_palette, ColorPalette)

    def test_create_brand_has_tagline(self):
        kit = self.bi.create_brand("TagCo", "education")
        assert len(kit.tagline) > 0

    def test_create_brand_has_style_guide(self):
        kit = self.bi.create_brand("StyleCo", "consulting")
        assert isinstance(kit.style_guide, dict)
        assert "colors" in kit.style_guide

    def test_generate_logo_concepts_returns_five(self):
        concepts = self.bi.generate_logo_concepts("TestCo", "technology")
        assert len(concepts) == 5

    def test_recommend_colors_known_industry(self):
        palette = self.bi.recommend_colors("technology")
        assert palette.primary.startswith("#")

    def test_recommend_colors_unknown_industry(self):
        palette = self.bi.recommend_colors("mystery industry")
        assert palette.primary.startswith("#")

    def test_define_brand_voice_returns_string(self):
        voice = self.bi.define_brand_voice("healthcare")
        assert isinstance(voice, str)
        assert len(voice) > 0

    def test_create_tagline_returns_string(self):
        tagline = self.bi.create_tagline("FooCo", "technology")
        assert isinstance(tagline, str)
        assert len(tagline) > 0

    def test_generate_style_guide_has_typography(self):
        kit = self.bi.create_brand("TypoCo", "retail")
        assert "typography" in kit.style_guide

    def test_list_brands_initially_empty(self):
        bi = BrandIdentity()
        assert bi.list_brands() == []

    def test_list_brands_after_create(self):
        self.bi.create_brand("ListCo", "tech")
        assert len(self.bi.list_brands()) == 1

    def test_get_brand_by_id(self):
        kit = self.bi.create_brand("GetCo", "retail")
        retrieved = self.bi.get_brand(kit.brand_id)
        assert retrieved.brand_id == kit.brand_id

    def test_get_brand_raises_for_unknown(self):
        with pytest.raises(KeyError):
            self.bi.get_brand("nonexistent-id")


# ===========================================================================
# WebsiteSetup
# ===========================================================================

class TestWebsiteSetup:
    def setup_method(self):
        self.ws = WebsiteSetup()

    def test_check_domain_returns_domain_result(self):
        result = self.ws.check_domain("myawesomebusiness.com")
        assert result.domain == "myawesomebusiness.com"
        assert result.status in DomainStatus

    def test_check_domain_has_alternatives(self):
        result = self.ws.check_domain("myawesomebusiness.com")
        assert len(result.alternatives) > 0

    def test_check_domain_price_available(self):
        result = self.ws.check_domain("myawesomebusiness.com")
        if result.status == DomainStatus.AVAILABLE:
            assert result.price_usd > 0

    def test_check_domain_taken_has_zero_price(self):
        # Short names are TAKEN by simulation
        result = self.ws.check_domain("ab.com")
        assert result.status == DomainStatus.TAKEN
        assert result.price_usd == 0.0

    def test_create_website_returns_project(self):
        project = self.ws.create_website("WebCo", "webcobusiness.com", WebsiteTemplate.SAAS)
        assert isinstance(project, WebsiteProject)

    def test_create_website_not_launched(self):
        project = self.ws.create_website("NotLaunchedCo", "notlaunched.com", WebsiteTemplate.BLOG)
        assert project.launched is False

    def test_create_website_has_pages(self):
        project = self.ws.create_website("PagesCo", "pages.com", WebsiteTemplate.LANDING_PAGE)
        assert len(project.pages) > 0

    def test_select_template_technology(self):
        template = self.ws.select_template("technology")
        assert template == WebsiteTemplate.SAAS

    def test_select_template_ecommerce(self):
        template = self.ws.select_template("e-commerce")
        assert template == WebsiteTemplate.ECOMMERCE

    def test_select_template_unknown(self):
        template = self.ws.select_template("unknown industry xyz")
        assert template in WebsiteTemplate

    def test_setup_seo_returns_dict(self):
        project = self.ws.create_website("SEOCo", "seoco.com", WebsiteTemplate.CORPORATE)
        seo = self.ws.setup_seo(project.project_id)
        assert isinstance(seo, dict)

    def test_setup_seo_has_keywords(self):
        project = self.ws.create_website("KeywordCo", "keyword.com", WebsiteTemplate.SAAS)
        seo = self.ws.setup_seo(project.project_id)
        assert "keywords" in seo

    def test_setup_seo_updates_score(self):
        project = self.ws.create_website("ScoreCo", "score.com", WebsiteTemplate.LANDING_PAGE)
        self.ws.setup_seo(project.project_id)
        assert project.seo_score > 0

    def test_launch_website_sets_launched(self):
        project = self.ws.create_website("LaunchCo", "launch.com", WebsiteTemplate.CORPORATE)
        launched = self.ws.launch_website(project.project_id)
        assert launched.launched is True

    def test_list_projects_initially_empty(self):
        ws = WebsiteSetup()
        assert ws.list_projects() == []

    def test_list_projects_after_create(self):
        self.ws.create_website("ListCo", "list.com", WebsiteTemplate.BLOG)
        assert len(self.ws.list_projects()) == 1

    def test_get_project_by_id(self):
        project = self.ws.create_website("GetCo", "get.com", WebsiteTemplate.PORTFOLIO)
        retrieved = self.ws.get_project(project.project_id)
        assert retrieved.project_id == project.project_id

    def test_get_project_raises_for_unknown(self):
        with pytest.raises(KeyError):
            self.ws.get_project("nonexistent-id")


# ===========================================================================
# BusinessLaunchPad — main bot
# ===========================================================================

class TestBusinessLaunchPadFree:
    def setup_method(self):
        self.bot = BusinessLaunchPad(tier=Tier.FREE)

    def test_create_plan_on_free_tier(self):
        result = self.bot.create_business_plan("FreeCo", "technology", "A startup")
        assert "plan_id" in result

    def test_free_plan_no_financial_projections(self):
        result = self.bot.create_business_plan("FreeCo2", "retail", "desc")
        assert "financial_projections" not in result

    def test_free_plan_no_pitch_deck(self):
        result = self.bot.create_business_plan("FreeCo3", "retail", "desc")
        assert "pitch_deck" not in result

    def test_free_plan_no_tam(self):
        result = self.bot.create_business_plan("FreeCo4", "technology", "desc")
        assert "tam_usd" not in result

    def test_free_market_research_blocked(self):
        with pytest.raises(BusinessLaunchPadTierError):
            self.bot.run_market_research("technology")

    def test_free_legal_formation_blocked(self):
        with pytest.raises(BusinessLaunchPadTierError):
            self.bot.form_legal_entity("FreeLegal", "llc", "CA")

    def test_free_brand_blocked(self):
        with pytest.raises(BusinessLaunchPadTierError):
            self.bot.create_brand("FreeBrand", "retail")

    def test_free_website_blocked(self):
        with pytest.raises(BusinessLaunchPadTierError):
            self.bot.setup_website("FreeWeb", "freeweb.com", "saas")

    def test_free_plan_quota_enforced(self):
        for i in range(3):
            self.bot.create_business_plan(f"Co{i}", "tech", "desc")
        with pytest.raises(BusinessLaunchPadTierError):
            self.bot.create_business_plan("OneMore", "tech", "desc")

    def test_dashboard_returns_string(self):
        assert isinstance(self.bot.dashboard(), str)

    def test_dashboard_shows_tier_name(self):
        assert "Free" in self.bot.dashboard()

    def test_get_launch_checklist_has_steps(self):
        checklist = self.bot.get_launch_checklist()
        assert len(checklist) >= 10


class TestBusinessLaunchPadPro:
    def setup_method(self):
        self.bot = BusinessLaunchPad(tier=Tier.PRO)

    def test_create_plan_pro_has_financial_projections(self):
        result = self.bot.create_business_plan("ProCo", "technology", "A SaaS")
        assert "financial_projections" in result

    def test_create_plan_pro_has_pitch_deck(self):
        result = self.bot.create_business_plan("ProCo2", "retail", "Online store")
        assert "pitch_deck" in result

    def test_create_plan_pro_has_tam(self):
        result = self.bot.create_business_plan("ProCo3", "finance", "Fintech")
        assert "tam_usd" in result

    def test_run_market_research_pro(self):
        result = self.bot.run_market_research("technology")
        assert "report_id" in result
        assert "competitors" in result

    def test_market_research_has_swot_on_pro(self):
        result = self.bot.run_market_research("healthcare")
        assert "swot" in result

    def test_form_legal_entity_pro(self):
        result = self.bot.form_legal_entity("LegalCo", "llc", "CA")
        assert "entity_id" in result
        assert result["entity_type"] == "llc"

    def test_form_legal_entity_invalid_type(self):
        with pytest.raises(BusinessLaunchPadError):
            self.bot.form_legal_entity("BadCo", "invalid_type", "CA")

    def test_create_brand_pro(self):
        result = self.bot.create_brand("BrandProCo", "technology")
        assert "brand_id" in result
        assert "color_palette" in result

    def test_setup_website_pro(self):
        result = self.bot.setup_website("WebProCo", "webproco.com", "saas")
        assert "project_id" in result
        assert "seo_setup" in result

    def test_setup_website_invalid_template(self):
        with pytest.raises(BusinessLaunchPadError):
            self.bot.setup_website("ErrCo", "errco.com", "not_a_template")

    def test_dashboard_shows_pro(self):
        assert "Pro" in self.bot.dashboard()


class TestBusinessLaunchPadEnterprise:
    def setup_method(self):
        self.bot = BusinessLaunchPad(tier=Tier.ENTERPRISE)

    def test_enterprise_plan_unlimited(self):
        for i in range(10):
            self.bot.create_business_plan(f"EntCo{i}", "technology", "desc")
        # Should not raise
        result = self.bot.create_business_plan("EntCo10", "technology", "desc")
        assert "plan_id" in result

    def test_enterprise_dashboard_shows_unlimited(self):
        dash = self.bot.dashboard()
        assert "Unlimited" in dash

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [FEATURE_WHITE_LABEL, FEATURE_API_ACCESS, FEATURE_COMPLIANCE_MONITORING]:
            assert cfg.has_feature(feat)


class TestExceptions:
    def test_tier_error_is_subclass_of_base(self):
        assert issubclass(BusinessLaunchPadTierError, BusinessLaunchPadError)

    def test_base_error_is_exception(self):
        assert issubclass(BusinessLaunchPadError, Exception)

    def test_raise_base_error(self):
        with pytest.raises(BusinessLaunchPadError):
            raise BusinessLaunchPadError("test")

    def test_raise_tier_error(self):
        with pytest.raises(BusinessLaunchPadTierError):
            raise BusinessLaunchPadTierError("tier test")
