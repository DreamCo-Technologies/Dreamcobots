"""
Tests for the DreamCo Auto-Bot Factory.

Covers:
- bots/bot_generator/request_interface.py  (RequestInterface, BotRequest)
- bots/bot_generator/feature_optimizer.py  (FeatureOptimizer)
- bots/bot_generator/code_generator.py     (CodeGenerator)
- bots/bot_generator/competitor_analyzer.py (CompetitorAnalyzer)
- bots/bot_generator/benchmarking_engine.py (BenchmarkingEngine)
- bots/bot_generator/revenue_tracker.py    (RevenueTracker)
- bots/ai_learning_system/learning_loop.py (LearningLoop)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.bot_generator.request_interface import (
    BotRequest,
    RequestInterface,
    RequestInterfaceError,
)
from bots.bot_generator.feature_optimizer import (
    FeatureOptimizer,
    FeatureOptimizerError,
    DREAMCO_CORE_OPTIMIZATIONS,
)
from bots.bot_generator.code_generator import CodeGenerator, CodeGeneratorError
from bots.bot_generator.competitor_analyzer import (
    CompetitorAnalyzer,
    CompetitorAnalyzerError,
    SIMULATED_COMPETITORS,
)
from bots.bot_generator.benchmarking_engine import (
    BenchmarkingEngine,
    BenchmarkingEngineError,
    COMPETITOR_BASELINES,
)
from bots.bot_generator.revenue_tracker import (
    RevenueTracker,
    RevenueTrackerError,
    TIER_PRICES_USD,
)
from bots.ai_learning_system.learning_loop import LearningLoop, LearningLoopError


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _tmp_path():
    return tempfile.mkdtemp()


def _tmp_json() -> str:
    """Return a path to a secure, empty temporary JSON file."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def _make_request(**kwargs):
    defaults = dict(
        category="Lead Generation",
        purpose="Capture qualified real-estate leads",
        features=["SMS outreach", "CRM sync", "follow-up automation"],
        target_audience="Real estate agents",
    )
    defaults.update(kwargs)
    return BotRequest(**defaults)


class _FakeGenerator:
    """Minimal generator stub for LearningLoop tests."""

    def __init__(self):
        self.created: list = []

    def create_bot(self, name: str) -> None:
        self.created.append(name)


class _FakeControlCenter:
    pass


# ===========================================================================
# Framework compliance
# ===========================================================================

class TestFrameworkCompliance:
    def test_request_interface_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "request_interface.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_feature_optimizer_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "feature_optimizer.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_code_generator_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "code_generator.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_competitor_analyzer_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "competitor_analyzer.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_benchmarking_engine_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "benchmarking_engine.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_revenue_tracker_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "bot_generator", "revenue_tracker.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()

    def test_learning_loop_has_global_ai_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "ai_learning_system", "learning_loop.py")
        assert "GLOBAL AI SOURCES FLOW" in open(path).read()


# ===========================================================================
# BotRequest
# ===========================================================================

class TestBotRequest:
    def test_basic_construction(self):
        req = _make_request()
        assert req.category == "Lead Generation"
        assert req.bot_name == "lead_generation_bot"

    def test_custom_bot_name(self):
        req = _make_request(bot_name="my_custom_bot")
        assert req.bot_name == "my_custom_bot"

    def test_to_dict_has_required_keys(self):
        req = _make_request()
        d = req.to_dict()
        for key in ("category", "purpose", "features", "target_audience",
                    "bot_name", "pricing_model", "priority"):
            assert key in d

    def test_empty_category_raises(self):
        with pytest.raises(ValueError, match="category"):
            BotRequest(category="", purpose="x", features=["f"])

    def test_empty_purpose_raises(self):
        with pytest.raises(ValueError, match="purpose"):
            BotRequest(category="Lead Generation", purpose="", features=["f"])

    def test_features_must_be_list(self):
        with pytest.raises(TypeError, match="list"):
            BotRequest(category="Lead Generation", purpose="x", features="not a list")


# ===========================================================================
# RequestInterface
# ===========================================================================

