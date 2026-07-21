"""
Tests for bots/ai_learning_system/ — DreamCo Global AI Learning System
"""

import sys
import os
import datetime

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.ai_learning_system.tiers import (
    Tier,
    TierConfig,
    FEATURE_SCRAPER,
    FEATURE_CLASSIFIER,
    FEATURE_SANDBOX,
    FEATURE_ANALYTICS,
    FEATURE_HYBRID_ENGINE,
    FEATURE_DEPLOYMENT,
    FEATURE_GOVERNANCE,
    FEATURE_SCHEDULER,
    FEATURE_KUBERNETES,
    FEATURE_GENETIC_ALGO,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)
from bots.ai_learning_system.ingestion import (
    DataIngestionLayer,
    DataSourceType,
    ContentType,
    IngestedRecord,
    IngestionLimitError,
)
from bots.ai_learning_system.classifier import (
    LearningMethodClassifier,
    LearningMethodType,
    ClassifiedMethod,
    ClassifierTierError,
)
from bots.ai_learning_system.sandbox import (
    SandboxTestingLayer,
    SandboxStatus,
    SandboxTestResult,
    SandboxTierError,
)
from bots.ai_learning_system.analytics import (
    PerformanceAnalyticsLayer,
    MethodRanking,
    AnalyticsTierError,
)
from bots.ai_learning_system.hybrid_engine import (
    HybridEvolutionEngine,
    HybridStrategy,
    HybridEngineTierError,
)
from bots.ai_learning_system.deployment import (
    DeploymentOrchestrator,
    BotApplication,
    Deployment,
    DeploymentStatus,
    DeploymentTierError,
    DeploymentNotFoundError,
)
from bots.ai_learning_system.governance import (
    GovernanceLayer,
    AccessRole,
    AuditLogEntry,
    GovernanceTierError,
    RBACError,
    ROLE_PERMISSIONS,
)
from bots.ai_learning_system.scheduler import (
    AutomationScheduler,
    ScheduleFrequency,
    JobStatus,
    ScheduledJob,
    SchedulerTierError,
    JobNotFoundError,
)
from bots.ai_learning_system.ai_learning_system import (
    AILearningSystem,
    AILearningSystemTierError,
)


