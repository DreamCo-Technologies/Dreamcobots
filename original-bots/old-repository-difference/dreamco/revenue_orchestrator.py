"""
RevenueOrchestrator — Autonomous revenue brain for DreamCobots.

Ranks bots by profitability, allocates the daily API budget proportionally,
executes the top earners, and records every decision to the
GlobalLearningLoop so the system can self-improve over time.

Usage
-----
    from dreamco.revenue_orchestrator import orchestrator

    # Run a single profitable cycle (blocking)
    import asyncio
    asyncio.run(orchestrator.run_profitable_bots())

    # Run continuously until interrupted
    asyncio.run(orchestrator.run_continuous())
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path bootstrap (allows running as __main__)
# ---------------------------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Optional imports (gracefully degraded)
# ---------------------------------------------------------------------------

try:
    from config.config_manager import config as _master_config
except Exception:
    _master_config = None  # type: ignore[assignment]

try:
    from global_learning_system.learning_loop import BotDecision, learning_loop as _learning_loop
except Exception:
    _learning_loop = None  # type: ignore[assignment]
    BotDecision = None  # type: ignore[assignment]


def _cfg(key: str, default: Any) -> Any:
    if _master_config is not None:
        return _master_config.get(key, default)
    return default


# ---------------------------------------------------------------------------
# BotInstance
# ---------------------------------------------------------------------------


@dataclass
class BotInstance:
    """Lightweight descriptor for a bot registered with the orchestrator."""

    name: str
    category: str = "general"
    status: str = "idle"
    profit_7d: float = 0.0
    runs_total: int = 0
    runs_success: int = 0
    budget_allocated: float = 0.0
    runner: Optional[Callable[..., Any]] = field(default=None, repr=False)

    @property
    def success_rate(self) -> float:
        if self.runs_total == 0:
            return 1.0
        return self.runs_success / self.runs_total

    @property
    def priority(self) -> int:
        """Lower number = higher priority (from master config)."""
        priorities: Dict[str, int] = _cfg("bot_priorities", {}) or {}
        return priorities.get(self.category, 99)


# ---------------------------------------------------------------------------
# RevenueOrchestrator
# ---------------------------------------------------------------------------


class RevenueOrchestrator:
    """
    Central revenue orchestrator.

    Responsibilities
    ----------------
    1. Maintain a registry of bot instances.
    2. Rank bots by profit, priority, and success rate.
    3. Allocate the daily API budget across the top earners.
    4. Execute bots asynchronously and record outcomes to the learning loop.
    5. Expose a continuous-run mode for the GitHub Actions CI loop.
    """

    def __init__(self) -> None:
        self._bots: Dict[str, BotInstance] = {}
        self.total_profit_today: float = 0.0
        self._cycle_count: int = 0
        self._register_bots()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_bots(self) -> None:
        """
        Auto-register bots from known categories.

        Extend this method (or call ``register_bot``) to wire in real runners.
        """
        default_categories = [
            ("trading_bot", "trading"),
            ("job_application_bot", "job_application"),
            ("content_generation_bot", "content_generation"),
            ("government_contracts_bot", "government_contracts"),
        ]
        for name, category in default_categories:
            self.register_bot(name, category=category)

    def register_bot(
        self,
        name: str,
        *,
        category: str = "general",
        runner: Optional[Callable[..., Any]] = None,
        initial_profit_7d: float = 0.0,
    ) -> BotInstance:
        """Add a bot to the orchestrator registry."""
        bot = BotInstance(
            name=name,
            category=category,
            profit_7d=initial_profit_7d,
            runner=runner,
        )
        self._bots[name] = bot
        logger.debug("Registered bot: %s (category=%s)", name, category)
        return bot

    # ------------------------------------------------------------------
    # Ranking & budget allocation
    # ------------------------------------------------------------------

    def ranked_bots(self) -> List[BotInstance]:
        """
        Return bots sorted by (priority ASC, profit_7d DESC, success_rate DESC).

        Lower priority number wins; ties broken by recent profit, then
        success rate.
        """
        return sorted(
            self._bots.values(),
            key=lambda b: (b.priority, -b.profit_7d, -b.success_rate),
        )

    def allocate_budgets(self) -> None:
        """Distribute ``resource_allocation.max_api_budget_daily`` across bots."""
        daily_budget: float = float(_cfg("resource_allocation.max_api_budget_daily", 200.0))
        ranked = self.ranked_bots()
        n = len(ranked)
        if n == 0:
            return
        # Simple equal-weight allocation; could be improved with weighted shares.
        per_bot = round(daily_budget / n, 2)
        for bot in ranked:
            bot.budget_allocated = per_bot

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def _run_bot_async(self, bot: BotInstance) -> Dict[str, Any]:
        """Execute a single bot and return a result dict."""
        import hashlib
        import time

        decision_id = hashlib.md5(
            f"{bot.name}:{time.time()}".encode()
        ).hexdigest()

        bot.status = "running"
        start = datetime.now(tz=timezone.utc)
        result: Dict[str, Any] = {}
        success = False
        revenue = 0.0

        try:
            if bot.runner is not None:
                raw = bot.runner(bot.name, "")
                if asyncio.iscoroutine(raw):
                    raw = await raw
                result = raw if isinstance(raw, dict) else {"output": raw}
                revenue = float(result.get("revenue_usd", 0.0))
            else:
                # Stub — no real runner attached yet
                result = {"output": f"stub run for {bot.name}"}

            success = True
            bot.runs_success += 1
            self.total_profit_today += revenue

        except Exception as exc:
            logger.exception("Bot %s raised an error: %s", bot.name, exc)
            result = {"error": str(exc)}

        finally:
            bot.runs_total += 1
            bot.status = "idle"

        elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()

        # Record to learning loop if available
        if _learning_loop is not None and BotDecision is not None:
            decision = BotDecision(
                decision_id=decision_id,
                bot_name=bot.name,
                action_type="bot_run",
                action_params={"budget": bot.budget_allocated},
                context={"cycle": self._cycle_count},
                prediction=bot.success_rate,
            )
            _learning_loop.record_decision(decision)
            _learning_loop.record_outcome(
                decision_id,
                actual_outcome=1.0 if success else 0.0,
                reward=revenue,
            )

        return {
            "bot_name": bot.name,
            "success": success,
            "revenue_usd": revenue,
            "elapsed_s": round(elapsed, 3),
            "result": result,
        }

    async def run_profitable_bots(self) -> List[Dict[str, Any]]:
        """
        Execute one orchestration cycle:

        1. Allocate budgets.
        2. Run all registered bots concurrently.
        3. Return per-bot result dicts.
        """
        self._cycle_count += 1
        self.allocate_budgets()
        ranked = self.ranked_bots()

        logger.info(
            "Cycle %d — running %d bots (daily profit so far: $%.2f)",
            self._cycle_count,
            len(ranked),
            self.total_profit_today,
        )

        tasks = [self._run_bot_async(bot) for bot in ranked]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return list(results)

    async def run_continuous(self, interval_seconds: int = 900) -> None:
        """
        Run orchestration cycles indefinitely, sleeping *interval_seconds*
        between each cycle (default 15 minutes, matching the GitHub Actions cron).
        """
        logger.info("RevenueOrchestrator entering continuous mode (interval=%ds)", interval_seconds)
        while True:
            try:
                results = await self.run_profitable_bots()
                successes = sum(1 for r in results if r.get("success"))
                total_rev = sum(r.get("revenue_usd", 0.0) for r in results)
                logger.info(
                    "Cycle %d complete — %d/%d succeeded, $%.2f revenue",
                    self._cycle_count,
                    successes,
                    len(results),
                    total_rev,
                )
            except Exception:
                logger.exception("Unhandled error in orchestration cycle")

            await asyncio.sleep(interval_seconds)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a lightweight status snapshot."""
        return {
            "orchestrator": "RevenueOrchestrator",
            "registered_bots": len(self._bots),
            "cycle_count": self._cycle_count,
            "total_profit_today_usd": round(self.total_profit_today, 2),
            "profit_target_daily_usd": _cfg("profit_targets.daily", 500.0),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }

    def summary(self) -> List[Dict[str, Any]]:
        """Return per-bot performance summary."""
        return [
            {
                "name": b.name,
                "category": b.category,
                "status": b.status,
                "profit_7d": b.profit_7d,
                "runs_total": b.runs_total,
                "runs_success": b.runs_success,
                "success_rate": round(b.success_rate, 3),
                "budget_allocated": b.budget_allocated,
                "priority": b.priority,
            }
            for b in self.ranked_bots()
        ]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

orchestrator = RevenueOrchestrator()

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(orchestrator.run_continuous())
