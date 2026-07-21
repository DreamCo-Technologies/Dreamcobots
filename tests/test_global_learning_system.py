"""
Tests for the DreamCo Global Learning System microservice architecture.

Covers all modules under global_learning_system/:
  ingestion, classifier, sandbox_lab, analytics, evolution,
  deployment, profit_layer, governance, database, api, dashboards
"""

import sys
import os

# Ensure repo root is on the path
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# ingestion
# ---------------------------------------------------------------------------
from global_learning_system.ingestion.paper_scraper import PaperScraper, Paper
from global_learning_system.ingestion.github_scraper import GitHubScraper, GitHubRepo
from global_learning_system.ingestion.kaggle_scraper import KaggleScraper, KaggleDataset
from global_learning_system.ingestion.dataset_normalizer import DatasetNormalizer, NormalizedRecord

# classifier
from global_learning_system.classifier.method_classifier import (
    MethodClassifier,
    ClassificationResult,
    CATEGORY_SUPERVISED,
    CATEGORY_REINFORCEMENT,
    CATEGORY_OTHER,
    ALL_CATEGORIES,
)
from global_learning_system.classifier.ai_method_tags import AIMethodTagger, MethodTag

# sandbox_lab
from global_learning_system.sandbox_lab.sandbox_runner import SandboxRunner, SandboxResult
from global_learning_system.sandbox_lab.experiment_manager import ExperimentManager, Experiment
from global_learning_system.sandbox_lab.metrics_collector import MetricsCollector, MetricEntry

# analytics
from global_learning_system.analytics.performance_engine import PerformanceEngine, PerformanceReport
from global_learning_system.analytics.learning_matrix import LearningMatrix, MatrixEntry

# evolution
from global_learning_system.evolution.hybrid_generator import HybridGenerator, HybridPipeline
from global_learning_system.evolution.genetic_optimizer import GeneticOptimizer, Individual
from global_learning_system.evolution.reinforcement_tuner import ReinforcementTuner, TuningStep

# deployment
from global_learning_system.deployment.strategy_deployer import StrategyDeployer, DeploymentRecord
from global_learning_system.deployment.bot_updater import BotUpdater, BotVersion

# profit_layer
from global_learning_system.profit_layer.roi_tracker import ROITracker, ROIRecord
from global_learning_system.profit_layer.market_adaptation import MarketAdaptation, MarketSignal

# governance
from global_learning_system.governance.security_layer import SecurityLayer, EncryptedPayload
from global_learning_system.governance.compliance_engine import (
    ComplianceEngine,
    AuditEntry,
    POLICY_GDPR,
    POLICY_HIPAA,
    ALL_POLICIES,
)

# database
from global_learning_system.database.models import Base, ResearchPaper, ExperimentResult, BotDeployment
from global_learning_system.database.postgres_connector import PostgresConnector, ConnectionConfig

# api
from global_learning_system.api.learning_api import LearningAPI, APIResponse
from global_learning_system.api.bot_control_api import BotControlAPI

# dashboards
from global_learning_system.dashboards.learning_dashboard import LearningDashboard, DashboardPanel
from global_learning_system.dashboards.sandbox_dashboard import SandboxDashboard
from global_learning_system.dashboards.profit_dashboard import ProfitDashboard


# ===========================================================================
# ingestion / PaperScraper
# ===========================================================================

class TestPaperScraper:
    def test_default_sources(self):
        scraper = PaperScraper()
        assert len(scraper.sources) == 3

    def test_scrape_returns_papers(self):
        scraper = PaperScraper(sources=["arxiv"], max_results=5)
        papers = scraper.scrape("deep learning")
        assert len(papers) > 0
        assert all(isinstance(p, Paper) for p in papers)

    def test_scrape_populates_ingested(self):
        scraper = PaperScraper(sources=["arxiv"])
        scraper.scrape("transformer")
        assert len(scraper.get_ingested()) > 0

    def test_clear_resets_ingested(self):
        scraper = PaperScraper(sources=["arxiv"])
        scraper.scrape("nlp")
        scraper.clear()
        assert scraper.get_ingested() == []

    def test_scrape_deduplicates(self):
        scraper = PaperScraper(sources=["arxiv"])
        papers1 = scraper.scrape("same query")
        papers2 = scraper.scrape("same query")
        # Second call should return the same set (deduplicated)
        assert len(papers2) == len(papers1)

    def test_paper_has_required_fields(self):
        scraper = PaperScraper(sources=["pubmed"])
        papers = scraper.scrape("medical imaging")
        p = papers[0]
        assert p.title
        assert p.source == "pubmed"
        assert p.url.startswith("https://")

    def test_unsupported_source_raises(self):
        scraper = PaperScraper(sources=["unknown_source"])
        with pytest.raises(ValueError, match="Unsupported source"):
            scraper.scrape("query")

    def test_multiple_sources(self):
        scraper = PaperScraper(sources=["arxiv", "semantic_scholar"])
        papers = scraper.scrape("diffusion models")
        sources_found = {p.source for p in papers}
        assert "arxiv" in sources_found
        assert "semantic_scholar" in sources_found


# ===========================================================================
# ingestion / GitHubScraper
# ===========================================================================