def _utc_now_naive() -> datetime.datetime:
    """Return a naive UTC datetime (no tzinfo) for use in test assertions."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 199.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 999.0

    def test_free_ingestion_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.ingestion_jobs_per_month == 100

    def test_pro_ingestion_limit(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.ingestion_jobs_per_month == 5_000

    def test_enterprise_unlimited_ingestion(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.ingestion_jobs_per_month is None

    def test_enterprise_is_unlimited_ingestion(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_ingestion() is True

    def test_free_not_unlimited_ingestion(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.is_unlimited_ingestion() is False

    def test_free_sandbox_containers_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.sandbox_containers == 0

    def test_pro_sandbox_containers(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.sandbox_containers == 10

    def test_enterprise_unlimited_containers(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.sandbox_containers is None

    def test_free_has_scraper(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_SCRAPER)

    def test_free_has_classifier(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_CLASSIFIER)

    def test_free_has_analytics(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_ANALYTICS)

    def test_free_has_scheduler(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_SCHEDULER)

    def test_free_no_sandbox(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_SANDBOX)

    def test_free_no_hybrid_engine(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_HYBRID_ENGINE)

    def test_free_no_governance(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_GOVERNANCE)

    def test_pro_has_sandbox(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_SANDBOX)

    def test_pro_has_hybrid_engine(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_HYBRID_ENGINE)

    def test_pro_has_deployment(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_DEPLOYMENT)

    def test_pro_has_governance(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_GOVERNANCE)

    def test_pro_no_kubernetes(self):
        cfg = get_tier_config(Tier.PRO)
        assert not cfg.has_feature(FEATURE_KUBERNETES)

    def test_pro_no_genetic_algo(self):
        cfg = get_tier_config(Tier.PRO)
        assert not cfg.has_feature(FEATURE_GENETIC_ALGO)

    def test_enterprise_has_kubernetes(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_KUBERNETES)

    def test_enterprise_has_genetic_algo(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_GENETIC_ALGO)

    def test_list_tiers_length(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_list_tiers_ordered_by_price(self):
        tiers = list_tiers()
        prices = [t.price_usd_monthly for t in tiers]
        assert prices == sorted(prices)

    def test_upgrade_from_free_is_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_from_pro_is_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_from_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_is_dataclass(self):
        cfg = get_tier_config(Tier.FREE)
        assert isinstance(cfg, TierConfig)

    def test_tier_name_strings(self):
        assert get_tier_config(Tier.FREE).name == "Free"
        assert get_tier_config(Tier.PRO).name == "Pro"
        assert get_tier_config(Tier.ENTERPRISE).name == "Enterprise"


# ===========================================================================
# Ingestion tests
# ===========================================================================

class TestIngestion:
    def _layer(self, tier=Tier.FREE):
        return DataIngestionLayer(tier)

    def test_ingest_returns_list(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "transformer")
        assert isinstance(records, list)

    def test_ingest_returns_ingested_records(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "transformer")
        assert all(isinstance(r, IngestedRecord) for r in records)

    def test_record_has_id(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "test")
        assert all(r.id for r in records)

    def test_record_has_url(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "test")
        assert all(r.url.startswith("http") for r in records)

    def test_record_novelty_in_range(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "test")
        assert all(0.0 <= r.novelty_score <= 1.0 for r in records)

    def test_record_source_matches(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.GITHUB, "pytorch")
        assert all(r.source == DataSourceType.GITHUB for r in records)

    def test_record_has_tags(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "test")
        assert all(isinstance(r.tags, list) for r in records)

    def test_max_results_respected(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.ARXIV, "test", max_results=3)
        assert len(records) <= 3

    def test_job_count_increments(self):
        layer = self._layer()
        layer.ingest(DataSourceType.ARXIV, "a")
        layer.ingest(DataSourceType.GITHUB, "b")
        assert layer._job_count == 2

    def test_get_records_accumulates(self):
        layer = self._layer()
        r1 = layer.ingest(DataSourceType.ARXIV, "a", max_results=2)
        r2 = layer.ingest(DataSourceType.GITHUB, "b", max_results=2)
        assert len(layer.get_records()) == len(r1) + len(r2)

    def test_jobs_remaining_decrements(self):
        layer = self._layer(Tier.FREE)
        before = layer.jobs_remaining()
        layer.ingest(DataSourceType.ARXIV, "x")
        assert layer.jobs_remaining() == before - 1

    def test_enterprise_jobs_remaining_none(self):
        layer = self._layer(Tier.ENTERPRISE)
        assert layer.jobs_remaining() is None

    def test_ingestion_limit_error(self):
        layer = self._layer(Tier.FREE)
        layer._job_count = layer.config.ingestion_jobs_per_month
        with pytest.raises(IngestionLimitError):
            layer.ingest(DataSourceType.ARXIV, "over limit")

    def test_reset_clears_jobs_and_records(self):
        layer = self._layer()
        layer.ingest(DataSourceType.ARXIV, "x")
        layer.reset()
        assert layer._job_count == 0
        assert layer.get_records() == []

    def test_stats_structure(self):
        layer = self._layer()
        layer.ingest(DataSourceType.ARXIV, "test")
        stats = layer.get_stats()
        assert "jobs_executed" in stats
        assert "total_records" in stats
        assert "records_by_source" in stats

    def test_kaggle_source(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.KAGGLE, "dataset")
        assert all(r.source == DataSourceType.KAGGLE for r in records)

    def test_ai_lab_source(self):
        layer = self._layer()
        records = layer.ingest(DataSourceType.AI_LAB, "model")
        assert all(r.source == DataSourceType.AI_LAB for r in records)


# ===========================================================================
# Classifier tests
# ===========================================================================

def _make_record(tags, title="Test Record", source=DataSourceType.ARXIV):
    return IngestedRecord(
        id="test-id",
        source=source,
        content_type=ContentType.RESEARCH_PAPER,
        title=title,
        url="https://example.com",
        tags=tags,
        language="English",
        novelty_score=0.75,
        ingested_at=_utc_now_naive(),
        metadata={"country": "USA", "lab_name": "OpenAI"},
    )


class TestClassifier:
    def _clf(self, tier=Tier.FREE):
        return LearningMethodClassifier(tier)

    def test_classify_returns_classified_method(self):
        clf = self._clf()
        record = _make_record(["supervised_learning", "classification"])
        result = clf.classify(record)
        assert isinstance(result, ClassifiedMethod)

    def test_classify_supervised_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["supervised_learning"]))
        assert result.method_type == LearningMethodType.SUPERVISED

    def test_classify_reinforcement_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["reinforcement_learning", "reward"]))
        assert result.method_type == LearningMethodType.REINFORCEMENT

    def test_classify_unsupervised_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["unsupervised_learning", "clustering"]))
        assert result.method_type == LearningMethodType.UNSUPERVISED

    def test_classify_transfer_learning_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["transfer_learning", "pre_trained"]))
        assert result.method_type == LearningMethodType.TRANSFER_LEARNING

    def test_classify_federated_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["federated_learning"]))
        assert result.method_type == LearningMethodType.FEDERATED_LEARNING

    def test_classify_meta_learning_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["meta_learning", "maml"]))
        assert result.method_type == LearningMethodType.META_LEARNING

    def test_classify_semi_supervised_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["semi_supervised_learning"]))
        assert result.method_type == LearningMethodType.SEMI_SUPERVISED

    def test_classify_self_supervised_keyword(self):
        clf = self._clf()
        result = clf.classify(_make_record(["self_supervised_learning", "contrastive"]))
        assert result.method_type == LearningMethodType.SELF_SUPERVISED

    def test_classify_default_supervised(self):
        clf = self._clf()
        result = clf.classify(_make_record(["unknown_tag_xyz"]))
        assert result.method_type == LearningMethodType.SUPERVISED

    def test_confidence_in_range(self):
        clf = self._clf()
        result = clf.classify(_make_record(["supervised_learning"]))
        assert 0.0 <= result.confidence <= 1.0

    def test_source_record_id_set(self):
        clf = self._clf()
        record = _make_record(["supervised_learning"])
        result = clf.classify(record)
        assert result.source_record_id == record.id

    def test_classify_batch_returns_list(self):
        clf = self._clf()
        records = [_make_record(["supervised_learning"]) for _ in range(3)]
        results = clf.classify_batch(records)
        assert len(results) == 3

    def test_get_classified_methods_accumulates(self):
        clf = self._clf()
        clf.classify(_make_record(["supervised_learning"]))
        clf.classify(_make_record(["reinforcement_learning"]))
        assert len(clf.get_classified_methods()) == 2

    def test_stats_structure(self):
        clf = self._clf()
        clf.classify(_make_record(["supervised_learning"]))
        stats = clf.get_stats()
        assert "total_classified" in stats
        assert "by_method_type" in stats
        assert "average_confidence" in stats

    def test_country_metadata_preserved(self):
        clf = self._clf()
        result = clf.classify(_make_record(["supervised_learning"]))
        assert result.country_of_origin == "USA"


# ===========================================================================
# Sandbox tests
# ===========================================================================

def _make_method(method_type=LearningMethodType.SUPERVISED, novelty=0.8):
    return ClassifiedMethod(
        id="method-id",
        title="Test Method",
        method_type=method_type,
        country_of_origin="USA",
        lab_name="DeepMind",
        novelty_score=novelty,
        confidence=0.85,
        tags=["supervised_learning"],
        classified_at=_utc_now_naive(),
        source_record_id="src-id",
    )


class TestSandbox:
    def _sandbox(self, tier=Tier.PRO):
        return SandboxTestingLayer(tier)

    def test_run_test_returns_result(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert isinstance(result, SandboxTestResult)

    def test_result_status_completed(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert result.status == SandboxStatus.COMPLETED

    def test_result_accuracy_in_range(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert result.accuracy is not None
        assert 0.0 <= result.accuracy <= 1.0

    def test_result_convergence_in_range(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert result.convergence_rate is not None
        assert 0.0 <= result.convergence_rate <= 1.0

    def test_result_resource_in_range(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert result.resource_consumption is not None
        assert 0.0 <= result.resource_consumption <= 100.0

    def test_result_has_container_id(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert result.container_id.startswith("dreamco-sandbox-")

    def test_result_has_started_at(self):
        sb = self._sandbox()
        result = sb.run_test(_make_method())
        assert isinstance(result.started_at, datetime.datetime)

    def test_run_batch_returns_list(self):
        sb = self._sandbox()
        methods = [_make_method() for _ in range(3)]
        results = sb.run_batch(methods)
        assert len(results) == 3

    def test_get_results_accumulates(self):
        sb = self._sandbox()
        sb.run_test(_make_method())
        sb.run_test(_make_method())
        assert len(sb.get_results()) == 2

    def test_free_tier_raises_sandbox_error(self):
        sb = SandboxTestingLayer(Tier.FREE)
        with pytest.raises(SandboxTierError):
            sb.run_test(_make_method())

    def test_pro_container_limit(self):
        sb = SandboxTestingLayer(Tier.PRO)
        sb._active_containers = sb.config.sandbox_containers
        with pytest.raises(SandboxTierError):
            sb.run_test(_make_method())

    def test_enterprise_no_container_limit(self):
        sb = SandboxTestingLayer(Tier.ENTERPRISE)
        sb._active_containers = 9999
        result = sb.run_test(_make_method())
        assert result.status == SandboxStatus.COMPLETED

    def test_stats_structure(self):
        sb = self._sandbox()
        sb.run_test(_make_method())
        stats = sb.get_stats()
        assert "total_runs" in stats
        assert "completed" in stats
        assert "average_accuracy" in stats


# ===========================================================================
# Analytics tests
# ===========================================================================

def _make_test_results_and_methods(n=5):
    methods = []
    test_results = []
    for i in range(n):
        m = ClassifiedMethod(
            id=f"m-{i}",
            title=f"Method {i}",
            method_type=LearningMethodType.SUPERVISED,
            country_of_origin="USA" if i % 2 == 0 else "UK",
            lab_name="Lab",
            novelty_score=0.5 + i * 0.05,
            confidence=0.8,
            tags=["supervised_learning"],
            classified_at=_utc_now_naive(),
        )
        methods.append(m)
        r = SandboxTestResult(
            id=f"r-{i}",
            method_id=m.id,
            status=SandboxStatus.COMPLETED,
            accuracy=0.7 + i * 0.04,
            convergence_rate=0.6 + i * 0.05,
            resource_consumption=50.0 - i * 3,
            runtime_seconds=20.0,
            container_id=f"container-{i}",
            started_at=_utc_now_naive(),
            completed_at=_utc_now_naive(),
        )
        test_results.append(r)
    return test_results, methods


class TestAnalytics:
    def _layer(self, tier=Tier.FREE):
        return PerformanceAnalyticsLayer(tier)

    def test_compute_rankings_returns_list(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods()
        rankings = layer.compute_rankings(results, methods)
        assert isinstance(rankings, list)

    def test_rankings_count_matches_methods(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(5)
        rankings = layer.compute_rankings(results, methods)
        assert len(rankings) == 5

    def test_ranking_is_method_ranking(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(3)
        rankings = layer.compute_rankings(results, methods)
        assert all(isinstance(r, MethodRanking) for r in rankings)

    def test_composite_score_in_range(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods()
        rankings = layer.compute_rankings(results, methods)
        assert all(0.0 <= r.composite_score <= 1.0 for r in rankings)

    def test_global_rank_one_is_best(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(5)
        rankings = layer.compute_rankings(results, methods)
        rank1 = next(r for r in rankings if r.global_rank == 1)
        assert rank1.composite_score == max(r.composite_score for r in rankings)

    def test_get_top_methods_returns_n(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(5)
        layer.compute_rankings(results, methods)
        top3 = layer.get_top_methods(3)
        assert len(top3) == 3

    def test_get_top_methods_sorted(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(5)
        layer.compute_rankings(results, methods)
        top = layer.get_top_methods(5)
        scores = [r.composite_score for r in top]
        assert scores == sorted(scores, reverse=True)

    def test_get_global_matrix(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(3)
        layer.compute_rankings(results, methods)
        matrix = layer.get_global_matrix()
        assert len(matrix) == 3

    def test_regional_rank_assigned(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(4)
        rankings = layer.compute_rankings(results, methods)
        assert all(r.regional_rank >= 1 for r in rankings)

    def test_stats_structure(self):
        layer = self._layer()
        results, methods = _make_test_results_and_methods(3)
        layer.compute_rankings(results, methods)
        stats = layer.get_stats()
        assert "total_ranked" in stats
        assert "top_method" in stats

    def test_empty_results_returns_empty_rankings(self):
        layer = self._layer()
        rankings = layer.compute_rankings([], [])
        assert rankings == []


# ===========================================================================
# Hybrid engine tests
# ===========================================================================

def _make_rankings(n=5):
    return [
        MethodRanking(
            method_id=f"m-{i}",
            method_title=f"Method {i}",
            global_rank=i + 1,
            regional_rank=1,
            region="USA",
            composite_score=1.0 - i * 0.1,
            accuracy_score=0.9 - i * 0.05,
            convergence_score=0.8 - i * 0.05,
            efficiency_score=0.7 - i * 0.05,
            test_count=2,
            computed_at=_utc_now_naive(),
        )
        for i in range(n)
    ]


class TestHybridEngine:
    def _engine(self, tier=Tier.PRO):
        return HybridEvolutionEngine(tier)

    def test_create_hybrid_returns_strategy(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert isinstance(strategy, HybridStrategy)

    def test_strategy_has_id(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert strategy.id

    def test_strategy_generation_zero(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert strategy.generation == 0

    def test_fitness_score_in_range(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert 0.0 <= strategy.fitness_score <= 1.0

    def test_accuracy_in_range(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert 0.0 <= strategy.accuracy <= 1.0

    def test_convergence_in_range(self):
        engine = self._engine()
        strategy = engine.create_hybrid(_make_rankings())
        assert 0.0 <= strategy.convergence_rate <= 1.0

    def test_free_tier_raises_hybrid_error(self):
        engine = HybridEvolutionEngine(Tier.FREE)
        with pytest.raises(HybridEngineTierError):
            engine.create_hybrid(_make_rankings())

    def test_evolve_returns_new_strategies(self):
        engine = self._engine()
        engine.create_hybrid(_make_rankings())
        evolved = engine.evolve(generations=2)
        assert len(evolved) == 2

    def test_evolve_increments_generation(self):
        engine = self._engine()
        engine.create_hybrid(_make_rankings())
        evolved = engine.evolve(generations=3)
        assert evolved[-1].generation == 3

    def test_get_strategies_cumulative(self):
        engine = self._engine()
        engine.create_hybrid(_make_rankings())
        engine.evolve(generations=2)
        assert len(engine.get_strategies()) == 3  # 1 initial + 2 evolved

    def test_get_best_strategy(self):
        engine = self._engine()
        engine.create_hybrid(_make_rankings())
        engine.evolve(generations=2)
        best = engine.get_best_strategy()
        assert best is not None
        assert best.fitness_score == max(s.fitness_score for s in engine.get_strategies())

    def test_get_best_strategy_none_when_empty(self):
        engine = self._engine()
        assert engine.get_best_strategy() is None

    def test_enterprise_has_genetic_algo_metadata(self):
        engine = HybridEvolutionEngine(Tier.ENTERPRISE)
        strategy = engine.create_hybrid(_make_rankings())
        assert strategy.metadata.get("genetic_algo") is True

    def test_stats_structure(self):
        engine = self._engine()
        engine.create_hybrid(_make_rankings())
        stats = engine.get_stats()
        assert "total_strategies" in stats
        assert "best_fitness" in stats


# ===========================================================================
# Deployment tests
# ===========================================================================

def _make_strategy(generation=0):
    return HybridStrategy(
        id="strat-id",
        name="TestHybrid",
        parent_method_ids=["m-0", "m-1"],
        method_types=["supervised_learning"],
        fitness_score=0.85,
        generation=generation,
        accuracy=0.88,
        convergence_rate=0.75,
        resource_consumption=42.0,
        created_at=_utc_now_naive(),
    )


class TestDeployment:
    def _orchestrator(self, tier=Tier.PRO):
        return DeploymentOrchestrator(tier)

    def test_deploy_returns_deployment(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        assert isinstance(deployment, Deployment)

    def test_deployment_status_deployed(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        assert deployment.status == DeploymentStatus.DEPLOYED

    def test_deployment_has_version(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        assert deployment.version

    def test_deployment_has_kubernetes_namespace(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        assert "dreamco" in deployment.kubernetes_namespace

    def test_deployment_has_replicas(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.TRADING)
        assert deployment.replicas > 0

    def test_free_tier_raises_deployment_error(self):
        orch = DeploymentOrchestrator(Tier.FREE)
        with pytest.raises(DeploymentTierError):
            orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)

    def test_rolling_update_returns_updated_deployment(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        new_strat = _make_strategy(generation=2)
        updated = orch.rolling_update(deployment.id, new_strat)
        assert updated.strategy_id == new_strat.id

    def test_rolling_update_status_deployed(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        new_strat = _make_strategy(generation=1)
        updated = orch.rolling_update(deployment.id, new_strat)
        assert updated.status == DeploymentStatus.DEPLOYED

    def test_rollback_sets_rolled_back_status(self):
        orch = self._orchestrator()
        deployment = orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        rolled = orch.rollback(deployment.id)
        assert rolled.status == DeploymentStatus.ROLLED_BACK

    def test_rollback_not_found_raises(self):
        orch = self._orchestrator()
        with pytest.raises(DeploymentNotFoundError):
            orch.rollback("nonexistent-id")

    def test_get_deployments_returns_all(self):
        orch = self._orchestrator()
        orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        orch.deploy(_make_strategy(), BotApplication.TRADING)
        assert len(orch.get_deployments()) == 2

    def test_stats_structure(self):
        orch = self._orchestrator()
        orch.deploy(_make_strategy(), BotApplication.REAL_ESTATE)
        stats = orch.get_stats()
        assert "total_deployments" in stats
        assert "by_status" in stats


# ===========================================================================
# Governance tests
# ===========================================================================

class TestGovernance:
    def _gov(self, tier=Tier.PRO):
        return GovernanceLayer(tier)

    def test_admin_can_ingest(self):
        gov = self._gov()
        assert gov.check_permission("alice", AccessRole.ADMIN, "ingest") is True

    def test_admin_can_deploy(self):
        gov = self._gov()
        assert gov.check_permission("alice", AccessRole.ADMIN, "deploy") is True

    def test_data_engineer_can_ingest(self):
        gov = self._gov()
        assert gov.check_permission("bob", AccessRole.DATA_ENGINEER, "ingest") is True

    def test_data_engineer_cannot_deploy(self):
        gov = self._gov()
        assert gov.check_permission("bob", AccessRole.DATA_ENGINEER, "deploy") is False

    def test_ml_engineer_can_sandbox(self):
        gov = self._gov()
        assert gov.check_permission("carol", AccessRole.ML_ENGINEER, "sandbox") is True

    def test_ml_engineer_cannot_deploy(self):
        gov = self._gov()
        assert gov.check_permission("carol", AccessRole.ML_ENGINEER, "deploy") is False

    def test_analyst_can_audit(self):
        gov = self._gov()
        assert gov.check_permission("dave", AccessRole.ANALYST, "audit") is True

    def test_analyst_cannot_ingest(self):
        gov = self._gov()
        assert gov.check_permission("dave", AccessRole.ANALYST, "ingest") is False

    def test_viewer_can_only_audit(self):
        gov = self._gov()
        assert gov.check_permission("eve", AccessRole.VIEWER, "audit") is True
        assert gov.check_permission("eve", AccessRole.VIEWER, "ingest") is False

    def test_enforce_raises_rbac_error(self):
        gov = self._gov()
        with pytest.raises(RBACError):
            gov.enforce("bob", AccessRole.VIEWER, "ingest")

    def test_enforce_allowed_does_not_raise(self):
        gov = self._gov()
        gov.enforce("alice", AccessRole.ADMIN, "ingest")  # should not raise

    def test_audit_log_records_entry(self):
        gov = self._gov()
        gov.check_permission("alice", AccessRole.ADMIN, "ingest")
        log = gov.get_audit_log()
        assert len(log) == 1

    def test_audit_log_entry_is_allowed(self):
        gov = self._gov()
        gov.check_permission("alice", AccessRole.ADMIN, "ingest")
        entry = gov.get_audit_log()[0]
        assert entry.status == "allowed"

    def test_audit_log_entry_is_denied(self):
        gov = self._gov()
        gov.check_permission("eve", AccessRole.VIEWER, "ingest")
        entry = gov.get_audit_log()[0]
        assert entry.status == "denied"

    def test_audit_log_is_immutable_copy(self):
        gov = self._gov()
        gov.check_permission("alice", AccessRole.ADMIN, "ingest")
        log = gov.get_audit_log()
        log.append("injected")
        assert len(gov.get_audit_log()) == 1

    def test_free_tier_raises_governance_error(self):
        gov = GovernanceLayer(Tier.FREE)
        with pytest.raises(GovernanceTierError):
            gov.check_permission("alice", AccessRole.ADMIN, "ingest")

    def test_audit_log_entry_structure(self):
        gov = self._gov()
        gov.check_permission("alice", AccessRole.ADMIN, "ingest")
        entry = gov.get_audit_log()[0]
        assert isinstance(entry, AuditLogEntry)
        assert entry.actor == "alice"
        assert entry.action == "ingest"

    def test_stats_structure(self):
        gov = self._gov()
        gov.check_permission("alice", AccessRole.ADMIN, "ingest")
        gov.check_permission("eve", AccessRole.VIEWER, "deploy")
        stats = gov.get_stats()
        assert stats["allowed"] == 1
        assert stats["denied"] == 1

    def test_role_permissions_all_roles_defined(self):
        for role in AccessRole:
            assert role in ROLE_PERMISSIONS


# ===========================================================================
# Scheduler tests
# ===========================================================================

class TestScheduler:
    def _scheduler(self, tier=Tier.FREE):
        return AutomationScheduler(tier)

    def test_schedule_job_returns_job(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        assert isinstance(job, ScheduledJob)

    def test_job_status_scheduled(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        assert job.status == JobStatus.SCHEDULED

    def test_job_has_next_run(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        assert isinstance(job.next_run, datetime.datetime)

    def test_job_next_run_in_future(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        assert job.next_run > _utc_now_naive()

    def test_run_job_updates_status(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        updated = sched.run_job(job.id)
        assert updated.status == JobStatus.COMPLETED

    def test_run_job_increments_run_count(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        sched.run_job(job.id)
        assert job.run_count == 1

    def test_run_job_sets_last_run(self):
        sched = self._scheduler()
        job = sched.schedule_job("daily-ingest", ScheduleFrequency.DAILY)
        sched.run_job(job.id)
        assert job.last_run is not None

    def test_run_job_not_found_raises(self):
        sched = self._scheduler()
        with pytest.raises(JobNotFoundError):
            sched.run_job("nonexistent-id")

    def test_get_jobs_returns_all(self):
        sched = self._scheduler()
        sched.schedule_job("j1", ScheduleFrequency.DAILY)
        sched.schedule_job("j2", ScheduleFrequency.WEEKLY)
        assert len(sched.get_jobs()) == 2

    def test_get_due_jobs_in_past(self):
        sched = self._scheduler()
        job = sched.schedule_job("past-job", ScheduleFrequency.DAILY)
        # Force next_run into the past
        job.next_run = _utc_now_naive() - datetime.timedelta(hours=1)
        due = sched.get_due_jobs()
        assert job in due

    def test_get_due_jobs_future_not_included(self):
        sched = self._scheduler()
        sched.schedule_job("future-job", ScheduleFrequency.DAILY)
        due = sched.get_due_jobs()
        assert len(due) == 0

    def test_weekly_next_run_about_7_days(self):
        sched = self._scheduler()
        before = _utc_now_naive()
        job = sched.schedule_job("weekly-job", ScheduleFrequency.WEEKLY)
        diff = (job.next_run - before).total_seconds()
        assert 6.9 * 86400 < diff < 7.1 * 86400

    def test_stats_structure(self):
        sched = self._scheduler()
        sched.schedule_job("j1", ScheduleFrequency.DAILY)
        stats = sched.get_stats()
        assert "total_jobs" in stats
        assert "total_runs" in stats


# ===========================================================================
# Full pipeline / AILearningSystem tests
# ===========================================================================

class TestAILearningSystem:
    def test_instantiate_free(self):
        system = AILearningSystem(Tier.FREE)
        assert system.tier == Tier.FREE

    def test_instantiate_pro(self):
        system = AILearningSystem(Tier.PRO)
        assert system.tier == Tier.PRO

    def test_instantiate_enterprise(self):
        system = AILearningSystem(Tier.ENTERPRISE)
        assert system.tier == Tier.ENTERPRISE

    def test_describe_tier_returns_string(self):
        system = AILearningSystem(Tier.FREE)
        output = system.describe_tier()
        assert "Free" in output

    def test_describe_tier_contains_price(self):
        system = AILearningSystem(Tier.PRO)
        output = system.describe_tier()
        assert "199" in output

    def test_show_upgrade_path_from_free(self):
        system = AILearningSystem(Tier.FREE)
        output = system.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise_no_upgrade(self):
        system = AILearningSystem(Tier.ENTERPRISE)
        output = system.show_upgrade_path()
        assert "top-tier" in output

    def test_run_ingestion_pipeline_returns_records(self):
        system = AILearningSystem(Tier.FREE)
        records = system.run_ingestion_pipeline([DataSourceType.ARXIV], "deep learning")
        assert len(records) > 0

    def test_run_full_pipeline_pro_returns_dict(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline(query="reinforcement learning", top_n=3)
        assert isinstance(result, dict)

    def test_run_full_pipeline_pro_has_stages(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline()
        assert "stages" in result

    def test_run_full_pipeline_pro_ingestion_completed(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline()
        assert result["stages"]["ingestion"]["status"] == "completed"

    def test_run_full_pipeline_pro_sandbox_completed(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline()
        assert result["stages"]["sandbox"]["status"] == "completed"

    def test_run_full_pipeline_pro_deployment_completed(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline()
        assert result["stages"]["deployment"]["status"] == "completed"

    def test_run_full_pipeline_free_sandbox_skipped(self):
        system = AILearningSystem(Tier.FREE)
        result = system.run_full_pipeline()
        assert "skipped" in result["stages"]["sandbox"]["status"]

    def test_run_full_pipeline_free_hybrid_skipped(self):
        system = AILearningSystem(Tier.FREE)
        result = system.run_full_pipeline()
        assert "skipped" in result["stages"]["hybrid_engine"]["status"]

    def test_run_full_pipeline_enterprise_completed(self):
        system = AILearningSystem(Tier.ENTERPRISE)
        result = system.run_full_pipeline(query="transformer")
        assert result["stages"]["deployment"]["status"] == "completed"

    def test_run_full_pipeline_has_summary(self):
        system = AILearningSystem(Tier.PRO)
        result = system.run_full_pipeline()
        assert "summary" in result
        assert "ingested" in result["summary"]

    def test_get_system_status_returns_dict(self):
        system = AILearningSystem(Tier.PRO)
        status = system.get_system_status()
        assert isinstance(status, dict)

    def test_get_system_status_has_all_subsystems(self):
        system = AILearningSystem(Tier.PRO)
        status = system.get_system_status()
        for key in ("ingestion", "classification", "sandbox", "analytics",
                    "hybrid_engine", "deployment", "governance", "scheduler"):
            assert key in status

    def test_run_full_pipeline_enterprise_genetic_algo(self):
        system = AILearningSystem(Tier.ENTERPRISE)
        result = system.run_full_pipeline()
        strategies = system.hybrid_engine.get_strategies()
        if strategies:
            assert strategies[0].metadata.get("genetic_algo") is True
