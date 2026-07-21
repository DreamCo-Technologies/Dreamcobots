from __future__ import annotations

import logging
from typing import Any

from dreamco_platform.observability.metrics import MetricsCollector
from dreamco_platform.observability.tracer import Tracer
from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace


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

    def observe_deposit(self, pheromone: PheromoneTrace, *, source: str = "swarm") -> None:
        labels = {"trace_type": pheromone.trace_type, "source": source}
        with self.tracer.span("stigmergy.deposit", trace_id=f"{source}:{pheromone.bot_id}") as span:
            span.set_tag("bot_id", pheromone.bot_id)
            span.set_tag("position", pheromone.position)
            span.set_tag("strength", pheromone.strength)
            self.metrics.increment("stigmergy.deposits_total", labels=labels)
            self.metrics.increment("stigmergy.active_traces_delta", labels=labels)
            self.metrics.set_gauge("stigmergy.last_strength", pheromone.strength, labels=labels)
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

    def observe_act(self, *, bot_id: str, action: str, source: str = "swarm") -> None:
        labels = {"bot_id": bot_id, "action": action, "source": source}
        with self.tracer.span("stigmergy.act", trace_id=f"{source}:{bot_id}") as span:
            span.set_tag("action", action)
            self.metrics.increment("stigmergy.actions_total", labels=labels)

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
