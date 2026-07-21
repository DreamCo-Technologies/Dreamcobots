"""
Global AI Learning Matrix Bot — tier-aware orchestrator for worldwide AI lab intelligence.

GLOBAL AI SOURCES FLOW: This bot integrates with the Dreamcobots GLOBAL AI SOURCES FLOW
framework to ingest, classify, benchmark, evolve, and govern AI learning methods across
50+ countries in real time.
"""

from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # CRITICAL — required for framework compliance

from bots.global_ai_learning_matrix.tiers import (
    Tier,
    get_tier_config,
    TierConfig,
    FEATURE_EVOLUTION_ENGINE,
    FEATURE_GOVERNANCE,
    FEATURE_CUSTOM_MODELS,
)
from bots.global_ai_learning_matrix.country_monitor import Country, CountryMonitor
from bots.global_ai_learning_matrix.learning_benchmarks import LearningMethod, LearningBenchmarks
from bots.global_ai_learning_matrix.evolution_engine import EvolutionEngine, EvolutionStage
from bots.global_ai_learning_matrix.governance import GovernanceLayer


class GlobalAILearningMatrixError(Exception):
    """Base exception for the Global AI Learning Matrix bot."""


class GlobalAILearningMatrixTierError(GlobalAILearningMatrixError):
    """Raised when a requested feature requires a higher tier."""


