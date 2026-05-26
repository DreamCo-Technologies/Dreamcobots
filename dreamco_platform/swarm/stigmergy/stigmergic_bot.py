from __future__ import annotations

import random
from enum import Enum
from typing import Any

from core.bot_base import BotBase
from dreamco_platform.swarm.stigmergy.environment import StigmergyEnvironment
from dreamco_platform.swarm.stigmergy.pheromone import SemanticPheromone


class ForagingRole(str, Enum):
    EXPLORER = "explorer"
    EXPLOITER = "exploiter"
    SCOUT = "scout"
    GUARDIAN = "guardian"
    SYNTHESIZER = "synthesizer"


class StigmergicBot(BotBase):
    def __init__(
        self,
        name: str,
        *,
        environment: StigmergyEnvironment,
        role: ForagingRole = ForagingRole.EXPLORER,
    ) -> None:
        super().__init__(name=name)
        self.environment = environment
        self.role = role

    def deposit_trace(
        self,
        *,
        trace_type: str,
        context: dict[str, Any],
        semantic_category: str,
        strength: float = 0.5,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
        economic_score: float = 0.0,
    ) -> SemanticPheromone:
        pheromone = SemanticPheromone(
            trace_type=trace_type,
            semantic_category=semantic_category,
            strength=strength,
            embedding=embedding or [],
            context=context,
            metadata=metadata or {},
            economic_score=economic_score,
            origin_lineage=[self.name],
        )
        self.environment.deposit(pheromone)
        return pheromone

    def sense_traces(
        self,
        *,
        context: dict[str, Any] | None = None,
        trace_types: list[str] | None = None,
        embedding: list[float] | None = None,
        limit: int = 20,
    ) -> list[SemanticPheromone]:
        return self.environment.read_traces(
            context=context,
            trace_types=trace_types,
            embedding=embedding,
            limit=limit,
        )

    def forage(
        self,
        *,
        context: dict[str, Any] | None = None,
        trace_types: list[str] | None = None,
        embedding: list[float] | None = None,
    ) -> dict[str, Any]:
        traces = self.sense_traces(context=context, trace_types=trace_types, embedding=embedding)
        if self.role == ForagingRole.EXPLORER:
            return {"mode": "explore", "selected": traces[0] if traces else None}
        if self.role == ForagingRole.EXPLOITER:
            return {"mode": "exploit", "selected": traces[0] if traces else None}
        if self.role == ForagingRole.SCOUT:
            selected = random.choice(traces) if len(traces) > 1 else (traces[0] if traces else None)
            return {"mode": "scout", "selected": selected}
        if self.role == ForagingRole.GUARDIAN:
            anomalies = [p for p in traces if p.volatility_score >= 0.6 or p.trust_score < 0.4]
            return {"mode": "guard", "selected": anomalies}
        summaries: dict[str, int] = {}
        for trace in traces:
            summaries[trace.semantic_category] = summaries.get(trace.semantic_category, 0) + 1
        return {"mode": "synthesize", "selected": summaries}