class TestGitHubScraper:
    def test_search_returns_repos(self):
        scraper = GitHubScraper()
        repos = scraper.search_repositories("machine learning")
        assert len(repos) > 0
        assert all(isinstance(r, GitHubRepo) for r in repos)

    def test_repo_has_url(self):
        scraper = GitHubScraper()
        repos = scraper.search_repositories("pytorch")
        assert all(r.url.startswith("https://") for r in repos)

    def test_clear(self):
        scraper = GitHubScraper()
        scraper.search_repositories("keras")
        scraper.clear()
        assert scraper.get_ingested() == []

    def test_get_ingested_accumulates(self):
        scraper = GitHubScraper()
        scraper.search_repositories("tensorflow")
        scraper.search_repositories("scikit-learn")
        assert len(scraper.get_ingested()) >= 2

    def test_language_filter_accepted(self):
        scraper = GitHubScraper()
        repos = scraper.search_repositories("deep learning", language="Python")
        assert all(r.language == "Python" for r in repos)


# ===========================================================================
# ingestion / KaggleScraper
# ===========================================================================

class TestKaggleScraper:
    def test_search_datasets(self):
        scraper = KaggleScraper()
        datasets = scraper.search_datasets("image classification")
        assert len(datasets) > 0
        assert all(isinstance(d, KaggleDataset) for d in datasets)

    def test_dataset_has_url(self):
        scraper = KaggleScraper()
        datasets = scraper.search_datasets("tabular")
        assert all(d.url.startswith("https://") for d in datasets)

    def test_clear(self):
        scraper = KaggleScraper()
        scraper.search_datasets("nlp")
        scraper.clear()
        assert scraper.get_ingested() == []

    def test_download_count_positive(self):
        scraper = KaggleScraper()
        datasets = scraper.search_datasets("regression")
        assert all(d.download_count > 0 for d in datasets)


# ===========================================================================
# ingestion / DatasetNormalizer
# ===========================================================================

class TestDatasetNormalizer:
    def test_normalize_basic(self):
        normalizer = DatasetNormalizer()
        raw = [{"feature_a": 1.0, "feature_b": 2.0, "label": "cat", "id": 1}]
        records = normalizer.normalize(raw, source="test")
        assert len(records) == 1
        assert records[0].label == "cat"
        assert records[0].source == "test"

    def test_remove_nulls_true(self):
        normalizer = DatasetNormalizer(remove_nulls=True)
        raw = [{"x": None, "y": 1.0}, {"x": 2.0, "y": 3.0}]
        records = normalizer.normalize(raw, source="src")
        assert len(records) == 1

    def test_remove_nulls_false(self):
        normalizer = DatasetNormalizer(remove_nulls=False)
        raw = [{"x": None, "y": 1.0}]
        records = normalizer.normalize(raw, source="src")
        assert len(records) == 1

    def test_lowercase_keys(self):
        normalizer = DatasetNormalizer(lowercase_keys=True)
        raw = [{"FeatureA": 1.0, "FeatureB": 2.0}]
        records = normalizer.normalize(raw, source="src")
        assert "featurea" in records[0].features

    def test_no_lowercase_keys(self):
        normalizer = DatasetNormalizer(lowercase_keys=False)
        raw = [{"FeatureA": 1.0}]
        records = normalizer.normalize(raw, source="src")
        assert "FeatureA" in records[0].features

    def test_normalize_schema(self):
        normalizer = DatasetNormalizer()
        raw = [{"value": "42.5"}]
        records = normalizer.normalize(raw, source="src")
        records = normalizer.normalize_schema(records, schema={"value": float})
        assert isinstance(records[0].features["value"], float)

    def test_record_id_auto_generated(self):
        normalizer = DatasetNormalizer()
        raw = [{"x": 1.0}]
        records = normalizer.normalize(raw, source="src")
        assert records[0].record_id == "src_0"


# ===========================================================================
# classifier / MethodClassifier
# ===========================================================================

class TestMethodClassifier:
    def test_classify_supervised(self):
        clf = MethodClassifier()
        result = clf.classify("A supervised classification model using random forest.")
        assert result.category == CATEGORY_SUPERVISED

    def test_classify_reinforcement(self):
        clf = MethodClassifier()
        result = clf.classify("Deep reinforcement learning with reward shaping.")
        assert result.category == CATEGORY_REINFORCEMENT

    def test_classify_unknown_returns_other(self):
        clf = MethodClassifier()
        result = clf.classify("xyz abc 123")
        assert result.category == CATEGORY_OTHER

    def test_classify_returns_result_type(self):
        clf = MethodClassifier()
        result = clf.classify("convolutional neural network")
        assert isinstance(result, ClassificationResult)

    def test_confidence_range(self):
        clf = MethodClassifier()
        result = clf.classify("regression model for prediction")
        assert 0.0 <= result.confidence <= 1.0

    def test_classify_batch(self):
        clf = MethodClassifier()
        texts = ["supervised classification", "clustering unsupervised", "reinforcement reward"]
        results = clf.classify_batch(texts)
        assert len(results) == 3

    def test_list_categories(self):
        clf = MethodClassifier()
        cats = clf.list_categories()
        assert len(cats) == len(ALL_CATEGORIES)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            MethodClassifier(confidence_threshold=1.5)

    def test_secondary_categories_present(self):
        clf = MethodClassifier()
        result = clf.classify("supervised classification with transfer learning fine-tuning")
        # May have secondary categories
        assert isinstance(result.secondary_categories, list)


# ===========================================================================
# classifier / AIMethodTagger
# ===========================================================================

