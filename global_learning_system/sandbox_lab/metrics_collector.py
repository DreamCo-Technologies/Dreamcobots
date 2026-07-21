"""
metrics_collector.py — Collects and logs experiment metrics.

Aggregates per-run metrics from sandbox experiments and exposes summary
statistics for downstream analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MetricEntry:
    """A single timestamped metric observation."""

    experiment_name: str
    run_id: str
    metric_name: str
    value: float
    step: Optional[int] = None


class MetricsCollector:
    """
    Collects, stores, and summarises experiment metrics.

    Parameters
    ----------
    experiment_name : str | None
        Optional default experiment name applied when logging metrics
        without an explicit name.
    """

    def __init__(self, experiment_name: Optional[str] = None):
        self.default_experiment = experiment_name or "default"
        self._entries: List[MetricEntry] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def log(
        self,
        metric_name: str,
        value: float,
        run_id: str = "run_0",
        experiment_name: Optional[str] = None,
        step: Optional[int] = None,
    ) -> MetricEntry:
        """
        Log a single metric value.

        Parameters
        ----------
        metric_name : str
            Name of the metric (e.g. ``"accuracy"``, ``"loss"``).
        value : float
            Numeric value to record.
        run_id : str
            Identifier for the run that produced this metric.
        experiment_name : str | None
            Override the collector's default experiment name.
        step : int | None
            Optional training step or epoch number.

        Returns
        -------
        MetricEntry
        """
        entry = MetricEntry(
            experiment_name=experiment_name or self.default_experiment,
            run_id=run_id,
            metric_name=metric_name,
            value=float(value),
            step=step,
        )
        self._entries.append(entry)
        return entry

    def log_dict(
        self,
        metrics: Dict[str, float],
        run_id: str = "run_0",
        experiment_name: Optional[str] = None,
        step: Optional[int] = None,
    ) -> List[MetricEntry]:
        """Log multiple metrics at once from a dictionary."""
        return [
            self.log(k, v, run_id=run_id, experiment_name=experiment_name, step=step)
            for k, v in metrics.items()
        ]

    def get_metrics(
        self,
        experiment_name: Optional[str] = None,
        metric_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[MetricEntry]:
        """
        Retrieve logged entries, with optional filters.

        Parameters
        ----------
        experiment_name : str | None
            Filter by experiment.
        metric_name : str | None
            Filter by metric name.
        run_id : str | None
            Filter by run identifier.
        """
        entries = self._entries
        if experiment_name is not None:
            entries = [e for e in entries if e.experiment_name == experiment_name]
        if metric_name is not None:
            entries = [e for e in entries if e.metric_name == metric_name]
        if run_id is not None:
            entries = [e for e in entries if e.run_id == run_id]
        return entries

    def summary(self, metric_name: str, experiment_name: Optional[str] = None) -> Dict[str, float]:
        """
        Return summary statistics (min, max, mean, last) for *metric_name*.

        Parameters
        ----------
        metric_name : str
            The metric to summarise.
        experiment_name : str | None
            Optional experiment filter.

        Returns
        -------
        dict with keys: ``min``, ``max``, ``mean``, ``last``, ``count``.

        Raises
        ------
        ValueError
            If no entries match the given filters.
        """
        entries = self.get_metrics(experiment_name=experiment_name, metric_name=metric_name)
        if not entries:
            raise ValueError(
                f"No entries found for metric '{metric_name}'"
                + (f" in experiment '{experiment_name}'" if experiment_name else "")
                + "."
            )
        values = [e.value for e in entries]
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "last": values[-1],
            "count": float(len(values)),
        }

    def clear(self) -> None:
        """Remove all logged entries."""
        self._entries = []
