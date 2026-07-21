"""
Bot Router — DreamCo Quantum Decision Bot.

Implements the Quantum Entanglement concept: every bot in the DreamCo
network is a node that can route decisions through the Quantum Engine.
When one bot finds an opportunity, all connected bots instantly update
their strategies to reflect the new best-path reality.

Each bot call returns an optimised action plan specific to that bot's
domain, derived from the shared quantum scoring result.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.quantum_decision_bot.quantum_engine import QuantumEngine
from bots.quantum_decision_bot.probability_model import ProbabilityModel


# ---------------------------------------------------------------------------
# Action templates per bot type
# ---------------------------------------------------------------------------

_BOT_ACTION_TEMPLATES: Dict[str, List[str]] = {
    "real_estate_bot": [
        "Analyse target property for {scenario} scenario",
        "Adjust financing strategy to match risk level {risk}",
        "Update exit strategy for {scenario} outcome",
        "Alert buyer network for properties matching {scenario} profile",
    ],
    "trade_bot": [
        "Recalibrate position sizing for {scenario} scenario",
        "Update stop-loss thresholds based on risk {risk}",
        "Scan for entry signals aligned with {scenario} path",
    ],
    "hustle_bot": [
        "Prioritise income streams matching {scenario} profile",
        "Redirect effort toward highest-probability hustles",
        "Scale winning activities in {scenario} direction",
    ],
    "money_bot": [
        "Redirect cash flow to {scenario} opportunity",
        "Adjust budget allocation for risk level {risk}",
        "Trigger opportunity scanner for {scenario} type",
    ],
    "saas_bot": [
        "Adjust pricing model for {scenario} market conditions",
        "Scale marketing spend toward {scenario} channels",
        "Update product roadmap priority for {scenario} outcome",
    ],
    "grant_bot": [
        "Filter grant opportunities for {scenario} risk tolerance",
        "Prioritise applications with highest success probability",
    ],
    "default": [
        "Execute {scenario} strategy",
        "Monitor performance against {scenario} projections",
        "Adjust parameters for risk level {risk}",
    ],
}


def _build_actions(bot_name: str, best_path: dict) -> List[str]:
    """Format action strings for *bot_name* based on *best_path*."""
    template_key = bot_name.lower()
    templates = _BOT_ACTION_TEMPLATES.get(template_key, _BOT_ACTION_TEMPLATES["default"])
    scenario = best_path.get("scenario", "moderate")
    risk = round(best_path.get("risk", 5.0), 1)
    return [t.format(scenario=scenario, risk=risk) for t in templates]


# ---------------------------------------------------------------------------
# BotRouter
# ---------------------------------------------------------------------------

class BotRouter:
    """
    Routes decisions for any named bot through the shared Quantum Engine.

    All bots share the same engine instance so a decision for one bot
    immediately reflects the latest probability model state — simulating
    quantum entanglement across the network.

    Parameters
    ----------
    engine : QuantumEngine, optional
        Shared engine instance.  If None, one is created automatically.
    """

    def __init__(self, engine: Optional[QuantumEngine] = None) -> None:
        self.engine = engine or QuantumEngine()
        self._routing_log: List[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, bot_name: str, context: dict) -> dict:
        """
        Run a quantum decision for *bot_name* with *context* and return an
        action plan tailored to that bot.

        Parameters
        ----------
        bot_name : str
            Name of the bot requesting a decision (e.g. ``"real_estate_bot"``).
        context : dict
            Decision context forwarded to the Quantum Engine.

        Returns
        -------
        dict
            Keys:
            - ``bot``         — bot name
            - ``decision``    — best quantum path result
            - ``next_actions``— ordered list of recommended actions
            - ``alternatives``— top alternative paths
            - ``risk_warning``— worst-case scenario details
        """
        result = self.engine.decide(context)
        best = result["best_path"]
        actions = _build_actions(bot_name, best)

        entry = {
            "bot": bot_name,
            "decision": best,
            "next_actions": actions,
            "alternatives": result["alternatives"],
            "risk_warning": result["worst_case"],
        }
        self._routing_log.append({"bot": bot_name, "score": best.get("score", 0)})
        return entry

    def route_all(self, bot_contexts: Dict[str, dict]) -> List[dict]:
        """
        Route multiple bots simultaneously — simulating entangled updates.

        Parameters
        ----------
        bot_contexts : dict
            Mapping of ``{bot_name: context_dict}``.

        Returns
        -------
        list[dict]
            Ordered list of routing results for each bot.
        """
        return [self.route(name, ctx) for name, ctx in bot_contexts.items()]

    def get_routing_log(self) -> List[dict]:
        """Return a log of all routing calls made through this router."""
        return list(self._routing_log)

    def network_status(self) -> dict:
        """Return a snapshot of the bot network state."""
        bots_routed = list({e["bot"] for e in self._routing_log})
        avg_score = (
            round(sum(e["score"] for e in self._routing_log) / len(self._routing_log), 4)
            if self._routing_log
            else 0.0
        )
        return {
            "total_routing_calls": len(self._routing_log),
            "unique_bots": len(bots_routed),
            "bots_active": bots_routed,
            "avg_decision_score": avg_score,
        }
