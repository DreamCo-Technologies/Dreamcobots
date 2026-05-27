from __future__ import annotations

import logging
from typing import Any

from dreamco_platform.observability.metrics import MetricsCollector
from dreamco_platform.observability.tracer import Tracer
from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace

try:  # pragma: no cover - optional dependency
    from opentelemetry import metrics as otel_metrics
    from opentelemetry import trace as otel_trace
except ImportError:  # pragma: no cover
    otel_metrics = None
    otel_trace = None


class StigmergyObserver:
    def __init__(
        self,
        *,
        metrics: MetricsCollector | None = None,
        tracer: Tracer | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.metrics = metrics or MetricsCollector()
        self.tracer = tracer or Tracer()
        self.logger = logger or logging.getLogger("dreamco.stigmergy")
        self._otel_tracer = otel_trace.get_tracer("dreamco.stigmergy") if otel_trace else None
        self._otel_meter = otel_metrics.get_meter("dreamco.stigmergy") if otel_metrics else None
        self._otel_deposit_counter = (
            self._otel_meter.create_counter("stigmergy.deposits_total")
            if self._otel_meter
            else None
        )
        self._otel_read_counter = (
            self._otel_meter.create_counter("stigmergy.reads_total")
            if self._otel_meter
            else None
        )
        self._otel_action_counter = (
            self._otel_meter.create_counter("stigmergy.actions_total")
            if self._otel_meter
            else None
        )
        self._otel_strength_histogram = (
            self._otel_meter.create_histogram("stigmergy.strength")
            if self._otel_meter
            else None
        )

    def observe_deposit(self, pheromone: PheromoneTrace, *, source: str = "swarm") -> None:
        labels = {"trace_type": pheromone.trace_type, "source": source}
        with self.tracer.span("stigmergy.deposit", trace_id=f"{source}:{pheromone.bot_id}") as span:
            span.set_tag("bot_id", pheromone.bot_id)
            span.set_tag("position", pheromone.position)
            span.set_tag("strength", pheromone.strength)
            self.metrics.increment("stigmergy.deposits_total", labels=labels)
            self.metrics.increment("stigmergy.active_traces_delta", labels=labels)
            self.metrics.set_gauge("stigmergy.last_strength", pheromone.strength, labels=labels)
        if self._otel_tracer:
            with self._otel_tracer.start_as_current_span("stigmergy.deposit") as span:
                span.set_attribute("bot_id", pheromone.bot_id)
                span.set_attribute("trace_type", pheromone.trace_type)
                span.set_attribute("strength", pheromone.strength)
                span.set_attribute("source", source)
        if self._otel_deposit_counter:
            self._otel_deposit_counter.add(1, attributes=labels)
        if self._otel_strength_histogram:
            self._otel_strength_histogram.record(pheromone.strength, attributes=labels)
        self.logger.info(
            "stigmergy_deposit",
            extra={
                "trace_type": pheromone.trace_type,
                "strength": pheromone.strength,
                "position": pheromone.position,
                "bot_id": pheromone.bot_id,
            },
        )

    def observe_read(self, *, trace_type: str, count: int, source: str = "swarm") -> None:
        labels = {"trace_type": trace_type, "source": source}
        with self.tracer.span("stigmergy.read", trace_id=f"{source}:{trace_type}") as span:
            span.set_tag("count", count)
            self.metrics.increment("stigmergy.reads_total", labels=labels)
            self.metrics.set_gauge("stigmergy.last_read_count", count, labels=labels)
        if self._otel_tracer:
            with self._otel_tracer.start_as_current_span("stigmergy.read") as span:
                span.set_attribute("trace_type", trace_type)
                span.set_attribute("count", count)
                span.set_attribute("source", source)
        if self._otel_read_counter:
            self._otel_read_counter.add(1, attributes=labels)

    def observe_act(self, *, bot_id: str, action: str, source: str = "swarm") -> None:
        labels = {"bot_id": bot_id, "action": action, "source": source}
        with self.tracer.span("stigmergy.act", trace_id=f"{source}:{bot_id}") as span:
            span.set_tag("action", action)
            self.metrics.increment("stigmergy.actions_total", labels=labels)
        if self._otel_tracer:
            with self._otel_tracer.start_as_current_span("stigmergy.act") as span:
                span.set_attribute("bot_id", bot_id)
                span.set_attribute("action", action)
                span.set_attribute("source", source)
        if self._otel_action_counter:
            self._otel_action_counter.add(1, attributes=labels)

    def observe_rejection(self, *, reason: str, source: str = "swarm") -> None:
        labels = {"reason": reason, "source": source}
        with self.tracer.span("stigmergy.reject", trace_id=f"{source}:{reason}") as span:
            span.set_tag("reason", reason)
            self.metrics.increment("stigmergy.rejections_total", labels=labels)
        if self._otel_tracer:
            with self._otel_tracer.start_as_current_span("stigmergy.reject") as span:
                span.set_attribute("reason", reason)
                span.set_attribute("source", source)
        self.logger.warning("stigmergy_rejection", extra={"reason": reason})

    def observe_stability(self, *, volatility: float, risk_total: float, source: str = "swarm") -> None:
        labels = {"source": source}
        self.metrics.set_gauge("stigmergy.strength_volatility", volatility, labels=labels)
        self.metrics.set_gauge("stigmergy.risk_total", risk_total, labels=labels)
        if self._otel_strength_histogram:
            self._otel_strength_histogram.record(volatility, attributes={"metric": "volatility", **labels})

    def heatmap(self, traces: list[PheromoneTrace]) -> dict[str, float]:
        heat: dict[str, float] = {}
        for trace in traces:
            key = f"{trace.position[0]}:{trace.position[1]}"
            heat[key] = heat.get(key, 0.0) + trace.strength
        return heat

    def prometheus_snapshot(self) -> str:
        snapshot = self.metrics.snapshot()
        lines: list[str] = []
        for family, entries in snapshot.items():
            for entry in entries:
                labels = ",".join(f'{k}="{v}"' for k, v in sorted(entry["labels"].items()))
                value = entry.get("value", entry.get("count", 0))
                metric = entry["name"].replace(".", "_")
                lines.append(f'{metric}{{{labels}}} {value}')
        return "\n".join(lines)

    def trace_snapshot(self, n: int = 50) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.tracer.recent_spans(n)]

    def anomaly_flags(self, traces: list[PheromoneTrace]) -> dict[str, int]:
        high_strength = sum(1 for trace in traces if trace.strength >= 0.9)
        high_risk = sum(1 for trace in traces if trace.risk >= 0.7)
        return {"high_strength_traces": high_strength, "high_risk_traces": high_risk}