class GlobalAILearningMatrix:
    """
    Global AI Learning Matrix — country-level lab intelligence with learning benchmarks,
    modular evolution tools, and governance dashboards.

    Tiers:
      - FREE ($0):        5 countries, basic learning methods, read-only dashboard
      - PRO ($49):        50 countries, all learning methods, evolution engine, governance
      - ENTERPRISE ($199): Unlimited countries, custom models, white-label, API access
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self._tier = tier
        self._tier_config: TierConfig = get_tier_config(tier)
        self._country_monitor = CountryMonitor()
        self._benchmarks = LearningBenchmarks()
        self._evolution_engine = EvolutionEngine()
        self._governance = GovernanceLayer()
        self._tracked_country_codes: list[str] = []

    # --- Properties ---

    @property
    def tier(self) -> Tier:
        return self._tier

    @property
    def tier_config(self) -> TierConfig:
        return self._tier_config

    # --- Tier gate helper ---

    def _require_feature(self, feature: str, friendly_name: str) -> None:
        if not self._tier_config.has_feature(feature):
            raise GlobalAILearningMatrixTierError(
                f"'{friendly_name}' is not available on the {self._tier.value.upper()} tier. "
                f"Upgrade to PRO or ENTERPRISE to unlock this feature."
            )

    # --- Dashboard ---

    def dashboard(self) -> str:
        global_stats = self._country_monitor.get_global_stats()
        top = self._country_monitor.get_top_countries(n=5)
        top_str = "\n".join(
            f"    {i+1}. {c.name} ({c.code}) — {c.lab_count} labs, health {c.health_score:.1f}"
            for i, c in enumerate(top)
        )
        ranked = self._benchmarks.rank_methods()
        method_str = ", ".join(f"{m.value}({s:.1f})" for m, s in ranked[:3])

        gov_score = self._governance.get_governance_score() if self._tier_config.has_feature(FEATURE_GOVERNANCE) else "N/A (PRO+)"
        evo_models = len(self._evolution_engine.list_models()) if self._tier_config.has_feature(FEATURE_EVOLUTION_ENGINE) else "N/A (PRO+)"

        lines = [
            "=" * 60,
            "  GLOBAL AI LEARNING MATRIX — Dashboard",
            f"  Tier: {self._tier_config.name}  |  ${self._tier_config.price_usd_monthly:.0f}/mo",
            "=" * 60,
            f"  Countries tracked : {global_stats['total_countries']}",
            f"  Total labs         : {global_stats['total_labs']:,}",
            f"  Avg health score   : {global_stats['avg_health_score']}",
            f"  Top region         : {global_stats['top_region']}",
            "",
            "  Top 5 Countries by Lab Count:",
            top_str,
            "",
            f"  Top Learning Methods (overall): {method_str}",
            "",
            f"  Governance score   : {gov_score}",
            f"  Evolution models   : {evo_models}",
            "=" * 60,
        ]
        return "\n".join(lines)

    # --- Country tracking ---

    def track_country(
        self,
        code: str,
        name: str,
        region: str,
        lab_count: int,
        active_models: int,
        health_score: float,
    ) -> dict:
        max_countries = self._tier_config.max_countries
        if max_countries is not None and code.upper() not in self._tracked_country_codes:
            if len(self._tracked_country_codes) >= max_countries:
                raise GlobalAILearningMatrixTierError(
                    f"Country limit of {max_countries} reached for the {self._tier.value.upper()} tier. "
                    "Upgrade to PRO or ENTERPRISE to track more countries."
                )
        country = Country(
            code=code.upper(),
            name=name,
            region=region,
            lab_count=lab_count,
            active_models=active_models,
            health_score=health_score,
        )
        self._country_monitor.add_country(country)
        if code.upper() not in self._tracked_country_codes:
            self._tracked_country_codes.append(code.upper())
        return {
            "code": country.code,
            "name": country.name,
            "region": country.region,
            "lab_count": country.lab_count,
            "active_models": country.active_models,
            "health_score": country.health_score,
        }

    def get_country_stats(self, code: str) -> dict:
        country = self._country_monitor.get_country(code)
        return {
            "code": country.code,
            "name": country.name,
            "region": country.region,
            "lab_count": country.lab_count,
            "active_models": country.active_models,
            "health_score": country.health_score,
        }

    # --- Learning benchmarks ---

    def run_benchmark(self, method: str) -> dict:
        try:
            lm = LearningMethod(method.lower())
        except ValueError:
            valid = [m.value for m in LearningMethod]
            raise GlobalAILearningMatrixError(
                f"Unknown learning method '{method}'. Valid values: {valid}"
            )
        b = self._benchmarks.get_benchmark(lm)
        return {
            "method": lm.value,
            "accuracy": b.accuracy,
            "speed_score": b.speed_score,
            "cost_score": b.cost_score,
            "use_cases": b.use_cases,
        }

    # --- Evolution engine (PRO+) ---

    def evolve_model(self, model_id: str, name: str) -> dict:
        self._require_feature(FEATURE_EVOLUTION_ENGINE, "Evolution Engine")
        model = self._evolution_engine.register_model(model_id, name)
        return {
            "model_id": model.model_id,
            "name": model.name,
            "stage": model.stage.value,
            "version": model.version,
            "performance_score": model.performance_score,
        }

    def advance_model(self, model_id: str) -> dict:
        self._require_feature(FEATURE_EVOLUTION_ENGINE, "Evolution Engine")
        model = self._evolution_engine.advance_stage(model_id)
        return {
            "model_id": model.model_id,
            "name": model.name,
            "stage": model.stage.value,
            "version": model.version,
            "iterations": model.iterations,
        }

    # --- Governance (PRO+) ---

    def check_governance(self) -> dict:
        self._require_feature(FEATURE_GOVERNANCE, "Governance")
        return self._governance.audit_report()

    def raise_governance_alert(self, policy_id: str, message: str) -> dict:
        self._require_feature(FEATURE_GOVERNANCE, "Governance")
        alert = self._governance.raise_alert(policy_id, message)
        return {
            "alert_id": alert.alert_id,
            "policy_id": alert.policy_id,
            "message": alert.message,
            "severity": alert.severity,
            "resolved": alert.resolved,
        }

    # --- Global health ---

    def get_global_health(self) -> dict:
        global_stats = self._country_monitor.get_global_stats()
        top_countries = [
            {"code": c.code, "name": c.name, "lab_count": c.lab_count, "health_score": c.health_score}
            for c in self._country_monitor.get_top_countries(n=5)
        ]
        ranked = self._benchmarks.rank_methods()
        benchmarks_summary = [{"method": m.value, "overall_score": s} for m, s in ranked[:3]]

        open_alerts: int
        if self._tier_config.has_feature(FEATURE_GOVERNANCE):
            open_alerts = len(self._governance.list_alerts(resolved=False))
            gov_score = self._governance.get_governance_score()
        else:
            open_alerts = 0
            gov_score = None

        return {
            "health_score": global_stats["avg_health_score"],
            "total_countries": global_stats["total_countries"],
            "total_labs": global_stats["total_labs"],
            "top_region": global_stats["top_region"],
            "open_alerts": open_alerts,
            "governance_score": gov_score,
            "top_countries": top_countries,
            "benchmarks_summary": benchmarks_summary,
        }
