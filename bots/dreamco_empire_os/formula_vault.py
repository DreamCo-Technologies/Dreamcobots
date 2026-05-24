"""
DreamCo Empire OS — Formula Vault Module

Stores, retrieves, executes, and auto-generates reusable computational formulas for
financial calculations, automation workflows, and intelligence systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class FormulaCategory(Enum):
    FINANCE = "finance"
    AUTOMATION = "automation"
    CODING = "coding"
    MARKETING = "marketing"
    ANALYTICS = "analytics"

    REAL_ESTATE = "real_estate"
    CAR_FLIPPING = "car_flipping"
    SALES = "sales"
    CAPITAL_DEPLOYMENT = "capital_deployment"
    RISK_MANAGEMENT = "risk_management"
    REVENUE_INTELLIGENCE = "revenue_intelligence"

    CUSTOM = "custom"


@dataclass
class Formula:
    """A stored reusable formula."""

    formula_id: str
    name: str
    category: FormulaCategory
    description: str
    expression: str
    variables: list
    example_inputs: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)
    target: str = ""
    formula_type: str = "system"
    required_inputs: list = field(default_factory=list)
    use_count: int = 0
    auto_generated: bool = False
    generation_strategy: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.required_inputs:
            self.required_inputs = list(self.variables)


# Built-in Formula Vault formulas (34)
_BUILTIN_FORMULAS = [
    {
        "formula_id": "capital_deployment_efficiency",
        "name": "Capital Deployment Efficiency",
        "category": FormulaCategory.CAPITAL_DEPLOYMENT,
        "description": "Measures how efficiently deployed capital generates returns.",
        "expression": "annual_returns / total_capital_deployed * 100",
        "variables": ["annual_returns", "total_capital_deployed"],
        "example_inputs": {"annual_returns": 180000.0, "total_capital_deployed": 1000000.0},
        "target": "15%+ annual return on deployed capital",
        "tags": ["efficiency", "returns", "deployment"],
    },
    {
        "formula_id": "debt_to_equity_ratio",
        "name": "Debt-to-Equity Ratio",
        "category": FormulaCategory.CAPITAL_DEPLOYMENT,
        "description": "Monitors leverage levels across the portfolio.",
        "expression": "total_liabilities / total_equity",
        "variables": ["total_liabilities", "total_equity"],
        "example_inputs": {"total_liabilities": 750000.0, "total_equity": 500000.0},
        "target": "D/E < 2.0 for conservative leverage",
        "tags": ["leverage", "debt", "equity"],
    },
    {
        "formula_id": "liquidity_ratio",
        "name": "Liquidity Ratio",
        "category": FormulaCategory.CAPITAL_DEPLOYMENT,
        "description": "Ensures adequate operating reserves relative to monthly burn rate.",
        "expression": "operating_reserves / monthly_burn_rate",
        "variables": ["operating_reserves", "monthly_burn_rate"],
        "example_inputs": {"operating_reserves": 120000.0, "monthly_burn_rate": 18000.0},
        "target": ">= 6 months of reserves for safety",
        "tags": ["liquidity", "reserves", "safety"],
    },
    {
        "formula_id": "reinvestment_multiplier",
        "name": "Reinvestment Multiplier",
        "category": FormulaCategory.CAPITAL_DEPLOYMENT,
        "description": "Calculates the optimal profit reinvestment amount for growth.",
        "expression": "net_profit * 0.60",
        "variables": ["net_profit"],
        "example_inputs": {"net_profit": 50000.0},
        "target": "60% reinvest, 30% reserve, 10% expansion",
        "tags": ["reinvestment", "growth", "allocation"],
    },
    {
        "formula_id": "capital_turn_rate",
        "name": "Capital Turn Rate",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Measures how many times capital is recycled per year.",
        "expression": "365 / average_hold_period_days",
        "variables": ["average_hold_period_days"],
        "example_inputs": {"average_hold_period_days": 28.0},
        "target": "12+ turns per year for maximum capital efficiency",
        "tags": ["capital", "turnover", "efficiency"],
    },
    {
        "formula_id": "car_spread_formula",
        "name": "Car Spread Formula",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Calculates the profit spread between market value and total costs.",
        "expression": "market_value - (purchase_price + repair_cost + fees)",
        "variables": ["market_value", "purchase_price", "repair_cost", "fees"],
        "example_inputs": {
            "market_value": 18000.0,
            "purchase_price": 12000.0,
            "repair_cost": 1500.0,
            "fees": 500.0,
        },
        "target": "Minimum 15-20% spread for viable deals",
        "tags": ["spread", "profit", "acquisition"],
    },
    {
        "formula_id": "daily_profit_rate",
        "name": "Daily Profit Rate",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Calculates profit per day held to compare deal efficiency.",
        "expression": "net_profit / days_held",
        "variables": ["net_profit", "days_held"],
        "example_inputs": {"net_profit": 2400.0, "days_held": 16.0},
        "target": "Higher daily profit = better capital deployment",
        "tags": ["profit", "daily", "efficiency"],
    },
    {
        "formula_id": "demand_velocity_score",
        "name": "Demand Velocity Score",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Measures how quickly a vehicle model sells in a given market.",
        "expression": "listings_sold_30_days / active_listings",
        "variables": ["listings_sold_30_days", "active_listings"],
        "example_inputs": {"listings_sold_30_days": 125.0, "active_listings": 90.0},
        "target": "Above 1.0 = high demand vehicle",
        "tags": ["demand", "velocity", "market"],
    },
    {
        "formula_id": "max_purchase_price",
        "name": "Max Purchase Price",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Calculates the maximum purchase price for profitable car flips.",
        "expression": "(expected_sale_price * 0.75) - repair_costs",
        "variables": ["expected_sale_price", "repair_costs"],
        "example_inputs": {"expected_sale_price": 22000.0, "repair_costs": 2500.0},
        "target": "Never exceed max purchase for profitability",
        "tags": ["acquisition", "max-price", "limit"],
    },
    {
        "formula_id": "repair_risk_multiplier",
        "name": "Repair Risk Multiplier",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Adjusts profit for repair cost uncertainty with a safety buffer.",
        "expression": "spread - (repair_estimate * 1.3)",
        "variables": ["spread", "repair_estimate"],
        "example_inputs": {"spread": 4500.0, "repair_estimate": 2000.0},
        "target": "Must remain positive after 30% buffer",
        "tags": ["repair", "risk", "buffer"],
    },
    {
        "formula_id": "time_to_liquidation",
        "name": "Time-to-Liquidation",
        "category": FormulaCategory.CAR_FLIPPING,
        "description": "Predicts average days to sell based on model and zip code data.",
        "expression": "avg_market_days",
        "variables": ["vehicle_model", "zip_code", "avg_market_days"],
        "required_inputs": ["avg_market_days"],
        "example_inputs": {"avg_market_days": 18.0},
        "target": "Target under 21 days for rapid turn",
        "tags": ["liquidation", "speed", "turnover"],
    },
    {
        "formula_id": "brrrr_recycle",
        "name": "BRRRR Recycle",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Validates if a BRRRR deal returns all invested capital through refinance.",
        "expression": "(arv * ltv_ratio) - (purchase_price + repairs + holding_costs)",
        "variables": ["arv", "ltv_ratio", "purchase_price", "repairs", "holding_costs"],
        "example_inputs": {
            "arv": 220000.0,
            "ltv_ratio": 0.75,
            "purchase_price": 120000.0,
            "repairs": 30000.0,
            "holding_costs": 7000.0,
        },
        "target": "Refi Amount >= Total Investment",
        "tags": ["brrrr", "refinance", "recycle"],
    },
    {
        "formula_id": "core_flip_spread",
        "name": "Core Flip Spread",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Determines if a property is a strong flip candidate by spread between ARV and total costs.",
        "expression": "(arv * 0.70) - (purchase_price + repairs)",
        "variables": ["arv", "purchase_price", "repairs"],
        "example_inputs": {"arv": 300000.0, "purchase_price": 180000.0, "repairs": 30000.0},
        "target": "Deal Score > $25,000 = Strong Flip Candidate",
        "tags": ["flip", "spread", "acquisition"],
    },
    {
        "formula_id": "debt_service_coverage",
        "name": "Debt Service Coverage",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Measures ability to cover debt payments from rental income.",
        "expression": "net_operating_income / annual_debt_service",
        "variables": ["net_operating_income", "annual_debt_service"],
        "example_inputs": {"net_operating_income": 45000.0, "annual_debt_service": 32000.0},
        "target": "DSCR >= 1.25 for safe leverage",
        "tags": ["leverage", "debt", "risk"],
    },
    {
        "formula_id": "equity_capture",
        "name": "Equity Capture",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Measures instant equity gained at purchase to ensure built-in margin.",
        "expression": "(arv - purchase_price) / arv * 100",
        "variables": ["arv", "purchase_price"],
        "example_inputs": {"arv": 260000.0, "purchase_price": 205000.0},
        "target": "15%+ minimum instant equity",
        "tags": ["equity", "acquisition", "leverage"],
    },
    {
        "formula_id": "maximum_allowable_offer",
        "name": "Maximum Allowable Offer",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Calculates the maximum price to offer on a flip deal using the 70% rule.",
        "expression": "(arv * 0.70) - repair_costs",
        "variables": ["arv", "repair_costs"],
        "example_inputs": {"arv": 280000.0, "repair_costs": 40000.0},
        "target": "Never exceed MAO for profitable flips",
        "tags": ["flip", "offer", "acquisition"],
    },
    {
        "formula_id": "motivation_score",
        "name": "Motivation Score",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Scores seller motivation level to determine negotiation leverage.",
        "expression": "(days_on_market * 0.2) + (price_drops * 5) + (vacant_flag * 10)",
        "variables": ["days_on_market", "price_drops", "vacant_flag"],
        "example_inputs": {"days_on_market": 75.0, "price_drops": 2.0, "vacant_flag": 1.0},
        "target": "Higher score = higher negotiation leverage",
        "tags": ["negotiation", "seller", "acquisition"],
    },
    {
        "formula_id": "rental_cashflow",
        "name": "Rental Cashflow",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Calculates cash-on-cash return for rental properties.",
        "expression": "((monthly_rent - monthly_expenses) * 12) / total_cash_invested * 100",
        "variables": ["monthly_rent", "monthly_expenses", "total_cash_invested"],
        "example_inputs": {"monthly_rent": 2200.0, "monthly_expenses": 1200.0, "total_cash_invested": 90000.0},
        "target": "Minimum 8-12% Cash-on-Cash Return",
        "tags": ["rental", "cashflow", "hold"],
    },
    {
        "formula_id": "rental_yield",
        "name": "Rental Yield",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Calculates annual rental yield as a percentage of property value.",
        "expression": "(monthly_rent * 12) / property_value * 100",
        "variables": ["monthly_rent", "property_value"],
        "example_inputs": {"monthly_rent": 2100.0, "property_value": 350000.0},
        "target": "5%+ gross yield for rental properties",
        "tags": ["rental", "yield", "analysis"],
    },
    {
        "formula_id": "section8_premium",
        "name": "Section 8 Premium",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Compares Section 8 voucher rates versus market rent for premium analysis.",
        "expression": "(section8_rate - market_rent) / market_rent * 100",
        "variables": ["section8_rate", "market_rent"],
        "example_inputs": {"section8_rate": 1900.0, "market_rent": 1700.0},
        "target": "Positive premium indicates above-market returns",
        "tags": ["section8", "rental", "government"],
    },
    {
        "formula_id": "wholesale_assignment_fee",
        "name": "Wholesale Assignment Fee",
        "category": FormulaCategory.REAL_ESTATE,
        "description": "Calculates assignment fee potential in a wholesale deal.",
        "expression": "end_buyer_price - contract_price",
        "variables": ["end_buyer_price", "contract_price"],
        "example_inputs": {"end_buyer_price": 155000.0, "contract_price": 147000.0},
        "target": "Minimum $5,000 assignment fee",
        "tags": ["wholesale", "assignment", "quick-profit"],
    },
    {
        "formula_id": "churn_prediction_score",
        "name": "Churn Prediction Score",
        "category": FormulaCategory.REVENUE_INTELLIGENCE,
        "description": "Predicts customer churn likelihood based on usage patterns.",
        "expression": "(login_frequency * 0.3) + (feature_usage * 0.4) + (support_tickets * -0.3)",
        "variables": ["login_frequency", "feature_usage", "support_tickets"],
        "example_inputs": {"login_frequency": 45.0, "feature_usage": 60.0, "support_tickets": 20.0},
        "target": "Score < 40 = high churn risk, intervene immediately",
        "tags": ["churn", "prediction", "retention"],
    },
    {
        "formula_id": "dynamic_pricing_optimizer",
        "name": "Dynamic Pricing Optimizer",
        "category": FormulaCategory.REVENUE_INTELLIGENCE,
        "description": "Adjusts pricing based on demand, competition, and capacity.",
        "expression": "base_price * (1 + demand_factor) * (1 - competition_pressure)",
        "variables": ["base_price", "demand_factor", "competition_pressure"],
        "example_inputs": {"base_price": 100.0, "demand_factor": 0.12, "competition_pressure": 0.08},
        "target": "Maximize revenue while maintaining conversion",
        "tags": ["pricing", "dynamic", "optimization"],
    },
    {
        "formula_id": "revenue_leak_score",
        "name": "Revenue Leak Score",
        "category": FormulaCategory.REVENUE_INTELLIGENCE,
        "description": "Identifies and quantifies revenue losses across the system.",
        "expression": "(failed_transactions + cart_abandonment_rate + pricing_errors) * avg_order_value",
        "variables": ["failed_transactions", "cart_abandonment_rate", "pricing_errors", "avg_order_value"],
        "example_inputs": {
            "failed_transactions": 80.0,
            "cart_abandonment_rate": 22.0,
            "pricing_errors": 12.0,
            "avg_order_value": 95.0,
        },
        "target": "Minimize leak score to zero",
        "tags": ["leak", "revenue", "detection"],
    },
    {
        "formula_id": "revenue_per_bot",
        "name": "Revenue Per Bot",
        "category": FormulaCategory.REVENUE_INTELLIGENCE,
        "description": "Tracks revenue generation efficiency per AI agent.",
        "expression": "total_revenue / active_bot_count",
        "variables": ["total_revenue", "active_bot_count"],
        "example_inputs": {"total_revenue": 450000.0, "active_bot_count": 120.0},
        "target": "Increasing RPB indicates platform efficiency",
        "tags": ["revenue", "bots", "efficiency"],
    },
    {
        "formula_id": "drawdown_recovery",
        "name": "Drawdown Recovery",
        "category": FormulaCategory.RISK_MANAGEMENT,
        "description": "Calculates time to recover from a portfolio drawdown.",
        "expression": "loss_amount / monthly_net_income",
        "variables": ["loss_amount", "monthly_net_income"],
        "example_inputs": {"loss_amount": 90000.0, "monthly_net_income": 18000.0},
        "target": "Recovery within 6 months for acceptable risk",
        "tags": ["drawdown", "recovery", "risk"],
    },
    {
        "formula_id": "portfolio_concentration",
        "name": "Portfolio Concentration",
        "category": FormulaCategory.RISK_MANAGEMENT,
        "description": "Measures exposure to any single asset type or market.",
        "expression": "single_asset_value / total_portfolio_value * 100",
        "variables": ["single_asset_value", "total_portfolio_value"],
        "example_inputs": {"single_asset_value": 180000.0, "total_portfolio_value": 900000.0},
        "target": "No single asset > 25% of total portfolio",
        "tags": ["diversification", "concentration", "portfolio"],
    },
    {
        "formula_id": "risk_adjusted_return",
        "name": "Risk-Adjusted Return",
        "category": FormulaCategory.RISK_MANAGEMENT,
        "description": "Adjusts returns for risk level to compare deals fairly.",
        "expression": "expected_return / risk_score",
        "variables": ["expected_return", "risk_score"],
        "example_inputs": {"expected_return": 28.0, "risk_score": 7.0},
        "target": "Higher RAR = better risk-adjusted opportunity",
        "tags": ["risk", "return", "comparison"],
    },
    {
        "formula_id": "cac_efficiency",
        "name": "CAC Efficiency",
        "category": FormulaCategory.SALES,
        "description": "Measures customer acquisition efficiency by comparing lifetime value to cost.",
        "expression": "customer_lifetime_value / customer_acquisition_cost",
        "variables": ["customer_lifetime_value", "customer_acquisition_cost"],
        "example_inputs": {"customer_lifetime_value": 2400.0, "customer_acquisition_cost": 600.0},
        "target": "LTV/CAC >= 3 for healthy unit economics",
        "tags": ["cac", "ltv", "efficiency"],
    },
    {
        "formula_id": "closing_probability",
        "name": "Closing Probability",
        "category": FormulaCategory.SALES,
        "description": "Predicts deal closing likelihood based on engagement signals.",
        "expression": "(meetings_held * 0.3) + (proposal_sent * 0.4) + (champion_score * 0.3)",
        "variables": ["meetings_held", "proposal_sent", "champion_score"],
        "example_inputs": {"meetings_held": 80.0, "proposal_sent": 1.0, "champion_score": 90.0},
        "target": "Above 70% = high-confidence close",
        "tags": ["closing", "probability", "prediction"],
    },
    {
        "formula_id": "commission_roi",
        "name": "Commission ROI",
        "category": FormulaCategory.SALES,
        "description": "Calculates return on investment for commission-based sales teams.",
        "expression": "(revenue_generated - total_commission_paid) / total_commission_paid * 100",
        "variables": ["revenue_generated", "total_commission_paid"],
        "example_inputs": {"revenue_generated": 800000.0, "total_commission_paid": 160000.0},
        "target": "Minimum 300% ROI on commission spend",
        "tags": ["commission", "roi", "team"],
    },
    {
        "formula_id": "funnel_leak_detection",
        "name": "Funnel Leak Detection",
        "category": FormulaCategory.SALES,
        "description": "Identifies conversion drop-offs between sales funnel stages.",
        "expression": "(stage_n_count - stage_n_plus_1_count) / stage_n_count * 100",
        "variables": ["stage_n_count", "stage_n_plus_1_count"],
        "example_inputs": {"stage_n_count": 1000.0, "stage_n_plus_1_count": 560.0},
        "target": "Identify stages with > 40% drop-off for optimization",
        "tags": ["funnel", "conversion", "optimization"],
    },
    {
        "formula_id": "lead_value_formula",
        "name": "Lead Value Formula",
        "category": FormulaCategory.SALES,
        "description": "Calculates expected value of each lead based on conversion probability.",
        "expression": "close_rate * average_deal_size",
        "variables": ["close_rate", "average_deal_size"],
        "example_inputs": {"close_rate": 0.25, "average_deal_size": 12000.0},
        "target": "Prioritize leads with highest expected value",
        "tags": ["leads", "value", "conversion"],
    },
    {
        "formula_id": "pipeline_velocity",
        "name": "Pipeline Velocity",
        "category": FormulaCategory.SALES,
        "description": "Measures speed of revenue flowing through the sales pipeline.",
        "expression": "(opportunities * win_rate * average_deal_size) / sales_cycle_days",
        "variables": ["opportunities", "win_rate", "average_deal_size", "sales_cycle_days"],
        "example_inputs": {"opportunities": 48.0, "win_rate": 0.28, "average_deal_size": 14000.0, "sales_cycle_days": 32.0},
        "target": "Increasing velocity indicates improving sales efficiency",
        "tags": ["pipeline", "velocity", "revenue"],
    },
]


class FormulaVault:
    """
    Formula Vault — store, retrieve, execute, and auto-create formulas.

    Comes pre-loaded with 34 strategic formulas across Real Estate, Car Flipping,
    Sales, Capital Deployment, Risk Management, and Revenue Intelligence.
    """

    def __init__(self) -> None:
        self._formulas: dict[str, Formula] = {}
        self._execution_log: list = []
        self._load_builtins()

    def _load_builtins(self) -> None:
        for fdata in _BUILTIN_FORMULAS:
            formula = Formula(**fdata)
            self._formulas[formula.formula_id] = formula

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_formula(
        self,
        formula_id: str,
        name: str,
        category: FormulaCategory,
        description: str,
        expression: str,
        variables: list,
        example_inputs: Optional[dict] = None,
        tags: Optional[list] = None,
        target: str = "",
        formula_type: str = "system",
        required_inputs: Optional[list] = None,
        auto_generated: bool = False,
        generation_strategy: Optional[str] = None,
    ) -> Formula:
        """Add a formula to the vault."""
        formula = Formula(
            formula_id=formula_id,
            name=name,
            category=category,
            description=description,
            expression=expression,
            variables=variables,
            example_inputs=example_inputs or {},
            tags=tags or [],
            target=target,
            formula_type=formula_type,
            required_inputs=required_inputs or [],
            auto_generated=auto_generated,
            generation_strategy=generation_strategy,
        )
        self._formulas[formula_id] = formula
        return formula

    def auto_create_formula(
        self,
        name: str,
        category: FormulaCategory,
        description: str,
        variables: list[str],
        tags: Optional[list[str]] = None,
        target: str = "",
        formula_id: Optional[str] = None,
    ) -> dict:
        """
        Create and register a formula automatically from intent + variable inputs.

        The vault infers a generation strategy (ratio, spread, weighted_score, etc.),
        builds an executable expression, and stores the generated formula.
        """
        if len(variables) == 0:
            raise ValueError("At least one variable is required to auto-create a formula.")

        normalised_vars = [self._normalise_identifier(v) for v in variables]
        strategy = self._infer_generation_strategy(name, description, tags or [])
        expression = self._build_expression(strategy, normalised_vars)

        resolved_formula_id = self._ensure_unique_formula_id(
            formula_id or self._slugify_formula_id(name)
        )

        sample_inputs = {var: float(index + 1) * 10.0 for index, var in enumerate(normalised_vars)}

        created = self.add_formula(
            formula_id=resolved_formula_id,
            name=name,
            category=category,
            description=description,
            expression=expression,
            variables=normalised_vars,
            example_inputs=sample_inputs,
            tags=tags or [],
            target=target,
            formula_type="system",
            required_inputs=normalised_vars,
            auto_generated=True,
            generation_strategy=strategy,
        )
        return _formula_to_dict(created)

    def get_formula(self, formula_id: str) -> dict:
        """Retrieve a formula by ID."""
        f = self._get(formula_id)
        return _formula_to_dict(f)

    def delete_formula(self, formula_id: str) -> bool:
        """Remove a formula from the vault. Returns True if deleted."""
        if formula_id in self._formulas:
            del self._formulas[formula_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, formula_id: str, inputs: dict) -> dict:
        """
        Evaluate a formula with the provided variable values.

        Required expression inputs must be numeric. Expression is evaluated
        using a restricted namespace containing only safe numeric inputs.
        """
        f = self._get(formula_id)

        missing = [v for v in f.required_inputs if v not in inputs]
        if missing:
            raise ValueError(f"Missing variables for '{formula_id}': {missing}")

        safe_inputs: dict[str, Any] = {}
        for required_name in f.required_inputs:
            value = inputs[required_name]
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Variable '{required_name}' must be numeric, got {type(value).__name__}."
                )
            safe_inputs[required_name] = float(value)

        # Allow only arithmetic expression characters and variables.
        if not re.fullmatch(r"[A-Za-z0-9_\s\+\-\*\/\(\)\.\%]+", f.expression):
            raise ValueError(f"Formula expression contains unsafe characters: {f.expression!r}")

        result = eval(f.expression, {"__builtins__": {}}, safe_inputs)  # noqa: S307

        f.use_count += 1
        self._execution_log.append(
            {
                "formula_id": formula_id,
                "inputs": inputs,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return {
            "formula_id": formula_id,
            "name": f.name,
            "inputs": inputs,
            "result": round(float(result), 4),
            "expression": f.expression,
        }

    # ------------------------------------------------------------------
    # Search & list
    # ------------------------------------------------------------------

    def list_formulas(self, category: Optional[FormulaCategory] = None) -> list:
        """List all formulas, optionally filtered by category."""
        formulas = list(self._formulas.values())
        if category:
            formulas = [f for f in formulas if f.category == category]
        return [_formula_to_dict(f) for f in formulas]

    def search(self, query: str) -> list:
        """Search formulas by name, description, target, or tags."""
        q = query.lower()
        results = []
        for f in self._formulas.values():
            if (
                q in f.name.lower()
                or q in f.description.lower()
                or q in f.target.lower()
                or any(q in tag.lower() for tag in f.tags)
            ):
                results.append(_formula_to_dict(f))
        return results

    def get_execution_log(self) -> list:
        """Return the full execution history."""
        return list(self._execution_log)

    def get_stats(self) -> dict:
        """Return vault statistics."""
        categories = sorted({f.category.value for f in self._formulas.values()})
        auto_generated_count = sum(1 for f in self._formulas.values() if f.auto_generated)
        return {
            "total_formulas": len(self._formulas),
            "total_executions": len(self._execution_log),
            "most_used": max(self._formulas.values(), key=lambda f: f.use_count).formula_id
            if self._formulas
            else None,
            "categories": categories,
            "auto_generated_formulas": auto_generated_count,
            "builtin_formulas": len(self._formulas) - auto_generated_count,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, formula_id: str) -> Formula:
        if formula_id not in self._formulas:
            raise KeyError(f"Formula '{formula_id}' not found in the vault.")
        return self._formulas[formula_id]

    @staticmethod
    def _normalise_identifier(variable_name: str) -> str:
        cleaned = re.sub(r"[^a-z0-9_]+", "_", variable_name.strip().lower()).strip("_")
        if not cleaned:
            raise ValueError(f"Invalid variable name: {variable_name!r}")
        if cleaned[0].isdigit():
            cleaned = f"var_{cleaned}"
        return cleaned

    @staticmethod
    def _slugify_formula_id(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
        return slug or "generated_formula"

    def _ensure_unique_formula_id(self, base_formula_id: str) -> str:
        if base_formula_id not in self._formulas:
            return base_formula_id

        suffix = 2
        while f"{base_formula_id}_{suffix}" in self._formulas:
            suffix += 1
        return f"{base_formula_id}_{suffix}"

    @staticmethod
    def _infer_generation_strategy(name: str, description: str, tags: list[str]) -> str:
        text = " ".join([name, description, *tags]).lower()

        if any(keyword in text for keyword in ["score", "probability", "prediction"]):
            return "weighted_score"
        if any(keyword in text for keyword in ["spread", "premium", "fee", "delta", "difference"]):
            return "spread"
        if any(keyword in text for keyword in ["ratio", "coverage", "yield", "concentration", "roi"]):
            return "ratio"
        if any(keyword in text for keyword in ["rate", "velocity", "turn"]):
            return "rate"
        if any(keyword in text for keyword in ["multiplier", "multiple"]):
            return "multiplier"
        return "additive"

    @staticmethod
    def _build_expression(strategy: str, variables: list[str]) -> str:
        if strategy == "weighted_score":
            weight = round(1 / len(variables), 4)
            return " + ".join(f"({v} * {weight})" for v in variables)

        if strategy == "spread":
            if len(variables) == 1:
                return variables[0]
            return f"{variables[0]} - ({' + '.join(variables[1:])})"

        if strategy == "ratio":
            if len(variables) == 1:
                return variables[0]
            return f"{variables[0]} / {variables[1]}"

        if strategy == "rate":
            if len(variables) == 1:
                return variables[0]
            return f"{variables[0]} / {variables[1]}"

        if strategy == "multiplier":
            return f"{variables[0]} * 1.25"

        if len(variables) == 1:
            return variables[0]
        return " + ".join(variables)


def _formula_to_dict(f: Formula) -> dict:
    return {
        "formula_id": f.formula_id,
        "name": f.name,
        "category": f.category.value,
        "description": f.description,
        "expression": f.expression,
        "variables": f.variables,
        "required_inputs": f.required_inputs,
        "example_inputs": f.example_inputs,
        "tags": f.tags,
        "target": f.target,
        "formula_type": f.formula_type,
        "auto_generated": f.auto_generated,
        "generation_strategy": f.generation_strategy,
        "use_count": f.use_count,
        "created_at": f.created_at,
    }
