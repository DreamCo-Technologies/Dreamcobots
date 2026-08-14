"""Evidence-driven Buddy multi-agent routing primitives.

The router chooses specialists by demonstrated capability, not by name alone.
It supports multi-agent plans, independent verification, bounded parallelism,
and evidence capture. It is intentionally provider/model agnostic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable

@dataclass(frozen=True)
class CapabilityEvidence:
    capability: str
    quality: float = 0.0
    speed: float = 0.0
    efficiency: float = 0.0
    reliability: float = 0.0
    safety: float = 0.0
    samples: int = 0

    @property
    def score(self) -> float:
        values=(self.quality,self.speed,self.efficiency,self.reliability,self.safety)
        return sum(values)/len(values) if values else 0.0

@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    capabilities: frozenset[str]
    evidence: tuple[CapabilityEvidence, ...] = ()
    limitations: frozenset[str] = frozenset()
    available_tools: frozenset[str] = frozenset()

    def evidence_for(self, capability: str) -> CapabilityEvidence | None:
        matches=[e for e in self.evidence if e.capability == capability and e.samples > 0]
        return max(matches, key=lambda e:e.score) if matches else None

@dataclass(frozen=True)
class TaskStep:
    step_id: str
    required_capabilities: frozenset[str]
    depends_on: frozenset[str] = frozenset()
    independent_verification: bool = False

@dataclass
class RoutePlan:
    steps: list[TaskStep]
    assignments: dict[str, list[str]] = field(default_factory=dict)
    unresolved: dict[str, list[str]] = field(default_factory=dict)

class AgentRouter:
    """Select the smallest high-evidence team that covers each step."""
    def __init__(self, agents: Iterable[AgentProfile], min_score: float = 0.60):
        self.agents=list(agents); self.min_score=min_score

    def rank(self, capability: str) -> list[AgentProfile]:
        ranked=[]
        for agent in self.agents:
            if capability not in agent.capabilities or capability in agent.limitations: continue
            evidence=agent.evidence_for(capability)
            if evidence and evidence.score >= self.min_score: ranked.append((evidence.score,agent))
        ranked.sort(key=lambda x:(x[0],x[1].agent_id), reverse=True)
        return [a for _,a in ranked]

    def plan(self, steps: Iterable[TaskStep], max_agents_per_step: int = 3) -> RoutePlan:
        plan=RoutePlan(list(steps))
        for step in plan.steps:
            selected=[]
            for capability in sorted(step.required_capabilities):
                candidates=self.rank(capability)
                if not candidates:
                    plan.unresolved.setdefault(step.step_id,[]).append(capability); continue
                # Prefer one agent that covers several requirements before adding specialists.
                candidates.sort(key=lambda a:(len(a.capabilities & step.required_capabilities), a.agent_id), reverse=True)
                chosen=next((a for a in candidates if a.agent_id not in selected), None)
                if chosen: selected.append(chosen.agent_id)
                if len(selected)>=max_agents_per_step: break
            if step.independent_verification and selected:
                for candidate in self.agents:
                    if candidate.agent_id in selected: continue
                    if all(candidate.evidence_for(c) and candidate.evidence_for(c).score >= self.min_score for c in step.required_capabilities):
                        selected.append(candidate.agent_id); break
            plan.assignments[step.step_id]=selected
        return plan
