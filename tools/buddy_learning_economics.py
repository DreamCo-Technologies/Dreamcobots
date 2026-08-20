#!/usr/bin/env python3
"""Choose learning actions using expected benchmark improvement per resource cost."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class LearningOption:
    name: str
    expected_gain: float
    seconds: float
    compute_cost: float
    reliability: float = 0.5

    @property
    def utility(self) -> float:
        cost = max(0.001, self.seconds * 0.001 + self.compute_cost)
        return (self.expected_gain * (0.5 + 0.5 * self.reliability)) / cost


def choose_options(options: list[LearningOption], budget: float, max_items: int = 5) -> list[LearningOption]:
    chosen: list[LearningOption] = []
    spent = 0.0
    for option in sorted(options, key=lambda item: item.utility, reverse=True):
        cost = option.seconds * 0.001 + option.compute_cost
        if spent + cost <= budget and len(chosen) < max_items:
            chosen.append(option)
            spent += cost
    return chosen
