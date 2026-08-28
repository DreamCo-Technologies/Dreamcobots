"""Explicit query types for separating observation from intervention."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CausalQuery:
    query_id: str
    kind: str
    variable: str
    value: str | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"observe", "intervene", "counterfactual"}:
            raise ValueError("kind must be observe, intervene, or counterfactual")
        if self.kind == "intervene" and self.value is None:
            raise ValueError("intervention requires a value")
        if self.kind == "counterfactual" and self.target is None:
            raise ValueError("counterfactual requires a target")


class CausalQueryPlanner:
    def classify(self, query: CausalQuery) -> str:
        return query.kind

    def requires_external_evidence(self, query: CausalQuery) -> bool:
        return query.kind in {"observe", "intervene", "counterfactual"}
