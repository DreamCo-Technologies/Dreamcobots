"""
Tests for bots/auto_bot_factory/ — AutoBotFactory, CompetitorAnalyzer,
StrategyFramework, SafetyController, and tier configuration.
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.auto_bot_factory.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_BOT_GENERATION,
    FEATURE_COMPETITOR_ANALYSIS,
    FEATURE_STRATEGY_FRAMEWORK,
    FEATURE_AUTO_DEPLOY,
    FEATURE_SAFETY_CONTROLLER,
    FEATURE_SELF_HEALING,
    FEATURE_PERSISTENT_MEMORY,
    FEATURE_REAL_METRICS,
    FEATURE_DECISION_ENGINE,
    FEATURE_USAGE_BILLING,
    FEATURE_FULL_AUTONOMY,
    FEATURE_GITHUB_DEPLOY,
)
from bots.auto_bot_factory.competitor_analyzer import (
    CompetitorAnalyzer,
    CompetitorProfile,
    MarketGap,
    AnalysisReport,
)
from bots.auto_bot_factory.strategy_framework import (
    StrategyFramework,
    StrategyCategory,
    Strategy,
)
from bots.auto_bot_factory.safety_controller import (
    SafetyController,
    SafetyLimitError,
    MAX_BOTS,
    MAX_MESSAGES_PER_CYCLE,
)
from bots.auto_bot_factory.auto_bot_factory import (
    AutoBotFactory,
    AutoBotFactoryError,
    AutoBotFactoryTierError,
    BotBlueprint,
    DeploymentRecord,
)


# ---------------------------------------------------------------------------
# Framework compliance
# ---------------------------------------------------------------------------

class TestFrameworkCompliance:
    def test_auto_bot_factory_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "auto_bot_factory", "auto_bot_factory.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_competitor_analyzer_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "auto_bot_factory", "competitor_analyzer.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_strategy_framework_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "auto_bot_factory", "strategy_framework.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_safety_controller_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "auto_bot_factory", "safety_controller.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------

class TestAutoBotFactoryTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_basic_tier_price(self):
        config = get_tier_config(Tier.BASIC)
        assert config.price_usd_monthly == 99.0

    def test_advanced_tier_price(self):
        config = get_tier_config(Tier.ADVANCED)
        assert config.price_usd_monthly == 299.0

    def test_enterprise_tier_usage_based(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.price_usd_monthly == 0.0
        assert config.usage_rate_usd > 0.0

    def test_basic_monthly_limit(self):
        config = get_tier_config(Tier.BASIC)
        assert config.max_bots_per_month == 10

    def test_advanced_monthly_limit(self):
        config = get_tier_config(Tier.ADVANCED)
        assert config.max_bots_per_month == 50

    def test_enterprise_unlimited(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.max_bots_per_month is None
        assert config.is_unlimited() is True

    def test_basic_has_bot_generation(self):
        config = get_tier_config(Tier.BASIC)
        assert config.has_feature(FEATURE_BOT_GENERATION)

    def test_basic_lacks_competitor_analysis(self):
        config = get_tier_config(Tier.BASIC)
        assert not config.has_feature(FEATURE_COMPETITOR_ANALYSIS)

    def test_advanced_has_competitor_analysis(self):
        config = get_tier_config(Tier.ADVANCED)
        assert config.has_feature(FEATURE_COMPETITOR_ANALYSIS)

    def test_advanced_has_strategy_framework(self):
        config = get_tier_config(Tier.ADVANCED)
        assert config.has_feature(FEATURE_STRATEGY_FRAMEWORK)

    def test_enterprise_has_full_autonomy(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.has_feature(FEATURE_FULL_AUTONOMY)

    def test_all_tiers_have_github_deploy(self):
        for tier in Tier:
            config = get_tier_config(tier)
            assert config.has_feature(FEATURE_GITHUB_DEPLOY)

    def test_upgrade_path_basic_to_advanced(self):
        upgrade = get_upgrade_path(Tier.BASIC)
        assert upgrade is not None
        assert upgrade.tier == Tier.ADVANCED

    def test_upgrade_path_enterprise_is_none(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None


# ---------------------------------------------------------------------------
# Competitor Analyzer
# ---------------------------------------------------------------------------

class TestCompetitorAnalyzer:
    def test_analyze_returns_report(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("lead_generation")
        assert isinstance(report, AnalysisReport)

    def test_report_has_competitors(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("lead_generation")
        assert len(report.competitors) > 0

    def test_report_has_gaps(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("lead_generation")
        assert len(report.gaps) > 0

    def test_report_has_top_features_missing(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("sales")
        assert len(report.top_features_missing) > 0

    def test_report_has_recommended_price(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("sales")
        assert report.recommended_price_usd > 0

    def test_report_to_dict(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("automation")
        d = report.to_dict()
        assert "query" in d
        assert "competitors" in d
        assert "gaps" in d
        assert "top_features_missing" in d
        assert "recommended_price_usd" in d
        assert "competitor_count" in d

    def test_competitor_profile_to_dict(self):
        profile = CompetitorProfile(
            name="TestBot",
            category="sales",
            source="test",
            rating=4.0,
        )
        d = profile.to_dict()
        assert d["name"] == "TestBot"
        assert d["category"] == "sales"
        assert d["rating"] == 4.0

    def test_market_gap_to_dict(self):
        gap = MarketGap(
            category="sales",
            description="No AI",
            opportunity_score=80.0,
        )
        d = gap.to_dict()
        assert d["description"] == "No AI"
        assert d["opportunity_score"] == 80.0

    def test_get_top_opportunities(self):
        analyzer = CompetitorAnalyzer()
        opps = analyzer.get_top_opportunities("lead_generation")
        assert isinstance(opps, list)
        assert len(opps) > 0
        # sorted descending by opportunity_score
        scores = [o["opportunity_score"] for o in opps]
        assert scores == sorted(scores, reverse=True)

    def test_get_feature_recommendations(self):
        analyzer = CompetitorAnalyzer()
        recs = analyzer.get_feature_recommendations("sales")
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_analysis_history_tracked(self):
        analyzer = CompetitorAnalyzer()
        analyzer.analyze("lead_generation")
        analyzer.analyze("sales")
        history = analyzer.get_analysis_history()
        assert len(history) == 2

    def test_default_category_fallback(self):
        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze("unknown_category_xyz")
        assert len(report.competitors) > 0


# ---------------------------------------------------------------------------
# Strategy Framework
# ---------------------------------------------------------------------------

class TestStrategyFramework:
    def test_total_strategies_is_200(self):
        fw = StrategyFramework()
        assert fw.total_strategies == 200

    def test_all_strategies_returns_200(self):
        fw = StrategyFramework()
        strategies = fw.get_all_strategies()
        assert len(strategies) == 200

    def test_eight_categories(self):
        categories = list(StrategyCategory)
        assert len(categories) == 8

    def test_each_category_has_25_strategies(self):
        fw = StrategyFramework()
        for cat in StrategyCategory:
            strategies = fw.get_by_category(cat)
            assert len(strategies) == 25, f"{cat.value} has {len(strategies)} strategies"

    def test_strategy_has_required_fields(self):
        fw = StrategyFramework()
        strategies = fw.get_all_strategies()
        for s in strategies[:5]:
            assert "id" in s
            assert "name" in s
            assert "category" in s
            assert "description" in s
            assert "priority" in s

    def test_get_top_strategies(self):
        fw = StrategyFramework()
        top = fw.get_top_strategies(n=10)
        assert len(top) == 10
        priorities = [s["priority"] for s in top]
        assert priorities == sorted(priorities, reverse=True)

    def test_get_top_strategies_by_category(self):
        fw = StrategyFramework()
        top = fw.get_top_strategies(n=5, category=StrategyCategory.MONETIZATION)
        assert len(top) == 5
        for s in top:
            assert s["category"] == StrategyCategory.MONETIZATION.value

    def test_get_strategy_by_id(self):
        fw = StrategyFramework()
        s = fw.get_strategy_by_id(1)
        assert s is not None
        assert s["id"] == 1

    def test_get_strategy_by_invalid_id(self):
        fw = StrategyFramework()
        assert fw.get_strategy_by_id(9999) is None

    def test_get_recommended_for_bot(self):
        fw = StrategyFramework()
        recs = fw.get_recommended_for_bot("lead_generation", top_n=10)
        assert len(recs) == 10

    def test_get_category_summary(self):
        fw = StrategyFramework()
        summary = fw.get_category_summary()
        assert len(summary) == 8
        for cat in StrategyCategory:
            assert cat.value in summary
            assert summary[cat.value]["count"] == 25

    def test_strategy_ids_are_unique(self):
        fw = StrategyFramework()
        ids = [s["id"] for s in fw.get_all_strategies()]
        assert len(ids) == len(set(ids))

    def test_categories_covered(self):
        fw = StrategyFramework()
        categories = {s["category"] for s in fw.get_all_strategies()}
        expected = {c.value for c in StrategyCategory}
        assert categories == expected


# ---------------------------------------------------------------------------
# Safety Controller
# ---------------------------------------------------------------------------

class TestSafetyController:
    def test_default_limits(self):
        sc = SafetyController()
        assert sc.max_bots == MAX_BOTS
        assert sc.max_messages_per_cycle == MAX_MESSAGES_PER_CYCLE

    def test_max_bots_is_200(self):
        assert MAX_BOTS == 200

    def test_max_messages_is_10(self):
        assert MAX_MESSAGES_PER_CYCLE == 10

    def test_register_bot(self):
        sc = SafetyController()

        class FakeBot:
            def run(self):
                return "ok"

        sc.register_bot("test_bot", FakeBot())
        assert sc.get_bot_count() == 1

    def test_register_bot_exceeds_limit(self):
        sc = SafetyController(max_bots=2)

        class FakeBot:
            def run(self):
                return "ok"

        sc.register_bot("bot1", FakeBot())
        sc.register_bot("bot2", FakeBot())
        with pytest.raises(SafetyLimitError):
            sc.register_bot("bot3", FakeBot())

    def test_check_bot_limit(self):
        sc = SafetyController(max_bots=3)

        class FakeBot:
            def run(self):
                return "ok"

        assert sc.check_bot_limit() is True
        sc.register_bot("b1", FakeBot())
        sc.register_bot("b2", FakeBot())
        sc.register_bot("b3", FakeBot())
        assert sc.check_bot_limit() is False

    def test_unregister_bot(self):
        sc = SafetyController()

        class FakeBot:
            def run(self):
                return "ok"

        sc.register_bot("test_bot", FakeBot())
        removed = sc.unregister_bot("test_bot")
        assert removed is True
        assert sc.get_bot_count() == 0

    def test_unregister_nonexistent_returns_false(self):
        sc = SafetyController()
        assert sc.unregister_bot("nonexistent") is False

    def test_message_limit(self):
        sc = SafetyController(max_messages_per_cycle=3)
        assert sc.record_message_sent() is True
        assert sc.record_message_sent() is True
        assert sc.record_message_sent() is True
        assert sc.record_message_sent() is False

    def test_reset_message_cycle(self):
        sc = SafetyController(max_messages_per_cycle=2)
        sc.record_message_sent()
        sc.record_message_sent()
        assert sc.check_message_limit() is False
        sc.reset_message_cycle()
        assert sc.check_message_limit() is True

    def test_messages_remaining(self):
        sc = SafetyController(max_messages_per_cycle=5)
        sc.record_message_sent()
        sc.record_message_sent()
        assert sc.get_messages_remaining() == 3

    def test_run_bot_safe_success(self):
        sc = SafetyController()

        class FakeBot:
            def run(self):
                return "success"

        sc.register_bot("good_bot", FakeBot())
        result = sc.run_bot_safe("good_bot", FakeBot())
        assert result == "success"

    def test_run_bot_safe_removes_crashed_bot(self):
        sc = SafetyController()

        class CrashBot:
            def run(self):
                raise RuntimeError("boom")

        bot = CrashBot()
        sc.register_bot("crash_bot", bot)
        result = sc.run_bot_safe("crash_bot", bot)
        assert "crashed" in result
        assert "crash_bot" in sc.get_removed_bots()
        assert sc.get_bot_count() == 0

    def test_crash_log_records_error(self):
        sc = SafetyController()

        class CrashBot:
            def run(self):
                raise ValueError("test error")

        bot = CrashBot()
        sc.register_bot("crash_bot", bot)
        sc.run_bot_safe("crash_bot", bot)
        log = sc.get_crash_log()
        assert len(log) == 1
        assert "test error" in log[0]["error"]

    def test_get_status(self):
        sc = SafetyController()
        status = sc.get_status()
        assert "bot_count" in status
        assert "max_bots" in status
        assert "messages_sent_this_cycle" in status
        assert "max_messages_per_cycle" in status
        assert "crash_count" in status


# ---------------------------------------------------------------------------
# Auto-Bot Factory
# ---------------------------------------------------------------------------

class TestAutoBotFactory:
    def test_create_bot_basic_tier(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(
            category="lead_generation",
            purpose="Generate roofing leads",
        )
        assert "bot_id" in result
        assert "blueprint" in result

    def test_create_bot_returns_blueprint(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(
            category="sales",
            purpose="Close deals",
            features=["SMS", "follow-up"],
        )
        bp = result["blueprint"]
        assert bp["category"] == "sales"
        assert bp["purpose"] == "Close deals"
        assert "SMS" in bp["requested_features"]

    def test_create_bot_advanced_includes_competitor_analysis(self):
        factory = AutoBotFactory(tier=Tier.ADVANCED)
        result = factory.create_bot(
            category="lead_generation",
            purpose="Beat competition",
        )
        assert result["analysis_report"] is not None
        assert result["competitor_gaps_addressed"] > 0

    def test_create_bot_basic_no_competitor_analysis(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(
            category="lead_generation",
            purpose="Generate leads",
        )
        assert result["analysis_report"] is None

    def test_create_bot_applies_strategies(self):
        factory = AutoBotFactory(tier=Tier.ADVANCED)
        result = factory.create_bot(
            category="automation",
            purpose="Automate workflows",
        )
        assert result["strategies_applied"] > 0

    def test_monthly_limit_basic(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        for _ in range(10):
            factory.create_bot(category="sales", purpose="test")
        with pytest.raises(AutoBotFactoryTierError):
            factory.create_bot(category="sales", purpose="test")

    def test_enterprise_unlimited(self):
        factory = AutoBotFactory(tier=Tier.ENTERPRISE)
        for i in range(60):
            result = factory.create_bot(category="sales", purpose=f"test {i}")
            assert "bot_id" in result

    def test_get_blueprints(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        factory.create_bot(category="sales", purpose="test 1")
        factory.create_bot(category="automation", purpose="test 2")
        blueprints = factory.get_blueprints()
        assert len(blueprints) == 2

    def test_get_summary(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        factory.create_bot(category="sales", purpose="test")
        summary = factory.get_summary()
        assert summary["bots_created"] == 1
        assert summary["total_strategies"] == 200

    def test_benchmark_bot(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(category="sales", purpose="test")
        bot_id = result["bot_id"]
        benchmark = factory.benchmark_bot(bot_id)
        assert benchmark["bot_id"] == bot_id
        assert "benchmark_targets" in benchmark

    def test_benchmark_unknown_bot(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.benchmark_bot("nonexistent")
        assert "error" in result

    def test_run_returns_status_string(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.run()
        assert "Auto-Bot Factory" in result

    def test_process_payload(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.process({
            "category": "sales",
            "purpose": "close deals",
            "features": ["SMS"],
        })
        assert "bot_id" in result

    def test_tier_error_on_missing_feature(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        with pytest.raises(AutoBotFactoryTierError):
            factory.create_bot(category="sales", purpose="test", deploy=True)

    def test_monetization_model_in_blueprint(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(category="lead_generation", purpose="test")
        bp = result["blueprint"]
        assert "monetization_model" in bp
        assert len(bp["monetization_model"]) > 0

    def test_github_deployment_target(self):
        factory = AutoBotFactory(tier=Tier.BASIC)
        result = factory.create_bot(category="sales", purpose="test")
        bp = result["blueprint"]
        assert bp["deployment_target"] == "github"

    def test_bot_ids_are_unique(self):
        factory = AutoBotFactory(tier=Tier.ENTERPRISE)
        ids = set()
        for _ in range(5):
            result = factory.create_bot(category="sales", purpose="test")
            ids.add(result["bot_id"])
        assert len(ids) == 5
