from __future__ import annotations

from dreamco_platform.swarm.runtime import DreamCoRuntime
from dreamco_platform.swarm.stigmergy.stigmergic_bot import ForagingRole, StigmergicBot


class StigmergyLeadGenBot(StigmergicBot):
    def __init__(self, runtime: DreamCoRuntime) -> None:
        super().__init__(
            name="StigmergyLeadGenBot",
            environment=runtime.stigmergy,
            role=ForagingRole.EXPLOITER,
        )

    def run_cycle(self) -> dict:
        traces = self.sense_traces(
            context={"vertical": "real_estate"},
            trace_types=["lead_opportunity"],
            limit=5,
        )
        if traces:
            return {"mode": "exploit", "trace_id": traces[0].id}
        fresh = self.deposit_trace(
            trace_type="lead_opportunity",
            semantic_category="real_estate_distress",
            context={"vertical": "real_estate"},
            strength=0.8,
            economic_score=0.3,
            metadata={"source": "exploration"},
        )
        return {"mode": "explore", "trace_id": fresh.id}

