"""
Tier configuration specific to the Finance Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

FINANCE_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Budget tracking (monthly)",
        "Expense categorization",
        "Savings tips & goal setting",
        "Basic net-worth snapshot",
    ],
    Tier.PRO.value: [
        "Investment portfolio analysis",
        "Tax estimator (W-2 & 1099)",
        "Cash flow reports (weekly/monthly)",
        "Debt payoff calculator",
        "Subscription expense auditor",
        "CSV/PDF financial exports",
    ],
    Tier.ENTERPRISE.value: [
        "Multi-entity accounting consolidation",
        "Regulatory compliance reporting (SOX, GAAP)",
        "ERP integration (QuickBooks, SAP)",
        "Scenario modelling & forecasting",
        "Dedicated CFO-level AI advisor",
        "Audit-ready financial packages",
    ],
}

FINANCE_TOOLS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "budget_tracker",
        "expense_categorizer",
        "savings_planner",
    ],
    Tier.PRO.value: [
        "budget_tracker",
        "expense_categorizer",
        "savings_planner",
        "portfolio_analyzer",
        "tax_estimator",
        "cash_flow_report",
        "debt_payoff_calculator",
    ],
    Tier.ENTERPRISE.value: [
        "budget_tracker",
        "expense_categorizer",
        "savings_planner",
        "portfolio_analyzer",
        "tax_estimator",
        "cash_flow_report",
        "debt_payoff_calculator",
        "multi_entity_consolidator",
        "compliance_reporter",
        "erp_sync",
        "scenario_modeler",
    ],
}


def get_finance_tier_info(tier: Tier) -> dict:
    """Return Finance Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "finance_features": FINANCE_EXTRA_FEATURES[tier.value],
        "tools": FINANCE_TOOLS[tier.value],
        "support_level": cfg.support_level,
    }
