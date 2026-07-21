"""
Tests for bots/big_bro_ai/

Covers all eleven core modules (plus tiers and integration): of the Big Bro AI Ecosystem:
  1. Tiers
  2. Personality Engine
  3. Memory System
  4. Mentor Engine
  5. Bot Factory
  6. Continuous Study Engine
  7. Prospectus System
  8. Courses-as-Systems
  9. Route & GPS Intelligence
  10. Sales & Monetization Engine
  11. Catalog & Franchise Engine
  12. Master Dashboard
  13. BigBroAI main class (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ------------------------------------------------------------------
# Tiers
# ------------------------------------------------------------------
from bots.big_bro_ai.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_CORE_MENTOR,
    FEATURE_BOT_FACTORY,
    FEATURE_CONTINUOUS_STUDY,
    FEATURE_FRANCHISE_ENGINE,
    FEATURE_WHITE_LABEL,
)

# ------------------------------------------------------------------
# Personality
# ------------------------------------------------------------------
from bots.big_bro_ai.personality import (
    PersonalityEngine,
    RelationshipTier,
    RoastMode,
    BIG_BRO_CORE_RULES,
    BIG_BRO_TRAITS,
    BIG_BRO_SIGNATURES,
    INTRO_SCRIPT,
    DREAMCO_PHILOSOPHY,
)

# ------------------------------------------------------------------
# Memory System
# ------------------------------------------------------------------
from bots.big_bro_ai.memory_system import (
    MemorySystem,
    MemorySystemError,
    UserProfile,
    MemoryEntry,
    LifeSituation,
)

# ------------------------------------------------------------------
# Mentor Engine
# ------------------------------------------------------------------
from bots.big_bro_ai.mentor_engine import (
    MentorEngine,
    MentorEngineError,
    MentorDomain,
    GrowthStage,
    MONEY_LESSONS,
    TECH_LESSONS,
    RELATIONSHIP_LESSONS,
    CONFIDENCE_LESSONS,
)

# ------------------------------------------------------------------
# Bot Factory
# ------------------------------------------------------------------
from bots.big_bro_ai.bot_factory import (
    BotFactory,
    BotFactoryError,
    BotCategory,
    BotStatus,
    BotProspectus,
    ManufacturedBot,
)

# ------------------------------------------------------------------
# Continuous Study Engine
# ------------------------------------------------------------------
from bots.big_bro_ai.continuous_study import (
    ContinuousStudyEngine,
    ContinuousStudyError,
    KnowledgeDomain,
    KnowledgePattern,
    StudyModule,
    BUILTIN_MODULES,
)

# ------------------------------------------------------------------
# Prospectus System
# ------------------------------------------------------------------
from bots.big_bro_ai.prospectus import (
    ProspectusSystem,
    ProspectusSystemError,
    Prospectus,
    ROIBridge,
    StudyPathItem,
    ProspectusStatus,
)

# ------------------------------------------------------------------
# Courses System
# ------------------------------------------------------------------
from bots.big_bro_ai.courses_system import (
    CoursesSystem,
    CoursesSystemError,
    Course,
    Lesson,
    CourseCategory,
    Enrollment,
)

# ------------------------------------------------------------------
# Route & GPS
# ------------------------------------------------------------------
from bots.big_bro_ai.route_gps import (
    RouteGPSIntelligence,
    RouteGPSError,
    Resource,
    Route,
    ResourceCategory,
    RouteType,
)

# ------------------------------------------------------------------
# Sales & Monetization
# ------------------------------------------------------------------
from bots.big_bro_ai.sales_monetization import (
    SalesMonetizationEngine,
    SalesMonetizationError,
    IncomeStream,
    IncomeStreamType,
    compound_interest,
    PAYMENT_METHODS,
)

# ------------------------------------------------------------------
# Catalog & Franchise
# ------------------------------------------------------------------
from bots.big_bro_ai.catalog_franchise import (
    CatalogFranchiseEngine,
    CatalogFranchiseError,
    CatalogItem,
    CatalogCategory,
    Franchise,
    FranchiseStatus,
    CatalogOrder,
)

# ------------------------------------------------------------------
# Master Dashboard
# ------------------------------------------------------------------
from bots.big_bro_ai.master_dashboard import (
    MasterDashboard,
    DashboardAlert,
    AlertLevel,
    PANEL_NAMES,
)

# ------------------------------------------------------------------
# BigBroAI (main)
# ------------------------------------------------------------------
from bots.big_bro_ai.big_bro_ai import BigBroAI, BigBroAIError, BigBroTierError


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_all_three_tiers_in_catalogue(self):
        assert set(TIER_CATALOGUE.keys()) == {"free", "pro", "enterprise"}

    def test_free_is_zero_cost(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_max_bots(self):
        assert get_tier_config(Tier.FREE).max_bots == 1

    def test_pro_max_bots(self):
        assert get_tier_config(Tier.PRO).max_bots == 10

    def test_enterprise_unlimited_bots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_bots is None
        assert cfg.is_unlimited_bots()

    def test_free_has_core_mentor(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_CORE_MENTOR)

    def test_free_has_bot_factory(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_BOT_FACTORY)

    def test_free_lacks_continuous_study(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_CONTINUOUS_STUDY)

    def test_pro_has_continuous_study(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CONTINUOUS_STUDY)

    def test_enterprise_has_franchise(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_FRANCHISE_ENGINE)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_list_tiers_returns_all_three(self):
        assert len(list_tiers()) == 3

    def test_upgrade_from_free_returns_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_from_pro_returns_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_from_enterprise_returns_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_ai_models(self):
        assert get_tier_config(Tier.FREE).max_ai_models == 3

    def test_pro_ai_models(self):
        assert get_tier_config(Tier.PRO).max_ai_models == 20


# ===========================================================================
# Personality Engine tests
# ===========================================================================

class TestPersonalityEngine:
    def setup_method(self):
        self.engine = PersonalityEngine(custom_name="Big Bro")

    def test_intro_script_contains_protect(self):
        assert "protect" in self.engine.introduce().lower()

    def test_community_intro_contains_grow(self):
        assert "grow" in self.engine.introduce(community_mode=True).lower()

    def test_greet_includes_name(self):
        greeting = self.engine.greet("Marcus")
        assert "Marcus" in greeting

    def test_greet_creator_tier(self):
        greeting = self.engine.greet("Jordan", RelationshipTier.CREATOR)
        assert "Jordan" in greeting

    def test_defend_creator(self):
        defense = self.engine.defend("Jordan", RelationshipTier.CREATOR)
        assert "Jordan" in defense

    def test_roast_targets_excuse_not_person(self):
        roast = self.engine.roast("I'll start tomorrow")
        assert "excuse" in roast.lower() or "tomorrow" in roast.lower()

    def test_roast_savage_mode(self):
        self.engine.roast_mode = RoastMode.SAVAGE
        roast = self.engine.roast("I'm not ready")
        assert "not ready" in roast or "excuse" in roast.lower()

    def test_roast_funny_mode(self):
        self.engine.roast_mode = RoastMode.FUNNY
        roast = self.engine.roast("I'm too busy")
        assert "too busy" in roast or "ready" in roast.lower()

    def test_check_rule_blocks_height(self):
        result = self.engine.check_rule("roast his height")
        assert not result["allowed"]

    def test_check_rule_allows_excuse_roast(self):
        result = self.engine.check_rule("roast his excuses")
        assert result["allowed"]

    def test_teach_philosophy_core(self):
        lesson = self.engine.teach_philosophy("core")
        assert "systems" in lesson.lower()

    def test_teach_philosophy_modo(self):
        lesson = self.engine.teach_philosophy("modo")
        assert "value" in lesson.lower()

    def test_signature_rotates(self):
        s1 = self.engine.get_signature(0)
        s2 = self.engine.get_signature(1)
        # Both are non-empty strings
        assert isinstance(s1, str) and len(s1) > 0
        assert isinstance(s2, str) and len(s2) > 0

    def test_status_returns_name(self):
        status = self.engine.status()
        assert status["name"] == "Big Bro"

    def test_core_rules_not_empty(self):
        assert len(BIG_BRO_CORE_RULES) >= 7

    def test_dreamco_philosophy_has_pillars(self):
        assert "pillars" in DREAMCO_PHILOSOPHY

    def test_traits_include_calm(self):
        assert "calm" in BIG_BRO_TRAITS

    def test_motivate_includes_name(self):
        msg = self.engine.motivate("Dre", RelationshipTier.FRIEND)
        assert "Dre" in msg

    def test_correct_includes_name(self):
        msg = self.engine.correct("Dre", RelationshipTier.INNER_CIRCLE)
        assert "Dre" in msg


# ===========================================================================
# Memory System tests
# ===========================================================================

class TestMemorySystem:
    def setup_method(self):
        self.ms = MemorySystem(max_profiles=100)

    def test_create_profile(self):
        profile = self.ms.create_profile("u001", "Marcus")
        assert profile.name == "Marcus"
        assert profile.user_id == "u001"

    def test_create_duplicate_raises(self):
        self.ms.create_profile("u001", "Marcus")
        with pytest.raises(MemorySystemError):
            self.ms.create_profile("u001", "Marcus2")

    def test_get_profile_returns_profile(self):
        self.ms.create_profile("u001", "Marcus")
        p = self.ms.get_profile("u001")
        assert p is not None and p.name == "Marcus"

    def test_get_missing_profile_returns_none(self):
        assert self.ms.get_profile("ghost") is None

    def test_delete_profile(self):
        self.ms.create_profile("u001", "Marcus")
        assert self.ms.delete_profile("u001")
        assert self.ms.get_profile("u001") is None

    def test_delete_missing_returns_false(self):
        assert not self.ms.delete_profile("ghost")

    def test_log_memory(self):
        self.ms.create_profile("u001", "Marcus")
        entry = self.ms.log_memory("u001", "stress", "school pressure", ["school"])
        assert entry.situation == "stress"

    def test_recall_mentions_name(self):
        self.ms.create_profile("u001", "Marcus")
        self.ms.log_memory("u001", "stress", "school was hard")
        recall = self.ms.recall("u001")
        assert "Marcus" in recall

    def test_recall_no_memory_returns_first_time_message(self):
        self.ms.create_profile("u001", "Marcus")
        recall = self.ms.recall("u001")
        assert "first" in recall.lower()

    def test_summary_returns_name(self):
        self.ms.create_profile("u001", "Marcus", nickname="M")
        summary = self.ms.summary("u001")
        assert summary["name"] == "Marcus"
        assert summary["nickname"] == "M"

    def test_profile_count(self):
        self.ms.create_profile("u001", "Marcus")
        self.ms.create_profile("u002", "Jordan")
        assert self.ms.profile_count() == 2

    def test_list_users(self):
        self.ms.create_profile("u001", "Marcus")
        self.ms.create_profile("u002", "Jordan")
        users = self.ms.list_users()
        assert "u001" in users and "u002" in users

    def test_max_profiles_enforced(self):
        ms = MemorySystem(max_profiles=2)
        ms.create_profile("u001", "A")
        ms.create_profile("u002", "B")
        with pytest.raises(MemorySystemError):
            ms.create_profile("u003", "C")

    def test_log_memory_unknown_user_raises(self):
        with pytest.raises(MemorySystemError):
            self.ms.log_memory("ghost", "stress", "test")

    def test_export_and_import(self):
        self.ms.create_profile("u001", "Marcus")
        exported = self.ms.export_all()
        ms2 = MemorySystem()
        count = ms2.import_profiles(exported)
        assert count == 1
        assert ms2.get_profile("u001") is not None

    def test_update_profile(self):
        self.ms.create_profile("u001", "Marcus")
        self.ms.update_profile("u001", nickname="Big M")
        p = self.ms.get_profile("u001")
        assert p.nickname == "Big M"

    def test_profile_add_goal(self):
        self.ms.create_profile("u001", "Marcus")
        p = self.ms.get_profile("u001")
        p.add_goal("Build a SaaS")
        assert "Build a SaaS" in p.goals

    def test_profile_add_win(self):
        self.ms.create_profile("u001", "Marcus")
        p = self.ms.get_profile("u001")
        p.add_win("First $100 online")
        assert "First $100 online" in p.wins

    def test_profile_memories_by_tag(self):
        self.ms.create_profile("u001", "Marcus")
        self.ms.log_memory("u001", "win", "Made $50", ["money", "wins"])
        self.ms.log_memory("u001", "stress", "School hard", ["school"])
        p = self.ms.get_profile("u001")
        money_entries = p.memories_by_tag("money")
        assert len(money_entries) == 1


# ===========================================================================
# Mentor Engine tests
# ===========================================================================

class TestMentorEngine:
    def setup_method(self):
        self.engine = MentorEngine()

    def test_teach_money_returns_lesson(self):
        result = self.engine.teach("u001", MentorDomain.MONEY)
        assert result["domain"] == "money"
        assert len(result["lesson"]) > 10

    def test_teach_tech_returns_lesson(self):
        result = self.engine.teach("u001", MentorDomain.TECH)
        assert result["domain"] == "tech"

    def test_teach_relationships(self):
        result = self.engine.teach("u001", MentorDomain.RELATIONSHIPS)
        assert result["domain"] == "relationships"

    def test_teach_specific_topic(self):
        result = self.engine.teach("u001", MentorDomain.MONEY, "subscriptions_vs_onetime")
        assert result["topic"] == "subscriptions_vs_onetime"
        assert not result["already_learned"]

    def test_teach_marks_as_learned(self):
        self.engine.teach("u001", MentorDomain.MONEY, "subscriptions_vs_onetime")
        result = self.engine.teach("u001", MentorDomain.MONEY, "subscriptions_vs_onetime")
        assert result["already_learned"]

    def test_teach_advances_through_lessons(self):
        """Each teach() call should return a different lesson."""
        seen = set()
        for _ in range(len(MONEY_LESSONS)):
            r = self.engine.teach("u001", MentorDomain.MONEY)
            seen.add(r["topic"])
        assert len(seen) >= len(MONEY_LESSONS)

    def test_growth_stage_seed_for_new_user(self):
        assert self.engine.assess_growth_stage("new_user") == GrowthStage.SEED

    def test_growth_stage_advances_with_lessons(self):
        for _ in range(5):
            self.engine.teach("u001", MentorDomain.MONEY)
        stage = self.engine.assess_growth_stage("u001")
        assert stage in (GrowthStage.GROWING, GrowthStage.BUILDING)

    def test_daily_task_returned(self):
        task = self.engine.daily_task("u001")
        assert isinstance(task, str) and len(task) > 5

    def test_growth_message_returned(self):
        msg = self.engine.growth_message("u001")
        assert isinstance(msg, str) and len(msg) > 5

    def test_progress_report_structure(self):
        report = self.engine.progress_report("u001")
        assert "growth_stage" in report
        assert "domains" in report
        assert "daily_task" in report

    def test_disabled_domain_raises(self):
        engine = MentorEngine(enabled_domains=[MentorDomain.MONEY])
        with pytest.raises(MentorEngineError):
            engine.teach("u001", MentorDomain.TECH)


# ===========================================================================
# Bot Factory tests
# ===========================================================================

class TestBotFactory:
    def setup_method(self):
        self.factory = BotFactory(max_bots=10)

    def test_create_bot_returns_manufactured_bot(self):
        bot = self.factory.create_bot(
            name="Mentor Bot",
            category=BotCategory.MENTOR,
            mission="Teach money systems to beginners.",
        )
        assert bot.name == "Mentor Bot"
        assert bot.category == BotCategory.MENTOR

    def test_bot_id_auto_assigned(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "Test mission")
        assert bot.bot_id.startswith("bot_")

    def test_bot_starts_in_blueprint_status(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "Test mission")
        assert bot.status == BotStatus.BLUEPRINT

    def test_create_bot_with_skills_and_objectives(self):
        bot = self.factory.create_bot(
            "Sales Bot",
            BotCategory.SALES,
            "Generate leads",
            core_skills=["lead gen", "CRM"],
            objectives=["100 leads/day"],
            revenue_goal_usd=5000.0,
            tools=["HubSpot", "Zapier"],
        )
        assert bot.prospectus.revenue_goal_usd == 5000.0
        assert "lead gen" in bot.prospectus.core_skills

    def test_readiness_score_increases_with_skills(self):
        bot_low = self.factory.create_bot("A", BotCategory.CUSTOM, "M")
        bot_high = self.factory.create_bot(
            "B",
            BotCategory.CUSTOM,
            "M",
            core_skills=["s1", "s2", "s3"],
            objectives=["o1", "o2"],
            tools=["t1"],
        )
        assert bot_high.readiness_score > bot_low.readiness_score

    def test_complete_task_increases_readiness(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "Mission")
        before = bot.readiness_score
        bot.complete_task("Build API")
        assert bot.readiness_score >= before

    def test_advance_status(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "Mission")
        advanced = self.factory.advance_bot(bot.bot_id)
        assert advanced.status == BotStatus.IN_PROGRESS

    def test_retire_bot(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "Mission")
        self.factory.retire_bot(bot.bot_id)
        assert self.factory.get_bot(bot.bot_id).status == BotStatus.RETIRED

    def test_list_bots(self):
        self.factory.create_bot("A", BotCategory.MENTOR, "M")
        self.factory.create_bot("B", BotCategory.MONEY, "M")
        assert len(self.factory.list_bots()) == 2

    def test_list_bots_filtered_by_category(self):
        self.factory.create_bot("A", BotCategory.MENTOR, "M")
        self.factory.create_bot("B", BotCategory.MONEY, "M")
        mentors = self.factory.list_bots(category=BotCategory.MENTOR)
        assert len(mentors) == 1

    def test_max_bots_enforced(self):
        factory = BotFactory(max_bots=2)
        factory.create_bot("A", BotCategory.CUSTOM, "M")
        factory.create_bot("B", BotCategory.CUSTOM, "M")
        with pytest.raises(BotFactoryError):
            factory.create_bot("C", BotCategory.CUSTOM, "M")

    def test_factory_report(self):
        self.factory.create_bot("A", BotCategory.MENTOR, "M")
        report = self.factory.factory_report()
        assert report["total_bots"] == 1
        assert "by_status" in report

    def test_log_error(self):
        bot = self.factory.create_bot("Test", BotCategory.CUSTOM, "M")
        bot.log_error("Connection timeout", "API call")
        assert len(bot.errors_log) == 1

    def test_record_revenue(self):
        bot = self.factory.create_bot("Test", BotCategory.MONEY, "M")
        bot.record_revenue(150.0)
        assert bot.revenue_earned_usd == 150.0


# ===========================================================================
# Continuous Study Engine tests
# ===========================================================================

class TestContinuousStudyEngine:
    def setup_method(self):
        self.engine = ContinuousStudyEngine(enabled=True)

    def test_builtin_modules_loaded(self):
        assert len(self.engine.list_modules()) >= len(BUILTIN_MODULES)

    def test_ingest_pattern(self):
        p = self.engine.ingest_pattern(
            domain=KnowledgeDomain.MONETIZATION,
            title="Subscription compound",
            summary="Subscriptions compound MRR monthly.",
            source="DreamCo research",
        )
        assert p.pattern_id.startswith("ptn_")
        assert p.domain == KnowledgeDomain.MONETIZATION

    def test_pattern_count_increases(self):
        before = self.engine.pattern_count()
        self.engine.ingest_pattern(KnowledgeDomain.AI_TOOLS, "Test", "Summary", "src")
        assert self.engine.pattern_count() == before + 1

    def test_search_by_domain(self):
        self.engine.ingest_pattern(KnowledgeDomain.FINANCE, "Finance tip", "Tip", "src")
        results = self.engine.search_patterns(domain=KnowledgeDomain.FINANCE)
        assert len(results) >= 1

    def test_search_monetizable_only(self):
        self.engine.ingest_pattern(
            KnowledgeDomain.MONETIZATION,
            "Revenue",
            "Makes money",
            "src",
            monetization_potential=True,
        )
        results = self.engine.search_patterns(monetizable_only=True)
        assert all(p.monetization_potential for p in results)

    def test_add_custom_module(self):
        before = len(self.engine.list_modules())
        self.engine.add_module("Custom", KnowledgeDomain.CODING, "Custom crawler")
        assert len(self.engine.list_modules()) == before + 1

    def test_deactivate_module(self):
        modules = self.engine.list_modules(active_only=True)
        first_id = modules[0].module_id
        self.engine.deactivate_module(first_id)
        active = [m for m in self.engine.list_modules() if m.module_id == first_id]
        assert not active[0].active

    def test_disabled_engine_raises_on_ingest(self):
        engine = ContinuousStudyEngine(enabled=False)
        with pytest.raises(ContinuousStudyError):
            engine.ingest_pattern(KnowledgeDomain.AI_TOOLS, "T", "S", "src")

    def test_study_report_structure(self):
        report = self.engine.study_report()
        assert "total_modules" in report
        assert "total_patterns" in report
        assert "enabled" in report

    def test_scan_count_increments_on_ingest(self):
        modules = self.engine.list_modules(active_only=True)
        domain_module = next(
            (m for m in modules if m.domain == KnowledgeDomain.AI_TOOLS), None
        )
        if domain_module:
            before = domain_module.scan_count
            self.engine.ingest_pattern(KnowledgeDomain.AI_TOOLS, "T", "S", "src")
            assert domain_module.scan_count == before + 1


# ===========================================================================
# Prospectus System tests
# ===========================================================================

class TestProspectusSystem:
    def setup_method(self):
        self.ps = ProspectusSystem()

    def test_create_prospectus(self):
        p = self.ps.create(
            bot_name="Sales Bot",
            executive_summary="Automates lead generation.",
            core_skills=["CRM integration", "Email automation"],
            objectives=["100 leads/day"],
        )
        assert p.bot_name == "Sales Bot"
        assert p.prospectus_id.startswith("prs_")

    def test_readiness_score_increases_with_content(self):
        p_low = self.ps.create("Bot A")
        p_high = self.ps.create(
            "Bot B",
            executive_summary="Full summary",
            core_skills=["s1", "s2", "s3"],
            objectives=["o1", "o2"],
        )
        assert p_high.readiness_score >= p_low.readiness_score

    def test_advance_status(self):
        p = self.ps.create("Test Bot")
        assert p.status == ProspectusStatus.DRAFT
        p.advance_status()
        assert p.status == ProspectusStatus.REVIEW

    def test_add_study_item(self):
        p = self.ps.create("Test Bot")
        item = p.add_study_item("APIs 101", "tech")
        assert item.topic == "APIs 101"

    def test_complete_study_item(self):
        p = self.ps.create("Test Bot")
        p.add_study_item("APIs 101", "tech")
        completed = p.complete_study_item(1)
        assert completed is not None
        assert completed.status == "complete"

    def test_add_checklist_item(self):
        p = self.ps.create("Test Bot")
        p.add_checklist_item("Deploy to production")
        assert len(p.checklist) == 1

    def test_complete_checklist_item(self):
        p = self.ps.create("Test Bot")
        p.add_checklist_item("Deploy to production")
        result = p.complete_checklist_item("Deploy to production")
        assert result
        assert p.checklist[0]["done"]

    def test_roi_bridge_annual_projection(self):
        roi = ROIBridge(
            revenue_model="subscription",
            monthly_revenue_target=1000.0,
            scale_multiplier=2.0,
        )
        assert roi.annual_revenue_projection() == 24000.0

    def test_list_all_returns_all(self):
        self.ps.create("Bot A")
        self.ps.create("Bot B")
        assert len(self.ps.list_all()) == 2

    def test_list_by_status(self):
        p = self.ps.create("Bot A")
        p.advance_status()  # REVIEW
        self.ps.create("Bot B")  # DRAFT
        drafts = self.ps.list_all(status=ProspectusStatus.DRAFT)
        assert len(drafts) == 1

    def test_system_report(self):
        self.ps.create("Bot A")
        report = self.ps.system_report()
        assert "total" in report
        assert "average_readiness_score" in report


# ===========================================================================
# Courses System tests
# ===========================================================================

class TestCoursesSystem:
    def setup_method(self):
        self.cs = CoursesSystem()

    def test_seed_courses_loaded(self):
        assert self.cs.course_count() >= 5

    def test_create_course(self):
        c = self.cs.create_course(
            "Test Course",
            CourseCategory.CODING,
            "Learn Python basics",
            price_usd=19.0,
        )
        assert c.title == "Test Course"
        assert c.course_id.startswith("crs_")

    def test_add_lesson(self):
        c = self.cs.create_course("Test", CourseCategory.TECH, "Desc")
        lesson = self.cs.add_lesson(
            c.course_id,
            title="APIs 101",
            content="APIs are bridges between systems.",
            takeaway="Master APIs to connect any two tools.",
        )
        assert lesson.title == "APIs 101"

    def test_enroll_user(self):
        courses = self.cs.list_courses()
        course_id = courses[0].course_id
        enrollment = self.cs.enroll("u001", course_id)
        assert enrollment.user_id == "u001"

    def test_complete_lesson(self):
        c = self.cs.create_course("Test", CourseCategory.TECH, "Desc")
        lesson = self.cs.add_lesson(c.course_id, "L1", "Content", "Takeaway")
        self.cs.enroll("u001", c.course_id)
        result = self.cs.complete_lesson("u001", c.course_id, lesson.lesson_id)
        assert result["progress_pct"] == 100.0

    def test_complete_lesson_unenrolled_raises(self):
        c = self.cs.create_course("Test", CourseCategory.TECH, "Desc")
        with pytest.raises(CoursesSystemError):
            self.cs.complete_lesson("ghost", c.course_id, "les_001")

    def test_list_courses_by_category(self):
        self.cs.create_course("A", CourseCategory.CODING, "D")
        coding_courses = self.cs.list_courses(category=CourseCategory.CODING)
        assert len(coding_courses) >= 1

    def test_revenue_summary(self):
        summary = self.cs.revenue_summary()
        assert "total_courses" in summary
        assert "total_catalog_value_usd" in summary

    def test_course_to_dict(self):
        c = self.cs.create_course("T", CourseCategory.MINDSET, "D", price_usd=10.0)
        d = c.to_dict()
        assert d["price_usd"] == 10.0


# ===========================================================================
# Route & GPS Intelligence tests
# ===========================================================================

class TestRouteGPS:
    def setup_method(self):
        self.gps = RouteGPSIntelligence(default_city="Atlanta", default_state="GA")

    def test_seed_resources_loaded(self):
        assert self.gps.resource_count() >= 4

    def test_add_resource(self):
        r = self.gps.add_resource(
            name="Local Food Bank",
            category=ResourceCategory.FOOD,
            description="Free groceries every Saturday.",
            city="Atlanta",
            free=True,
        )
        assert r.name == "Local Food Bank"
        assert r.resource_id.startswith("res_")

    def test_search_by_category(self):
        results = self.gps.search_resources(category=ResourceCategory.COMMUNITY)
        assert len(results) >= 1

    def test_search_free_only(self):
        results = self.gps.search_resources(free_only=True)
        assert all(r.free for r in results)

    def test_navigate_returns_routes(self):
        routes = self.gps.navigate("business")
        assert len(routes) >= 1
        assert isinstance(routes[0], Route)

    def test_navigate_with_city_filter(self):
        self.gps.add_resource(
            "City Resource", ResourceCategory.COMMUNITY, "Local", city="Miami", free=True
        )
        routes = self.gps.navigate("community", city="Miami")
        # Should find Miami-specific + national resources
        assert isinstance(routes, list)

    def test_create_route(self):
        resources = self.gps.search_resources()
        r_id = resources[0].resource_id
        route = self.gps.create_route(
            route_type=RouteType.SERVICE,
            resource_id=r_id,
            steps=["Go online", "Fill form"],
            big_bro_tip="Take this step today.",
        )
        assert route.route_id.startswith("rte_")
        assert len(route.steps) == 2

    def test_gps_report_structure(self):
        report = self.gps.gps_report()
        assert "total_resources" in report
        assert "default_city" in report


# ===========================================================================
# Sales & Monetization Engine tests
# ===========================================================================

class TestSalesMonetizationEngine:
    def setup_method(self):
        self.engine = SalesMonetizationEngine()

    def test_seed_streams_loaded(self):
        assert len(self.engine.list_streams()) >= 4

    def test_create_stream(self):
        s = self.engine.create_stream(
            name="Roast Bot License",
            stream_type=IncomeStreamType.DIGITAL_PRODUCT,
            price_usd=97.0,
        )
        assert s.name == "Roast Bot License"

    def test_recurring_stream_monthly_revenue(self):
        s = self.engine.create_stream(
            "Sub", IncomeStreamType.SUBSCRIPTION, 49.0, is_recurring=True
        )
        s.add_customers(10)
        assert s.monthly_revenue_usd == 490.0

    def test_non_recurring_stream_zero_mrr(self):
        s = self.engine.create_stream(
            "One-time", IncomeStreamType.ONE_TIME, 97.0, is_recurring=False
        )
        assert s.monthly_revenue_usd == 0.0

    def test_record_transaction(self):
        streams = self.engine.list_streams()
        s_id = streams[0].stream_id
        tx = self.engine.record_transaction(s_id, 49.0, "cust_001")
        assert tx["amount"] == 49.0

    def test_total_revenue(self):
        streams = self.engine.list_streams()
        self.engine.record_transaction(streams[0].stream_id, 100.0)
        assert self.engine.total_revenue() >= 100.0

    def test_compound_interest(self):
        result = self.engine.calculate_compound(1000.0, 0.07, 10)
        assert result["final_amount"] > 1000.0
        assert "explanation" in result

    def test_compound_interest_function(self):
        result = compound_interest(1000.0, 0.10, 5)
        assert result["final_amount"] > 1000.0
        assert result["growth_multiplier"] > 1.0

    def test_project_goal(self):
        result = self.engine.project_goal(5, 20.0)
        assert result["daily_revenue_usd"] == 100.0
        assert result["monthly_revenue_usd"] == 3000.0
        assert "explanation" in result

    def test_revenue_dashboard(self):
        dashboard = self.engine.revenue_dashboard()
        assert "total_streams" in dashboard
        assert "payment_methods_supported" in dashboard
        assert len(dashboard["payment_methods_supported"]) >= 10

    def test_payment_methods_present(self):
        assert "stripe" in PAYMENT_METHODS
        assert "paypal" in PAYMENT_METHODS
        assert "apple_pay" in PAYMENT_METHODS


# ===========================================================================
# Catalog & Franchise Engine tests
# ===========================================================================

class TestCatalogFranchiseEngine:
    def setup_method(self):
        self.engine = CatalogFranchiseEngine()

    def test_seed_catalog_loaded(self):
        assert self.engine.item_count() >= 5

    def test_add_item(self):
        item = self.engine.add_item(
            "Test Bot", CatalogCategory.BOTS, "A test bot", 99.0
        )
        assert item.name == "Test Bot"
        assert item.item_id.startswith("itm_")

    def test_commission_calculation(self):
        item = self.engine.add_item("T", CatalogCategory.BOTS, "Desc", 100.0, commission_pct=0.30)
        assert item.commission_amount() == 30.0

    def test_search_catalog_by_category(self):
        results = self.engine.search_catalog(category=CatalogCategory.AI_TOOLS)
        assert len(results) >= 1

    def test_search_catalog_by_tag(self):
        results = self.engine.search_catalog(tag="bots")
        assert len(results) >= 1

    def test_search_catalog_max_price(self):
        results = self.engine.search_catalog(max_price=50.0)
        assert all(i.price_usd <= 50.0 for i in results)

    def test_open_franchise(self):
        f = self.engine.open_franchise("Marcus", "Atlanta, GA")
        assert f.owner_name == "Marcus"
        assert f.status == FranchiseStatus.PENDING

    def test_activate_franchise(self):
        f = self.engine.open_franchise("Marcus", "Atlanta")
        self.engine.activate_franchise(f.franchise_id)
        assert self.engine.get_franchise(f.franchise_id).status == FranchiseStatus.ACTIVE

    def test_place_order(self):
        items = self.engine.search_catalog()
        order = self.engine.place_order("cust_001", items[0].item_id)
        assert order.order_id.startswith("ord_")
        assert order.amount_usd == items[0].price_usd

    def test_place_order_through_franchise(self):
        f = self.engine.open_franchise("Marcus", "Atlanta")
        self.engine.activate_franchise(f.franchise_id)
        items = self.engine.search_catalog()
        order = self.engine.place_order("cust_001", items[0].item_id, f.franchise_id)
        assert order.commission_usd > 0
        franchise = self.engine.get_franchise(f.franchise_id)
        assert franchise.total_orders == 1

    def test_place_order_unknown_item_raises(self):
        with pytest.raises(CatalogFranchiseError):
            self.engine.place_order("cust_001", "itm_9999")

    def test_catalog_report_structure(self):
        report = self.engine.catalog_report()
        assert "total_catalog_items" in report
        assert "total_franchises" in report

    def test_franchise_count(self):
        before = self.engine.franchise_count()
        self.engine.open_franchise("Jordan", "Miami, FL")
        assert self.engine.franchise_count() == before + 1


# ===========================================================================
# Master Dashboard tests
# ===========================================================================

class TestMasterDashboard:
    def setup_method(self):
        self.dashboard = MasterDashboard(big_bro_name="Big Bro", tier="pro")

    def test_panel_names_defined(self):
        assert "overview" in PANEL_NAMES
        assert "bot_factory" in PANEL_NAMES
        assert "sales_monetization" in PANEL_NAMES

    def test_update_and_get_panel(self):
        self.dashboard.update_panel("bot_factory", {"total_bots": 5})
        panel = self.dashboard.get_panel("bot_factory")
        assert panel["total_bots"] == 5

    def test_add_alert(self):
        alert = self.dashboard.add_alert(AlertLevel.WARNING, "bot_factory", "Low readiness")
        assert alert.level == AlertLevel.WARNING

    def test_get_alerts_filtered(self):
        self.dashboard.add_alert(AlertLevel.INFO, "study", "Pattern found")
        self.dashboard.add_alert(AlertLevel.ERROR, "factory", "Bot failed")
        errors = self.dashboard.get_alerts(level=AlertLevel.ERROR)
        assert all(a.level == AlertLevel.ERROR for a in errors)

    def test_clear_alerts(self):
        self.dashboard.add_alert(AlertLevel.INFO, "test", "Test")
        cleared = self.dashboard.clear_alerts()
        assert cleared >= 1
        assert len(self.dashboard.get_alerts()) == 0

    def test_snapshot_contains_panels(self):
        snap = self.dashboard.snapshot()
        assert "panels" in snap
        assert "big_bro_name" in snap
        assert snap["big_bro_name"] == "Big Bro"

    def test_kpi_summary_returns_dict(self):
        self.dashboard.update_panel("sales_monetization", {"total_revenue_usd": 500.0})
        kpis = self.dashboard.kpi_summary()
        assert "total_revenue_usd" in kpis

    def test_export_for_browser(self):
        result = self.dashboard.export_for_device("browser")
        assert result["device"] == "browser"
        assert result["no_download_required"]

    def test_export_for_xbox(self):
        result = self.dashboard.export_for_device("xbox")
        assert result["device"] == "xbox"

    def test_export_unknown_device_defaults_to_browser(self):
        result = self.dashboard.export_for_device("playstation5")
        assert result["device"] == "browser"


# ===========================================================================
# BigBroAI Integration tests
# ===========================================================================

class TestBigBroAI:
    def setup_method(self):
        self.big_bro = BigBroAI(tier=Tier.PRO, name="Big Bro", city="Atlanta")

    def test_tier_info(self):
        info = self.big_bro.tier_info()
        assert info["tier"] == "pro"
        assert info["name"] == "Pro"

    def test_upgrade_info_from_free(self):
        bb = BigBroAI(tier=Tier.FREE)
        info = bb.upgrade_info()
        assert info is not None
        assert info["tier"] == "pro"

    def test_upgrade_info_from_enterprise_is_none(self):
        bb = BigBroAI(tier=Tier.ENTERPRISE)
        assert bb.upgrade_info() is None

    def test_introduce(self):
        intro = self.big_bro.introduce()
        assert "Big Bro" in intro

    def test_greet_user(self):
        greeting = self.big_bro.greet("Marcus")
        assert "Marcus" in greeting

    def test_roast_excuse(self):
        roast = self.big_bro.roast("I'll do it later")
        assert "later" in roast or "excuse" in roast.lower()

    def test_defend_creator(self):
        defense = self.big_bro.defend("Jordan")
        assert "Jordan" in defense

    def test_create_user_profile(self):
        result = self.big_bro.create_user("u001", "Marcus", nickname="M")
        assert result["name"] == "Marcus"

    def test_remember_user(self):
        self.big_bro.create_user("u001", "Marcus")
        recall = self.big_bro.remember("u001")
        assert "Marcus" in recall

    def test_log_life_event(self):
        self.big_bro.create_user("u001", "Marcus")
        entry = self.big_bro.log_life_event("u001", "stress", "School is hard", ["school"])
        assert entry["situation"] == "stress"

    def test_teach_money(self):
        result = self.big_bro.teach("u001", MentorDomain.MONEY)
        assert result["domain"] == "money"

    def test_teach_tech(self):
        result = self.big_bro.teach("u001", MentorDomain.TECH)
        assert result["domain"] == "tech"

    def test_progress_report(self):
        self.big_bro.teach("u001", MentorDomain.MONEY)
        report = self.big_bro.progress_report("u001")
        assert "growth_stage" in report

    def test_create_bot(self):
        bot = self.big_bro.create_bot(
            "Mentor Bot", BotCategory.MENTOR, "Teach financial freedom"
        )
        assert bot["name"] == "Mentor Bot"

    def test_factory_report(self):
        self.big_bro.create_bot("Test", BotCategory.CUSTOM, "M")
        report = self.big_bro.factory_report()
        assert report["total_bots"] >= 1

    def test_create_prospectus(self):
        p = self.big_bro.create_prospectus("Sales Bot", executive_summary="Lead gen")
        assert p["bot_name"] == "Sales Bot"

    def test_list_courses(self):
        courses = self.big_bro.list_courses()
        assert len(courses) >= 5

    def test_enroll_in_course(self):
        courses = self.big_bro.list_courses()
        course_id = courses[0]["course_id"]
        enrollment = self.big_bro.enroll_in_course("u001", course_id)
        assert enrollment["user_id"] == "u001"

    def test_find_resources(self):
        routes = self.big_bro.find_resources("business")
        assert isinstance(routes, list)

    def test_revenue_dashboard(self):
        dashboard = self.big_bro.revenue_dashboard()
        assert "total_streams" in dashboard

    def test_project_income(self):
        result = self.big_bro.project_income(5, 20.0)
        assert result["daily_revenue_usd"] == 100.0
        assert result["monthly_revenue_usd"] == 3000.0

    def test_compound_interest(self):
        result = self.big_bro.compound_interest(1000.0, 0.07, 10)
        assert result["final_amount"] > 1000.0

    def test_browse_catalog(self):
        items = self.big_bro.browse_catalog()
        assert len(items) >= 5

    def test_open_franchise(self):
        bb = BigBroAI(tier=Tier.ENTERPRISE)
        f = bb.open_franchise("Marcus", "Atlanta, GA")
        assert f["owner_name"] == "Marcus"

    def test_get_dashboard(self):
        dashboard = self.big_bro.get_dashboard()
        assert "panels" in dashboard
        assert dashboard["big_bro_name"] == "Big Bro"

    def test_get_dashboard_for_xbox(self):
        result = self.big_bro.get_dashboard_for_device("xbox")
        assert result["device"] == "xbox"

    def test_chat_greeting(self):
        response = self.big_bro.chat("hello")
        assert "message" in response
        assert response["source"] == "BigBroAI"

    def test_chat_money_question(self):
        response = self.big_bro.chat("how do I make money?")
        assert len(response["message"]) > 10

    def test_chat_tech_question(self):
        response = self.big_bro.chat("how do I build an AI bot?")
        assert len(response["message"]) > 10

    def test_chat_daily_task(self):
        response = self.big_bro.chat("what's my task today?")
        assert "task" in response["message"].lower() or len(response["message"]) > 5

    def test_chat_dashboard_request(self):
        response = self.big_bro.chat("show me the dashboard status")
        assert "Revenue" in response["message"] or "status" in response["message"].lower()

    def test_chat_upgrade_request(self):
        bb = BigBroAI(tier=Tier.FREE)
        response = bb.chat("how do I upgrade my tier?")
        assert len(response["message"]) > 10

    def test_chat_dreamco_philosophy(self):
        response = self.big_bro.chat("explain the dreamco philosophy")
        assert "system" in response["message"].lower() or len(response["message"]) > 10

    def test_process_alias(self):
        result = self.big_bro.process("hello")
        assert "message" in result

    def test_free_tier_lacks_franchise(self):
        bb = BigBroAI(tier=Tier.FREE)
        with pytest.raises(BigBroTierError):
            bb.open_franchise("Test", "City")

    def test_free_tier_lacks_continuous_study_on_study_engine(self):
        bb = BigBroAI(tier=Tier.FREE)
        assert not bb.study_engine.enabled

    def test_set_roast_mode(self):
        self.big_bro.set_roast_mode(RoastMode.SAVAGE)
        assert self.big_bro.personality.roast_mode == RoastMode.SAVAGE

    def test_big_bro_name_set_correctly(self):
        bb = BigBroAI(name="Mentor Supreme")
        assert bb.name == "Mentor Supreme"
        assert bb.personality.custom_name == "Mentor Supreme"

    def test_flow_attribute_present(self):
        """GlobalAISourcesFlow pipeline must be initialised."""
        assert hasattr(self.big_bro, "flow")
        assert self.big_bro.flow is not None
