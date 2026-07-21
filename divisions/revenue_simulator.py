"""
Revenue Simulation Engine for DreamCo Divisions.

Provides a unified revenue simulator that works across all DreamCo divisions
(DreamRealEstate, DreamSalesPro, DreamFinance, etc.).

Features:
  - MRR/ARR compound growth modeling with churn
  - Per-division revenue projections
  - Bot package bundling revenue scenarios
  - Enterprise license revenue modeling
  - Break-even analysis

Usage
-----
    from divisions.revenue_simulator import RevenueSimulator

    sim = RevenueSimulator()
    result = sim.simulate(
        division="DreamSalesPro",
        tier="Pro",
        starting_mrr=10000,
        growth_rate=0.12,
        months=24,
    )
    print(result)

Developer notes
---------------
- All methods return plain dicts for JSON serialisation.
- The simulator is stateless; create a new instance per simulation run
  or pass all parameters explicitly.
- To add a new pricing model, add a ``_model_*`` method and register it
  in ``PRICING_MODELS``.
"""
# GLOBAL AI SOURCES FLOW

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: DreamCo bundle tiers and their representative monthly prices.
BUNDLE_TIERS: Dict[str, Dict[str, Any]] = {
    "Starter+": {
        "price_usd": 99,
        "bot_slots": 3,
        "description": "Up to 3 Pro bots from any division",
    },
    "Growth+": {
        "price_usd": 299,
        "bot_slots": 10,
        "description": "Up to 10 Pro/Enterprise bots from any division",
    },
    "Empire": {
        "price_usd": 999,
        "bot_slots": None,
        "description": "Unlimited bots across all divisions, white-label included",
    },
}

#: Representative per-tier monthly prices for ARR modelling.
DIVISION_TIER_PRICES: Dict[str, Dict[str, float]] = {
    "DreamRealEstate": {"Pro": 199.0, "Enterprise": 499.0},
    "DreamSalesPro": {"Pro": 199.0, "Enterprise": 499.0},
    "DreamFinance": {"Pro": 199.0, "Enterprise": 499.0},
}


# ---------------------------------------------------------------------------
# RevenueSimulator
# ---------------------------------------------------------------------------


