"""
genetic_optimizer.py — Implements evolutionary / genetic algorithms.

Applies genetic operations (selection, crossover, mutation) to evolve
AI model configurations towards higher performance scores as evaluated
by the DreamCo sandbox and analytics layers.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Individual:
    """A single member of the genetic population."""

    individual_id: str
    genome: Dict[str, Any]
    fitness: float = 0.0
    generation: int = 0


class GeneticOptimizer:
    """
    Evolves AI configurations using a simple genetic algorithm.

    Parameters
    ----------
    population_size : int
        Number of individuals in each generation.
    mutation_rate : float
        Probability (0–1) that a gene mutates during reproduction.
    elite_fraction : float
        Fraction of the top individuals that are carried over unchanged.
    seed : int | None
        Optional random seed for reproducibility.
    """

    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.1,
        elite_fraction: float = 0.2,
        seed: Optional[int] = None,
    ):
        if not 0.0 <= mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be between 0 and 1.")
        if not 0.0 <= elite_fraction <= 1.0:
            raise ValueError("elite_fraction must be between 0 and 1.")

        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_fraction = elite_fraction
        self._rng = random.Random(seed)
        self._population: List[Individual] = []
        self._generation = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def initialise(self, genome_factory: Callable[[], Dict[str, Any]]) -> List[Individual]:
        """
        Create the initial population using *genome_factory*.

        Parameters
        ----------
        genome_factory : callable
            Zero-argument callable returning a random genome dict.
        """
        self._generation = 0
        self._population = [
            Individual(
                individual_id=f"gen0_ind{i}",
                genome=genome_factory(),
                generation=0,
            )
            for i in range(self.population_size)
        ]
        return list(self._population)

    def evaluate(self, fitness_fn: Callable[[Dict[str, Any]], float]) -> None:
        """
        Evaluate fitness for all individuals using *fitness_fn*.

        Parameters
        ----------
        fitness_fn : callable
            Receives a genome dict and returns a float fitness score.
        """
        for ind in self._population:
            ind.fitness = fitness_fn(ind.genome)

    def evolve(self) -> List[Individual]:
        """
        Produce the next generation via selection, crossover, and mutation.

        Returns
        -------
        list[Individual]
            The new population.
        """
        self._generation += 1
        gen = self._generation
        sorted_pop = sorted(self._population, key=lambda x: x.fitness, reverse=True)

        elite_n = max(1, int(len(sorted_pop) * self.elite_fraction))
        new_pop: List[Individual] = [
            Individual(
                individual_id=f"gen{gen}_elite{i}",
                genome=dict(ind.genome),
                fitness=ind.fitness,
                generation=gen,
            )
            for i, ind in enumerate(sorted_pop[:elite_n])
        ]

        while len(new_pop) < self.population_size:
            parent_a = self._tournament_select(sorted_pop)
            parent_b = self._tournament_select(sorted_pop)
            child_genome = self._crossover(parent_a.genome, parent_b.genome)
            child_genome = self._mutate(child_genome)
            new_pop.append(
                Individual(
                    individual_id=f"gen{gen}_ind{len(new_pop)}",
                    genome=child_genome,
                    generation=gen,
                )
            )

        self._population = new_pop
        return list(self._population)

    def best(self) -> Optional[Individual]:
        """Return the individual with the highest fitness score."""
        if not self._population:
            return None
        return max(self._population, key=lambda x: x.fitness)

    def get_population(self) -> List[Individual]:
        """Return the current population."""
        return list(self._population)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _tournament_select(self, population: List[Individual], k: int = 3) -> Individual:
        """Return the fittest individual from a random *k*-subset."""
        contestants = self._rng.sample(population, min(k, len(population)))
        return max(contestants, key=lambda x: x.fitness)

    def _crossover(self, g1: Dict[str, Any], g2: Dict[str, Any]) -> Dict[str, Any]:
        """Uniform crossover: each gene independently selected from either parent."""
        keys = list(set(g1) | set(g2))
        child: Dict[str, Any] = {}
        for key in keys:
            if key in g1 and key in g2:
                child[key] = self._rng.choice([g1[key], g2[key]])
            elif key in g1:
                child[key] = g1[key]
            else:
                child[key] = g2[key]
        return child

    def _mutate(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """Apply random mutations to numeric genes."""
        result = dict(genome)
        for key, val in result.items():
            if self._rng.random() < self.mutation_rate and isinstance(val, (int, float)):
                delta = val * 0.1 * (self._rng.random() * 2 - 1)
                # Always use float arithmetic to avoid truncation when val is int.
                result[key] = float(val) + delta
        return result
