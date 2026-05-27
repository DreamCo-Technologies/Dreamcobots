from __future__ import annotations

from dataclasses import asdict
from collections import deque
import os
import time
from typing import Protocol

from dreamco_platform.swarm.stigmergy.governance import GovernanceDecision, StigmergyGovernance
from dreamco_platform.swarm.stigmergy.observer import StigmergyObserver
from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace
from dreamco_platform.swarm.stigmergy.replay import FileDurableEventStore, InMemoryEventStore, StigmergyEvent
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
        max_total_risk: float = 20.0,
        max_strength_volatility: float = 0.35,
        volatility_window: int = 25,
    ) -> None:
        self.observer = observer or StigmergyObserver()
        self.governance = governance or StigmergyGovernance()
        self.safety = safety or SwarmSafetyControls()
        self.event_store = event_store or InMemoryEventStore()
        self._active_traces: list[PheromoneTrace] = []
        self.max_total_risk = max_total_risk
        self.max_strength_volatility = max_strength_volatility
        self._recent_strengths: deque[float] = deque(maxlen=max(3, volatility_window))

    def active_traces(self) -> list[PheromoneTrace]:
        return list(self._active_traces)

    def deposit(self, trace: PheromoneTrace, *, bot_role: str = "worker", approval: bool = False) -> GovernanceDecision:
        required_approvals = self.governance.required_approvals_for(trace.trace_type)
        approval_count = self._extract_approval_count(trace, explicit_approval=approval)
        action_key = self._action_key(trace)
        self.safety.enforce(
            action="deposit",
            bot_id=trace.bot_id,
            high_impact=trace.strength >= 0.9 or required_approvals > 0,
            approved=approval,
            action_key=action_key,
            approval_count=approval_count,
            required_approvals=required_approvals,
        )
        decision = self.governance.validate_deposit(trace, bot_role=bot_role)
        if not decision.allowed:
            self.observer.observe_rejection(reason=decision.reason)
            self.event_store.append(
                StigmergyEvent(
                    event_type="stigmergy.rejected",
                    payload={**asdict(trace), "reason": decision.reason},
                    timestamp=time.time(),
                )
            )
            return decision
        stability_decision = self._economic_guardrail(trace)
        if stability_decision is not None:
            self.observer.observe_rejection(reason=stability_decision.reason)
            self.event_store.append(
                StigmergyEvent(
                    event_type="stigmergy.rejected",
                    payload={**asdict(trace), "reason": stability_decision.reason},
                    timestamp=time.time(),
                )
            )
            return stability_decision
        self._active_traces.append(trace)
        self._recent_strengths.append(trace.strength)
        self.observer.observe_deposit(trace)
        self.observer.observe_stability(
            volatility=self._strength_volatility_with(trace.strength),
            risk_total=sum(t.risk for t in self._active_traces),
        )
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
            "total_risk": sum(trace.risk for trace in traces),
            "volatility": self._strength_volatility_with(),
            "heatmap": self.observer.heatmap(traces),
            "anomalies": self.observer.anomaly_flags(traces),
            "prometheus": self.observer.prometheus_snapshot(),
            "traces": self.observer.trace_snapshot(),
        }

    def _action_key(self, trace: PheromoneTrace) -> str:
        return f"{trace.trace_type}:{trace.position[0]}:{trace.position[1]}"

    def _extract_approval_count(self, trace: PheromoneTrace, *, explicit_approval: bool) -> int:
        metadata = trace.metadata if isinstance(trace.metadata, dict) else {}
        if explicit_approval:
            return max(1, int(metadata.get("approval_count", 1)))
        approved_by = metadata.get("approved_by")
        if isinstance(approved_by, list):
            return len({str(approver) for approver in approved_by})
        return int(metadata.get("approval_count", 0))

    def _strength_volatility_with(self, candidate: float | None = None) -> float:
        strengths = list(self._recent_strengths)
        if candidate is not None:
            strengths.append(candidate)
        if len(strengths) <= 1:
            return 0.0
        mean = sum(strengths) / len(strengths)
        return (sum((value - mean) ** 2 for value in strengths) / len(strengths)) ** 0.5

    def _economic_guardrail(self, trace: PheromoneTrace) -> GovernanceDecision | None:
        projected_total_risk = sum(t.risk for t in self._active_traces) + trace.risk
        projected_volatility = self._strength_volatility_with(trace.strength)
        if projected_total_risk > self.max_total_risk:
            self.safety.open_circuit()
            return GovernanceDecision(False, "risk budget exceeded; circuit opened")
        if projected_volatility > self.max_strength_volatility:
            return GovernanceDecision(False, "strength volatility exceeds stability threshold")
        return None


class PersistentStigmergyEnvironment(StigmergyEnvironment):
    def __init__(
        self,
        *,
        redis_store: RedisStore | None = None,
        durable_store: DurableStore | None = None,
        archive_store: ArchiveStore | None = None,
        durable_event_log_path: str | None = None,
        governance_policy_path: str | None = None,
        **kwargs,
    ) -> None:
        governance_path = governance_policy_path or os.environ.get("STIGMERGY_GOVERNANCE_PATH")
        if governance_path and "governance" not in kwargs:
            kwargs["governance"] = StigmergyGovernance.from_yaml(governance_path)
        event_log_path = durable_event_log_path or os.environ.get("STIGMERGY_EVENT_LOG_PATH")
        if event_log_path and durable_store is None:
            durable_store = FileDurableEventStore(event_log_path)
        super().__init__(**kwargs)
        self.redis_store = redis_store
        self.durable_store = durable_store
        self.archive_store = archive_store

    def deposit(self, trace: PheromoneTrace, *, bot_role: str = "worker", approval: bool = False) -> GovernanceDecision:
        decision = super().deposit(trace, bot_role=bot_role, approval=approval)
        if not decision.allowed:
            return decision
        event = StigmergyEvent(event_type="stigmergy.deposit", payload=asdict(trace))
        try:
            if self.redis_store:
                self.redis_store.put_active_trace(trace)
            if self.durable_store:
                self.durable_store.append_trace_event(event)
            if self.archive_store:
                self.archive_store.snapshot(self.active_traces())
        except Exception as exc:  # noqa: BLE001
            self._rollback_trace(trace)
            reason = f"persistence failure: {exc}"
            self.observer.observe_rejection(reason=reason)
            self.event_store.append(
                StigmergyEvent(
                    event_type="stigmergy.persistence_failure",
                    payload={**asdict(trace), "error": str(exc)},
                    timestamp=time.time(),
                )
            )
            return GovernanceDecision(False, reason)
        return decision

    def reload_from_durable_storage(self) -> list[PheromoneTrace]:
        traces: list[PheromoneTrace] = []
        if self.durable_store:
            traces = self.durable_store.load_active_traces()
        elif self.redis_store:
            traces = self.redis_store.get_active_traces()
        self._active_traces = list(traces)
        self._recent_strengths = deque((trace.strength for trace in traces), maxlen=self._recent_strengths.maxlen)
        return self.active_traces()

    def _rollback_trace(self, trace: PheromoneTrace) -> None:
        for index in range(len(self._active_traces) - 1, -1, -1):
            if self._active_traces[index] == trace:
                self._active_traces.pop(index)
                break
