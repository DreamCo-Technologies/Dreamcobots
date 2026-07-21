"""
experiment_manager.py — Manages multiple experiment types in the sandbox lab.

Provides a registry for named experiments, supports A/B test orchestration,
and coordinates experiment lifecycle (create → run → analyse → archive).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Experiment:
    """Definition of a single sandbox experiment."""

    name: str
    description: str
    experiment_type: str  # "ab_test" | "adversarial" | "benchmark" | "custom"
    fn: Callable[[], Any]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExperimentManager:
    """
    Registry and lifecycle manager for sandbox experiments.

    Parameters
    ----------
    max_experiments : int | None
        Maximum number of experiments that can be registered concurrently.
        ``None`` means unlimited.
    """

    VALID_TYPES = {"ab_test", "adversarial", "benchmark", "custom"}

    def __init__(self, max_experiments: Optional[int] = None):
        self.max_experiments = max_experiments
        self._experiments: Dict[str, Experiment] = {}
        self._archived: List[str] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register(self, experiment: Experiment) -> None:
        """
        Register an experiment.

        Parameters
        ----------
        experiment : Experiment

        Raises
        ------
        ValueError
            If the name is already registered, the type is unknown, or the
            capacity limit is exceeded.
        """
        if experiment.name in self._experiments:
            raise ValueError(f"Experiment '{experiment.name}' is already registered.")
        if experiment.experiment_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unknown experiment type '{experiment.experiment_type}'. "
                f"Valid types: {sorted(self.VALID_TYPES)}"
            )
        if self.max_experiments is not None and len(self._experiments) >= self.max_experiments:
            raise ValueError(
                f"Maximum experiment capacity ({self.max_experiments}) reached."
            )
        self._experiments[experiment.name] = experiment

    def get(self, name: str) -> Experiment:
        """Retrieve a registered experiment by name."""
        if name not in self._experiments:
            raise KeyError(f"Experiment '{name}' not found.")
        return self._experiments[name]

    def list_experiments(self, experiment_type: Optional[str] = None) -> List[Experiment]:
        """List registered experiments, optionally filtered by *experiment_type*."""
        exps = list(self._experiments.values())
        if experiment_type is not None:
            exps = [e for e in exps if e.experiment_type == experiment_type]
        return exps

    def archive(self, name: str) -> None:
        """Remove an experiment from the active registry and mark it archived."""
        if name not in self._experiments:
            raise KeyError(f"Experiment '{name}' not found.")
        del self._experiments[name]
        self._archived.append(name)

    def is_archived(self, name: str) -> bool:
        """Return ``True`` if *name* has been archived."""
        return name in self._archived

    def get_archived(self) -> List[str]:
        """Return the list of archived experiment names."""
        return list(self._archived)

    def count(self) -> int:
        """Return the number of currently registered experiments."""
        return len(self._experiments)
