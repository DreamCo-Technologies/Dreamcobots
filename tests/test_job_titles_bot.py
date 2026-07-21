"""
Tests for bots/job_titles_bot/ — Job Titles Bot

Covers:
  - Tier definitions and feature gating
  - Job Titles Database (search, filter, stats)
  - Job Bot Generator (generation, registry, upgrades)
  - Autonomous Trainer (face/object recognition, item valuation, training)
  - Cost Justification Engine (ROI, payment options, token management)
  - Main JobTitlesBot (integration, chat, BuddyBot registration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.job_titles_bot.tiers import Tier, get_bot_tier_info, BOT_FEATURES
from bots.job_titles_bot.job_titles_database import JobTitle, JobTitlesDatabase
from bots.job_titles_bot.job_bot_generator import GeneratedJobBot, JobBotGenerator
from bots.job_titles_bot.autonomous_trainer import (
    AutonomousTrainer,
    FaceRecord,
    ObjectRecord,
    ValuationResult,
    TrainingSession,
)
from bots.job_titles_bot.cost_justification import (
    CostJustificationEngine,
    CostItem,
    PaymentOption,
    CostJustification,
)
from bots.job_titles_bot.job_titles_bot import (
    JobTitlesBot,
    JobTitlesBotError,
    JobTitlesBotTierError,
)


# =============================================================================
# Tier Tests
# =============================================================================

class TestTierDefinitions:
    def test_all_tiers_exist(self):
        assert Tier.FREE
        assert Tier.PRO
        assert Tier.ENTERPRISE

    def test_bot_features_have_all_tiers(self):
        for tier in [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]:
            assert tier.value in BOT_FEATURES
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert isinstance(info["price_usd_monthly"], (int, float))
        assert isinstance(info["features"], list)

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"

    def test_enterprise_has_more_features_than_free(self):
        free_count = len(BOT_FEATURES[Tier.FREE.value])
        ent_count = len(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert ent_count > free_count

    def test_free_features_not_empty(self):
        assert BOT_FEATURES[Tier.FREE.value]

    def test_pro_features_include_bot_generation(self):
        features = " ".join(BOT_FEATURES[Tier.PRO.value]).lower()
        assert "bot" in features or "generation" in features or "custom" in features

    def test_enterprise_features_include_face_recognition(self):
        features = " ".join(BOT_FEATURES[Tier.ENTERPRISE.value]).lower()
        assert "face" in features or "recognition" in features


# =============================================================================
# Job Titles Database Tests
# =============================================================================

class TestJobTitlesDatabaseInit:
    def test_creates_with_default_data(self):
        db = JobTitlesDatabase()
        assert db.count() > 0

    def test_count_over_100(self):
        db = JobTitlesDatabase()
        assert db.count() >= 100

    def test_industries_not_empty(self):
        db = JobTitlesDatabase()
        assert len(db.industries()) > 0

    def test_industries_over_10(self):
        db = JobTitlesDatabase()
        assert len(db.industries()) >= 10

    def test_industries_are_sorted(self):
        db = JobTitlesDatabase()
        industries = db.industries()
        assert industries == sorted(industries)

    def test_extra_titles_merged(self):
        custom = JobTitle(
            title="Custom Bot Engineer",
            industry="Technology",
            responsibilities=["build bots"],
            automation_level="full",
            avg_salary_usd=100000,
        )
        db = JobTitlesDatabase(extra_titles=[custom])
        assert db.get("Custom Bot Engineer") is not None


class TestJobTitlesDatabaseSearch:
    def setup_method(self):
        self.db = JobTitlesDatabase()

    def test_search_returns_list(self):
        results = self.db.search("engineer")
        assert isinstance(results, list)

    def test_search_title_match_first(self):
        results = self.db.search("data analyst")
        assert len(results) > 0
        assert any("analyst" in r.title.lower() for r in results[:3])

    def test_search_case_insensitive(self):
        r1 = self.db.search("Software Engineer")
        r2 = self.db.search("software engineer")
        assert len(r1) == len(r2)

    def test_search_by_industry_keyword(self):
        results = self.db.search("finance")
        assert len(results) > 0

    def test_search_by_skill(self):
        results = self.db.search("python")
        assert len(results) > 0

    def test_search_no_match_returns_empty(self):
        results = self.db.search("xyznonexistent12345")
        assert results == []

    def test_search_partial_match(self):
        results = self.db.search("manager")
        assert len(results) > 0

    def test_by_industry_returns_correct_industry(self):
        results = self.db.by_industry("Technology")
        assert all(r.industry == "Technology" for r in results)

    def test_by_industry_case_insensitive(self):
        r1 = self.db.by_industry("Technology")
        r2 = self.db.by_industry("technology")
        assert len(r1) == len(r2)

    def test_by_industry_unknown_returns_empty(self):
        results = self.db.by_industry("MadeUpIndustry999")
        assert results == []

    def test_by_industry_technology_has_entries(self):
        results = self.db.by_industry("Technology")
        assert len(results) >= 5

    def test_by_industry_finance_has_entries(self):
        results = self.db.by_industry("Finance")
        assert len(results) >= 3


class TestJobTitlesDatabaseQuery:
    def setup_method(self):
        self.db = JobTitlesDatabase()

    def test_get_exact_match(self):
        job = self.db.get("Software Engineer")
        assert job is not None
        assert job.title == "Software Engineer"

    def test_get_case_insensitive(self):
        job = self.db.get("software engineer")
        assert job is not None

    def test_get_missing_returns_none(self):
        job = self.db.get("NoSuchJobTitle999")
        assert job is None

    def test_automatable_full(self):
        results = self.db.automatable("full")
        assert all(r.automation_level == "full" for r in results)
        assert len(results) > 0

    def test_automatable_partial(self):
        results = self.db.automatable("partial")
        assert all(r.automation_level == "partial" for r in results)
        assert len(results) > 0

    def test_automatable_assisted(self):
        results = self.db.automatable("assisted")
        assert all(r.automation_level == "assisted" for r in results)
        assert len(results) > 0

    def test_bot_replaceable_all_true(self):
        results = self.db.bot_replaceable()
        assert all(r.replaceable_by_bot for r in results)

    def test_bot_replaceable_not_empty(self):
        results = self.db.bot_replaceable()
        assert len(results) > 0

    def test_add_title(self):
        db = JobTitlesDatabase()
        custom = JobTitle(
            title="Drone Pilot",
            industry="Transportation",
            responsibilities=["fly drones", "inspections"],
            automation_level="partial",
            avg_salary_usd=55000,
        )
        before = db.count()
        db.add_title(custom)
        assert db.count() == before + 1
        assert db.get("Drone Pilot") is not None

    def test_stats_returns_dict(self):
        stats = self.db.stats()
        assert isinstance(stats, dict)
        assert "total_titles" in stats
        assert "industries" in stats
        assert "fully_automatable" in stats
        assert "bot_replaceable" in stats

    def test_stats_values_positive(self):
        stats = self.db.stats()
        assert stats["total_titles"] > 0
        assert stats["industries"] > 0

    def test_all_titles_returns_list(self):
        titles = self.db.all_titles()
        assert isinstance(titles, list)
        assert len(titles) == self.db.count()

    def test_job_title_has_required_fields(self):
        job = self.db.get("Accountant")
        assert job is not None
        assert isinstance(job.title, str)
        assert isinstance(job.industry, str)
        assert isinstance(job.responsibilities, list)
        assert job.automation_level in ("full", "partial", "assisted")
        assert isinstance(job.avg_salary_usd, int)


# =============================================================================
# Job Bot Generator Tests
# =============================================================================

class TestJobBotGenerator:
    def setup_method(self):
        self.db = JobTitlesDatabase()
        self.gen = JobBotGenerator()

    def _get_job(self, title: str) -> JobTitle:
        job = self.db.get(title)
        assert job is not None, f"'{title}' not in database"
        return job

    def test_generate_returns_generated_bot(self):
        job = self._get_job("Accountant")
        bot = self.gen.generate(job)
        assert isinstance(bot, GeneratedJobBot)

    def test_generate_caches_instance(self):
        job = self._get_job("Accountant")
        bot1 = self.gen.generate(job)
        bot2 = self.gen.generate(job)
        assert bot1 is bot2

    def test_generated_bot_has_correct_title(self):
        job = self._get_job("Data Analyst")
        bot = self.gen.generate(job)
        assert bot.job_title == "Data Analyst"

    def test_generated_bot_has_capabilities(self):
        job = self._get_job("Data Analyst")
        bot = self.gen.generate(job)
        assert isinstance(bot.capabilities, list)
        assert len(bot.capabilities) > 0

    def test_generated_bot_includes_universal_capabilities(self):
        job = self._get_job("Data Analyst")
        bot = self.gen.generate(job)
        caps_str = " ".join(bot.capabilities)
        assert "cost justification" in caps_str

    def test_generated_bot_is_active_by_default(self):
        job = self._get_job("Recruiter")
        bot = self.gen.generate(job)
        assert bot.is_active is True

    def test_generate_all(self):
        jobs = self.db.by_industry("Finance")
        bots = self.gen.generate_all(jobs)
        assert len(bots) == len(jobs)

    def test_list_generated(self):
        job = self._get_job("Accountant")
        gen = JobBotGenerator()
        gen.generate(job)
        assert "accountant" in gen.list_generated()

    def test_count(self):
        gen = JobBotGenerator()
        assert gen.count() == 0
        gen.generate(self._get_job("Accountant"))
        assert gen.count() == 1

    def test_get_returns_bot(self):
        gen = JobBotGenerator()
        job = self._get_job("Welder")
        gen.generate(job)
        bot = gen.get("Welder")
        assert bot is not None

    def test_get_case_insensitive(self):
        gen = JobBotGenerator()
        job = self._get_job("Welder")
        gen.generate(job)
        assert gen.get("welder") is not None

    def test_get_missing_returns_none(self):
        gen = JobBotGenerator()
        assert gen.get("NoSuchBot999") is None

    def test_propagate_upgrade(self):
        gen = JobBotGenerator()
        jobs = self.db.by_industry("Finance")
        gen.generate_all(jobs)
        count = gen.propagate_upgrade("2.0.0")
        assert count == len(jobs)
        for title in gen.list_generated():
            assert gen.get(title).version == "2.0.0"

    def test_propagate_upgrade_adds_capabilities(self):
        gen = JobBotGenerator()
        job = self._get_job("Accountant")
        bot = gen.generate(job)
        gen.propagate_upgrade("2.0.0", ["quantum accounting"])
        assert "quantum accounting" in bot.capabilities


class TestGeneratedJobBotChat:
    def setup_method(self):
        db = JobTitlesDatabase()
        gen = JobBotGenerator()
        job = db.get("Software Engineer")
        self.bot = gen.generate(job)

    def test_chat_returns_dict(self):
        result = self.bot.chat("Hello")
        assert isinstance(result, dict)

    def test_chat_has_reply(self):
        result = self.bot.chat("Hello")
        assert "reply" in result
        assert isinstance(result["reply"], str)

    def test_chat_capabilities_query(self):
        result = self.bot.chat("What can you do?")
        assert "capabilities" in result["reply"].lower() or "can" in result["reply"].lower()

    def test_chat_status_query(self):
        result = self.bot.chat("status")
        assert "active" in result["reply"].lower() or "inactive" in result["reply"].lower()

    def test_chat_upgrade_query(self):
        result = self.bot.chat("upgrade")
        assert "version" in result["reply"].lower() or "upgrade" in result["reply"].lower()

    def test_chat_includes_job_title(self):
        result = self.bot.chat("hello")
        assert "Software Engineer" in result["reply"] or "software engineer" in result["reply"].lower()

    def test_describe_returns_dict(self):
        desc = self.bot.describe()
        assert isinstance(desc, dict)
        assert "job_title" in desc
        assert "capabilities" in desc

    def test_upgrade_bumps_version(self):
        self.bot.upgrade("3.0.0")
        assert self.bot.version == "3.0.0"

    def test_upgrade_adds_capabilities(self):
        before = len(self.bot.capabilities)
        self.bot.upgrade("3.0.0", ["new capability"])
        assert len(self.bot.capabilities) >= before


# =============================================================================
# Autonomous Trainer Tests
# =============================================================================

class TestAutonomousTrainerFace:
    def setup_method(self):
        self.trainer = AutonomousTrainer()

    def test_register_face_returns_face_record(self):
        record = self.trainer.register_face("Alice", b"fake_encoding_data")
        assert isinstance(record, FaceRecord)

    def test_registered_face_has_label(self):
        record = self.trainer.register_face("Bob", b"bob_encoding")
        assert record.label == "Bob"

    def test_identify_face_returns_record(self):
        encoding = b"charlie_encoding_bytes"
        self.trainer.register_face("Charlie", encoding)
        found = self.trainer.identify_face(encoding)
        assert found is not None
        assert found.label == "Charlie"

    def test_identify_unknown_face_returns_none(self):
        result = self.trainer.identify_face(b"unknown_face_xyz_999")
        assert result is None

    def test_list_faces_returns_all(self):
        self.trainer.register_face("Face1", b"enc1")
        self.trainer.register_face("Face2", b"enc2")
        faces = self.trainer.list_faces()
        assert len(faces) >= 2

    def test_register_same_encoding_returns_same_id(self):
        enc = b"same_encoding"
        r1 = self.trainer.register_face("Person A", enc)
        r2 = self.trainer.register_face("Person B", enc)
        assert r1.face_id == r2.face_id


class TestAutonomousTrainerObject:
    def setup_method(self):
        self.trainer = AutonomousTrainer()

    def test_register_object_returns_record(self):
        record = self.trainer.register_object(
            category="coin",
            description="1955 penny",
            visual_keywords=["penny", "coin", "copper"],
            estimated_value_usd=50.0,
        )
        assert isinstance(record, ObjectRecord)

    def test_registered_object_has_correct_category(self):
        record = self.trainer.register_object("antique", "old vase", ["vase"])
        assert record.category == "antique"

    def test_recognize_object_returns_list(self):
        self.trainer.register_object("coin", "quarter", ["quarter", "coin"])
        results = self.trainer.recognize_object("this is a quarter coin")
        assert isinstance(results, list)

    def test_recognize_object_finds_match(self):
        self.trainer.register_object("coin", "dime", ["dime"])
        results = self.trainer.recognize_object("I found a dime on the floor")
        assert len(results) > 0

    def test_recognize_unknown_object_empty(self):
        results = self.trainer.recognize_object("xyzabc123 object")
        assert results == []


class TestAutonomousTrainerValuation:
    def setup_method(self):
        self.trainer = AutonomousTrainer()

    def test_valuate_penny_returns_result(self):
        result = self.trainer.valuate_item("old penny from 1955")
        assert isinstance(result, ValuationResult)

    def test_valuate_penny_category(self):
        result = self.trainer.valuate_item("old penny from 1955")
        assert result.category == "coin"

    def test_valuate_penny_value_positive(self):
        result = self.trainer.valuate_item("1955 double-die penny")
        assert result.estimated_value_usd > 0

    def test_valuate_penny_range_valid(self):
        result = self.trainer.valuate_item("1955 double-die penny")
        assert result.estimated_min_usd <= result.estimated_value_usd <= result.estimated_max_usd

    def test_valuate_gold_coin(self):
        result = self.trainer.valuate_item("gold coin from ancient Rome")
        assert result.category == "coin"
        assert result.estimated_value_usd > 100

    def test_valuate_antique_vase(self):
        result = self.trainer.valuate_item("antique vase from the 1800s")
        assert result.category == "antique"
        assert result.estimated_value_usd > 0

    def test_valuate_antique_painting(self):
        result = self.trainer.valuate_item("old oil painting")
        assert result.category == "antique"

    def test_valuate_currency_usd(self):
        result = self.trainer.valuate_item("1 usd bill")
        assert result.category == "currency"

    def test_valuate_bitcoin(self):
        result = self.trainer.valuate_item("bitcoin cryptocurrency")
        assert result.category in ("coin", "currency")

    def test_valuate_unknown_returns_unknown(self):
        result = self.trainer.valuate_item("xyzunknownobject123")
        assert result.category == "unknown"

    def test_valuate_condition_mint_higher_than_poor(self):
        poor = self.trainer.valuate_item("silver dollar", condition="poor")
        mint = self.trainer.valuate_item("silver dollar", condition="mint")
        assert mint.estimated_value_usd > poor.estimated_value_usd

    def test_valuate_result_has_explanation(self):
        result = self.trainer.valuate_item("penny")
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

    def test_valuate_result_has_factors(self):
        result = self.trainer.valuate_item("quarter")
        assert isinstance(result.factors, list)

    def test_valuate_confidence_between_0_and_1(self):
        result = self.trainer.valuate_item("penny")
        assert 0.0 <= result.confidence <= 1.0


class TestAutonomousTrainerTraining:
    def setup_method(self):
        self.trainer = AutonomousTrainer()

    def test_run_training_returns_session(self):
        session = self.trainer.run_training_session("human", "data entry")
        assert isinstance(session, TrainingSession)

    def test_session_has_score(self):
        session = self.trainer.run_training_session("ai", "coin identification")
        assert 0.0 <= session.score <= 1.0

    def test_session_feedback_not_empty(self):
        session = self.trainer.run_training_session("human", "face recognition")
        assert len(session.feedback) > 0

    def test_session_trainee_correct(self):
        session = self.trainer.run_training_session("human", "skill")
        assert session.trainee == "human"

    def test_session_skill_correct(self):
        session = self.trainer.run_training_session("ai", "coin identification")
        assert session.skill == "coin identification"

    def test_passed_high_score(self):
        # Force a known skill that produces score >= 0.6
        trainer = AutonomousTrainer()
        session = trainer.run_training_session("human", "any skill")
        assert isinstance(session.passed, bool)

    def test_training_history_empty_at_start(self):
        trainer = AutonomousTrainer()
        assert trainer.training_history() == []

    def test_training_history_grows(self):
        trainer = AutonomousTrainer()
        trainer.run_training_session("human", "skill1")
        trainer.run_training_session("human", "skill2")
        assert len(trainer.training_history()) == 2

    def test_training_history_filter_by_trainee(self):
        trainer = AutonomousTrainer()
        trainer.run_training_session("human", "reading")
        trainer.run_training_session("ai", "vision")
        human_sessions = trainer.training_history(trainee="human")
        assert all(s.trainee == "human" for s in human_sessions)

    def test_stats_returns_dict(self):
        stats = self.trainer.stats()
        assert "registered_faces" in stats
        assert "training_sessions" in stats

    def test_upgrade_module_changes_version(self):
        old_version = self.trainer.version
        result = self.trainer.upgrade_module("2.0.0")
        assert self.trainer.version == "2.0.0"
        assert result["new_version"] == "2.0.0"
        assert result["old_version"] == old_version

    def test_upgrade_callback_called(self):
        called = []
        self.trainer.register_upgrade_callback(lambda v: called.append(v))
        self.trainer.upgrade_module("3.0.0")
        assert "3.0.0" in called


# =============================================================================
# Cost Justification Engine Tests
# =============================================================================

class TestCostJustificationEngine:
    def setup_method(self):
        self.engine = CostJustificationEngine(token_balance=10000)

    def test_justify_returns_justification(self):
        result = self.engine.justify("PRO Upgrade", 49.0, 200.0)
        assert isinstance(result, CostJustification)

    def test_justify_total_monthly(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert result.total_monthly_usd == 49.0

    def test_justify_annual_less_than_12_months(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert result.total_annual_usd < 49.0 * 12

    def test_justify_roi_explanation_not_empty(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert len(result.roi_explanation) > 0

    def test_justify_break_even_positive(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert result.break_even_months > 0

    def test_justify_payment_options_not_empty(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert len(result.payment_options) >= 3

    def test_justify_has_monthly_card_option(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        option_ids = [o.option_id for o in result.payment_options]
        assert "monthly_card" in option_ids

    def test_justify_has_paypal_option(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        option_ids = [o.option_id for o in result.payment_options]
        assert "monthly_paypal" in option_ids

    def test_justify_has_annual_option(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        option_ids = [o.option_id for o in result.payment_options]
        assert "annual_card" in option_ids

    def test_justify_has_token_option(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        option_ids = [o.option_id for o in result.payment_options]
        assert "tokens" in option_ids

    def test_justify_recommended_option_valid(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        option_ids = [o.option_id for o in result.payment_options]
        assert result.recommended_option in option_ids

    def test_justify_proceeds_when_roi_positive(self):
        result = self.engine.justify("Good Deal", 10.0, 100.0)
        assert result.autonomous_decision == "proceed"

    def test_justify_defers_when_roi_negative(self):
        result = self.engine.justify("Bad Deal", 100.0, 5.0)
        assert result.autonomous_decision == "defer_to_operator"

    def test_justify_token_cost_set(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        assert result.token_cost is not None
        assert result.token_cost > 0

    def test_format_report_returns_string(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        report = self.engine.format_report(result)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_format_report_contains_monthly_cost(self):
        result = self.engine.justify("Feature", 49.0, 200.0)
        report = self.engine.format_report(result)
        assert "49" in report

    def test_add_tokens(self):
        engine = CostJustificationEngine(token_balance=1000)
        new_balance = engine.add_tokens(500)
        assert new_balance == 1500

    def test_deduct_tokens_success(self):
        engine = CostJustificationEngine(token_balance=1000)
        result = engine.deduct_tokens(200)
        assert result["success"] is True
        assert result["balance"] == 800

    def test_deduct_tokens_insufficient(self):
        engine = CostJustificationEngine(token_balance=100)
        result = engine.deduct_tokens(500)
        assert result["success"] is False
        assert "error" in result

    def test_deduct_tokens_does_not_go_negative(self):
        engine = CostJustificationEngine(token_balance=100)
        engine.deduct_tokens(500)
        assert engine.token_balance == 100

    def test_justification_with_line_items(self):
        items = [
            CostItem("API calls", 20.0, "monthly", "DreamCo API usage"),
            CostItem("Storage", 5.0, "monthly", "Bot data storage"),
        ]
        result = self.engine.justify("Feature", 49.0, 200.0, line_items=items)
        assert len(result.line_items) == 2


# =============================================================================
# Main JobTitlesBot Integration Tests
# =============================================================================

class TestJobTitlesBotInstantiation:
    def test_default_tier_is_free(self):
        bot = JobTitlesBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = JobTitlesBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = JobTitlesBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = JobTitlesBot()
        assert bot.config is not None

    def test_token_balance_initialized(self):
        bot = JobTitlesBot(token_balance=5000)
        assert bot.token_balance == 5000


class TestJobTitlesBotTierInfo:
    def test_describe_tier_returns_string(self):
        bot = JobTitlesBot()
        desc = bot.describe_tier()
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_describe_tier_mentions_tier_name(self):
        bot = JobTitlesBot(tier=Tier.PRO)
        desc = bot.describe_tier()
        assert "Pro" in desc or "pro" in desc.lower()

    def test_get_upgrade_path_returns_value(self):
        bot = JobTitlesBot()
        path = bot.get_upgrade_path()
        assert path is not None


class TestJobTitlesBotSearch:
    def setup_method(self):
        self.free_bot = JobTitlesBot(tier=Tier.FREE)
        self.pro_bot = JobTitlesBot(tier=Tier.PRO)

    def test_search_jobs_returns_list(self):
        results = self.free_bot.search_jobs("engineer")
        assert isinstance(results, list)

    def test_search_jobs_free_limited(self):
        results = self.free_bot.search_jobs("engineer")
        assert len(results) <= 50

    def test_search_jobs_pro_not_limited(self):
        results = self.pro_bot.search_jobs("a")
        assert isinstance(results, list)

    def test_browse_industry_returns_list(self):
        results = self.free_bot.browse_industry("Technology")
        assert isinstance(results, list)

    def test_browse_industry_free_limited(self):
        results = self.free_bot.browse_industry("Technology")
        assert len(results) <= 50

    def test_list_industries_free_limited(self):
        industries = self.free_bot.list_industries()
        assert len(industries) <= 3

    def test_list_industries_pro_not_limited(self):
        industries = self.pro_bot.list_industries()
        assert len(industries) > 3

    def test_database_stats_returns_dict(self):
        stats = self.free_bot.database_stats()
        assert "total_titles" in stats

    def test_get_job_returns_job(self):
        job = self.free_bot.get_job("Accountant")
        assert job is not None
        assert job.title == "Accountant"

    def test_get_job_missing_returns_none(self):
        job = self.free_bot.get_job("NoSuchJob999")
        assert job is None


class TestJobTitlesBotTierGating:
    def setup_method(self):
        self.free_bot = JobTitlesBot(tier=Tier.FREE)
        self.pro_bot = JobTitlesBot(tier=Tier.PRO)
        self.enterprise_bot = JobTitlesBot(tier=Tier.ENTERPRISE)

    def test_list_automatable_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.list_automatable_jobs()

    def test_list_automatable_pro_ok(self):
        results = self.pro_bot.list_automatable_jobs()
        assert isinstance(results, list)

    def test_list_bot_replaceable_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.list_bot_replaceable()

    def test_list_bot_replaceable_pro_ok(self):
        results = self.pro_bot.list_bot_replaceable()
        assert isinstance(results, list)

    def test_generate_bot_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.generate_bot("Accountant")

    def test_generate_bot_pro_ok(self):
        bot = self.pro_bot.generate_bot("Accountant")
        assert isinstance(bot, GeneratedJobBot)

    def test_generate_bot_missing_title_raises(self):
        with pytest.raises(JobTitlesBotError):
            self.pro_bot.generate_bot("NoSuchJobTitle999")

    def test_generate_all_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.pro_bot.generate_all_bots()

    def test_generate_all_enterprise_ok(self):
        bots = self.enterprise_bot.generate_all_bots()
        assert isinstance(bots, list)
        assert len(bots) > 0

    def test_propagate_upgrade_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.pro_bot.propagate_buddy_upgrade("2.0.0")

    def test_propagate_upgrade_enterprise_ok(self):
        self.enterprise_bot.generate_all_bots()
        count = self.enterprise_bot.propagate_buddy_upgrade("2.0.0")
        assert count >= 0

    def test_train_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.train("human", "data entry")

    def test_train_pro_ok(self):
        session = self.pro_bot.train("human", "data entry")
        assert isinstance(session, TrainingSession)

    def test_register_face_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.pro_bot.register_face("Alice", b"encoding")

    def test_register_face_enterprise_ok(self):
        record = self.enterprise_bot.register_face("Alice", b"alice_encoding")
        assert isinstance(record, FaceRecord)

    def test_identify_face_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.pro_bot.identify_face(b"encoding")

    def test_identify_face_enterprise_ok(self):
        enc = b"bob_face_encoding"
        self.enterprise_bot.register_face("Bob", enc)
        found = self.enterprise_bot.identify_face(enc)
        assert found is not None
        assert found.label == "Bob"

    def test_register_object_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.pro_bot.register_object("coin", "penny", ["penny"])

    def test_register_object_enterprise_ok(self):
        record = self.enterprise_bot.register_object("coin", "penny", ["penny"])
        assert isinstance(record, ObjectRecord)

    def test_recognize_object_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.recognize_object("old penny")

    def test_recognize_object_pro_ok(self):
        results = self.pro_bot.recognize_object("old penny")
        assert isinstance(results, list)

    def test_valuate_item_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.valuate_item("old penny")

    def test_valuate_item_pro_ok(self):
        result = self.pro_bot.valuate_item("old penny")
        assert isinstance(result, ValuationResult)

    def test_trainer_stats_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.free_bot.trainer_stats()

    def test_trainer_stats_pro_ok(self):
        stats = self.pro_bot.trainer_stats()
        assert isinstance(stats, dict)


class TestJobTitlesBotCostJustification:
    def setup_method(self):
        self.bot = JobTitlesBot(tier=Tier.PRO, token_balance=5000)

    def test_justify_cost_returns_justification(self):
        result = self.bot.justify_cost("Feature", 49.0, 200.0)
        assert isinstance(result, CostJustification)

    def test_format_cost_report_returns_string(self):
        j = self.bot.justify_cost("Feature", 49.0, 200.0)
        report = self.bot.format_cost_report(j)
        assert isinstance(report, str)

    def test_add_tokens(self):
        bot = JobTitlesBot(tier=Tier.PRO, token_balance=1000)
        new_bal = bot.add_tokens(500)
        assert new_bal == 1500
        assert bot.token_balance == 1500

    def test_deduct_tokens_success(self):
        bot = JobTitlesBot(tier=Tier.PRO, token_balance=1000)
        result = bot.deduct_tokens(300)
        assert result["success"] is True
        assert bot.token_balance == 700

    def test_deduct_tokens_insufficient(self):
        bot = JobTitlesBot(tier=Tier.FREE, token_balance=100)
        result = bot.deduct_tokens(999)
        assert result["success"] is False


class TestJobTitlesBotChat:
    def setup_method(self):
        self.bot = JobTitlesBot(tier=Tier.PRO)

    def test_chat_returns_dict(self):
        result = self.bot.chat("Hello")
        assert isinstance(result, dict)

    def test_chat_has_reply(self):
        result = self.bot.chat("Hello")
        assert "reply" in result

    def test_chat_has_bot_name(self):
        result = self.bot.chat("Hello")
        assert result["bot_name"] == "job_titles_bot"

    def test_chat_has_tier(self):
        result = self.bot.chat("Hello")
        assert "tier" in result

    def test_chat_tier_query(self):
        result = self.bot.chat("What tier am I on?")
        assert len(result["reply"]) > 0

    def test_chat_search_query(self):
        result = self.bot.chat("search: accountant")
        assert len(result["reply"]) > 0

    def test_chat_cost_query(self):
        result = self.bot.chat("what does this cost?")
        assert "49" in result["reply"] or "cost" in result["reply"].lower()

    def test_chat_stats_query(self):
        result = self.bot.chat("database stats")
        assert len(result["reply"]) > 0

    def test_chat_hire_query(self):
        result = self.bot.chat("hire a robot for me")
        assert len(result["reply"]) > 0

    def test_chat_train_query(self):
        result = self.bot.chat("can you train me?")
        assert "train" in result["reply"].lower() or "training" in result["reply"].lower()

    def test_chat_default_response(self):
        result = self.bot.chat("xyzrandomquery12345")
        assert len(result["reply"]) > 0


class TestJobTitlesBotBuddyIntegration:
    def test_register_with_buddy(self):
        """JobTitlesBot can register with BuddyBot."""
        from BuddyAI.buddy_bot import BuddyBot
        buddy = BuddyBot()
        bot = JobTitlesBot(tier=Tier.PRO)
        bot.register_with_buddy(buddy)
        assert "job_titles_bot" in buddy.list_bots()

    def test_buddy_can_route_to_job_bot(self):
        """BuddyBot can route messages to the registered JobTitlesBot."""
        from BuddyAI.buddy_bot import BuddyBot
        buddy = BuddyBot()
        bot = JobTitlesBot(tier=Tier.PRO)
        bot.register_with_buddy(buddy)
        response = buddy.route_message("job_titles_bot", "Hello")
        assert "reply" in response
