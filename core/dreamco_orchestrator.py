"""
DreamCo Orchestrator — Central Brain

Wires every DreamCo bot together into a single revenue-validated,
auto-scaling pipeline:

    BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE

Usage
-----
    from core.dreamco_orchestrator import DreamCoOrchestrator

    orch = DreamCoOrchestrator()
    results = orch.run_all_bots()
"""

from __future__ import annotations

import importlib
import sys
import os
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Revenue Validator
# ---------------------------------------------------------------------------

SCALE_THRESHOLD: float = 1000.0   # USD — bots above this are cloned
MAINTAIN_THRESHOLD: float = 100.0  # USD — bots above this are kept


class RevenueValidator:
    """Validates a bot_output dict and returns a scoring result."""

    def validate(self, bot_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a bot's output dict.

        Parameters
        ----------
        bot_output : dict
            Must contain at least ``revenue`` and optionally
            ``conversion_rate`` and ``leads_generated``.

        Returns
        -------
        dict
            Keys: revenue, conversion_rate, leads_generated, status, scale, message
        """
        revenue: float = float(bot_output.get("revenue", 0))
        conversion_rate: float = float(bot_output.get("conversion_rate", 0.0))
        leads_generated: int = int(bot_output.get("leads_generated", 0))

        if revenue >= SCALE_THRESHOLD:
            status = "scale"
            scale = True
        elif revenue >= MAINTAIN_THRESHOLD:
            status = "maintain"
            scale = False
        else:
            status = "underperforming"
            scale = False

        return {
            "revenue": revenue,
            "conversion_rate": conversion_rate,
            "leads_generated": leads_generated,
            "status": status,
            "scale": scale,
            "message": (
                f"🚀 Revenue ${revenue:.2f} exceeded scale threshold"
                if scale
                else f"📊 Status: {status} (revenue: ${revenue:.2f})"
            ),
        }


# ---------------------------------------------------------------------------
# Auto Scaler
# ---------------------------------------------------------------------------


class AutoScaler:
    """Triggers cloning of profitable bots into new niches."""

    def clone_bot(self, bot_name: str) -> str:
        """Return a clone notification for *bot_name*."""
        return f"[AutoScaler] Cloning '{bot_name}' into new niche — deploying scaled instance"


# ---------------------------------------------------------------------------
# DreamCo Orchestrator
# ---------------------------------------------------------------------------


class DreamCoOrchestrator:
    """
    Central brain — runs bots, validates revenue, and auto-scales winners.

    Parameters
    ----------
    bots_root : str
        Python package root to resolve bot module paths (defaults to repo root).
    """

    def __init__(self, bots_root: Optional[str] = None) -> None:
        self.validator = RevenueValidator()
        self.scaler = AutoScaler()
        if bots_root:
            sys.path.insert(0, bots_root)

    # ------------------------------------------------------------------
    # Single-bot processing
    # ------------------------------------------------------------------

    def process_bot(self, bot_name: str, bot_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an already-executed bot's output and scale if warranted.

        Parameters
        ----------
        bot_name : str
            Human-readable label for the bot.
        bot_output : dict
            Dict with at minimum ``revenue`` key.

        Returns
        -------
        dict
            Validation result enriched with scaling info.
        """
        result = self.validator.validate(bot_output)
        print(f"[{bot_name}] → {result['message']}")

        if result["scale"]:
            print(self.scaler.clone_bot(bot_name))

        return result

    def run_bot(self, bot_path: str, bot_name: str) -> Dict[str, Any]:
        """
        Dynamically import *bot_path* (dotted module path or absolute file path),
        call its ``run()`` function, and process the returned output.

        Parameters
        ----------
        bot_path : str
            Either a dotted Python module path (e.g. ``bots.real_estate_bot.real_estate_bot``)
            or an absolute file system path to a ``.py`` file.
        bot_name : str
            Human-readable label used in log output.

        Returns
        -------
        dict
            ``{ bot, output, validation }`` on success or ``{ bot, error }`` on failure.
        """
        try:
            if os.path.isfile(bot_path):
                # File-path import -- handles directories with hyphens (e.g. government-contract-grant-bot)
                import importlib.util as _util
                spec = _util.spec_from_file_location(bot_name, bot_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot load spec from '{bot_path}'")
                module = _util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore[union-attr]
            else:
                module = importlib.import_module(bot_path)

            bot_output: Dict[str, Any] = module.run()  # type: ignore[attr-defined]

            validation = self.process_bot(bot_name, bot_output)

            return {
                "bot": bot_name,
                "output": bot_output,
                "validation": validation,
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {"bot": bot_name, "error": str(exc)}

    # ------------------------------------------------------------------
    # Full network run
    # ------------------------------------------------------------------

    def run_all_bots(self) -> List[Dict[str, Any]]:
        """
        Run all registered DreamCo bots and return collected results.

        Bots living in directories with hyphens are loaded via file path rather
        than dotted module names (Python identifiers cannot contain hyphens).
        Any bot that raises an exception is captured with an ``error`` key
        rather than crashing the whole run.

        Returns
        -------
        list of dict
        """
        # Determine repo root relative to this file
        _root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        bots: List[tuple[str, str]] = [
            # Core 7 bots required by the DreamCo God Mode spec
            (
                "bots.real_estate_bot.real_estate_bot",
                "real_estate_bot",
            ),
            (
                "bots.deal_finder_bot.deal_finder_bot",
                "deal_finder_bot",
            ),
            (
                "bots.revenue_engine_bot.revenue_engine_bot",
                "revenue_engine_bot",
            ),
            (
                "bots.dreamco_payments.dreamco_payments",
                "dreamco_payments",
            ),
            (
                "bots.multi_source_lead_scraper.lead_scraper",
                "multi_source_lead_scraper",
            ),
            (
                os.path.join(_root, "bots", "government-contract-grant-bot", "government_contract_grant_bot.py"),
                "gov_contract_grant_bot",
            ),
            (
                os.path.join(_root, "bots", "ai-models-integration", "ai_models_integration.py"),
                "ai_models_integration_bot",
            ),
            # Additional bots
            (
                os.path.join(_root, "bots", "ai-side-hustle-bots", "bot.py"),
                "side_hustle_bot",
            ),
            (
                os.path.join(_root, "bots", "selenium-job-application-bot", "bot.py"),
                "job_bot",
            ),
        ]

        results: List[Dict[str, Any]] = []
        for bot_path, bot_name in bots:
            results.append(self.run_bot(bot_path, bot_name))

        return results

    # ------------------------------------------------------------------
    # Summary helper
    # ------------------------------------------------------------------

    def summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from :meth:`run_all_bots` into a summary dict.

        Parameters
        ----------
        results : list of dict

        Returns
        -------
        dict
        """
        total_revenue = sum(
            float(r.get("output", {}).get("revenue", 0))
            for r in results
            if "output" in r and r["output"] is not None
        )
        total_leads = sum(
            int(r.get("output", {}).get("leads_generated", 0))
            for r in results
            if "output" in r and r["output"] is not None
        )
        scaling_bots = [
            r["bot"]
            for r in results
            if r.get("validation", {}) and r["validation"].get("scale")
        ]
        failed_bots = [r["bot"] for r in results if "error" in r]

        return {
            "total_revenue": round(total_revenue, 2),
            "total_leads": total_leads,
            "scaling_bots": scaling_bots,
            "failed_bots": failed_bots,
            "bots_run": len(results),
        }
