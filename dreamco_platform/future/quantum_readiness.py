"""Quantum readiness scoring for cryptography and optimization portfolios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class Workload:
    name: str
    classical_cost: float
    quantum_advantage_potential: float
    cryptography_exposure: float


class QuantumReadinessAdvisor:
    def readiness_score(self, workloads: Iterable[Workload]) -> Dict[str, float]:
        entries = list(workloads)
        if not entries:
            return {"migration_readiness": 0.0, "pq_risk": 0.0, "opportunity": 0.0}
        opportunity = sum(w.quantum_advantage_potential * w.classical_cost for w in entries) / max(sum(w.classical_cost for w in entries), 1)
        pq_risk = sum(w.cryptography_exposure for w in entries) / len(entries)
        migration = max(0.0, min(1.0, opportunity * 0.6 + (1 - pq_risk) * 0.4))
        return {
            "migration_readiness": round(migration, 3),
            "pq_risk": round(pq_risk, 3),
            "opportunity": round(opportunity, 3),
        }

    def prioritize(self, workloads: Iterable[Workload]) -> List[Dict[str, float | str]]:
        ranked = []
        for workload in workloads:
            score = workload.quantum_advantage_potential * 0.7 + workload.cryptography_exposure * 0.3
            ranked.append({
                "name": workload.name,
                "priority_score": round(score, 3),
                "recommended_track": "post_quantum" if workload.cryptography_exposure > 0.5 else "research",
            })
        return sorted(ranked, key=lambda item: item["priority_score"], reverse=True)

    def roadmap(self, workloads: Iterable[Workload]) -> List[str]:
        items = self.prioritize(workloads)
        steps: List[str] = []
        for item in items:
            if item["recommended_track"] == "post_quantum":
                steps.append(f"Inventory cryptographic dependencies for {item['name']} and plan PQC migration.")
            else:
                steps.append(f"Prototype hybrid optimization workflow for {item['name']}.")
        return steps


def sample_portfolio() -> List[Workload]:
    return [
        Workload("fraud-scoring", 0.7, 0.3, 0.6),
        Workload("route-optimization", 0.9, 0.8, 0.2),
        Workload("simulation", 0.8, 0.7, 0.1),
    ]
