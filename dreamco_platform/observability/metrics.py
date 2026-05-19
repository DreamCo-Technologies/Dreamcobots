"""
DreamCo Platform — Metrics Collector
======================================

``MetricsCollector`` aggregates numeric measurements across capability
executions and bot operations.

Supported metric types
----------------------
* **Counter** — monotonically increasing (e.g. invocation count)
* **Gauge**   — point-in-time value (e.g. active workers)
* **Histogram** — distribution of values (e.g. latency buckets)

All metrics are labelled with a ``source`` tag so they can be grouped by
bot, capability, or workflow.

Usage::

    metrics = MetricsCollector()
    metrics.increment("capability.invocations", labels={"capability_id": "lead.scrape"})
    metrics.record("capability.latency_ms", 42.5, labels={"capability_id": "lead.scrape"})
    snapshot = metrics.snapshot()
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Metric types
# ---------------------------------------------------------------------------

@dataclass
class CounterMetric:
    name: str
    labels: dict[str, str]
    value: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def increment(self, by: float = 1.0) -> None:
        self.value += by
        self.last_updated = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": "counter", "value": self.value, "labels": self.labels}


@dataclass
class GaugeMetric:
    name: str
    labels: dict[str, str]
    value: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def set(self, value: float) -> None:
        self.value = value
        self.last_updated = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": "gauge", "value": self.value, "labels": self.labels}


@dataclass
class HistogramMetric:
    name: str
    labels: dict[str, str]
    _samples: list[float] = field(default_factory=list, repr=False)
    last_updated: float = field(default_factory=time.time)

    def observe(self, value: float) -> None:
        self._samples.append(value)
        self.last_updated = time.time()

    @property
    def count(self) -> int:
        return len(self._samples)

    @property
    def sum(self) -> float:
        return sum(self._samples)

    @property
    def mean(self) -> float:
        return self.sum / self.count if self._samples else 0.0

    def percentile(self, p: float) -> float:
        if not self._samples:
            return 0.0
        sorted_samples = sorted(self._samples)
        idx = max(0, int(len(sorted_samples) * p / 100) - 1)
        return sorted_samples[idx]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "histogram",
            "count": self.count,
            "sum": self.sum,
            "mean": self.mean,
            "p50": self.percentile(50),
            "p95": self.percentile(95),
            "p99": self.percentile(99),
            "labels": self.labels,
        }


# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------

def _label_key(labels: dict[str, str]) -> str:
    return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))


class MetricsCollector:
    """Aggregates counters, gauges, and histograms."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, CounterMetric] = {}
        self._gauges: dict[str, GaugeMetric] = {}
        self._histograms: dict[str, HistogramMetric] = {}

    # ------------------------------------------------------------------
    # Counter
    # ------------------------------------------------------------------

    def increment(self, name: str, by: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            if key not in self._counters:
                self._counters[key] = CounterMetric(name=name, labels=labels or {})
            self._counters[key].increment(by)

    def counter_value(self, name: str, labels: dict[str, str] | None = None) -> float:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            m = self._counters.get(key)
        return m.value if m else 0.0

    # ------------------------------------------------------------------
    # Gauge
    # ------------------------------------------------------------------

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            if key not in self._gauges:
                self._gauges[key] = GaugeMetric(name=name, labels=labels or {})
            self._gauges[key].set(value)

    def gauge_value(self, name: str, labels: dict[str, str] | None = None) -> float:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            m = self._gauges.get(key)
        return m.value if m else 0.0

    # ------------------------------------------------------------------
    # Histogram
    # ------------------------------------------------------------------

    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = HistogramMetric(name=name, labels=labels or {})
            self._histograms[key].observe(value)

    def histogram(self, name: str, labels: dict[str, str] | None = None) -> HistogramMetric | None:
        key = f"{name}:{_label_key(labels or {})}"
        with self._lock:
            return self._histograms.get(key)

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": [m.to_dict() for m in self._counters.values()],
                "gauges": [m.to_dict() for m in self._gauges.values()],
                "histograms": [m.to_dict() for m in self._histograms.values()],
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