class TestAIMethodTagger:
    def test_tag_returns_list(self):
        tagger = AIMethodTagger()
        tags = tagger.tag("reinforcement learning with neural network")
        assert isinstance(tags, list)

    def test_tag_finds_builtin_tags(self):
        tagger = AIMethodTagger()
        tags = tagger.tag("transformer attention model")
        names = [t.name for t in tags]
        assert "transformer" in names

    def test_tag_batch(self):
        tagger = AIMethodTagger()
        results = tagger.tag_batch(["NLP model", "computer vision"])
        assert len(results) == 2

    def test_add_custom_tag(self):
        tagger = AIMethodTagger()
        custom = MethodTag("custom_method", "custom_category", "A custom method.")
        tagger.add_tag(custom)
        assert tagger.get_tag("custom_method") is not None

    def test_list_tags_all(self):
        tagger = AIMethodTagger()
        tags = tagger.list_tags()
        assert len(tags) > 0

    def test_list_tags_by_category(self):
        tagger = AIMethodTagger()
        arch_tags = tagger.list_tags(category="architecture")
        assert all(t.category == "architecture" for t in arch_tags)

    def test_get_tag_not_found_returns_none(self):
        tagger = AIMethodTagger()
        assert tagger.get_tag("nonexistent") is None

    def test_alias_matching(self):
        tagger = AIMethodTagger()
        # "bert" is an alias of the transformer tag
        tags = tagger.tag("BERT-based classification model")
        names = [t.name for t in tags]
        assert "transformer" in names


# ===========================================================================
# sandbox_lab / SandboxRunner
# ===========================================================================

class TestSandboxRunner:
    def test_run_success(self):
        runner = SandboxRunner()
        result = runner.run("test_exp", fn=lambda: 42)
        assert result.status == "success"
        assert result.output == 42

    def test_run_failure_captured(self):
        runner = SandboxRunner()
        result = runner.run("fail_exp", fn=lambda: 1 / 0)
        assert result.status == "failed"
        assert result.error is not None

    def test_run_logged_in_history(self):
        runner = SandboxRunner(enable_logging=True)
        runner.run("logged_exp", fn=lambda: "ok")
        assert len(runner.get_history()) == 1

    def test_no_logging(self):
        runner = SandboxRunner(enable_logging=False)
        runner.run("silent_exp", fn=lambda: 1)
        assert len(runner.get_history()) == 0

    def test_clear_history(self):
        runner = SandboxRunner()
        runner.run("e1", fn=lambda: 1)
        runner.clear_history()
        assert runner.get_history() == []

    def test_metrics_fn_called(self):
        runner = SandboxRunner()
        result = runner.run(
            "metrics_exp",
            fn=lambda: {"score": 0.9},
            metrics_fn=lambda out: {"accuracy": out["score"]},
        )
        assert result.metrics.get("accuracy") == pytest.approx(0.9)

    def test_result_has_run_id(self):
        runner = SandboxRunner()
        result = runner.run("id_exp", fn=lambda: None)
        assert result.run_id != ""

    def test_duration_ms_non_negative(self):
        runner = SandboxRunner()
        result = runner.run("dur_exp", fn=lambda: None)
        assert result.duration_ms >= 0


# ===========================================================================
# sandbox_lab / ExperimentManager
# ===========================================================================

class TestExperimentManager:
    def _make_exp(self, name="exp1", etype="benchmark"):
        return Experiment(name=name, description="desc", experiment_type=etype, fn=lambda: None)

    def test_register_and_get(self):
        mgr = ExperimentManager()
        exp = self._make_exp()
        mgr.register(exp)
        assert mgr.get("exp1") is exp

    def test_duplicate_raises(self):
        mgr = ExperimentManager()
        mgr.register(self._make_exp())
        with pytest.raises(ValueError, match="already registered"):
            mgr.register(self._make_exp())

    def test_invalid_type_raises(self):
        mgr = ExperimentManager()
        with pytest.raises(ValueError, match="Unknown experiment type"):
            mgr.register(Experiment("e", "desc", "invalid_type", fn=lambda: None))

    def test_capacity_limit(self):
        mgr = ExperimentManager(max_experiments=1)
        mgr.register(self._make_exp("e1"))
        with pytest.raises(ValueError, match="capacity"):
            mgr.register(self._make_exp("e2"))

    def test_archive(self):
        mgr = ExperimentManager()
        mgr.register(self._make_exp())
        mgr.archive("exp1")
        assert mgr.is_archived("exp1")
        assert mgr.count() == 0

    def test_list_by_type(self):
        mgr = ExperimentManager()
        mgr.register(self._make_exp("ab1", "ab_test"))
        mgr.register(self._make_exp("bm1", "benchmark"))
        ab_tests = mgr.list_experiments(experiment_type="ab_test")
        assert len(ab_tests) == 1

    def test_get_not_found_raises(self):
        mgr = ExperimentManager()
        with pytest.raises(KeyError):
            mgr.get("missing")


# ===========================================================================
# sandbox_lab / MetricsCollector
# ===========================================================================

