"""
Hybrid evolution engine for the DreamCo Global AI Learning System.

Combines top-ranked methods into hybrid AI strategies using a simulated
genetic algorithm (selection → crossover → mutation → fitness evaluation).
"""

from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_HYBRID_ENGINE, FEATURE_GENETIC_ALGO
from .analytics import MethodRanking
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class HybridStrategy:
    """A composite AI/ML strategy produced by the evolution engine.

    Attributes
    ----------
    id : str
        Unique identifier (UUID4).
    name : str
        Human-readable strategy name.
    parent_method_ids : List[str]
        IDs of the MethodRankings that were combined.
    method_types : List[str]
        Learning method type values of the parent methods.
    fitness_score : float
        Overall fitness on a 0.0–1.0 scale.
    generation : int
        Evolution generation number (0 = initial crossover).
    accuracy : float
        Predicted accuracy of the hybrid (0.0–1.0).
    convergence_rate : float
        Predicted convergence rate (0.0–1.0).
    resource_consumption : float
        Predicted CPU utilisation (0–100).
    created_at : datetime.datetime
        UTC timestamp of strategy creation.
    metadata : dict
        Extra information (mutation rate, crossover points, etc.).
    """

    id: str
    name: str
    parent_method_ids: List[str]
    method_types: List[str]
    fitness_score: float
    generation: int
    accuracy: float
    convergence_rate: float
    resource_consumption: float
    created_at: datetime.datetime
    metadata: dict = field(default_factory=dict)


class HybridEngineTierError(Exception):
    """Raised when the current tier does not support the hybrid engine."""


def _crossover(parents: List[MethodRanking]) -> dict:
    """Simulate one-point crossover of parent method metrics."""
    n = len(parents)
    if n == 0:
        return {"accuracy": 0.5, "convergence": 0.5, "resource": 50.0}
    avg_acc = sum(p.accuracy_score for p in parents) / n
    avg_conv = sum(p.convergence_score for p in parents) / n
    avg_eff = sum(p.efficiency_score for p in parents) / n
    # resource_consumption ≈ inverse of efficiency
    avg_resource = (1.0 - avg_eff) * 100.0
    return {
        "accuracy": avg_acc,
        "convergence": avg_conv,
        "resource": avg_resource,
    }


def _mutate(metrics: dict, generation: int) -> dict:
    """Apply a small deterministic mutation to the crossover metrics."""
    # Mutation rate decreases with each generation (simulated annealing feel)
    rate = max(0.01, 0.05 - generation * 0.005)
    return {
        "accuracy": min(1.0, metrics["accuracy"] + rate * 0.8),
        "convergence": min(1.0, metrics["convergence"] + rate * 0.6),
        "resource": max(1.0, metrics["resource"] - rate * 15),
    }


def _fitness(metrics: dict) -> float:
    """Compute a fitness score from the mutated metrics."""
    efficiency = 1.0 - metrics["resource"] / 100.0
    return round(
        0.50 * metrics["accuracy"] + 0.30 * metrics["convergence"] + 0.20 * efficiency,
        4,
    )


