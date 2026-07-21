"""
DreamCo Scheduler — Auto-Run System

Runs the full DreamCo bot cycle on a configurable interval so bots
generate revenue continuously without manual intervention.

Usage
-----
    python -m core.scheduler             # runs every hour (default)
    python -m core.scheduler --interval 1800   # every 30 minutes
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from typing import Optional

from core.dreamco_orchestrator import DreamCoOrchestrator


class Scheduler:
    """
    Runs the DreamCo orchestrator on a fixed interval.

    Parameters
    ----------
    interval_seconds : int
        Seconds between each bot-cycle run (default: 3600 — hourly).
    max_cycles : int or None
        Maximum number of cycles to run.  ``None`` (default) runs forever.
    orchestrator : DreamCoOrchestrator or None
        Orchestrator instance to use.  A new one is created if not provided.
    """

    def __init__(
        self,
        interval_seconds: int = 3600,
        max_cycles: Optional[int] = None,
        orchestrator: Optional[DreamCoOrchestrator] = None,
    ) -> None:
        self.interval_seconds = interval_seconds
        self.max_cycles = max_cycles
        self.orchestrator = orchestrator or DreamCoOrchestrator()
        self._cycles_run: int = 0

    @property
    def cycles_run(self) -> int:
        """Number of cycles completed so far."""
        return self._cycles_run

    def run_cycle(self) -> dict:
        """Execute one full bot cycle and return the summary."""
        ts = datetime.now(timezone.utc).isoformat()
        print(f"\n[{ts}] Running DreamCo cycle #{self._cycles_run + 1}…")

        results = self.orchestrator.run_all_bots()
        summary = self.orchestrator.summary(results)
        self._cycles_run += 1

        print(
            f"[Cycle {self._cycles_run}] Complete — "
            f"Revenue: ${summary['total_revenue']}, "
            f"Leads: {summary['total_leads']}, "
            f"Scaling: {summary['scaling_bots'] or 'none'}"
        )
        return summary

    def run_forever(self) -> None:
        """Block and run cycles indefinitely (or until max_cycles is reached)."""
        print(
            f"⏱️  DreamCo Scheduler started — "
            f"interval: {self.interval_seconds}s, "
            f"max cycles: {self.max_cycles or '∞'}"
        )

        while True:
            self.run_cycle()

            if self.max_cycles is not None and self._cycles_run >= self.max_cycles:
                print(f"✅ Reached max cycles ({self.max_cycles}). Scheduler stopped.")
                break

            time.sleep(self.interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="DreamCo Scheduler")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Seconds between bot-cycle runs (default: 3600)",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Stop after N cycles (omit for infinite loop)",
    )
    args = parser.parse_args()

    scheduler = Scheduler(interval_seconds=args.interval, max_cycles=args.max_cycles)
    scheduler.run_forever()


if __name__ == "__main__":
    main()
