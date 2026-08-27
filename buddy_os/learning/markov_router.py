"""Governed bridge from Markov predictions into Buddy route scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from .markov_engine import MarkovChain


@dataclass(frozen=True)
class RouteScore:
    route: str
    transition_probability: float
    score: float


class MarkovRouteAdvisor:
    """Use learned transition dynamics as one bounded routing feature.

    The advisor never executes actions and never overrides policy. It only
    produces ranked evidence that an existing Buddy planner can combine with
    capability, quality, cost, latency, risk, and approval signals.
    """

    def __init__(self, smoothing: float = 0.1) -> None:
        self.model = MarkovChain(smoothing=smoothing)

    def learn(self, traces: Iterable[Sequence[str]]) -> "MarkovRouteAdvisor":
        self.model.fit(traces)
        return self

    def rank(self, current_state: str, candidate_routes: Iterable[str]) -> List[RouteScore]:
        ranked: List[RouteScore] = []
        for route in candidate_routes:
            probability = self.model.transition_probability(current_state, route)
            ranked.append(RouteScore(route, probability, probability))
        ranked.sort(key=lambda item: (-item.score, item.route))
        return ranked

    def evidence(self, current_state: str, candidate_routes: Iterable[str]) -> Dict[str, object]:
        """Return JSON-friendly evidence for logs/UI without taking action."""
        ranked = self.rank(current_state, candidate_routes)
        return {
            "current_state": current_state,
            "ranked_routes": [
                {
                    "route": item.route,
                    "transition_probability": item.transition_probability,
                    "score": item.score,
                }
                for item in ranked
            ],
            "authority": "advisory",
            "execution": "none",
        }
