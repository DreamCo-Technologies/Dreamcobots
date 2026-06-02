from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PerformanceGenome:
    latency_profile: List[float]
    throughput_curve: List[float]
    error_signature: Dict[str, float]
    cost_fingerprint: List[float]

    @staticmethod
    def diff(genome_a: 'PerformanceGenome', genome_b: 'PerformanceGenome') -> 'GenomeDiff':
        latency_delta = [b - a for a, b in zip(genome_a.latency_profile, genome_b.latency_profile)]
        throughput_delta = [b - a for a, b in zip(genome_a.throughput_curve, genome_b.throughput_curve)]
        error_delta = {key: genome_b.error_signature.get(key, 0.0) - genome_a.error_signature.get(key, 0.0) for key in set(genome_a.error_signature) | set(genome_b.error_signature)}
        cost_delta = [b - a for a, b in zip(genome_a.cost_fingerprint, genome_b.cost_fingerprint)]
        return GenomeDiff(latency_delta, throughput_delta, error_delta, cost_delta)


@dataclass
class GenomeDiff:
    latency_delta: List[float]
    throughput_delta: List[float]
    error_delta: Dict[str, float]
    cost_delta: List[float]


class GenomeLibrary:
    def __init__(self) -> None:
        self.history: Dict[str, List[PerformanceGenome]] = {}

    def add(self, deployment_id: str, genome: PerformanceGenome) -> None:
        self.history.setdefault(deployment_id, []).append(genome)

    def detect_regression(self, deployment_id: str) -> GenomeDiff | None:
        genomes = self.history.get(deployment_id, [])
        if len(genomes) < 2:
            return None
        return PerformanceGenome.diff(genomes[-2], genomes[-1])
