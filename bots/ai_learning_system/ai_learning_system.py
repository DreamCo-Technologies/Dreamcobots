"""
DreamCo Global AI Learning System — main orchestrator.

Coordinates all subsystem layers: ingestion, classification, sandbox testing,
performance analytics, hybrid evolution, deployment, governance, and scheduling.

Usage
-----
    from bots.ai_learning_system import AILearningSystem
    from bots.ai_learning_system.tiers import Tier

    system = AILearningSystem(tier=Tier.PRO)
    result = system.run_full_pipeline(query="transformer")
    print(result["summary"])
"""

from typing import List, Optional

from .tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)
from .ingestion import DataIngestionLayer, DataSourceType, IngestedRecord
from .classifier import LearningMethodClassifier, ClassifiedMethod
from .sandbox import SandboxTestingLayer, SandboxTestResult
from .analytics import PerformanceAnalyticsLayer, MethodRanking
from .hybrid_engine import HybridEvolutionEngine, HybridStrategy
from .deployment import DeploymentOrchestrator, BotApplication, Deployment
from .governance import GovernanceLayer
from .scheduler import AutomationScheduler, ScheduleFrequency
from framework import GlobalAISourcesFlow  # noqa: F401


class AILearningSystemTierError(Exception):
    """Raised when a pipeline step is unavailable on the current tier."""


class AILearningSystem:
    """DreamCo Global AI Learning System orchestrator.

    Coordinates all layers: ingestion, classification, sandbox testing,
    performance analytics, hybrid evolution, deployment, governance, and
    scheduling.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.ingestion = DataIngestionLayer(tier)
        self.classifier = LearningMethodClassifier(tier)
        self.sandbox = SandboxTestingLayer(tier)
        self.analytics = PerformanceAnalyticsLayer(tier)
        self.hybrid_engine = HybridEvolutionEngine(tier)
        self.deployment = DeploymentOrchestrator(tier)
        self.governance = GovernanceLayer(tier)
        self.scheduler = AutomationScheduler(tier)

    # ------------------------------------------------------------------
    # Pipeline methods
    # ------------------------------------------------------------------

    def run_ingestion_pipeline(
        self,
        sources: List[DataSourceType],
        query: str,
    ) -> List[IngestedRecord]:
        """Run the ingestion pipeline across multiple sources.

        Parameters
        ----------
        sources : List[DataSourceType]
            Data sources to scrape.
        query : str
            Search query forwarded to each source.

        Returns
        -------
        List[IngestedRecord]
            Combined normalised records from all sources.
        """
        all_records: List[IngestedRecord] = []
        for source in sources:
            records = self.ingestion.ingest(source, query)
            all_records.extend(records)
        return all_records

    def run_full_pipeline(
        self,
        query: str = "deep learning",
        top_n: int = 5,
    ) -> dict:
        """Run the complete end-to-end pipeline.

        Stages (skipped if not available on the current tier):
        1. Ingest from all four sources
        2. Classify ingested records
        3. Sandbox test (PRO+)
        4. Compute analytics rankings
        5. Create hybrid strategy (PRO+)
        6. Evolve hybrid (PRO+, ENTERPRISE uses genetic algorithms)
        7. Deploy to first bot application (PRO+)

        Parameters
        ----------
        query : str
            Search query for the ingestion stage.
        top_n : int
            Number of top methods to pass to the hybrid engine.

        Returns
        -------
        dict
            Summary of each pipeline stage with result counts and status.
        """
        result: dict = {
            "tier": self.tier.value,
            "query": query,
            "stages": {},
        }

        # Stage 1: Ingest
        all_sources = [
            DataSourceType.ARXIV,
            DataSourceType.GITHUB,
            DataSourceType.KAGGLE,
            DataSourceType.AI_LAB,
        ]
        records = self.run_ingestion_pipeline(all_sources, query)
        result["stages"]["ingestion"] = {
            "status": "completed",
            "records_ingested": len(records),
        }

        # Stage 2: Classify
        methods = self.classifier.classify_batch(records)
        result["stages"]["classification"] = {
            "status": "completed",
            "methods_classified": len(methods),
        }

        # Stage 3: Sandbox (PRO+)
        test_results: List[SandboxTestResult] = []
        if self.config.has_feature("sandbox_testing"):
            test_results = self.sandbox.run_batch(methods)
            result["stages"]["sandbox"] = {
                "status": "completed",
                "tests_run": len(test_results),
            }
        else:
            result["stages"]["sandbox"] = {"status": "skipped (upgrade required)"}

        # Stage 4: Analytics
        rankings: List[MethodRanking] = []
        if test_results:
            rankings = self.analytics.compute_rankings(test_results, methods)
        result["stages"]["analytics"] = {
            "status": "completed" if rankings else "skipped (no test results)",
            "methods_ranked": len(rankings),
        }

        # Stage 5: Hybrid engine (PRO+)
        strategy: Optional[HybridStrategy] = None
        if self.config.has_feature("hybrid_evolution_engine") and rankings:
            strategy = self.hybrid_engine.create_hybrid(rankings, top_n=top_n)
            self.hybrid_engine.evolve(generations=2)
            strategy = self.hybrid_engine.get_best_strategy()
            result["stages"]["hybrid_engine"] = {
                "status": "completed",
                "strategies_created": len(self.hybrid_engine.get_strategies()),
                "best_fitness": strategy.fitness_score if strategy else None,
            }
        else:
            result["stages"]["hybrid_engine"] = {
                "status": "skipped (upgrade required or no rankings)"
            }

        # Stage 6: Deploy (PRO+)
        if self.config.has_feature("deployment_orchestration") and strategy:
            deployment = self.deployment.deploy(strategy, BotApplication.REAL_ESTATE)
            result["stages"]["deployment"] = {
                "status": "completed",
                "deployment_id": deployment.id,
                "application": deployment.bot_application.value,
                "version": deployment.version,
            }
        else:
            result["stages"]["deployment"] = {
                "status": "skipped (upgrade required or no strategy)"
            }

        result["summary"] = (
            f"Pipeline complete: {len(records)} records ingested, "
            f"{len(methods)} classified, "
            f"{len(test_results)} tested, "
            f"{len(rankings)} ranked."
        )
        return result

    # ------------------------------------------------------------------
    # Informational methods
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable description of the current tier."""
        cfg = self.config
        limit = (
            "Unlimited"
            if cfg.is_unlimited_ingestion()
            else f"{cfg.ingestion_jobs_per_month:,}"
        )
        containers = (
            "Unlimited"
            if cfg.sandbox_containers is None
            else str(cfg.sandbox_containers)
        )
        lines = [
            f"=== {cfg.name} AI Learning System Tier ===",
            f"Price     : ${cfg.price_usd_monthly:.2f}/month",
            f"Ingestion : {limit} jobs/month",
            f"Containers: {containers}",
            f"Support   : {cfg.support_level}",
            "",
            "Features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Return information about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_features = set(self.config.features)
        new_features = [f for f in next_cfg.features if f not in current_features]

        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price : ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for feat in new_features:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing AILearningSystem or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    def get_system_status(self) -> dict:
        """Return a status summary of all subsystems."""
        return {
            "tier": self.tier.value,
            "ingestion": self.ingestion.get_stats(),
            "classification": self.classifier.get_stats(),
            "sandbox": self.sandbox.get_stats(),
            "analytics": self.analytics.get_stats(),
            "hybrid_engine": self.hybrid_engine.get_stats(),
            "deployment": self.deployment.get_stats(),
            "governance": self.governance.get_stats(),
            "scheduler": self.scheduler.get_stats(),
        }
