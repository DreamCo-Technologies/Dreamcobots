"""Real-time supply chain optimizer."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence


@dataclass(frozen=True)
class SupplyNode:
    supplier: str
    lead_time_days: float
    reliability_score: float
    cost: float


class OptimizationObjective(str, Enum):
    minimize_cost = "minimize_cost"
    minimize_latency = "minimize_latency"
    maximize_resilience = "maximize_resilience"


@dataclass
class OptimalPlan:
    selected_nodes: List[SupplyNode]
    objective: OptimizationObjective
    total_cost: float
    latency_days: float
    resilience_score: float
    alternatives: List[List[SupplyNode]]
    disruption_notes: List[str]


class SupplyChainOptimizer:
    def _score(self, node: SupplyNode, objective: OptimizationObjective) -> float:
        if objective == OptimizationObjective.minimize_cost:
            return node.cost + (1.0 - node.reliability_score) * 10
        if objective == OptimizationObjective.minimize_latency:
            return node.lead_time_days + (1.0 - node.reliability_score) * 5
        return -(node.reliability_score * 100 - node.cost - node.lead_time_days)

    def simulate_disruption(self, nodes: Sequence[SupplyNode]) -> List[str]:
        notes: List[str] = []
        for node in nodes:
            if node.reliability_score < 0.8:
                notes.append(f"{node.supplier} is disruption-prone; pre-book backup capacity.")
            if node.lead_time_days > 14:
                notes.append(f"{node.supplier} has long lead times; consider regional buffering.")
        return notes or ["No critical disruptions predicted from current routing."]

    def alternative_routing(self, nodes: Sequence[SupplyNode], objective: OptimizationObjective) -> List[List[SupplyNode]]:
        ranked = sorted(nodes, key=lambda node: self._score(node, objective))
        return [[node] for node in ranked[1:4]]

    def optimize(self, nodes: Sequence[SupplyNode], objective: OptimizationObjective) -> OptimalPlan:
        ranked = sorted(nodes, key=lambda node: self._score(node, objective))
        selected = ranked[: max(1, min(3, len(ranked)))]
        total_cost = round(sum(node.cost for node in selected), 2)
        latency = round(sum(node.lead_time_days for node in selected) / max(1, len(selected)), 2)
        resilience = round(sum(node.reliability_score for node in selected) / max(1, len(selected)), 3)
        alternatives = self.alternative_routing(nodes, objective)
        notes = self.simulate_disruption(selected)
        return OptimalPlan(selected, objective, total_cost, latency, resilience, alternatives, notes)
