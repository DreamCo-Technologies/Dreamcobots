"""Tests for bots/global_ai_learning_matrix/ — Global AI Learning Matrix bot."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.global_ai_learning_matrix.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    BOT_FEATURES,
    FEATURE_EVOLUTION_ENGINE,
    FEATURE_GOVERNANCE,
    FEATURE_CUSTOM_MODELS,
    FEATURE_COUNTRY_TRACKING,
    FEATURE_LEARNING_BENCHMARKS,
    FEATURE_DASHBOARD,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_FEDERATED_LEARNING,
    FEATURE_REAL_TIME_MONITORING,
)
from bots.global_ai_learning_matrix.country_monitor import Country, CountryMonitor
from bots.global_ai_learning_matrix.learning_benchmarks import (
    LearningMethod,
    BenchmarkResult,
    LearningBenchmarks,
)
from bots.global_ai_learning_matrix.evolution_engine import (
    EvolutionStage,
    ModelEvolution,
    EvolutionEngine,
)
from bots.global_ai_learning_matrix.governance import (
    GovernancePolicy,
    GovernanceAlert,
    GovernanceLayer,
)
from bots.global_ai_learning_matrix.global_ai_learning_matrix import (
    GlobalAILearningMatrix,
    GlobalAILearningMatrixError,
    GlobalAILearningMatrixTierError,
)


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------


class TestTierEnum:
    def test_free_value(self):
        assert Tier.FREE.value == "free"

    def test_pro_value(self):
        assert Tier.PRO.value == "pro"

    def test_enterprise_value(self):
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_three_tiers_exist(self):
        assert len(Tier) == 3


class TestTierConfig:
    def test_free_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_countries(self):
        assert get_tier_config(Tier.FREE).max_countries == 5

    def test_pro_max_countries(self):
        assert get_tier_config(Tier.PRO).max_countries == 50

    def test_enterprise_unlimited_countries(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_countries is None
        assert cfg.is_unlimited_countries()

    def test_free_not_unlimited(self):
        assert not get_tier_config(Tier.FREE).is_unlimited_countries()

    def test_list_tiers_length(self):
        assert len(list_tiers()) == 3

    def test_list_tiers_returns_tier_configs(self):
        for cfg in list_tiers():
            assert isinstance(cfg, TierConfig)


class TestTierFeatures:
    def test_free_has_country_tracking(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_COUNTRY_TRACKING)

    def test_free_has_benchmarks(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_LEARNING_BENCHMARKS)

    def test_free_has_dashboard(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_DASHBOARD)

    def test_free_lacks_evolution(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_EVOLUTION_ENGINE)

    def test_free_lacks_governance(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_GOVERNANCE)

    def test_pro_has_evolution(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_EVOLUTION_ENGINE)

    def test_pro_has_governance(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_GOVERNANCE)

    def test_pro_has_federated(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_FEDERATED_LEARNING)

    def test_pro_has_real_time_monitoring(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_REAL_TIME_MONITORING)

    def test_pro_lacks_custom_models(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_CUSTOM_MODELS)

    def test_enterprise_has_custom_models(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_CUSTOM_MODELS)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_API_ACCESS)

    def test_bot_features_keys(self):
        assert set(BOT_FEATURES.keys()) == {"free", "pro", "enterprise"}


# ---------------------------------------------------------------------------
# CountryMonitor
# ---------------------------------------------------------------------------


class TestCountryDataclass:
    def test_country_fields(self):
        c = Country("US", "United States", "Americas", 100, 200, 95.0)
        assert c.code == "US"
        assert c.name == "United States"
        assert c.region == "Americas"
        assert c.lab_count == 100
        assert c.active_models == 200
        assert c.health_score == 95.0


class TestCountryMonitorInit:
    def test_initializes_with_50_plus_countries(self):
        cm = CountryMonitor()
        assert len(cm.list_countries()) >= 50

    def test_us_exists(self):
        cm = CountryMonitor()
        us = cm.get_country("US")
        assert us.code == "US"

    def test_multiple_regions_present(self):
        cm = CountryMonitor()
        regions = {c.region for c in cm.list_countries()}
        assert len(regions) >= 4


class TestCountryMonitorGetCountry:
    def test_get_existing_country(self):
        cm = CountryMonitor()
        c = cm.get_country("JP")
        assert c.name == "Japan"

    def test_get_is_case_insensitive(self):
        cm = CountryMonitor()
        c = cm.get_country("jp")
        assert c.code == "JP"

    def test_get_nonexistent_raises_key_error(self):
        cm = CountryMonitor()
        with pytest.raises(KeyError):
            cm.get_country("ZZ")


class TestCountryMonitorListCountries:
    def test_list_all(self):
        cm = CountryMonitor()
        assert len(cm.list_countries()) >= 50

    def test_list_by_region(self):
        cm = CountryMonitor()
        americas = cm.list_countries(region="Americas")
        assert len(americas) >= 5
        for c in americas:
            assert c.region == "Americas"

    def test_list_region_case_insensitive(self):
        cm = CountryMonitor()
        r1 = cm.list_countries(region="europe")
        r2 = cm.list_countries(region="Europe")
        assert len(r1) == len(r2)

    def test_unknown_region_returns_empty(self):
        cm = CountryMonitor()
        assert cm.list_countries(region="Atlantis") == []


class TestCountryMonitorUpdateLabCount:
    def test_update_lab_count(self):
        cm = CountryMonitor()
        cm.update_lab_count("US", 999)
        assert cm.get_country("US").lab_count == 999

    def test_update_nonexistent_raises(self):
        cm = CountryMonitor()
        with pytest.raises(KeyError):
            cm.update_lab_count("ZZ", 10)


class TestCountryMonitorTopCountries:
    def test_top_returns_n(self):
        cm = CountryMonitor()
        top = cm.get_top_countries(n=5)
        assert len(top) == 5

    def test_top_ordered_by_lab_count(self):
        cm = CountryMonitor()
        top = cm.get_top_countries(n=10)
        lab_counts = [c.lab_count for c in top]
        assert lab_counts == sorted(lab_counts, reverse=True)

    def test_top_default_is_10(self):
        cm = CountryMonitor()
        assert len(cm.get_top_countries()) == 10


class TestCountryMonitorAddCountry:
    def test_add_new_country(self):
        cm = CountryMonitor()
        c = Country("XX", "Test Country", "Asia-Pacific", 5, 10, 60.0)
        cm.add_country(c)
        assert cm.get_country("XX").name == "Test Country"

    def test_add_overwrites_existing(self):
        cm = CountryMonitor()
        c = Country("US", "Updated US", "Americas", 1, 1, 50.0)
        cm.add_country(c)
        assert cm.get_country("US").name == "Updated US"


class TestCountryMonitorGlobalStats:
    def test_global_stats_keys(self):
        cm = CountryMonitor()
        stats = cm.get_global_stats()
        for key in ("total_countries", "total_labs", "avg_health_score", "top_region"):
            assert key in stats

    def test_total_countries_positive(self):
        cm = CountryMonitor()
        assert cm.get_global_stats()["total_countries"] > 0

    def test_total_labs_positive(self):
        cm = CountryMonitor()
        assert cm.get_global_stats()["total_labs"] > 0

    def test_avg_health_score_range(self):
        cm = CountryMonitor()
        score = cm.get_global_stats()["avg_health_score"]
        assert 0.0 <= score <= 100.0

    def test_top_region_is_string(self):
        cm = CountryMonitor()
        assert isinstance(cm.get_global_stats()["top_region"], str)


# ---------------------------------------------------------------------------
# LearningBenchmarks
# ---------------------------------------------------------------------------


class TestLearningMethodEnum:
    def test_all_methods_present(self):
        methods = {m.value for m in LearningMethod}
        expected = {
            "supervised", "unsupervised", "transfer",
            "self_supervised", "reinforcement", "federated", "semi_supervised",
        }
        assert methods == expected


class TestLearningBenchmarksGet:
    def test_get_supervised(self):
        lb = LearningBenchmarks()
        b = lb.get_benchmark(LearningMethod.SUPERVISED)
        assert isinstance(b, BenchmarkResult)
        assert b.method == LearningMethod.SUPERVISED

    def test_accuracy_range(self):
        lb = LearningBenchmarks()
        for m in LearningMethod:
            b = lb.get_benchmark(m)
            assert 0.0 <= b.accuracy <= 100.0

    def test_speed_score_range(self):
        lb = LearningBenchmarks()
        for m in LearningMethod:
            b = lb.get_benchmark(m)
            assert 0.0 <= b.speed_score <= 100.0

    def test_cost_score_range(self):
        lb = LearningBenchmarks()
        for m in LearningMethod:
            b = lb.get_benchmark(m)
            assert 0.0 <= b.cost_score <= 100.0

    def test_use_cases_not_empty(self):
        lb = LearningBenchmarks()
        for m in LearningMethod:
            assert len(lb.get_benchmark(m).use_cases) > 0


class TestLearningBenchmarksList:
    def test_list_returns_all(self):
        lb = LearningBenchmarks()
        assert len(lb.list_benchmarks()) == len(LearningMethod)

    def test_list_returns_benchmark_results(self):
        lb = LearningBenchmarks()
        for b in lb.list_benchmarks():
            assert isinstance(b, BenchmarkResult)


class TestLearningBenchmarksGetBest:
    def test_get_best_accuracy(self):
        lb = LearningBenchmarks()
        best = lb.get_best_method("accuracy")
        assert isinstance(best, LearningMethod)

    def test_get_best_speed(self):
        lb = LearningBenchmarks()
        best = lb.get_best_method("speed")
        assert isinstance(best, LearningMethod)

    def test_get_best_cost(self):
        lb = LearningBenchmarks()
        best = lb.get_best_method("cost")
        assert isinstance(best, LearningMethod)

    def test_unknown_criteria_raises(self):
        lb = LearningBenchmarks()
        with pytest.raises(ValueError):
            lb.get_best_method("popularity")


class TestLearningBenchmarksCompare:
    def test_compare_returns_dict(self):
        lb = LearningBenchmarks()
        result = lb.compare_methods([LearningMethod.SUPERVISED, LearningMethod.FEDERATED])
        assert isinstance(result, dict)

    def test_compare_has_expected_keys(self):
        lb = LearningBenchmarks()
        result = lb.compare_methods([LearningMethod.SUPERVISED])
        assert "supervised" in result
        for key in ("accuracy", "speed_score", "cost_score", "use_cases"):
            assert key in result["supervised"]

    def test_compare_empty_list(self):
        lb = LearningBenchmarks()
        assert lb.compare_methods([]) == {}


class TestLearningBenchmarksRank:
    def test_rank_length(self):
        lb = LearningBenchmarks()
        ranked = lb.rank_methods()
        assert len(ranked) == len(LearningMethod)

    def test_rank_is_sorted_descending(self):
        lb = LearningBenchmarks()
        ranked = lb.rank_methods()
        scores = [s for _, s in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_rank_tuple_structure(self):
        lb = LearningBenchmarks()
        for method, score in lb.rank_methods():
            assert isinstance(method, LearningMethod)
            assert isinstance(score, float)


# ---------------------------------------------------------------------------
# EvolutionEngine
# ---------------------------------------------------------------------------


class TestEvolutionStageEnum:
    def test_all_stages(self):
        stages = {s.value for s in EvolutionStage}
        assert stages == {"init", "training", "testing", "optimizing", "deployed", "retired"}


class TestEvolutionEngineRegister:
    def test_register_returns_model_evolution(self):
        ee = EvolutionEngine()
        m = ee.register_model("m1", "Test Model")
        assert isinstance(m, ModelEvolution)

    def test_register_sets_init_stage(self):
        ee = EvolutionEngine()
        m = ee.register_model("m1", "Test Model")
        assert m.stage == EvolutionStage.INIT

    def test_register_duplicate_raises(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test Model")
        with pytest.raises(ValueError):
            ee.register_model("m1", "Duplicate")

    def test_register_sets_initial_version(self):
        ee = EvolutionEngine()
        m = ee.register_model("m1", "Test Model")
        assert m.version == "0.1.0"


class TestEvolutionEngineAdvance:
    def test_advance_changes_stage(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        m = ee.advance_stage("m1")
        assert m.stage == EvolutionStage.TRAINING

    def test_advance_increments_iterations(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        m = ee.advance_stage("m1")
        assert m.iterations == 1

    def test_advance_full_lifecycle(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        stages = []
        for _ in range(5):
            m = ee.advance_stage("m1")
            stages.append(m.stage)
        assert stages[-1] == EvolutionStage.RETIRED

    def test_advance_beyond_retired_raises(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        for _ in range(5):
            ee.advance_stage("m1")
        with pytest.raises(ValueError):
            ee.advance_stage("m1")

    def test_advance_nonexistent_raises(self):
        ee = EvolutionEngine()
        with pytest.raises(KeyError):
            ee.advance_stage("ghost")


class TestEvolutionEngineUpdatePerformance:
    def test_update_performance(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        ee.update_performance("m1", 88.5)
        assert ee.get_model("m1").performance_score == 88.5

    def test_invalid_score_raises(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        with pytest.raises(ValueError):
            ee.update_performance("m1", 110.0)

    def test_negative_score_raises(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "Test")
        with pytest.raises(ValueError):
            ee.update_performance("m1", -1.0)


class TestEvolutionEngineList:
    def test_list_all(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "A")
        ee.register_model("m2", "B")
        assert len(ee.list_models()) == 2

    def test_list_by_stage(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "A")
        ee.register_model("m2", "B")
        ee.advance_stage("m1")  # m1 → TRAINING
        init_models = ee.list_models(stage=EvolutionStage.INIT)
        assert len(init_models) == 1
        assert init_models[0].model_id == "m2"

    def test_list_empty_initially(self):
        ee = EvolutionEngine()
        assert ee.list_models() == []


class TestEvolutionEngineReport:
    def test_report_keys(self):
        ee = EvolutionEngine()
        report = ee.get_evolution_report()
        for key in ("total_models", "stage_distribution", "avg_performance_score", "top_model"):
            assert key in report

    def test_report_empty(self):
        ee = EvolutionEngine()
        report = ee.get_evolution_report()
        assert report["total_models"] == 0
        assert report["top_model"] is None

    def test_report_with_models(self):
        ee = EvolutionEngine()
        ee.register_model("m1", "A")
        ee.update_performance("m1", 75.0)
        report = ee.get_evolution_report()
        assert report["total_models"] == 1
        assert report["avg_performance_score"] == 75.0
        assert report["top_model"]["model_id"] == "m1"


# ---------------------------------------------------------------------------
# GovernanceLayer
# ---------------------------------------------------------------------------


class TestGovernancePolicyDataclass:
    def test_policy_fields(self):
        p = GovernancePolicy("p1", "Test", "Desc", True, "high")
        assert p.policy_id == "p1"
        assert p.enabled is True
        assert p.severity == "high"


class TestGovernanceLayerInit:
    def test_has_default_policies(self):
        gl = GovernanceLayer()
        assert len(gl.list_policies()) >= 10

    def test_critical_policies_exist(self):
        gl = GovernanceLayer()
        critical = gl.list_policies(severity="critical")
        assert len(critical) >= 1


class TestGovernanceLayerGetPolicy:
    def test_get_existing_policy(self):
        gl = GovernanceLayer()
        p = gl.get_policy("pol-001")
        assert p.policy_id == "pol-001"

    def test_get_nonexistent_raises(self):
        gl = GovernanceLayer()
        with pytest.raises(KeyError):
            gl.get_policy("pol-999")


class TestGovernanceLayerListPolicies:
    def test_list_all(self):
        gl = GovernanceLayer()
        assert len(gl.list_policies()) >= 10

    def test_list_by_severity(self):
        gl = GovernanceLayer()
        high = gl.list_policies(severity="high")
        for p in high:
            assert p.severity == "high"

    def test_list_unknown_severity_empty(self):
        gl = GovernanceLayer()
        assert gl.list_policies(severity="extreme") == []


class TestGovernanceLayerAlerts:
    def test_raise_alert_returns_alert(self):
        gl = GovernanceLayer()
        alert = gl.raise_alert("pol-001", "Data breach detected.")
        assert isinstance(alert, GovernanceAlert)
        assert not alert.resolved

    def test_raise_alert_sets_severity_from_policy(self):
        gl = GovernanceLayer()
        alert = gl.raise_alert("pol-001", "msg")
        assert alert.severity == gl.get_policy("pol-001").severity

    def test_raise_alert_nonexistent_policy_raises(self):
        gl = GovernanceLayer()
        with pytest.raises(KeyError):
            gl.raise_alert("pol-999", "msg")

    def test_resolve_alert(self):
        gl = GovernanceLayer()
        alert = gl.raise_alert("pol-001", "msg")
        gl.resolve_alert(alert.alert_id)
        assert gl._alerts[alert.alert_id].resolved

    def test_resolve_nonexistent_raises(self):
        gl = GovernanceLayer()
        with pytest.raises(KeyError):
            gl.resolve_alert("alert-doesnotexist")

    def test_list_alerts_all(self):
        gl = GovernanceLayer()
        gl.raise_alert("pol-001", "a")
        gl.raise_alert("pol-002", "b")
        assert len(gl.list_alerts()) == 2

    def test_list_alerts_unresolved(self):
        gl = GovernanceLayer()
        a1 = gl.raise_alert("pol-001", "a")
        a2 = gl.raise_alert("pol-002", "b")
        gl.resolve_alert(a1.alert_id)
        unresolved = gl.list_alerts(resolved=False)
        assert len(unresolved) == 1
        assert unresolved[0].alert_id == a2.alert_id

    def test_list_alerts_resolved(self):
        gl = GovernanceLayer()
        a1 = gl.raise_alert("pol-001", "a")
        gl.resolve_alert(a1.alert_id)
        resolved = gl.list_alerts(resolved=True)
        assert len(resolved) == 1


class TestGovernanceScore:
    def test_score_100_no_alerts(self):
        gl = GovernanceLayer()
        score = gl.get_governance_score()
        assert 0.0 <= score <= 100.0

    def test_score_decreases_with_unresolved_alerts(self):
        gl = GovernanceLayer()
        score_before = gl.get_governance_score()
        gl.raise_alert("pol-001", "critical issue")
        score_after = gl.get_governance_score()
        assert score_after < score_before

    def test_score_in_range(self):
        gl = GovernanceLayer()
        for _ in range(5):
            gl.raise_alert("pol-001", "issue")
        assert 0.0 <= gl.get_governance_score() <= 100.0


class TestGovernanceAuditReport:
    def test_audit_report_keys(self):
        gl = GovernanceLayer()
        report = gl.audit_report()
        for key in (
            "total_policies", "enabled_policies", "total_alerts",
            "open_alerts", "resolved_alerts", "open_by_severity", "governance_score",
        ):
            assert key in report

    def test_audit_total_policies(self):
        gl = GovernanceLayer()
        report = gl.audit_report()
        assert report["total_policies"] >= 10

    def test_audit_alert_counts(self):
        gl = GovernanceLayer()
        a = gl.raise_alert("pol-001", "x")
        report = gl.audit_report()
        assert report["total_alerts"] == 1
        assert report["open_alerts"] == 1
        assert report["resolved_alerts"] == 0
        gl.resolve_alert(a.alert_id)
        report2 = gl.audit_report()
        assert report2["resolved_alerts"] == 1


# ---------------------------------------------------------------------------
# GlobalAILearningMatrix — main bot
# ---------------------------------------------------------------------------


class TestGlobalAILearningMatrixInit:
    def test_default_tier_is_free(self):
        bot = GlobalAILearningMatrix()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = GlobalAILearningMatrix(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_tier_config_not_none(self):
        bot = GlobalAILearningMatrix()
        assert bot.tier_config is not None

    def test_tier_config_price_free(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        assert bot.tier_config.price_usd_monthly == 0.0

    def test_exception_hierarchy(self):
        assert issubclass(GlobalAILearningMatrixTierError, GlobalAILearningMatrixError)


class TestGlobalAILearningMatrixDashboard:
    def test_dashboard_returns_string(self):
        bot = GlobalAILearningMatrix()
        assert isinstance(bot.dashboard(), str)

    def test_dashboard_contains_tier_name(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        dash = bot.dashboard()
        assert "Pro" in dash

    def test_dashboard_contains_countries(self):
        bot = GlobalAILearningMatrix()
        assert "Countries" in bot.dashboard() or "countries" in bot.dashboard().lower()

    def test_dashboard_free_governance_na(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        assert "N/A" in bot.dashboard()


class TestGlobalAILearningMatrixCountryTracking:
    def test_track_country_returns_dict(self):
        bot = GlobalAILearningMatrix()
        result = bot.track_country("AA", "Alpha", "Americas", 10, 20, 80.0)
        assert isinstance(result, dict)

    def test_track_country_dict_fields(self):
        bot = GlobalAILearningMatrix()
        result = bot.track_country("AA", "Alpha", "Americas", 10, 20, 80.0)
        for key in ("code", "name", "region", "lab_count", "active_models", "health_score"):
            assert key in result

    def test_free_limit_5_countries(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        for i in range(5):
            bot.track_country(f"C{i}", f"Country{i}", "Europe", 1, 1, 50.0)
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.track_country("C5", "ExtraCountry", "Europe", 1, 1, 50.0)

    def test_pro_allows_50_countries(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        for i in range(50):
            bot.track_country(f"P{i:02d}", f"Country{i}", "Europe", 1, 1, 50.0)
        # 51st should raise
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.track_country("P50", "TooMany", "Europe", 1, 1, 50.0)

    def test_enterprise_unlimited_countries(self):
        bot = GlobalAILearningMatrix(tier=Tier.ENTERPRISE)
        for i in range(60):
            bot.track_country(f"E{i:02d}", f"Country{i}", "Europe", 1, 1, 50.0)
        # No error expected

    def test_get_country_stats(self):
        bot = GlobalAILearningMatrix()
        stats = bot.get_country_stats("US")
        assert stats["code"] == "US"

    def test_get_country_stats_keys(self):
        bot = GlobalAILearningMatrix()
        stats = bot.get_country_stats("JP")
        for key in ("code", "name", "region", "lab_count", "active_models", "health_score"):
            assert key in stats


class TestGlobalAILearningMatrixBenchmarks:
    def test_run_benchmark_returns_dict(self):
        bot = GlobalAILearningMatrix()
        result = bot.run_benchmark("supervised")
        assert isinstance(result, dict)

    def test_run_benchmark_has_fields(self):
        bot = GlobalAILearningMatrix()
        result = bot.run_benchmark("federated")
        for key in ("method", "accuracy", "speed_score", "cost_score", "use_cases"):
            assert key in result

    def test_run_benchmark_unknown_raises(self):
        bot = GlobalAILearningMatrix()
        with pytest.raises(GlobalAILearningMatrixError):
            bot.run_benchmark("quantum_magic")

    def test_run_benchmark_all_methods(self):
        bot = GlobalAILearningMatrix()
        for m in LearningMethod:
            result = bot.run_benchmark(m.value)
            assert result["method"] == m.value


class TestGlobalAILearningMatrixEvolution:
    def test_evolve_model_pro(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        result = bot.evolve_model("m1", "Model One")
        assert result["model_id"] == "m1"
        assert result["stage"] == "init"

    def test_evolve_model_enterprise(self):
        bot = GlobalAILearningMatrix(tier=Tier.ENTERPRISE)
        result = bot.evolve_model("m1", "Model One")
        assert isinstance(result, dict)

    def test_evolve_model_free_raises_tier_error(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.evolve_model("m1", "Model One")

    def test_advance_model_pro(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        bot.evolve_model("m1", "Model One")
        result = bot.advance_model("m1")
        assert result["stage"] == "training"

    def test_advance_model_free_raises_tier_error(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.advance_model("m1")


class TestGlobalAILearningMatrixGovernance:
    def test_check_governance_pro(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        result = bot.check_governance()
        assert isinstance(result, dict)
        assert "governance_score" in result

    def test_check_governance_free_raises(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.check_governance()

    def test_raise_governance_alert_pro(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        alert = bot.raise_governance_alert("pol-001", "Test alert")
        assert "alert_id" in alert
        assert alert["policy_id"] == "pol-001"
        assert not alert["resolved"]

    def test_raise_governance_alert_free_raises(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        with pytest.raises(GlobalAILearningMatrixTierError):
            bot.raise_governance_alert("pol-001", "msg")


class TestGlobalAILearningMatrixGlobalHealth:
    def test_get_global_health_returns_dict(self):
        bot = GlobalAILearningMatrix()
        result = bot.get_global_health()
        assert isinstance(result, dict)

    def test_get_global_health_keys(self):
        bot = GlobalAILearningMatrix()
        result = bot.get_global_health()
        for key in (
            "health_score", "total_countries", "total_labs",
            "top_region", "open_alerts", "governance_score",
            "top_countries", "benchmarks_summary",
        ):
            assert key in result

    def test_get_global_health_governance_none_for_free(self):
        bot = GlobalAILearningMatrix(tier=Tier.FREE)
        result = bot.get_global_health()
        assert result["governance_score"] is None

    def test_get_global_health_governance_score_pro(self):
        bot = GlobalAILearningMatrix(tier=Tier.PRO)
        result = bot.get_global_health()
        assert result["governance_score"] is not None

    def test_get_global_health_top_countries_list(self):
        bot = GlobalAILearningMatrix()
        result = bot.get_global_health()
        assert isinstance(result["top_countries"], list)
        assert len(result["top_countries"]) <= 5

    def test_get_global_health_benchmarks_summary(self):
        bot = GlobalAILearningMatrix()
        result = bot.get_global_health()
        assert isinstance(result["benchmarks_summary"], list)
        assert len(result["benchmarks_summary"]) == 3
