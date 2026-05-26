from __future__ import annotations

from dataclasses import asdict
import time
from typing import Protocol

from dreamco_platform.swarm.stigmergy.governance import GovernanceDecision, StigmergyGovernance
from dreamco_platform.swarm.stigmergy.observer import StigmergyObserver
from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace
from dreamco_platform.swarm.stigmergy.replay import InMemoryEventStore, StigmergyEvent
from dreamco_platform.swarm.stigmergy.safety import SwarmSafetyControls


class RedisStore(Protocol):
    def put_active_trace(self, trace: PheromoneTrace) -> None: ...

    def get_active_traces(self) -> list[PheromoneTrace]: ...


class DurableStore(Protocol):
    def append_trace_event(self, event: StigmergyEvent) -> None: ...

    def load_active_traces(self) -> list[PheromoneTrace]: ...


class ArchiveStore(Protocol):
    def snapshot(self, traces: list[PheromoneTrace]) -> None: ...


class StigmergyEnvironment:
    def __init__(
        self,
        *,
        observer: StigmergyObserver | None = None,
        governance: StigmergyGovernance | None = None,
        safety: SwarmSafetyControls | None = None,
        event_store: InMemoryEventStore | None = None,
    ) -> None:
        self.observer = observer or StigmergyObserver()
        self.governance = governance or StigmergyGovernance()
        self.safety = safety or SwarmSafetyControls()
        self.event_store = event_store or InMemoryEventStore()
        self._active_traces: list[PheromoneTrace] = []

    def active_traces(self) -> list[PheromoneTrace]:
        return list(self._active_traces)

    def deposit(self, trace: PheromoneTrace, *, bot_role: str = "worker", approval: bool = False) -> GovernanceDecision:
        self.safety.enforce(action="deposit", bot_id=trace.bot_id, high_impact=trace.strength >= 0.9, approved=approval)
        decision = self.governance.validate_deposit(trace, bot_role=bot_role)
        if not decision.allowed:
            return decision
        self._active_traces.append(trace)
        self.observer.observe_deposit(trace)
        self.event_store.append(
            StigmergyEvent(
                event_type="stigmergy.deposit",
                payload=asdict(trace),
                timestamp=time.time(),
            )
        )
        return decision

    def traces_at(self, position: tuple[int, int]) -> list[PheromoneTrace]:
        traces = [trace for trace in self._active_traces if trace.position == position]
        self.observer.observe_read(trace_type="all", count=len(traces))
        return traces

    def metrics(self) -> dict:
        traces = self.active_traces()
        return {
            "active_trace_count": len(traces),
            "total_strength": sum(trace.strength for trace in traces),
            "heatmap": self.observer.heatmap(traces),
            "prometheus": self.observer.prometheus_snapshot(),
            "traces": self.observer.trace_snapshot(),
        }


class PersistentStigmergyEnvironment(StigmergyEnvironment):
    def __init__(
        self,
        *,
        redis_store: RedisStore | None = None,
        durable_store: DurableStore | None = None,
        archive_store: ArchiveStore | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.redis_store = redis_store
        self.durable_store = durable_store
        self.archive_store = archive_store

    def deposit(self, trace: PheromoneTrace, *, bot_role: str = "worker", approval: bool = False) -> GovernanceDecision:
        decision = super().deposit(trace, bot_role=bot_role, approval=approval)
        if not decision.allowed:
            return decision
        event = StigmergyEvent(event_type="stigmergy.deposit", payload=asdict(trace))
        if self.redis_store:
            self.redis_store.put_active_trace(trace)
        if self.durable_store:
            self.durable_store.append_trace_event(event)
        if self.archive_store:
            self.archive_store.snapshot(self.active_traces())
        return decision

    def reload_from_durable_storage(self) -> list[PheromoneTrace]:
        traces: list[PheromoneTrace] = []
        if self.durable_store:
            traces = self.durable_store.load_active_traces()
        elif self.redis_store:
            traces = self.redis_store.get_active_traces()
        self._active_traces = list(traces)
        return self.active_traces()