class TestMetricsCollector:
    def test_log_entry_returned(self):
        mc = MetricsCollector()
        entry = mc.log("accuracy", 0.95)
        assert isinstance(entry, MetricEntry)
        assert entry.value == 0.95

    def test_log_dict(self):
        mc = MetricsCollector()
        entries = mc.log_dict({"loss": 0.1, "accuracy": 0.9})
        assert len(entries) == 2

    def test_get_metrics_filter_by_name(self):
        mc = MetricsCollector()
        mc.log("accuracy", 0.8)
        mc.log("loss", 0.2)
        entries = mc.get_metrics(metric_name="accuracy")
        assert all(e.metric_name == "accuracy" for e in entries)

    def test_summary_stats(self):
        mc = MetricsCollector(experiment_name="exp1")
        mc.log("f1", 0.7, experiment_name="exp1")
        mc.log("f1", 0.9, experiment_name="exp1")
        summary = mc.summary("f1", experiment_name="exp1")
        assert summary["min"] == pytest.approx(0.7)
        assert summary["max"] == pytest.approx(0.9)
        assert summary["mean"] == pytest.approx(0.8)

    def test_summary_no_entries_raises(self):
        mc = MetricsCollector()
        with pytest.raises(ValueError):
            mc.summary("nonexistent_metric")

    def test_clear(self):
        mc = MetricsCollector()
        mc.log("x", 1.0)
        mc.clear()
        assert mc.get_metrics() == []

    def test_step_recorded(self):
        mc = MetricsCollector()
        entry = mc.log("loss", 0.5, step=10)
        assert entry.step == 10


# ===========================================================================
# analytics / PerformanceEngine
# ===========================================================================

class TestPerformanceEngine:
    def _results(self):
        return [
            {"experiment_name": "exp_a", "metrics": {"accuracy": 0.9}},
            {"experiment_name": "exp_b", "metrics": {"accuracy": 0.7}},
            {"experiment_name": "exp_c", "metrics": {"accuracy": 0.8}},
        ]

    def test_analyse_returns_report(self):
        engine = PerformanceEngine()
        report = engine.analyse(self._results())
        assert isinstance(report, PerformanceReport)

    def test_best_is_highest(self):
        engine = PerformanceEngine(primary_metric="accuracy", higher_is_better=True)
        report = engine.analyse(self._results())
        assert report.best_experiment == "exp_a"

    def test_worst_is_lowest(self):
        engine = PerformanceEngine(primary_metric="accuracy", higher_is_better=True)
        report = engine.analyse(self._results())
        assert report.worst_experiment == "exp_b"

    def test_empty_results_raises(self):
        engine = PerformanceEngine()
        with pytest.raises(ValueError):
            engine.analyse([])

    def test_compare_improvement(self):
        engine = PerformanceEngine()
        baseline = {"experiment_name": "base", "metrics": {"accuracy": 0.7}}
        candidate = {"experiment_name": "cand", "metrics": {"accuracy": 0.9}}
        cmp = engine.compare(baseline, candidate)
        assert cmp["better"] is True
        assert cmp["improvement"] == pytest.approx(0.2)

    def test_lower_is_better(self):
        engine = PerformanceEngine(primary_metric="loss", higher_is_better=False)
        results = [
            {"experiment_name": "a", "metrics": {"loss": 0.1}},
            {"experiment_name": "b", "metrics": {"loss": 0.5}},
        ]
        report = engine.analyse(results)
        assert report.best_experiment == "a"


# ===========================================================================
# analytics / LearningMatrix
# ===========================================================================

class TestLearningMatrix:
    def _entry(self, mid="m1", name="Method1", cat="supervised_learning", score=0.8):
        return MatrixEntry(method_id=mid, method_name=name, category=cat, score=score)

    def test_upsert_and_get(self):
        matrix = LearningMatrix()
        matrix.upsert(self._entry())
        assert matrix.get("m1") is not None

    def test_rank_order(self):
        matrix = LearningMatrix()
        matrix.upsert(self._entry("m1", score=0.8))
        matrix.upsert(self._entry("m2", score=0.9))
        ranked = matrix.rank()
        assert ranked[0].method_id == "m2"

    def test_rank_top_n(self):
        matrix = LearningMatrix()
        for i in range(5):
            matrix.upsert(self._entry(f"m{i}", score=float(i) / 5))
        ranked = matrix.rank(top_n=3)
        assert len(ranked) == 3

    def test_rank_by_category(self):
        matrix = LearningMatrix()
        matrix.upsert(self._entry("m1", cat="supervised_learning"))
        matrix.upsert(self._entry("m2", cat="unsupervised_learning"))
        ranked = matrix.rank(category="supervised_learning")
        assert all(e.category == "supervised_learning" for e in ranked)

    def test_remove_existing(self):
        matrix = LearningMatrix()
        matrix.upsert(self._entry())
        removed = matrix.remove("m1")
        assert removed is True
        assert matrix.get("m1") is None

    def test_remove_nonexistent_returns_false(self):
        matrix = LearningMatrix()
        assert matrix.remove("nonexistent") is False

    def test_summary(self):
        matrix = LearningMatrix()
        matrix.upsert(self._entry("m1", score=0.8))
        matrix.upsert(self._entry("m2", score=0.6))
        summary = matrix.summary()
        assert summary["count"] == 2
        assert summary["max_score"] == pytest.approx(0.8)

    def test_decay_factor(self):
        matrix = LearningMatrix(decay_factor=0.5)
        matrix.upsert(self._entry("m1", score=1.0))
        matrix.upsert(self._entry("m1", score=0.0))
        entry = matrix.get("m1")
        assert entry.score == pytest.approx(0.5)

    def test_invalid_decay_raises(self):
        with pytest.raises(ValueError):
            LearningMatrix(decay_factor=1.5)


# ===========================================================================
# evolution / HybridGenerator
# ===========================================================================

