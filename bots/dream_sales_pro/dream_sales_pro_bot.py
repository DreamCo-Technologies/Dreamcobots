"""
DreamSalesPro Division Module — Main bot implementation.

Provides:
  - DreamSalesProBot: orchestrates all DreamSalesPro automation tasks.
  - Automation hooks for lead generation, campaign execution, revenue
    simulation, pipeline management, and white-label client onboarding.
  - Integration with the DreamCo payment system for SaaS/Enterprise billing.

Usage
-----
    from bots.dream_sales_pro.dream_sales_pro_bot import DreamSalesProBot
    from bots.dream_sales_pro.tiers import DSPtier

    bot = DreamSalesProBot(tier=DSPtier.ENTERPRISE)
    print(bot.run())
    print(bot.generate_leads(icp={"industry": "SaaS", "size": "50-200"}, count=10))
    print(bot.simulate_revenue(mrr=50000, growth_rate=0.15, months=12))
    print(bot.execute_outreach_campaign(campaign_id="CAMP-001"))

Developer notes
---------------
- All public methods return plain dicts for JSON serialisation.
- ``run()`` is required by the Dreamcobots framework.
- Revenue simulation uses a deterministic model; wire it to your CRM/billing
  system in production for real ARR/MRR data.
- To add a new automation task, add a method and update AUTOMATION_REGISTRY.
"""
# GLOBAL AI SOURCES FLOW

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.dream_sales_pro.tiers import DSPtier, get_tier_config, get_upgrade_path

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

_MODULE_DIR = Path(__file__).parent
_REPO_ROOT = _MODULE_DIR.parent.parent
_BOTS_JSON = _REPO_ROOT / "divisions" / "DreamSalesPro" / "bots.json"


