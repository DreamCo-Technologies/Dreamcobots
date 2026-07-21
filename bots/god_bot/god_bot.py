"""
God Bot — Master Controller

Central orchestrator that manages all individual DreamCo bot operations,
aggregates leads and revenue metrics, and automates the monetization pipeline.

Usage
-----
    from bots.god_bot.god_bot import GodBot

    god = GodBot()
    summary = god.run_all()   # run once
    god.start(interval_minutes=10)  # run every 10 minutes (blocking)
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401 - framework compliance marker

import importlib.util as _util
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Metrics store
# ---------------------------------------------------------------------------

_metrics_store: List[Dict[str, Any]] = []


def save_metrics(result: Dict[str, Any]) -> None:
    """Persist *result* to the in-process metrics store.

    Each entry is timestamped at the moment it is saved.  In production this
    can be replaced by a database write or an API call.
    """
    _metrics_store.append({**result, "saved_at": datetime.now(timezone.utc).isoformat()})


def get_metrics() -> List[Dict[str, Any]]:
    """Return all saved metrics entries."""
    return list(_metrics_store)


# ---------------------------------------------------------------------------
# Bot registry
# ---------------------------------------------------------------------------

# Each entry is (module_path_or_file, bot_name)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BOT_REGISTRY: List[tuple[str, str]] = [
    (
        os.path.join(_ROOT, "bots", "government-contract-grant-bot", "government_contract_grant_bot.py"),
        "gov_bot",
    ),
    (
        "bots.real_estate_bot.real_estate_bot",
        "real_estate_bot",
    ),
    (
        os.path.join(_ROOT, "bots", "ai-side-hustle-bots", "bot.py"),
        "side_hustle_bot",
    ),
    (
        os.path.join(_ROOT, "bots", "selenium-job-application-bot", "bot.py"),
        "job_bot",
    ),
]


# ---------------------------------------------------------------------------
# God Bot
# ---------------------------------------------------------------------------


class GodBot:
    """Master controller that oversees all individual bot operations.

    Parameters
    ----------
    registry : list of (str, str), optional
        Custom bot registry in the format [(module_path, bot_name), ...].
        Defaults to :data:`BOT_REGISTRY`.
    """

    def __init__(self, registry: Optional[List[tuple[str, str]]] = None) -> None:
        self.registry = registry if registry is not None else BOT_REGISTRY
        sys.path.insert(0, _ROOT)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_and_run(self, bot_path: str, bot_name: str) -> Dict[str, Any]:
        """Import *bot_path* and call its module-level ``run()`` function.

        Returns a dict with ``bot``, ``result`` (the run output), and any
        ``error`` on failure.
        """
        try:
            if os.path.isfile(bot_path):
                spec = _util.spec_from_file_location(bot_name, bot_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot load spec from '{bot_path}'")
                module = _util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore[union-attr]
            else:
                import importlib
                module = importlib.import_module(bot_path)

            result: Dict[str, Any] = module.run()  # type: ignore[attr-defined]
            return {"bot": bot_name, "result": result}
        except Exception as exc:  # pylint: disable=broad-except
            return {"bot": bot_name, "error": str(exc)}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_all(self) -> Dict[str, Any]:
        """Run every registered bot once and return an aggregated summary.

        Returns
        -------
        dict
            Keys: ``total_revenue``, ``total_leads``, ``bots_run``,
            ``failed_bots``, ``results``.
        """
        total_revenue = 0
        total_leads = 0
        results: List[Dict[str, Any]] = []
        failed_bots: List[str] = []

        for bot_path, bot_name in self.registry:
            entry = self._load_and_run(bot_path, bot_name)
            results.append(entry)

            if "error" in entry:
                failed_bots.append(bot_name)
            else:
                bot_result = entry.get("result", {})
                total_revenue += bot_result.get("revenue", 0)
                # Support both "leads" and "leads_generated" keys
                total_leads += bot_result.get("leads_generated", bot_result.get("leads", 0))
                save_metrics({**bot_result, "bot": bot_name})

        summary: Dict[str, Any] = {
            "total_revenue": total_revenue,
            "total_leads": total_leads,
            "bots_run": len(self.registry),
            "failed_bots": failed_bots,
            "results": results,
        }
        print(
            f"[GodBot] Cycle complete — "
            f"revenue=${total_revenue} | leads={total_leads} | "
            f"failed={len(failed_bots)}"
        )
        return summary

    def start(self, interval_minutes: int = 10, max_cycles: Optional[int] = None) -> None:
        """Run all bots on a recurring schedule.

        Parameters
        ----------
        interval_minutes : int
            How often (in minutes) to run the full bot suite. Default 10.
        max_cycles : int, optional
            If set, stop after this many cycles. Useful for testing.
        """
        interval_seconds = interval_minutes * 60
        cycles = 0

        print(f"[GodBot] Starting scheduler — interval={interval_minutes}min")

        while True:
            self.run_all()
            cycles += 1

            if max_cycles is not None and cycles >= max_cycles:
                print(f"[GodBot] Reached max_cycles={max_cycles}. Stopping.")
                break

            time.sleep(interval_seconds)


# ---------------------------------------------------------------------------
# Module-level run() — DreamCo OS orchestrator interface
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Runs all registered bots once and returns the aggregated summary.
    """
    god = GodBot()
    return god.run_all()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    god = GodBot()
    god.start(interval_minutes=10)