class TestHybridGenerator:
    def test_generate_returns_pipeline(self):
        gen = HybridGenerator()
        candidates = [
            {"method_id": "m1", "score": 0.9},
            {"method_id": "m2", "score": 0.8},
        ]
        pipeline = gen.generate(candidates)
        assert isinstance(pipeline, HybridPipeline)

    def test_pipeline_components(self):
        gen = HybridGenerator(max_components=2)
        candidates = [
            {"method_id": "m1", "score": 0.9},
            {"method_id": "m2", "score": 0.7},
            {"method_id": "m3", "score": 0.5},
        ]
        pipeline = gen.generate(candidates)
        assert len(pipeline.component_methods) == 2

    def test_empty_candidates_raises(self):
        gen = HybridGenerator()
        with pytest.raises(ValueError):
            gen.generate([])

    def test_invalid_strategy_raises(self):
        with pytest.raises(ValueError):
            HybridGenerator(combination_strategy="invalid")

    def test_list_generated(self):
        gen = HybridGenerator()
        gen.generate([{"method_id": "m1", "score": 0.9}])
        assert len(gen.list_generated()) == 1

    def test_expected_score_computed(self):
        gen = HybridGenerator()
        candidates = [{"method_id": "m1", "score": 0.8}]
        pipeline = gen.generate(candidates)
        assert pipeline.expected_score == pytest.approx(0.8)


# ===========================================================================
# evolution / GeneticOptimizer
# ===========================================================================

class TestGeneticOptimizer:
    def _genome_factory(self):
        return {"lr": 0.01, "dropout": 0.5, "layers": 3}

    def test_initialise(self):
        opt = GeneticOptimizer(population_size=10, seed=42)
        pop = opt.initialise(self._genome_factory)
        assert len(pop) == 10

    def test_evaluate(self):
        opt = GeneticOptimizer(population_size=5, seed=0)
        opt.initialise(self._genome_factory)
        opt.evaluate(lambda g: g["lr"] * 100)
        best = opt.best()
        assert best is not None

    def test_evolve_same_size(self):
        opt = GeneticOptimizer(population_size=8, seed=1)
        opt.initialise(self._genome_factory)
        opt.evaluate(lambda g: 1.0)
        new_pop = opt.evolve()
        assert len(new_pop) == 8

    def test_invalid_mutation_rate_raises(self):
        with pytest.raises(ValueError):
            GeneticOptimizer(mutation_rate=1.5)

    def test_invalid_elite_fraction_raises(self):
        with pytest.raises(ValueError):
            GeneticOptimizer(elite_fraction=-0.1)

    def test_best_returns_individual(self):
        opt = GeneticOptimizer(population_size=5, seed=99)
        opt.initialise(self._genome_factory)
        opt.evaluate(lambda g: g.get("lr", 0) * 10)
        best = opt.best()
        assert isinstance(best, Individual)


# ===========================================================================
# evolution / ReinforcementTuner
# ===========================================================================

class TestReinforcementTuner:
    def test_tune_returns_dict(self):
        tuner = ReinforcementTuner(max_steps=5)
        result = tuner.tune({"lr": 0.01}, reward_fn=lambda p: 1.0)
        assert isinstance(result, dict)

    def test_history_populated(self):
        tuner = ReinforcementTuner(max_steps=3)
        tuner.tune({"lr": 0.01}, reward_fn=lambda p: 1.0)
        assert len(tuner.get_history()) == 3

    def test_best_params_not_none_after_tune(self):
        tuner = ReinforcementTuner(max_steps=5)
        tuner.tune({"x": 1.0}, reward_fn=lambda p: p["x"])
        assert tuner.best_params() is not None

    def test_reset_clears_history(self):
        tuner = ReinforcementTuner(max_steps=5)
        tuner.tune({"x": 1.0}, reward_fn=lambda p: 1.0)
        tuner.reset()
        assert tuner.get_history() == []

    def test_invalid_lr_raises(self):
        with pytest.raises(ValueError):
            ReinforcementTuner(learning_rate=0.0)

    def test_invalid_discount_raises(self):
        with pytest.raises(ValueError):
            ReinforcementTuner(discount_factor=1.5)

    def test_n_steps_override(self):
        tuner = ReinforcementTuner(max_steps=100)
        tuner.tune({"x": 1.0}, reward_fn=lambda p: 1.0, n_steps=2)
        assert len(tuner.get_history()) == 2


# ===========================================================================
# deployment / StrategyDeployer
# ===========================================================================

class TestStrategyDeployer:
    def test_deploy_creates_record(self):
        deployer = StrategyDeployer()
        rec = deployer.deploy("d1", "s1", ["bot_a"])
        assert rec.status == "deployed"

    def test_staging_mode(self):
        deployer = StrategyDeployer(staging_mode=True)
        rec = deployer.deploy("d1", "s1", ["bot_a"])
        assert rec.status == "pending"

    def test_promote(self):
        deployer = StrategyDeployer(staging_mode=True)
        deployer.deploy("d1", "s1", ["bot_a"])
        rec = deployer.promote("d1")
        assert rec.status == "deployed"

    def test_rollback(self):
        deployer = StrategyDeployer()
        deployer.deploy("d1", "s1", ["bot_a"])
        rec = deployer.rollback("d1")
        assert rec.status == "rolled_back"

    def test_duplicate_deploy_raises(self):
        deployer = StrategyDeployer()
        deployer.deploy("d1", "s1", ["bot_a"])
        with pytest.raises(ValueError):
            deployer.deploy("d1", "s2", ["bot_b"])

    def test_empty_bots_raises(self):
        deployer = StrategyDeployer()
        with pytest.raises(ValueError):
            deployer.deploy("d1", "s1", [])

    def test_list_deployments_filter(self):
        deployer = StrategyDeployer()
        deployer.deploy("d1", "s1", ["bot_a"])
        records = deployer.list_deployments(status="deployed")
        assert len(records) == 1

    def test_get_record_not_found_raises(self):
        deployer = StrategyDeployer()
        with pytest.raises(KeyError):
            deployer.get_record("missing")


