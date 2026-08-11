from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

VALID_STATES = {"VERIFIED", "PARTIAL", "DISCONNECTED", "MISSING", "TARGET_ONLY", "NOT_APPLICABLE"}


@dataclass(frozen=True)
class CapabilityEvidence:
    category_id: str
    productivity_job: str
    state: str
    evidence: str = ""
    user_value: int = 1
    frequency: int = 1
    dependency_value: int = 1
    revenue_value: int = 1
    risk: int = 1

    def validate(self) -> None:
        if self.state not in VALID_STATES:
            raise ValueError(f"invalid state: {self.state}")
        for value in (self.user_value, self.frequency, self.dependency_value, self.revenue_value, self.risk):
            if not 1 <= value <= 5:
                raise ValueError("priority dimensions must be between 1 and 5")

    @property
    def gap_score(self) -> int:
        self.validate()
        state_weight = {
            "VERIFIED": 0,
            "PARTIAL": 2,
            "DISCONNECTED": 3,
            "MISSING": 5,
            "TARGET_ONLY": 4,
            "NOT_APPLICABLE": 0,
        }[self.state]
        positive = self.user_value + self.frequency + self.dependency_value + self.revenue_value
        return state_weight * positive * max(1, 6 - self.risk)


@dataclass(frozen=True)
class GapRecommendation:
    category_id: str
    productivity_job: str
    state: str
    gap_score: int
    action: str
    evidence: str


def recommend_gap_action(item: CapabilityEvidence) -> GapRecommendation:
    item.validate()
    if item.state == "VERIFIED":
        action = "keep regression tests and refresh evidence when dependencies change"
    elif item.state == "PARTIAL":
        action = "extend existing capability and add missing workflow/tool coverage"
    elif item.state == "DISCONNECTED":
        action = "connect or repair the existing tool/API/integration before building a duplicate"
    elif item.state == "MISSING":
        action = "search for reusable components, then build a task-scoped specialist if the gap is real"
    elif item.state == "TARGET_ONLY":
        action = "implement and sandbox-test before presenting this as a Buddy capability"
    else:
        action = "no implementation required for this category"
    return GapRecommendation(item.category_id, item.productivity_job, item.state, item.gap_score, action, item.evidence)


def rank_gaps(items: Iterable[CapabilityEvidence]) -> list[GapRecommendation]:
    recommendations = [recommend_gap_action(item) for item in items]
    return sorted(recommendations, key=lambda item: item.gap_score, reverse=True)


def category_coverage(items: Iterable[CapabilityEvidence], category_id: str) -> float:
    selected = [item for item in items if item.category_id == category_id and item.state != "NOT_APPLICABLE"]
    if not selected:
        return 0.0
    weights = {"VERIFIED": 1.0, "PARTIAL": 0.5, "DISCONNECTED": 0.25, "MISSING": 0.0, "TARGET_ONLY": 0.0}
    return round(sum(weights[item.state] for item in selected) / len(selected) * 100, 2)