class TestRequestInterface:
    def test_submit_returns_bot_request(self):
        ri = RequestInterface()
        req = ri.submit(
            category="Lead Generation",
            purpose="Find roofing leads",
            features=["SMS", "CRM"],
        )
        assert isinstance(req, BotRequest)

    def test_list_requests_grows(self):
        ri = RequestInterface()
        ri.submit(category="Marketing", purpose="x", features=["f"])
        ri.submit(category="Analytics", purpose="y", features=["g"])
        assert len(ri.list_requests()) == 2

    def test_invalid_pricing_model_raises(self):
        ri = RequestInterface()
        with pytest.raises(RequestInterfaceError, match="pricing_model"):
            ri.submit(
                category="Marketing",
                purpose="x",
                features=["f"],
                pricing_model="barter",
            )

    def test_invalid_priority_raises(self):
        ri = RequestInterface()
        with pytest.raises(RequestInterfaceError, match="priority"):
            ri.submit(
                category="Marketing",
                purpose="x",
                features=["f"],
                priority="critical",
            )

    def test_empty_features_raises(self):
        ri = RequestInterface()
        with pytest.raises(RequestInterfaceError, match="features"):
            ri.submit(category="Marketing", purpose="x", features=[])

    def test_list_categories_returns_list(self):
        ri = RequestInterface()
        cats = ri.list_categories()
        assert isinstance(cats, list)
        assert "Lead Generation" in cats

    def test_get_summary_structure(self):
        ri = RequestInterface()
        ri.submit(category="Marketing", purpose="x", features=["f"], priority="high")
        summary = ri.get_summary()
        assert summary["total_requests"] == 1
        assert "Marketing" in summary["categories"]

    def test_run_returns_string(self):
        ri = RequestInterface()
        ri.submit(category="Analytics", purpose="x", features=["f"])
        result = ri.run()
        assert "RequestInterface" in result
        assert "1" in result


# ===========================================================================
# FeatureOptimizer
# ===========================================================================

class TestFeatureOptimizer:
    def test_optimize_returns_dict_with_required_keys(self):
        opt = FeatureOptimizer()
        req = _make_request()
        result = opt.optimize(req)
        for key in ("optimized_features", "dreamco_additions", "competitor_gaps",
                    "priority_score", "category", "total_features"):
            assert key in result

    def test_dreamco_additions_are_always_present(self):
        opt = FeatureOptimizer()
        req = _make_request()
        result = opt.optimize(req)
        for addition in result["dreamco_additions"]:
            assert addition in DREAMCO_CORE_OPTIMIZATIONS

    def test_original_features_preserved(self):
        opt = FeatureOptimizer()
        req = _make_request(features=["unique_feature_xyz"])
        result = opt.optimize(req)
        assert "unique_feature_xyz" in result["optimized_features"]

    def test_no_duplicate_features(self):
        opt = FeatureOptimizer()
        req = _make_request()
        result = opt.optimize(req)
        lower = [f.lower() for f in result["optimized_features"]]
        assert len(lower) == len(set(lower))

    def test_unknown_category_uses_defaults(self):
        opt = FeatureOptimizer()
        req = _make_request(category="Quantum Teleportation")
        result = opt.optimize(req)
        assert len(result["optimized_features"]) > 0

    def test_competitor_gaps_injected(self):
        competitor_data = [
            {
                "category": "Lead Generation",
                "weak_points": ["no voice outreach", "poor deduplication"],
            }
        ]
        opt = FeatureOptimizer(competitor_data=competitor_data)
        req = _make_request(category="Lead Generation")
        result = opt.optimize(req)
        assert "no voice outreach" in result["competitor_gaps"]

    def test_set_competitor_data_updates_gaps(self):
        opt = FeatureOptimizer()
        opt.set_competitor_data([
            {"category": "Analytics", "weak_points": ["gap_a"]}
        ])
        req = _make_request(category="Analytics")
        result = opt.optimize(req)
        assert "gap_a" in result["competitor_gaps"]

    def test_empty_features_raises(self):
        opt = FeatureOptimizer()
        req = _make_request(features=["placeholder"])
        req.features = []
        with pytest.raises(FeatureOptimizerError, match="features"):
            opt.optimize(req)

    def test_priority_score_between_0_and_1(self):
        opt = FeatureOptimizer()
        req = _make_request()
        result = opt.optimize(req)
        assert 0.0 <= result["priority_score"] <= 1.0

    def test_list_dreamco_optimizations(self):
        opt = FeatureOptimizer()
        opts = opt.list_dreamco_optimizations()
        assert len(opts) == len(DREAMCO_CORE_OPTIMIZATIONS)

    def test_run_returns_string(self):
        opt = FeatureOptimizer()
        assert "FeatureOptimizer" in opt.run()