# ===========================================================================
# deployment / BotUpdater
# ===========================================================================

class TestBotUpdater:
    def test_register_version(self):
        updater = BotUpdater()
        bv = updater.register_version("bot1", "1.0.0", ["model_a"])
        assert isinstance(bv, BotVersion)
        assert bv.is_active

    def test_auto_activate_deactivates_previous(self):
        updater = BotUpdater(auto_activate=True)
        updater.register_version("bot1", "1.0.0", ["m1"])
        updater.register_version("bot1", "2.0.0", ["m2"])
        active = updater.active_version("bot1")
        assert active.version == "2.0.0"

    def test_activate_specific(self):
        updater = BotUpdater(auto_activate=False)
        updater.register_version("bot1", "1.0.0", ["m1"])
        updater.register_version("bot1", "2.0.0", ["m2"])
        updater.activate("bot1", "1.0.0")
        assert updater.active_version("bot1").version == "1.0.0"

    def test_list_versions(self):
        updater = BotUpdater()
        updater.register_version("bot1", "1.0.0", ["m1"])
        updater.register_version("bot1", "1.1.0", ["m1", "m2"])
        assert len(updater.list_versions("bot1")) == 2

    def test_trigger_retrain(self):
        updater = BotUpdater()
        updater.register_version("bot1", "1.0.0", ["m1"])
        result = updater.trigger_retrain("bot1")
        assert result["status"] == "retraining_scheduled"

    def test_trigger_retrain_unknown_raises(self):
        updater = BotUpdater()
        with pytest.raises(KeyError):
            updater.trigger_retrain("unknown_bot")

    def test_list_bots(self):
        updater = BotUpdater()
        updater.register_version("bot1", "1.0.0", ["m1"])
        updater.register_version("bot2", "1.0.0", ["m2"])
        assert set(updater.list_bots()) == {"bot1", "bot2"}


# ===========================================================================
# profit_layer / ROITracker
# ===========================================================================

class TestROITracker:
    def test_record_creates_entry(self):
        tracker = ROITracker()
        rec = tracker.record("s1", "2025-Q1", revenue=1000.0, cost=500.0)
        assert isinstance(rec, ROIRecord)
        assert rec.profit == pytest.approx(500.0)

    def test_roi_calculated(self):
        tracker = ROITracker()
        tracker.record("s1", "2025-Q1", revenue=1000.0, cost=500.0)
        summary = tracker.summary("s1")
        assert summary["roi"] == pytest.approx(1.0)

    def test_negative_revenue_raises(self):
        tracker = ROITracker()
        with pytest.raises(ValueError):
            tracker.record("s1", "Q1", revenue=-100.0, cost=200.0)

    def test_summary_all(self):
        tracker = ROITracker()
        tracker.record("s1", "Q1", revenue=500.0, cost=100.0)
        tracker.record("s2", "Q1", revenue=300.0, cost=150.0)
        summary = tracker.summary()
        assert summary["total_revenue"] == pytest.approx(800.0)

    def test_top_strategies(self):
        tracker = ROITracker()
        tracker.record("s1", "Q1", revenue=1000.0, cost=100.0)
        tracker.record("s2", "Q1", revenue=500.0, cost=250.0)
        top = tracker.top_strategies(top_n=1)
        assert top[0]["strategy_id"] == "s1"

    def test_zero_cost_roi(self):
        tracker = ROITracker()
        rec = tracker.record("s1", "Q1", revenue=1000.0, cost=0.0)
        assert rec.roi == 0.0


# ===========================================================================
# profit_layer / MarketAdaptation
# ===========================================================================

class TestMarketAdaptation:
    def test_observe_no_alert_within_threshold(self):
        ma = MarketAdaptation(drift_threshold=0.1)
        ma.set_baseline("s1", 0.9)
        sig = ma.observe("s1", 0.92)
        assert sig.alert is False

    def test_observe_alert_beyond_threshold(self):
        ma = MarketAdaptation(drift_threshold=0.05)
        ma.set_baseline("s1", 0.9)
        sig = ma.observe("s1", 0.8)
        assert sig.alert is True

    def test_get_alerts(self):
        ma = MarketAdaptation(drift_threshold=0.05)
        ma.set_baseline("s1", 0.9)
        ma.observe("s1", 0.8)
        alerts = ma.get_alerts()
        assert len(alerts) == 1

    def test_adaptation_report(self):
        ma = MarketAdaptation(drift_threshold=0.05)
        ma.set_baseline("s1", 0.9)
        ma.observe("s1", 0.8)
        report = ma.adaptation_report("s1")
        assert "recommendation" in report
        assert report["alert_count"] == 1

    def test_invalid_signal_type_raises(self):
        ma = MarketAdaptation()
        with pytest.raises(ValueError):
            ma.observe("s1", 0.8, signal_type="unknown_type")

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            MarketAdaptation(drift_threshold=0.0)


