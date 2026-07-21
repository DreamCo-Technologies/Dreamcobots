"""
Money Engine — DreamCo Quantum Decision Bot.

Autonomous income scanning, ranking, and execution planning.  Scans across
multiple income domains, runs quantum scoring on each opportunity, and
returns a ranked action list so the user (or automated system) always knows
the highest-probability money move to execute next.

This is the "reality-testing engine before spending money" layer.
"""

from __future__ import annotations

from typing import List, Optional

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.quantum_decision_bot.quantum_engine import QuantumEngine
from bots.quantum_decision_bot.probability_model import ProbabilityModel


# ---------------------------------------------------------------------------
# Opportunity catalogue
# ---------------------------------------------------------------------------

_DEFAULT_OPPORTUNITIES = [
    {
        "id": "local_biz_ai_marketing",
        "type": "service",
        "name": "Local Business AI Marketing Package",
        "description": "Offer AI-powered marketing automation to local businesses",
        "base_profit": 1_500,
        "risk": 3.0,
        "volatility": 0.15,
        "time_to_revenue_days": 7,
        "effort": "low",
    },
    {
        "id": "saas_subscription",
        "type": "saas",
        "name": "SaaS Subscription Product",
        "description": "Launch a monthly SaaS product with recurring revenue",
        "base_profit": 5_000,
        "risk": 6.0,
        "volatility": 0.3,
        "time_to_revenue_days": 30,
        "effort": "high",
    },
    {
        "id": "real_estate_flip",
        "type": "real_estate",
        "name": "Fix & Flip Property",
        "description": "Buy, renovate, and sell a residential property",
        "base_profit": 40_000,
        "risk": 7.0,
        "volatility": 0.35,
        "time_to_revenue_days": 90,
        "effort": "high",
    },
    {
        "id": "affiliate_funnel",
        "type": "affiliate",
        "name": "Affiliate Marketing Funnel",
        "description": "Build a traffic funnel targeting high-commission affiliate offers",
        "base_profit": 800,
        "risk": 2.0,
        "volatility": 0.2,
        "time_to_revenue_days": 14,
        "effort": "medium",
    },
    {
        "id": "content_automation",
        "type": "content",
        "name": "Content Automation System",
        "description": "Sell content creation automation to creators and brands",
        "base_profit": 2_000,
        "risk": 3.5,
        "volatility": 0.2,
        "time_to_revenue_days": 10,
        "effort": "low",
    },
    {
        "id": "lead_gen_service",
        "type": "service",
        "name": "Lead Generation Service",
        "description": "Provide qualified leads to businesses via automated scrapers",
        "base_profit": 1_200,
        "risk": 3.0,
        "volatility": 0.15,
        "time_to_revenue_days": 5,
        "effort": "low",
    },
    {
        "id": "crypto_trading",
        "type": "trading",
        "name": "Crypto Trading Bot Deployment",
        "description": "Deploy algorithmic trading bot on a crypto exchange",
        "base_profit": 3_000,
        "risk": 8.5,
        "volatility": 0.5,
        "time_to_revenue_days": 7,
        "effort": "medium",
    },
    {
        "id": "digital_product",
        "type": "digital",
        "name": "Digital Product (Course / Template)",
        "description": "Create and sell a high-value digital product or course",
        "base_profit": 3_500,
        "risk": 2.5,
        "volatility": 0.25,
        "time_to_revenue_days": 21,
        "effort": "medium",
    },
]


# ---------------------------------------------------------------------------
# MoneyEngine
# ---------------------------------------------------------------------------