class HybridEvolutionEngine:
    """Combines top-ranked methods and evolves them over multiple generations.

    Parameters
    ----------
    tier : Tier
        Subscription tier (PRO and above enable the hybrid engine;
        ENTERPRISE unlocks full genetic algorithm evolution).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._strategies: List[HybridStrategy] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_hybrid(
        self,
        rankings: List[MethodRanking],
        top_n: int = 5,
    ) -> HybridStrategy:
        """Create a hybrid strategy from the top-ranked methods.

        Performs selection → crossover → mutation → fitness evaluation.

        Parameters
        ----------
        rankings : List[MethodRanking]
            Global ranking list (best-first).
        top_n : int
            Number of top methods to combine.

        Returns
        -------
        HybridStrategy
            The first-generation hybrid strategy.

        Raises
        ------
        HybridEngineTierError
            If the current tier does not support the hybrid engine.
        """
        self._check_tier()

        selected = sorted(rankings, key=lambda r: r.composite_score, reverse=True)[:top_n]
        if not selected:
            selected = rankings[:top_n]

        generation = 0
        metrics = _crossover(selected)
        if self.config.has_feature(FEATURE_GENETIC_ALGO):
            metrics = _mutate(metrics, generation)

        fitness = _fitness(metrics)
        method_types = list({r.method_title for r in selected})

        strategy = HybridStrategy(
            id=str(uuid.uuid4()),
            name=f"DreamHybrid-Gen{generation}-{uuid.uuid4().hex[:6].upper()}",
            parent_method_ids=[r.method_id for r in selected],
            method_types=method_types,
            fitness_score=fitness,
            generation=generation,
            accuracy=round(min(1.0, metrics["accuracy"]), 4),
            convergence_rate=round(min(1.0, metrics["convergence"]), 4),
            resource_consumption=round(max(0.0, metrics["resource"]), 2),
            created_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            metadata={
                "top_n_selected": len(selected),
                "genetic_algo": self.config.has_feature(FEATURE_GENETIC_ALGO),
                "mutation_applied": self.config.has_feature(FEATURE_GENETIC_ALGO),
            },
        )
        self._strategies.append(strategy)
        return strategy

    def evolve(self, generations: int = 3) -> List[HybridStrategy]:
        """Evolve the best existing strategy for *generations* steps.

        Parameters
        ----------
        generations : int
            Number of additional evolution steps.

        Returns
        -------
        List[HybridStrategy]
            Newly created strategies (one per generation).

        Raises
        ------
        HybridEngineTierError
            If no base strategy exists or the tier is insufficient.
        """
        self._check_tier()
        if not self._strategies:
            raise HybridEngineTierError(
                "No base strategy to evolve. Call create_hybrid() first."
            )

        new_strategies: List[HybridStrategy] = []
        current = self._strategies[-1]

        for _ in range(generations):
            gen_num = current.generation + 1
            parent_metrics = {
                "accuracy": current.accuracy,
                "convergence": current.convergence_rate,
                "resource": current.resource_consumption,
            }
            metrics = _mutate(parent_metrics, gen_num)
            fitness = _fitness(metrics)

            evolved = HybridStrategy(
                id=str(uuid.uuid4()),
                name=f"DreamHybrid-Gen{gen_num}-{uuid.uuid4().hex[:6].upper()}",
                parent_method_ids=[current.id],
                method_types=list(current.method_types),
                fitness_score=fitness,
                generation=gen_num,
                accuracy=round(min(1.0, metrics["accuracy"]), 4),
                convergence_rate=round(min(1.0, metrics["convergence"]), 4),
                resource_consumption=round(max(0.0, metrics["resource"]), 2),
                created_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                metadata={
                    "evolved_from": current.id,
                    "genetic_algo": self.config.has_feature(FEATURE_GENETIC_ALGO),
                },
            )
            self._strategies.append(evolved)
            new_strategies.append(evolved)
            current = evolved

        return new_strategies

    def get_strategies(self) -> List[HybridStrategy]:
        """Return all strategies created so far."""
        return list(self._strategies)

    def get_best_strategy(self) -> Optional[HybridStrategy]:
        """Return the strategy with the highest fitness score, or None."""
        if not self._strategies:
            return None
        return max(self._strategies, key=lambda s: s.fitness_score)

    def get_stats(self) -> dict:
        """Return a summary of the evolution engine state."""
        best = self.get_best_strategy()
        return {
            "total_strategies": len(self._strategies),
            "max_generation": max((s.generation for s in self._strategies), default=0),
            "best_fitness": best.fitness_score if best else None,
            "best_strategy_id": best.id if best else None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_HYBRID_ENGINE):
            raise HybridEngineTierError(
                f"The hybrid evolution engine is not available on the "
                f"{self.config.name} tier. Upgrade to Pro or Enterprise."
            )