# ===========================================================================
# governance / SecurityLayer
# ===========================================================================

class TestSecurityLayer:
    def test_encrypt_decrypt_roundtrip(self):
        sl = SecurityLayer()
        payload = sl.encrypt("secret message")
        recovered = sl.decrypt(payload)
        assert recovered == "secret message"

    def test_encrypt_returns_payload(self):
        sl = SecurityLayer()
        payload = sl.encrypt("hello")
        assert isinstance(payload, EncryptedPayload)
        assert payload.key_id == "default"

    def test_sign_and_verify(self):
        sl = SecurityLayer()
        sig = sl.sign("important data")
        assert sl.verify("important data", sig) is True

    def test_verify_tampered_fails(self):
        sl = SecurityLayer()
        sig = sl.sign("original")
        assert sl.verify("tampered", sig) is False

    def test_hash_data_deterministic(self):
        sl = SecurityLayer()
        h1 = sl.hash_data("test")
        h2 = sl.hash_data("test")
        assert h1 == h2

    def test_rotate_key(self):
        import os
        sl = SecurityLayer()
        new_key = os.urandom(32)
        sl.rotate_key(new_key, "v2")
        assert sl.key_id == "v2"

    def test_encrypt_empty_string(self):
        sl = SecurityLayer()
        payload = sl.encrypt("")
        assert sl.decrypt(payload) == ""


# ===========================================================================
# governance / ComplianceEngine
# ===========================================================================

class TestComplianceEngine:
    def test_check_permitted(self):
        engine = ComplianceEngine()
        result = engine.check("alice", "read", "resource_a")
        assert result is True

    def test_enforce_does_not_raise_when_permitted(self):
        engine = ComplianceEngine()
        engine.enforce("alice", "write", "resource_b")

    def test_audit_log_populated(self):
        engine = ComplianceEngine()
        engine.check("alice", "read", "resource_a")
        log = engine.get_audit_log()
        assert len(log) == 1
        assert isinstance(log[0], AuditEntry)

    def test_audit_filter_by_actor(self):
        engine = ComplianceEngine()
        engine.check("alice", "read", "r1")
        engine.check("bob", "write", "r2")
        alice_log = engine.get_audit_log(actor="alice")
        assert all(e.actor == "alice" for e in alice_log)

    def test_enable_policy(self):
        engine = ComplianceEngine(active_policies=[POLICY_GDPR])
        engine.enable_policy(POLICY_HIPAA)
        assert POLICY_HIPAA in engine.active_policies

    def test_disable_policy(self):
        engine = ComplianceEngine(active_policies=[POLICY_GDPR, POLICY_HIPAA])
        engine.disable_policy(POLICY_HIPAA)
        assert POLICY_HIPAA not in engine.active_policies

    def test_unknown_policy_raises(self):
        with pytest.raises(ValueError):
            ComplianceEngine(active_policies=["UNKNOWN"])

    def test_event_ids_unique(self):
        engine = ComplianceEngine()
        engine.check("a", "r", "res")
        engine.check("b", "w", "res")
        ids = [e.event_id for e in engine.get_audit_log()]
        assert len(set(ids)) == 2


# ===========================================================================
# database / models
# ===========================================================================

class TestDatabaseModels:
    def test_research_paper_fields(self):
        paper = ResearchPaper(title="Test Paper", source="arxiv", url="https://example.com")
        assert paper.title == "Test Paper"
        assert paper.source == "arxiv"

    def test_experiment_result_defaults(self):
        er = ExperimentResult(run_id="r1", experiment_name="exp1")
        assert er.status == "pending"

    def test_bot_deployment_defaults(self):
        bd = BotDeployment(deployment_id="d1", strategy_id="s1", bot_name="bot1")
        assert bd.status == "pending"

    def test_base_registry_populated(self):
        models = Base.get_all_models()
        model_names = [m.__name__ for m in models]
        assert "ResearchPaper" in model_names
        assert "ExperimentResult" in model_names
        assert "BotDeployment" in model_names

    def test_tablename_defined(self):
        assert ResearchPaper.__tablename__ == "research_papers"
        assert ExperimentResult.__tablename__ == "experiment_results"
        assert BotDeployment.__tablename__ == "bot_deployments"


# ===========================================================================
# database / PostgresConnector
# ===========================================================================

class TestPostgresConnector:
    def test_initial_not_connected(self):
        conn = PostgresConnector()
        assert conn.is_connected is False

    def test_connect(self):
        conn = PostgresConnector()
        conn.connect()
        assert conn.is_connected is True

    def test_disconnect(self):
        conn = PostgresConnector()
        conn.connect()
        conn.disconnect()
        assert conn.is_connected is False

    def test_execute_when_disconnected_raises(self):
        conn = PostgresConnector()
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.execute("SELECT 1")

    def test_execute_logs_query(self):
        conn = PostgresConnector()
        conn.connect()
        conn.execute("SELECT * FROM research_papers")
        assert len(conn.get_query_log()) == 1

    def test_health_check(self):
        conn = PostgresConnector()
        health = conn.health_check()
        assert "connected" in health
        assert "host" in health

    def test_dsn_format(self):
        config = ConnectionConfig(host="db_host", port=5432, database="mydb", user="user", password="pass")
        assert "db_host" in config.dsn
        assert "5432" in config.dsn


# ===========================================================================
# api / LearningAPI
# ===========================================================================