class MoneyEngine:
    """
    Autonomous money / opportunity scanner.

    Scans a catalogue of income opportunities, runs quantum scoring on each,
    and returns a ranked action plan ordered by score (best first).

    Parameters
    ----------
    engine : QuantumEngine, optional
        Shared quantum engine for scoring opportunities.
    """

    def __init__(self, engine: Optional[QuantumEngine] = None) -> None:
        self.engine = engine or QuantumEngine()
        self._custom_opportunities: List[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_opportunity(self, opportunity: dict) -> None:
        """Add a custom income opportunity to the scanner."""
        self._custom_opportunities.append(opportunity)

    def scan(self, filter_type: Optional[str] = None, top_n: int = 5) -> dict:
        """
        Scan all opportunities, score them, and return ranked results.

        Parameters
        ----------
        filter_type : str, optional
            If provided, only opportunities matching ``type == filter_type``
            are included.
        top_n : int
            Return the top-N ranked opportunities (default 5).

        Returns
        -------
        dict
            Keys: ``ranked_opportunities``, ``top_opportunity``,
            ``total_scanned``.
        """
        all_opps = list(_DEFAULT_OPPORTUNITIES) + self._custom_opportunities

        if filter_type:
            all_opps = [o for o in all_opps if o.get("type") == filter_type]

        scored: List[dict] = []
        for opp in all_opps:
            context = {
                "base_profit": opp["base_profit"],
                "risk": opp["risk"],
                "volatility": opp.get("volatility", 0.2),
            }
            result = self.engine.decide(context)
            best = result["best_path"]
            scored.append({
                **opp,
                "quantum_score": best["score"],
                "probability_of_profit": best["probability_of_profit"],
                "recommended_action": self._build_action(opp, best),
            })

        scored.sort(key=lambda x: x["quantum_score"], reverse=True)
        ranked = scored[:top_n]

        return {
            "total_scanned": len(all_opps),
            "top_opportunity": ranked[0] if ranked else None,
            "ranked_opportunities": ranked,
        }

    def execute_plan(self, opportunity: dict) -> dict:
        """
        Generate an execution plan for a single opportunity.

        Returns a step-by-step action plan tailored to the opportunity type.
        """
        opp_type = opportunity.get("type", "default")
        name = opportunity.get("name", "Opportunity")
        profit = opportunity.get("base_profit", 0)
        risk = opportunity.get("risk", 5.0)

        steps = _EXECUTION_STEPS.get(opp_type, _EXECUTION_STEPS["default"])

        return {
            "opportunity": name,
            "type": opp_type,
            "projected_profit": profit,
            "risk_level": risk,
            "execution_steps": steps,
            "estimated_days": opportunity.get("time_to_revenue_days", 30),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _build_action(opp: dict, best_path: dict) -> str:
        name = opp.get("name", "this opportunity")
        scenario = best_path.get("scenario", "moderate")
        prob = round(best_path.get("probability_of_profit", 0) * 100, 1)
        return f"Execute '{name}' via {scenario} path — {prob}% profit probability"


# ---------------------------------------------------------------------------
# Execution step templates
# ---------------------------------------------------------------------------

_EXECUTION_STEPS: dict = {
    "service": [
        "Identify 10 target clients in your niche",
        "Craft a one-page AI service proposal",
        "Reach out via DM, email, or cold call",
        "Deliver a free audit or demo to warm prospects",
        "Close at $500–$2000/month retainer",
    ],
    "saas": [
        "Define core problem and MVP feature set",
        "Build a landing page and collect pre-signups",
        "Develop MVP in 2–4 weeks",
        "Launch to pre-signup list",
        "Iterate based on first 10 paying users",
    ],
    "real_estate": [
        "Identify target market and deal criteria",
        "Run Quantum simulation on 5 candidate properties",
        "Secure financing (hard money / private lender)",
        "Execute renovation within budget",
        "List and close within target timeline",
    ],
    "affiliate": [
        "Select 3 high-commission affiliate programs",
        "Build content funnel (blog / YouTube / TikTok)",
        "Drive organic traffic to funnel",
        "A/B test CTAs and offers",
        "Scale winning traffic channel",
    ],
    "content": [
        "Identify content type in demand (video / written / design)",
        "Build automation workflow using AI tools",
        "Package as a done-for-you service",
        "Outreach to 20 potential clients",
        "Deliver and upsell monthly retainer",
    ],
    "trading": [
        "Configure bot strategy parameters",
        "Paper trade for 7 days to validate performance",
        "Allocate small starting capital",
        "Monitor daily and adjust thresholds",
        "Scale capital based on verified returns",
    ],
    "digital": [
        "Identify high-value knowledge gap in your niche",
        "Outline and record/write the digital product",
        "Set up sales page and payment link",
        "Promote to existing audience or paid ads",
        "Automate delivery and upsell sequence",
    ],
    "default": [
        "Research opportunity in detail",
        "Run Quantum simulation to validate",
        "Build minimal viable execution plan",
        "Execute first step within 24 hours",
        "Track and optimise based on results",
    ],
}