class RevenueSimulator:
    """
    Unified revenue simulation engine for DreamCo divisions.

    This class is intentionally stateless; every method takes explicit
    parameters and returns a self-contained result dict.
    """

    # ------------------------------------------------------------------
    # Core MRR/ARR simulation
    # ------------------------------------------------------------------

    def simulate(
        self,
        starting_mrr: float,
        growth_rate: float,
        months: int = 12,
        churn_rate: float = 0.05,
        division: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulate MRR/ARR growth over *months* using a compound-growth model.

        Parameters
        ----------
        starting_mrr : float
            Starting Monthly Recurring Revenue in USD.
        growth_rate : float
            Monthly growth rate as a decimal (e.g. 0.15 = 15%).
        months : int
            Number of months to project.
        churn_rate : float
            Monthly churn rate as a decimal (e.g. 0.05 = 5%).
        division : str | None
            Optional division name for labelling.
        tier : str | None
            Optional tier name for labelling.

        Returns
        -------
        dict
            Month-by-month projections plus an aggregated summary.

        Raises
        ------
        ValueError
            If *months* < 1 or *churn_rate* is outside [0.0, 1.0).
        """
        if months < 1:
            raise ValueError("months must be at least 1")
        if not (0.0 <= churn_rate < 1.0):
            raise ValueError("churn_rate must be between 0.0 and 1.0")
        if starting_mrr < 0:
            raise ValueError("starting_mrr must be non-negative")

        projections: List[Dict[str, Any]] = []
        current_mrr = starting_mrr

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

        final_mrr = projections[-1]["mrr_usd"] if projections else starting_mrr
        arr = round(final_mrr * 12, 2)
        total_revenue = round(sum(p["mrr_usd"] for p in projections), 2)
        growth_multiplier = round(final_mrr / starting_mrr, 2) if starting_mrr else 0.0

        return {
            "simulation": "mrr_arr_growth",
            "division": division,
            "tier": tier,
            "inputs": {
                "starting_mrr_usd": starting_mrr,
                "monthly_growth_rate": growth_rate,
                "monthly_churn_rate": churn_rate,
                "months": months,
            },
            "projections": projections,
            "summary": {
                "final_mrr_usd": final_mrr,
                "arr_usd": arr,
                "total_revenue_usd": total_revenue,
                "growth_multiplier": growth_multiplier,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Break-even analysis
    # ------------------------------------------------------------------

    def break_even(
        self,
        fixed_costs_usd: float,
        variable_cost_pct: float,
        price_per_unit_usd: float,
    ) -> Dict[str, Any]:
        """
        Calculate break-even units and revenue.

        Parameters
        ----------
        fixed_costs_usd : float
            Total fixed costs per month (infrastructure, staff, etc.).
        variable_cost_pct : float
            Variable cost as a fraction of revenue (e.g. 0.20 = 20%).
        price_per_unit_usd : float
            Price per subscription or transaction in USD.

        Returns
        -------
        dict
            Break-even analysis including units, revenue, and margin.

        Raises
        ------
        ValueError
            If *variable_cost_pct* >= 1.0 (impossible to break even).
        """
        if variable_cost_pct >= 1.0:
            raise ValueError(
                "variable_cost_pct must be < 1.0 (cannot have 100%+ variable cost)"
            )
        if price_per_unit_usd <= 0:
            raise ValueError("price_per_unit_usd must be positive")

        contribution_margin = price_per_unit_usd * (1 - variable_cost_pct)
        break_even_units = fixed_costs_usd / contribution_margin
        break_even_revenue = break_even_units * price_per_unit_usd

        return {
            "simulation": "break_even",
            "inputs": {
                "fixed_costs_usd": fixed_costs_usd,
                "variable_cost_pct": variable_cost_pct,
                "price_per_unit_usd": price_per_unit_usd,
            },
            "contribution_margin_usd": round(contribution_margin, 2),
            "break_even_units": round(break_even_units, 1),
            "break_even_revenue_usd": round(break_even_revenue, 2),
            "gross_margin_pct": round((1 - variable_cost_pct) * 100, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Bundle revenue modeling
    # ------------------------------------------------------------------

    def model_bundle_revenue(
        self,
        bundle_name: str,
        subscriber_count: int,
        months: int = 12,
        growth_rate: float = 0.08,
        churn_rate: float = 0.04,
    ) -> Dict[str, Any]:
        """
        Model recurring revenue for a DreamCo bot bundle package.

        Parameters
        ----------
        bundle_name : str
            One of "Starter+", "Growth+", or "Empire".
        subscriber_count : int
            Initial number of bundle subscribers.
        months : int
            Projection period in months.
        growth_rate : float
            Monthly subscriber growth rate.
        churn_rate : float
            Monthly subscriber churn rate.

        Returns
        -------
        dict
            Bundle revenue projections.

        Raises
        ------
        KeyError
            If *bundle_name* is not a recognised DreamCo bundle.
        """
        if bundle_name not in BUNDLE_TIERS:
            raise KeyError(
                f"Unknown bundle '{bundle_name}'. "
                f"Choose from: {list(BUNDLE_TIERS.keys())}"
            )

        bundle = BUNDLE_TIERS[bundle_name]
        price = bundle["price_usd"]
        starting_mrr = subscriber_count * price

        result = self.simulate(
            starting_mrr=starting_mrr,
            growth_rate=growth_rate,
            months=months,
            churn_rate=churn_rate,
        )
        result["simulation"] = "bundle_revenue"
        result["bundle"] = {
            "name": bundle_name,
            "price_usd": price,
            "description": bundle["description"],
            "starting_subscribers": subscriber_count,
        }
        return result

    # ------------------------------------------------------------------
    # Enterprise license revenue
    # ------------------------------------------------------------------

    def model_enterprise_revenue(
        self,
        division: str,
        license_count: int,
        months: int = 12,
        growth_rate: float = 0.05,
        churn_rate: float = 0.02,
    ) -> Dict[str, Any]:
        """
        Model enterprise license revenue for a given division.

        Parameters
        ----------
        division : str
            Division name (e.g. "DreamRealEstate", "DreamSalesPro").
        license_count : int
            Initial number of enterprise licenses sold.
        months : int
            Projection period in months.
        growth_rate : float
            Monthly license growth rate.
        churn_rate : float
            Monthly license churn rate.

        Returns
        -------
        dict
            Enterprise revenue projections.
        """
        prices = DIVISION_TIER_PRICES.get(division, {"Enterprise": 499.0})
        price_per_license = prices.get("Enterprise", 499.0)
        starting_mrr = license_count * price_per_license

        result = self.simulate(
            starting_mrr=starting_mrr,
            growth_rate=growth_rate,
            months=months,
            churn_rate=churn_rate,
            division=division,
            tier="Enterprise",
        )
        result["simulation"] = "enterprise_license_revenue"
        result["license_info"] = {
            "division": division,
            "starting_licenses": license_count,
            "price_per_license_usd": price_per_license,
        }
        return result
