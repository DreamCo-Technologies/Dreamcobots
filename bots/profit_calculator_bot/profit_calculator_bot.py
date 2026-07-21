"""Profit Calculator Bot — tier-aware P&L, break-even, and pricing analysis."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config
from bots.profit_calculator_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class ProfitCalculatorBot:
    """Tier-aware profit and financial analysis bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="ProfitCalculatorBot")

    def calculate_gross_profit(self, revenue: float, cogs: float) -> dict:
        gross_profit = revenue - cogs
        gross_margin_pct = (gross_profit / revenue * 100) if revenue != 0 else 0.0
        return {
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "tier_used": self.tier.value,
        }

    def calculate_break_even(self, fixed_costs: float, variable_cost_per_unit: float, selling_price: float) -> dict:
        contribution_margin = selling_price - variable_cost_per_unit
        if contribution_margin <= 0:
            raise ValueError("Selling price must exceed variable cost per unit to reach break-even")
        break_even_units = math.ceil(fixed_costs / contribution_margin)
        break_even_revenue = break_even_units * selling_price
        contribution_margin_ratio = (contribution_margin / selling_price * 100) if selling_price != 0 else 0.0
        return {
            "fixed_costs": fixed_costs,
            "variable_cost_per_unit": variable_cost_per_unit,
            "selling_price": selling_price,
            "break_even_units": break_even_units,
            "break_even_revenue": round(break_even_revenue, 2),
            "contribution_margin": round(contribution_margin, 2),
            "contribution_margin_ratio": round(contribution_margin_ratio, 2),
            "tier_used": self.tier.value,
        }

    def build_pl_statement(self, revenue: float, cogs: float, operating_expenses: float) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Full P&L statement requires PRO or ENTERPRISE tier")
        gross_profit = revenue - cogs
        gross_margin_pct = (gross_profit / revenue * 100) if revenue != 0 else 0.0
        operating_income = gross_profit - operating_expenses
        operating_margin_pct = (operating_income / revenue * 100) if revenue != 0 else 0.0
        tax = operating_income * 0.25 if operating_income > 0 else 0.0
        net_income = operating_income - tax
        net_margin_pct = (net_income / revenue * 100) if revenue != 0 else 0.0
        return {
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "operating_expenses": operating_expenses,
            "operating_income": round(operating_income, 2),
            "operating_margin_pct": round(operating_margin_pct, 2),
            "net_income": round(net_income, 2),
            "net_margin_pct": round(net_margin_pct, 2),
            "tier_used": self.tier.value,
        }

    def optimize_pricing(self, cost: float, target_margin: float, competitor_price: float = None) -> dict:
        recommended_price = cost / (1 - target_margin) if target_margin < 1 else cost
        actual_margin = ((recommended_price - cost) / recommended_price * 100) if recommended_price != 0 else 0.0

        result = {
            "cost": cost,
            "target_margin": target_margin,
            "recommended_price": round(recommended_price, 2),
            "actual_margin": round(actual_margin, 2),
            "competitor_price": competitor_price,
            "competitive_delta": None,
            "strategy": None,
            "tier_used": self.tier.value,
        }

        if competitor_price is not None:
            delta = round(recommended_price - competitor_price, 2)
            result["competitive_delta"] = delta
            if recommended_price < competitor_price:
                result["strategy"] = "undercut"
            elif recommended_price > competitor_price * 1.10:
                result["strategy"] = "premium"
            else:
                result["strategy"] = "competitive"

        return result

    def run_what_if(self, scenario_dict: dict) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("What-if scenarios require PRO or ENTERPRISE tier")
        revenue_change = scenario_dict.get("revenue_change_pct", 0) / 100
        cogs_change = scenario_dict.get("cogs_change_pct", 0) / 100
        fixed_costs = scenario_dict.get("fixed_costs", 0)

        base_revenue = scenario_dict.get("base_revenue", 100_000)
        base_cogs = scenario_dict.get("base_cogs", 60_000)

        def _calc(rev, cogs):
            gp = rev - cogs
            gm = (gp / rev * 100) if rev != 0 else 0.0
            oi = gp - fixed_costs
            ni = oi * 0.75 if oi > 0 else oi
            return {
                "revenue": round(rev, 2),
                "cogs": round(cogs, 2),
                "gross_profit": round(gp, 2),
                "gross_margin_pct": round(gm, 2),
                "operating_income": round(oi, 2),
                "net_income": round(ni, 2),
            }

        base = _calc(base_revenue, base_cogs)
        optimistic = _calc(base_revenue * (1 + revenue_change + 0.1), base_cogs * (1 + cogs_change - 0.05))
        pessimistic = _calc(base_revenue * (1 + revenue_change - 0.15), base_cogs * (1 + cogs_change + 0.10))

        return {
            "base": base,
            "optimistic": optimistic,
            "pessimistic": pessimistic,
            "tier_used": self.tier.value,
        }

    def run(self):
        return self.flow.run_pipeline(
            raw_data={"domain": "profit_calculation"},
            learning_method="supervised",
        )
