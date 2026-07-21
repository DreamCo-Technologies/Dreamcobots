"""
hybrid_generator.py — Generates new hybrid training pipelines.

Combines the highest-ranked methods from the Global Learning Matrix to
produce hybrid model configurations that leverage the strengths of
multiple AI approaches simultaneously.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HybridPipeline:
    """Describes a generated hybrid training pipeline."""

    pipeline_id: str
    name: str
    component_methods: List[str]
    combination_strategy: str  # "ensemble" | "sequential" | "weighted_vote"
    expected_score: float
    config: Dict[str, Any] = field(default_factory=dict)


class HybridGenerator:
    """
    Generates hybrid AI method pipelines from top-ranked components.

    Parameters
    ----------
    max_components : int
        Maximum number of constituent methods per hybrid pipeline.
    combination_strategy : str
        How components are combined: ``"ensemble"``, ``"sequential"``, or
        ``"weighted_vote"``.
    """

    VALID_STRATEGIES = {"ensemble", "sequential", "weighted_vote"}

    def __init__(
        self,
        max_components: int = 3,
        combination_strategy: str = "ensemble",
    ):
        if combination_strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Unknown strategy '{combination_strategy}'. "
                f"Valid: {sorted(self.VALID_STRATEGIES)}"
            )
        self.max_components = max_components
        self.combination_strategy = combination_strategy
        self._generated: List[HybridPipeline] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(
        self,
        candidates: List[Dict[str, Any]],
        pipeline_id: Optional[str] = None,
    ) -> HybridPipeline:
        """
        Generate a hybrid pipeline from *candidates*.

        Each candidate dict must have ``"method_id"`` (str) and
        ``"score"`` (float) keys.

        Parameters
        ----------
        candidates : list[dict]
            Ranked candidate methods (highest score first).
        pipeline_id : str | None
            Optional explicit pipeline identifier.

        Returns
        -------
        HybridPipeline
        """
        if not candidates:
            raise ValueError("candidates must be non-empty.")

        top = candidates[: self.max_components]
        ids = [c["method_id"] for c in top]
        scores = [c["score"] for c in top]
        expected = sum(scores) / len(scores)
        pid = pipeline_id or f"hybrid_{'-'.join(ids[:2])}"
        name = f"Hybrid({', '.join(ids)})"

        pipeline = HybridPipeline(
            pipeline_id=pid,
            name=name,
            component_methods=ids,
            combination_strategy=self.combination_strategy,
            expected_score=round(expected, 6),
            config={"weights": [round(s / sum(scores), 4) for s in scores]},
        )
        self._generated.append(pipeline)
        return pipeline

    def list_generated(self) -> List[HybridPipeline]:
        """Return all generated pipelines in this session."""
        return list(self._generated)
