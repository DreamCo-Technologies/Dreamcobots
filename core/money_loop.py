"""
DreamCo MoneyLoopEngine — Autonomous revenue generation loop.

The Money Loop repeatedly executes a workflow of revenue-generating bots,
validates each cycle's earnings, auto-scales winners, and accumulates
metrics across cycles.

Usage
-----
    from core.money_loop import MoneyLoopEngine
    from core.workflow import WorkflowEngine, WorkflowStep

    workflow = WorkflowEngine(name="revenue_chain")
    workflow.add_bot(RealEstateBot(), task={"location": "austin"})
    workflow.add_bot(DealFinderBot(), task={})

    loop = MoneyLoopEngine(workflow=workflow, max_cycles=3)
    report = loop.run()
    print(report["total_revenue"])
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.base_bot import RESULT_STATUS_SUCCESS, RESULT_STATUS_FAILED
from core.dreamco_orchestrator import RevenueValidator, AutoScaler
from core.workflow import WorkflowEngine, WorkflowResult


# ---------------------------------------------------------------------------
# CycleReport
# ---------------------------------------------------------------------------


@dataclass
class CycleReport:
    """Result of a single Money Loop cycle."""

    cycle: int
    workflow_result: WorkflowResult
    revenue: float
    leads: int
    validation: dict
    scaled_bots: List[str] = field(default_factory=list)
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "cycle": self.cycle,
            "revenue": self.revenue,
            "leads": self.leads,
            "validation_status": self.validation.get("status"),
            "scaled_bots": self.scaled_bots,
            "elapsed_ms": self.elapsed_ms,
            "workflow_status": self.workflow_result.status,
        }


# ---------------------------------------------------------------------------
# MoneyLoopEngine
# ---------------------------------------------------------------------------


class MoneyLoopEngine:
    """
    Autonomous revenue-generating loop.

    Runs the provided *workflow* repeatedly (up to *max_cycles*), validates
    revenue after each cycle, and triggers the ``AutoScaler`` for bots that
    cross the scale threshold.

    Parameters
    ----------
    workflow : WorkflowEngine
        The configured bot-chain to execute each cycle.
    max_cycles : int
        Maximum number of cycles to run.  Use ``1`` for a single pass.
    cycle_delay_seconds : float
        Seconds to pause between cycles (useful for rate-limiting).
    """

    def __init__(
        self,
        workflow: WorkflowEngine,
        max_cycles: int = 1,
        cycle_delay_seconds: float = 0.0,
    ) -> None:
        self.workflow = workflow
        self.max_cycles = max_cycles
        self.cycle_delay_seconds = cycle_delay_seconds
        self._validator = RevenueValidator()
        self._scaler = AutoScaler()
        self._cycle_reports: List[CycleReport] = []

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """
        Execute the money loop for up to *max_cycles* iterations.

        Returns
        -------
        dict
            ``{ total_cycles, total_revenue, total_leads, cycles, scaled_bots }``
        """
        total_revenue = 0.0
        total_leads = 0
        all_scaled: List[str] = []

        for cycle_num in range(1, self.max_cycles + 1):
            cycle_start = time.monotonic()

            workflow_result = self.workflow.run()

            # Aggregate revenue + leads from all successful step results
            cycle_revenue = 0.0
            cycle_leads = 0
            for step in workflow_result.steps:
                step_result = step.get("result") or {}
                if step_result:
                    cycle_revenue += float(step_result.get("data", {}).get("revenue", 0))
                    cycle_leads += int(step_result.get("data", {}).get("leads_generated", 0))

            validation = self._validator.validate(
                {"revenue": cycle_revenue, "leads_generated": cycle_leads}
            )

            scaled: List[str] = []
            if validation.get("scale"):
                for step in workflow_result.steps:
                    bot_name = step.get("bot_name", step.get("bot_id", "unknown"))
                    msg = self._scaler.clone_bot(bot_name)
                    scaled.append(msg)
            all_scaled.extend(scaled)
            total_revenue += cycle_revenue
            total_leads += cycle_leads

            elapsed_ms = round((time.monotonic() - cycle_start) * 1000, 2)
            report = CycleReport(
                cycle=cycle_num,
                workflow_result=workflow_result,
                revenue=cycle_revenue,
                leads=cycle_leads,
                validation=validation,
                scaled_bots=scaled,
                elapsed_ms=elapsed_ms,
            )
            self._cycle_reports.append(report)

            if cycle_num < self.max_cycles and self.cycle_delay_seconds > 0:
                time.sleep(self.cycle_delay_seconds)

        return {
            "total_cycles": len(self._cycle_reports),
            "total_revenue": round(total_revenue, 2),
            "total_leads": total_leads,
            "cycles": [r.to_dict() for r in self._cycle_reports],
            "scaled_bots": all_scaled,
        }

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get_cycle_reports(self) -> List[CycleReport]:
        """Return all :class:`CycleReport` instances generated so far."""
        return list(self._cycle_reports)

    def total_revenue(self) -> float:
        """Return the cumulative revenue across all completed cycles."""
        return round(sum(r.revenue for r in self._cycle_reports), 2)

    def total_leads(self) -> int:
        """Return the cumulative lead count across all completed cycles."""
        return sum(r.leads for r in self._cycle_reports)