class TestLearningAPI:
    def test_health_route(self):
        api = LearningAPI()
        resp = api.dispatch("/api/v1/learning/health", "GET")
        assert resp.status == "ok"
        assert resp.data["healthy"] is True

    def test_matrix_rank_route(self):
        api = LearningAPI()
        resp = api.dispatch("/api/v1/learning/matrix/rank", "GET")
        assert resp.status == "ok"

    def test_classify_post(self):
        api = LearningAPI()
        resp = api.dispatch("/api/v1/learning/classify", "POST", payload={"text": "deep RL"})
        assert resp.status == "ok"

    def test_ingest_post(self):
        api = LearningAPI()
        resp = api.dispatch("/api/v1/learning/ingest", "POST", payload={"query": "nlp"})
        assert resp.status == "ok"

    def test_unknown_route_returns_error(self):
        api = LearningAPI()
        resp = api.dispatch("/api/v1/learning/nonexistent", "GET")
        assert resp.status == "error"

    def test_register_custom_route(self):
        api = LearningAPI()
        api.register_route("/custom", "GET", lambda: APIResponse(status="ok", data="custom"))
        resp = api.dispatch("/api/v1/learning/custom", "GET")
        assert resp.status == "ok"

    def test_list_routes_non_empty(self):
        api = LearningAPI()
        routes = api.list_routes()
        assert len(routes) > 0


# ===========================================================================
# api / BotControlAPI
# ===========================================================================

class TestBotControlAPI:
    def test_health_route(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/health", "GET")
        assert resp.status == "ok"

    def test_list_bots(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/list", "GET")
        assert resp.status == "ok"

    def test_deploy_post(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/deploy", "POST", payload={"deployment_id": "d1", "strategy_id": "s1"})
        assert resp.status == "ok"

    def test_rollback_post(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/rollback", "POST", payload={"deployment_id": "d1"})
        assert resp.status == "ok"

    def test_retrain_post(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/retrain", "POST", payload={"bot_name": "bot1"})
        assert resp.status == "ok"

    def test_unknown_route_error(self):
        api = BotControlAPI()
        resp = api.dispatch("/api/v1/bots/unknown", "GET")
        assert resp.status == "error"

    def test_list_routes(self):
        api = BotControlAPI()
        assert len(api.list_routes()) > 0


# ===========================================================================
# dashboards / LearningDashboard
# ===========================================================================

class TestLearningDashboard:
    def test_render_returns_string(self):
        dash = LearningDashboard()
        output = dash.render()
        assert isinstance(output, str)

    def test_update_and_summary(self):
        dash = LearningDashboard()
        dash.update("matrix_entries", 42)
        summary = dash.summary()
        assert summary["matrix_entries"] == 42

    def test_add_panel(self):
        dash = LearningDashboard()
        panel = DashboardPanel(title="Top Methods", content=["m1: 0.95", "m2: 0.90"])
        dash.add_panel(panel)
        output = dash.render()
        assert "Top Methods" in output

    def test_clear(self):
        dash = LearningDashboard()
        dash.update("x", 1)
        dash.clear()
        assert dash.summary() == {}

    def test_title_in_render(self):
        dash = LearningDashboard(title="My Custom Dashboard")
        output = dash.render()
        assert "My Custom Dashboard" in output


# ===========================================================================
# dashboards / SandboxDashboard
# ===========================================================================

class TestSandboxDashboard:
    def test_record_and_render(self):
        dash = SandboxDashboard()
        dash.record_run({"experiment_name": "exp1", "status": "success", "duration_ms": 150.0, "metrics": {}})
        output = dash.render()
        assert "exp1" in output

    def test_summary_counts(self):
        dash = SandboxDashboard()
        dash.record_run({"experiment_name": "e1", "status": "success", "duration_ms": 100.0, "metrics": {}})
        dash.record_run({"experiment_name": "e2", "status": "failed", "duration_ms": 50.0, "metrics": {}})
        summary = dash.summary()
        assert summary["total"] == 2
        assert summary["success"] == 1
        assert summary["failed"] == 1

    def test_clear(self):
        dash = SandboxDashboard()
        dash.record_run({"experiment_name": "e1", "status": "success", "duration_ms": 10.0, "metrics": {}})
        dash.clear()
        assert dash.summary()["total"] == 0


# ===========================================================================
# dashboards / ProfitDashboard
# ===========================================================================

class TestProfitDashboard:
    def test_record_roi_and_render(self):
        dash = ProfitDashboard()
        dash.record_roi({"strategy_id": "s1", "revenue": 1000.0, "cost": 400.0})
        output = dash.render()
        assert "1,000.00" in output or "1000" in output

    def test_summary(self):
        dash = ProfitDashboard()
        dash.record_roi({"strategy_id": "s1", "revenue": 500.0, "cost": 200.0})
        summary = dash.summary()
        assert summary["total_profit"] == pytest.approx(300.0)

    def test_market_alert_count(self):
        dash = ProfitDashboard()
        dash.record_signal({"strategy_id": "s1", "value": 0.7, "alert": True})
        dash.record_signal({"strategy_id": "s2", "value": 0.9, "alert": False})
        summary = dash.summary()
        assert summary["market_alert_count"] == 1

    def test_clear(self):
        dash = ProfitDashboard()
        dash.record_roi({"strategy_id": "s1", "revenue": 100.0, "cost": 50.0})
        dash.clear()
        assert dash.summary()["total_revenue"] == 0.0