def _load_bots() -> List[Dict[str, Any]]:
    """Load the DreamSalesPro bot catalogue from JSON.

    Returns an empty list on any read/parse error (graceful degradation).
    """
    try:
        with open(_BOTS_JSON, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class DSPAccessError(PermissionError):
    """Raised when a feature requires a higher tier."""


# ---------------------------------------------------------------------------
# DreamSalesProBot
# ---------------------------------------------------------------------------


class DreamSalesProBot:
    """
    Orchestrates DreamSalesPro division automation tasks.

    Parameters
    ----------
    tier : DSPtier
        Subscription tier.  Defaults to PRO.
    """

    def __init__(self, tier: DSPtier = DSPtier.PRO) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._bots: List[Dict[str, Any]] = _load_bots()

    # ------------------------------------------------------------------
    # Framework-required method
    # ------------------------------------------------------------------

    def run(self) -> str:
        """
        Execute a lightweight status check.

        Required by the Dreamcobots framework (tools/check_bot_framework.py).
        Returns a human-readable status string.
        """
        bot_count = len(self._bots)
        categories = {b["category"] for b in self._bots}
        return (
            f"DreamSalesProBot [{self.tier.value}] running. "
            f"Catalogue: {bot_count} bots across {len(categories)} categories. "
            f"White-label: {self.config.has_feature('white_label_saas')}."
        )

    # ------------------------------------------------------------------
    # Catalogue helpers
    # ------------------------------------------------------------------

    def list_bots(
        self,
        category: Optional[str] = None,
        tier_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return all bots, optionally filtered by category and/or tier."""
        results = list(self._bots)
        if category:
            results = [
                b for b in results if category.lower() in b.get("category", "").lower()
            ]
        if tier_filter:
            results = [b for b in results if b.get("tier") == tier_filter]
        return results

    def get_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Return a single bot by its botId, or None if not found."""
        for bot in self._bots:
            if bot.get("botId") == bot_id:
                return bot
        return None

    def list_categories(self) -> List[str]:
        """Return all unique category names, sorted alphabetically."""
        return sorted({b["category"] for b in self._bots})

    # ------------------------------------------------------------------
    # Lead generation
    # ------------------------------------------------------------------

    def generate_leads(
        self,
        icp: Dict[str, Any],
        count: int = 10,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Simulate multi-source lead generation based on an ICP profile.

        In production, wire this to your lead scraper API(s): LinkedIn,
        Apollo, ZoomInfo, Hunter.io, or custom scrapers.

        Parameters
        ----------
        icp : dict
            Ideal Customer Profile attributes (industry, size, title, etc.).
        count : int
            Number of leads to generate.
        sources : list[str] | None
            Data sources to query.  Defaults to core sources.

        Returns
        -------
        dict
            Lead list with verification scores and enrichment data.
        """
        self._require_feature("lead_scraping")

        if sources is None:
            sources = ["LinkedIn", "Apollo", "Google Maps", "Crunchbase"]

        rng = random.Random(str(icp) + str(count))
        industries = [
            icp.get("industry", "SaaS"),
            "FinTech",
            "PropTech",
            "E-Commerce",
            "Healthcare IT",
        ]
        titles = ["CEO", "VP Sales", "Director of Growth", "Head of Revenue", "CRO"]

        leads = [
            {
                "lead_id": f"DSP-LEAD-{rng.randint(10000, 99999)}",
                "first_name": rng.choice(["Jordan", "Alex", "Taylor", "Morgan", "Casey"]),
                "last_name": rng.choice(["Smith", "Johnson", "Williams", "Brown", "Davis"]),
                "title": rng.choice(titles),
                "company": f"{rng.choice(['Apex', 'Nova', 'Peak', 'Crest', 'Vibe'])} {rng.choice(industries)}",
                "industry": rng.choice(industries),
                "email_confidence": rng.randint(75, 99),
                "source": rng.choice(sources),
                "intent_score": rng.randint(60, 100),
                "verified": rng.random() > 0.15,
            }
            for _ in range(count)
        ]

        return {
            "division": "DreamSalesPro",
            "task": "lead_generation",
            "icp": icp,
            "sources": sources,
            "leads_generated": len(leads),
            "leads": leads,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Campaign execution
    # ------------------------------------------------------------------

    def execute_outreach_campaign(
        self,
        campaign_id: str,
        channels: Optional[List[str]] = None,
        max_sends: int = 500,
    ) -> Dict[str, Any]:
        """
        Execute a multi-channel outreach campaign.

        In production, integrate with your email/SMS/LinkedIn APIs:
        SendGrid, Twilio, LinkedIn Sales Navigator, Salesloft, etc.

        Parameters
        ----------
        campaign_id : str
            Unique campaign identifier.
        channels : list[str] | None
            Channels to use.  Defaults to email + LinkedIn.
        max_sends : int
            Maximum sends per channel (budget cap).

        Returns
        -------
        dict
            Campaign execution summary with simulated delivery metrics.
        """
        self._require_feature("cold_email_sequences")

        if channels is None:
            channels = ["email", "linkedin"]

        rng = random.Random(campaign_id)
        channel_results = {}
        for channel in channels:
            sent = min(max_sends, rng.randint(int(max_sends * 0.7), max_sends))
            delivered = int(sent * rng.uniform(0.92, 0.99))
            opened = int(delivered * rng.uniform(0.18, 0.35))
            replied = int(opened * rng.uniform(0.05, 0.15))
            channel_results[channel] = {
                "sent": sent,
                "delivered": delivered,
                "opened": opened,
                "replied": replied,
                "open_rate_pct": round(opened / delivered * 100, 1) if delivered else 0,
                "reply_rate_pct": round(replied / delivered * 100, 1) if delivered else 0,
            }

        return {
            "division": "DreamSalesPro",
            "task": "outreach_campaign",
            "campaign_id": campaign_id,
            "channels": channels,
            "results": channel_results,
            "status": "executed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Revenue simulation
    # ------------------------------------------------------------------

    def simulate_revenue(
        self,
        mrr: float,
        growth_rate: float,
        months: int = 12,
        churn_rate: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Simulate MRR/ARR growth with churn over a given period.

        This is a deterministic compound-growth model.  Wire it to your
        actual billing system (Stripe, Chargebee) in production.

        Parameters
        ----------
        mrr : float
            Starting Monthly Recurring Revenue in USD.
        growth_rate : float
            Monthly growth rate as a decimal (e.g. 0.15 = 15%).
        months : int
            Number of months to simulate.
        churn_rate : float
            Monthly churn rate as a decimal (e.g. 0.05 = 5%).

        Returns
        -------
        dict
            Month-by-month MRR projections and ARR summary.
        """
        self._require_feature("saas_subscription")

        if months < 1:
            raise ValueError("months must be at least 1")
        if not (0.0 <= churn_rate < 1.0):
            raise ValueError("churn_rate must be between 0.0 and 1.0")

        projections = []
        current_mrr = mrr
        for month in range(1, months + 1):
            new_revenue = current_mrr * growth_rate
            churned = current_mrr * churn_rate
            current_mrr = current_mrr + new_revenue - churned
            projections.append(
                {
                    "month": month,
                    "mrr_usd": round(current_mrr, 2),
                    "new_revenue_usd": round(new_revenue, 2),
                    "churned_usd": round(churned, 2),
                    "net_new_usd": round(new_revenue - churned, 2),
                }
            )

        final_mrr = projections[-1]["mrr_usd"]
        arr = round(final_mrr * 12, 2)
        total_revenue = round(sum(p["mrr_usd"] for p in projections), 2)

        return {
            "division": "DreamSalesPro",
            "task": "revenue_simulation",
            "inputs": {
                "starting_mrr_usd": mrr,
                "monthly_growth_rate": growth_rate,
                "monthly_churn_rate": churn_rate,
                "months": months,
            },
            "projections": projections,
            "summary": {
                "final_mrr_usd": final_mrr,
                "arr_usd": arr,
                "total_revenue_usd": total_revenue,
                "growth_multiplier": round(final_mrr / mrr, 2) if mrr else 0,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Pipeline management
    # ------------------------------------------------------------------

    def get_pipeline_summary(
        self,
        pipeline_id: str,
        stages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a pipeline health summary for a given pipeline.

        Parameters
        ----------
        pipeline_id : str
            Unique pipeline identifier.
        stages : list[str] | None
            Pipeline stage names.  Defaults to standard sales stages.

        Returns
        -------
        dict
            Pipeline summary with deal counts and weighted value.
        """
        self._require_feature("pipeline_management")

        if stages is None:
            stages = [
                "Prospecting",
                "Qualification",
                "Demo",
                "Proposal",
                "Negotiation",
                "Closed Won",
                "Closed Lost",
            ]

        rng = random.Random(pipeline_id)
        stage_data = []
        for stage in stages:
            deals = rng.randint(2, 20)
            avg_value = rng.randint(5_000, 100_000)
            prob = rng.randint(10, 95)
            stage_data.append(
                {
                    "stage": stage,
                    "deals": deals,
                    "total_value_usd": deals * avg_value,
                    "weighted_value_usd": int(deals * avg_value * prob / 100),
                    "win_probability_pct": prob,
                    "avg_days_in_stage": rng.randint(3, 21),
                }
            )

        total_weighted = sum(s["weighted_value_usd"] for s in stage_data)
        return {
            "division": "DreamSalesPro",
            "task": "pipeline_summary",
            "pipeline_id": pipeline_id,
            "stages": stage_data,
            "total_weighted_pipeline_usd": total_weighted,
            "pipeline_health": "HEALTHY" if total_weighted > 500_000 else "NEEDS ATTENTION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Payment integration
    # ------------------------------------------------------------------

    def get_payment_info(self, bot_id: str) -> Dict[str, Any]:
        """
        Return DreamCo payment details for a specific bot subscription.

        Parameters
        ----------
        bot_id : str
            The botId from the bots.json catalogue.
        """
        bot = self.get_bot(bot_id)
        if bot is None:
            return {"error": f"Bot '{bot_id}' not found in DreamSalesPro catalogue."}

        return {
            "division": "DreamSalesPro",
            "bot_id": bot_id,
            "bot_name": bot["botName"],
            "pricing_type": bot["pricingType"],
            "price": bot["price"],
            "tier": bot["tier"],
            "checkout_params": {
                "product": bot_id,
                "division": "DreamSalesPro",
                "tier": bot["tier"],
                "pricing_type": bot["pricingType"],
            },
        }

    def describe_tier(self) -> str:
        """Return a human-readable description of the current tier."""
        lines = [
            f"=== {self.config.name} DreamSalesPro Tier ===",
            f"Price range: {self.config.price_range}",
            f"Bot access: {self.config.bot_access}",
            f"API access: {self.config.api_access}",
            f"Support: {self.config.support_level}",
            "Features:",
        ]
        for f in self.config.features:
            lines.append(f"  ✓ {f}")
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(f"\nUpgrade to {upgrade.value} for more features.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        """Raise DSPAccessError if *feature* is not available on current tier."""
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = (
                f"Feature '{feature}' is not available on the {self.tier.value} tier."
            )
            if upgrade:
                msg += f" Upgrade to {upgrade.value} to unlock this feature."
            raise DSPAccessError(msg)


# ---------------------------------------------------------------------------
# Automation registry
# Developer note: register new automation tasks here so they can be
# discovered and invoked programmatically by the control centre.
# ---------------------------------------------------------------------------

AUTOMATION_REGISTRY: Dict[str, str] = {
    "generate_leads": "Multi-source ICP-targeted lead generation",
    "execute_outreach_campaign": "Multi-channel outreach campaign execution",
    "simulate_revenue": "MRR/ARR revenue simulation with churn modeling",
    "get_pipeline_summary": "Pipeline health summary with weighted value",
    "get_payment_info": "DreamCo payment details for a bot subscription",
}