# ===========================================================================
# CodeGenerator
# ===========================================================================

class TestCodeGenerator:
    def test_generate_returns_required_keys(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        result = gen.generate(req)
        for key in ("bot_name", "class_name", "modules", "generated_at"):
            assert key in result

    def test_modules_has_required_entries(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        result = gen.generate(req)
        for mod in ("bot_main", "monetization", "tracking", "readme"):
            assert mod in result["modules"]

    def test_bot_main_contains_framework_marker(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        result = gen.generate(req)
        assert "GLOBAL AI SOURCES FLOW" in result["modules"]["bot_main"]

    def test_optimized_features_used_when_provided(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        custom_features = ["custom_feature_abc", "custom_feature_xyz"]
        result = gen.generate(req, optimized_features=custom_features)
        assert "custom_feature_abc" in result["modules"]["bot_main"]

    def test_bot_name_slugified(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request(category="Real Estate")
        result = gen.generate(req)
        assert " " not in result["bot_name"]

    def test_write_files_creates_disk_artifacts(self):
        tmp = _tmp_path()
        gen = CodeGenerator(output_dir=tmp)
        req = _make_request()
        result = gen.generate(req, write_files=True)
        assert "file_paths" in result
        for path in result["file_paths"].values():
            assert os.path.exists(path)

    def test_generation_log_grows(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        gen.generate(req)
        gen.generate(req)
        assert len(gen.get_generation_log()) == 2

    def test_run_returns_string(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        assert "CodeGenerator" in gen.run()

    def test_monetization_has_tier_prices(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request()
        result = gen.generate(req)
        mon = result["modules"]["monetization"]
        assert "TIER_PRICES" in mon
        assert '"basic": 99.0' in mon
        assert '"pro": 299.0' in mon

    def test_readme_has_bot_name(self):
        gen = CodeGenerator(output_dir=_tmp_path())
        req = _make_request(category="Data Scraping")
        result = gen.generate(req)
        assert "data_scraping_bot" in result["modules"]["readme"]


# ===========================================================================
# CompetitorAnalyzer
# ===========================================================================

class TestCompetitorAnalyzer:
    def test_analyze_known_category(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        report = analyzer.analyze("Lead Generation")
        assert report["category"] == "Lead Generation"
        assert len(report["competitors"]) > 0

    def test_analyze_returns_required_keys(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        report = analyzer.analyze("Marketing")
        for key in ("category", "competitors", "avg_rating", "avg_price_usd",
                    "gaps", "pricing_benchmark", "analyzed_at"):
            assert key in report

    def test_analyze_unknown_category_returns_empty(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        report = analyzer.analyze("Quantum Teleportation")
        assert report["competitors"] == []
        assert report["gaps"] == []

    def test_gaps_extracted_from_weak_points(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        report = analyzer.analyze("Data Scraping")
        assert len(report["gaps"]) > 0

    def test_pricing_benchmark_structure(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        report = analyzer.analyze("Sales Automation")
        pb = report["pricing_benchmark"]
        assert "min_usd" in pb and "max_usd" in pb and "avg_usd" in pb

    def test_empty_category_raises(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        with pytest.raises(CompetitorAnalyzerError, match="category"):
            analyzer.analyze("   ")

    def test_scrape_and_save_persists_to_file(self):
        tmp = _tmp_json()
        analyzer = CompetitorAnalyzer(data_path=tmp, simulated=True)
        result = analyzer.scrape_and_save(["Lead Generation"])
        assert result["saved"] > 0
        assert os.path.exists(tmp)
        with open(tmp) as fh:
            data = json.load(fh)
        assert "competitors" in data
        os.unlink(tmp)

    def test_list_competitors_returns_all(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        all_comps = analyzer.list_competitors()
        assert len(all_comps) == len(SIMULATED_COMPETITORS)

    def test_list_competitors_filtered_by_category(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        lead_comps = analyzer.list_competitors(category="Lead Generation")
        assert all(c["category"] == "Lead Generation" for c in lead_comps)

    def test_run_returns_string(self):
        analyzer = CompetitorAnalyzer(simulated=True)
        assert "CompetitorAnalyzer" in analyzer.run()

    def test_load_from_file(self):
        tmp = _tmp_json()
        analyzer = CompetitorAnalyzer(data_path=tmp, simulated=True)
        analyzer.scrape_and_save()
        # Re-load from file
        analyzer2 = CompetitorAnalyzer(data_path=tmp, simulated=False)
        assert len(analyzer2.list_competitors()) > 0
        os.unlink(tmp)


# ===========================================================================
# BenchmarkingEngine
# ===========================================================================

class TestBenchmarkingEngine:
    def test_run_benchmark_returns_required_keys(self):
        tmp = _tmp_json()
        engine = BenchmarkingEngine(results_path=tmp)
        result = engine.run_benchmark("test_bot", "Lead Generation")
        for key in ("bot_name", "category", "scores", "baseline", "delta",
                    "passed", "verdict", "tested_at"):
            assert key in result
        if os.path.exists(tmp):
            os.unlink(tmp)

    def test_dreamco_bots_beat_baseline(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        result = engine.run_benchmark("lead_gen_bot", "Lead Generation")
        assert result["passed"] is True

    def test_scores_have_all_metrics(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        result = engine.run_benchmark("bot", "Marketing")
        for metric in ("speed", "scalability", "ux", "revenue", "reliability"):
            assert metric in result["scores"]

    def test_unknown_category_uses_default_baseline(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        result = engine.run_benchmark("bot", "Quantum Computing")
        assert result["passed"] is True

    def test_results_persisted_to_file(self):
        tmp = _tmp_json()
        engine = BenchmarkingEngine(results_path=tmp)
        engine.run_benchmark("test_bot", "Analytics")
        with open(tmp) as fh:
            data = json.load(fh)
        assert len(data["results"]) == 1
        os.unlink(tmp)

    def test_get_results_filtered_by_bot_name(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        engine.run_benchmark("bot_a", "Marketing")
        engine.run_benchmark("bot_b", "Analytics")
        assert len(engine.get_results("bot_a")) == 1

    def test_run_improvement_cycle_returns_list(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        cycles = engine.run_improvement_cycle("bot", "Lead Generation", max_cycles=2)
        assert isinstance(cycles, list)
        assert len(cycles) >= 1

    def test_improvement_cycle_stops_early_on_pass(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        # DreamCo bots always pass, so should stop after 1 cycle
        cycles = engine.run_improvement_cycle("bot", "Lead Generation", max_cycles=5)
        assert len(cycles) == 1

    def test_empty_bot_name_raises(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        with pytest.raises(BenchmarkingEngineError, match="bot_name"):
            engine.run_benchmark("  ", "Analytics")

    def test_run_returns_string(self):
        engine = BenchmarkingEngine(results_path=_tmp_json())
        assert "BenchmarkingEngine" in engine.run()


# ===========================================================================
# RevenueTracker
# ===========================================================================

class TestRevenueTracker:
    def test_record_subscription_basic(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        charge = tracker.record_subscription("bot_a", tier="basic")
        assert charge == TIER_PRICES_USD["basic"]

    def test_record_subscription_pro(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        charge = tracker.record_subscription("bot_b", tier="pro")
        assert charge == TIER_PRICES_USD["pro"]

    def test_record_action_enterprise_charges(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        tracker.record_subscription("bot_e", tier="enterprise")
        charge = tracker.record_action("bot_e", count=10)
        assert charge == pytest.approx(0.50)

    def test_record_action_non_enterprise_no_charge(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        tracker.record_subscription("bot_b", tier="basic")
        charge = tracker.record_action("bot_b", count=100)
        assert charge == 0.0

    def test_get_report_structure(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        tracker.record_subscription("bot_a", tier="pro")
        report = tracker.get_report("bot_a")
        for key in ("bot_name", "tier", "subscriptions", "billable_actions",
                    "total_revenue_usd"):
            assert key in report

    def test_get_report_unknown_bot_returns_zero(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        report = tracker.get_report("nonexistent_bot")
        assert report["total_revenue_usd"] == 0.0

    def test_get_total_revenue_sums_all_bots(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        tracker.record_subscription("bot_a", tier="basic")
        tracker.record_subscription("bot_b", tier="pro")
        total = tracker.get_total_revenue()
        assert total == pytest.approx(TIER_PRICES_USD["basic"] + TIER_PRICES_USD["pro"])

    def test_get_underperformers(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        # bot_x has no revenue
        tracker._ensure("bot_x")
        underperformers = tracker.get_underperformers(threshold_usd=100.0)
        assert "bot_x" in underperformers

    def test_invalid_tier_raises(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        with pytest.raises(RevenueTrackerError, match="tier"):
            tracker.record_subscription("bot", tier="diamond")

    def test_negative_action_count_raises(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        with pytest.raises(RevenueTrackerError, match="count"):
            tracker.record_action("bot", count=-1)

    def test_persistence_round_trip(self):
        tmp = _tmp_json()
        tracker = RevenueTracker(revenue_path=tmp)
        tracker.record_subscription("bot_a", tier="pro")
        # Re-load
        tracker2 = RevenueTracker(revenue_path=tmp)
        assert tracker2.get_report("bot_a")["total_revenue_usd"] == TIER_PRICES_USD["pro"]
        os.unlink(tmp)

    def test_list_bots_returns_all(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        tracker.record_subscription("b1", tier="basic")
        tracker.record_subscription("b2", tier="pro")
        bots = tracker.list_bots()
        assert len(bots) == 2

    def test_run_returns_string(self):
        tracker = RevenueTracker(revenue_path=_tmp_json())
        assert "RevenueTracker" in tracker.run()


# ===========================================================================
# LearningLoop
# ===========================================================================

class TestLearningLoop:
    def _make_loop(self, threshold=30):
        gen = _FakeGenerator()
        cc = _FakeControlCenter()
        return LearningLoop(cc, gen, underperform_threshold=threshold), gen

    def test_track_performance_returns_entry(self):
        loop, _ = self._make_loop()
        entry = loop.track_performance("bot_a", score=50)
        assert entry["bot_name"] == "bot_a"
        assert entry["score"] == 50
        assert entry["status"] == "healthy"

    def test_underperforming_status(self):
        loop, _ = self._make_loop(threshold=40)
        entry = loop.track_performance("bot_b", score=25)
        assert entry["status"] == "underperforming"

    def test_get_underperformers_returns_correct_bots(self):
        loop, _ = self._make_loop(threshold=40)
        loop.track_performance("good_bot", score=80)
        loop.track_performance("bad_bot", score=20)
        underperformers = loop.get_underperformers()
        assert "bad_bot" in underperformers
        assert "good_bot" not in underperformers

    def test_only_latest_score_considered(self):
        loop, _ = self._make_loop(threshold=40)
        loop.track_performance("bot_x", score=10)  # underperforming
        loop.track_performance("bot_x", score=90)  # now healthy
        assert "bot_x" not in loop.get_underperformers()

    def test_optimize_calls_create_bot(self):
        loop, gen = self._make_loop(threshold=40)
        loop.track_performance("bad_bot", score=20)
        records = loop.optimize()
        assert len(records) == 1
        assert "bad_bot_optimized" in gen.created

    def test_optimize_no_underperformers_returns_empty(self):
        loop, gen = self._make_loop()
        loop.track_performance("good_bot", score=80)
        records = loop.optimize()
        assert records == []
        assert gen.created == []

    def test_optimize_history_grows(self):
        loop, _ = self._make_loop(threshold=50)
        loop.track_performance("bot_a", score=20)
        loop.optimize()
        loop.optimize()
        assert len(loop.get_optimization_history()) == 2

    def test_get_performance_log(self):
        loop, _ = self._make_loop()
        loop.track_performance("bot_a", score=55)
        loop.track_performance("bot_b", score=70)
        log = loop.get_performance_log()
        assert len(log) == 2

    def test_invalid_score_raises(self):
        loop, _ = self._make_loop()
        with pytest.raises(LearningLoopError, match="score"):
            loop.track_performance("bot", score=150)

    def test_invalid_score_negative_raises(self):
        loop, _ = self._make_loop()
        with pytest.raises(LearningLoopError, match="score"):
            loop.track_performance("bot", score=-5)

    def test_track_revenue_fallback_returns_float(self):
        loop, _ = self._make_loop()
        revenue = loop.track_revenue()
        assert isinstance(revenue, float)

    def test_count_leads_fallback_returns_int(self):
        loop, _ = self._make_loop()
        leads = loop.count_leads()
        assert isinstance(leads, int)

    def test_run_returns_string(self):
        loop, _ = self._make_loop()
        loop.track_performance("bot_a", score=50)
        result = loop.run()
        assert "LearningLoop" in result

    def test_control_center_get_total_revenue_used(self):
        class CCWithRevenue:
            def get_total_revenue(self):
                return 500.0

        gen = _FakeGenerator()
        loop = LearningLoop(CCWithRevenue(), gen)
        assert loop.track_revenue() == 500.0

    def test_control_center_count_leads_used(self):
        class CCWithLeads:
            def count_leads(self):
                return 42

        gen = _FakeGenerator()
        loop = LearningLoop(CCWithLeads(), gen)
        assert loop.count_leads() == 42


# ===========================================================================
# Integration: full pipeline
# ===========================================================================

class TestAutoFactoryPipeline:
    """End-to-end test simulating the complete Auto-Bot Factory workflow."""

    def test_full_pipeline(self):
        # 1. Submit request
        ri = RequestInterface()
        req = ri.submit(
            category="Lead Generation",
            purpose="Generate and qualify roofing leads",
            features=["SMS outreach", "CRM sync"],
            target_audience="Roofing contractors",
            priority="high",
        )
        assert isinstance(req, BotRequest)

        # 2. Analyze competitors
        analyzer = CompetitorAnalyzer(simulated=True)
        comp_report = analyzer.analyze("Lead Generation")
        assert len(comp_report["gaps"]) > 0

        # 3. Optimize features
        optimizer = FeatureOptimizer(competitor_data=comp_report["competitors"])
        opt_result = optimizer.optimize(req)
        assert len(opt_result["optimized_features"]) > len(req.features)

        # 4. Generate code
        gen = CodeGenerator(output_dir=_tmp_path())
        gen_result = gen.generate(req, optimized_features=opt_result["optimized_features"])
        assert "GLOBAL AI SOURCES FLOW" in gen_result["modules"]["bot_main"]

        # 5. Benchmark
        tmp_bench = _tmp_json()
        engine = BenchmarkingEngine(results_path=tmp_bench)
        bench = engine.run_benchmark(gen_result["bot_name"], req.category)
        assert bench["passed"] is True
        if os.path.exists(tmp_bench):
            os.unlink(tmp_bench)

        # 6. Track revenue
        tmp_rev = _tmp_json()
        tracker = RevenueTracker(revenue_path=tmp_rev)
        charge = tracker.record_subscription(gen_result["bot_name"], tier="pro")
        assert charge == TIER_PRICES_USD["pro"]
        if os.path.exists(tmp_rev):
            os.unlink(tmp_rev)

        # 7. Learning loop
        fake_gen = _FakeGenerator()
        loop = LearningLoop(_FakeControlCenter(), fake_gen)
        loop.track_performance(gen_result["bot_name"], score=85)
        assert gen_result["bot_name"] not in loop.get_underperformers()
