"""
DreamCo Empire OS — Formula Vault Module

Stores, retrieves, and executes reusable computational formulas for
financial calculations, automation workflows, and coding solutions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class FormulaCategory(Enum):
    FINANCE = "finance"
    AUTOMATION = "automation"
    CODING = "coding"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
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
    use_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Built-in empire formulas
_BUILTIN_FORMULAS = [
    {
        "formula_id": "roi_monthly",
        "name": "Monthly ROI",
        "category": FormulaCategory.FINANCE,
        "description": "Return on investment as a monthly percentage.",
        "expression": "(revenue - cost) / cost * 100",
        "variables": ["revenue", "cost"],
        "example_inputs": {"revenue": 1500.0, "cost": 1000.0},
        "tags": ["roi", "finance", "monthly"],
    },
    {
        "formula_id": "compound_growth",
        "name": "Compound Growth",
        "category": FormulaCategory.FINANCE,
        "description": "Future value using compound growth: P*(1+r)^n",
        "expression": "principal * (1 + rate) ** periods",
        "variables": ["principal", "rate", "periods"],
        "example_inputs": {"principal": 1000.0, "rate": 0.05, "periods": 12},
        "tags": ["compound", "growth", "interest"],
    },
    {
        "formula_id": "profit_margin",
        "name": "Profit Margin",
        "category": FormulaCategory.FINANCE,
        "description": "Net profit margin as a percentage.",
        "expression": "(revenue - expenses) / revenue * 100",
        "variables": ["revenue", "expenses"],
        "example_inputs": {"revenue": 5000.0, "expenses": 3500.0},
        "tags": ["profit", "margin"],
    },
    {
        "formula_id": "bot_daily_profit",
        "name": "Bot Daily Profit",
        "category": FormulaCategory.AUTOMATION,
        "description": "Estimated daily profit from a bot given run count and success rate.",
        "expression": "runs_per_day * success_rate * revenue_per_success - daily_cost",
        "variables": ["runs_per_day", "success_rate", "revenue_per_success", "daily_cost"],
        "example_inputs": {"runs_per_day": 100, "success_rate": 0.8, "revenue_per_success": 5.0, "daily_cost": 10.0},
        "tags": ["bot", "profit", "automation"],
    },
    {
        "formula_id": "cac",
        "name": "Customer Acquisition Cost",
        "category": FormulaCategory.MARKETING,
        "description": "Average cost to acquire a single customer.",
        "expression": "total_marketing_spend / new_customers",
        "variables": ["total_marketing_spend", "new_customers"],
        "example_inputs": {"total_marketing_spend": 2000.0, "new_customers": 50},
        "tags": ["cac", "marketing", "acquisition"],
    },
    {
        "formula_id": "ltv",
        "name": "Customer Lifetime Value",
        "category": FormulaCategory.MARKETING,
        "description": "Total revenue expected from a customer over their lifetime.",
        "expression": "avg_monthly_revenue * avg_lifespan_months",
        "variables": ["avg_monthly_revenue", "avg_lifespan_months"],
        "example_inputs": {"avg_monthly_revenue": 50.0, "avg_lifespan_months": 24},
        "tags": ["ltv", "retention", "revenue"],
    },
    {
        "formula_id": "break_even",
        "name": "Break-Even Point",
        "category": FormulaCategory.FINANCE,
        "description": "Units to sell before covering fixed costs.",
        "expression": "fixed_costs / (price_per_unit - variable_cost_per_unit)",
        "variables": ["fixed_costs", "price_per_unit", "variable_cost_per_unit"],
        "example_inputs": {"fixed_costs": 5000.0, "price_per_unit": 100.0, "variable_cost_per_unit": 60.0},
        "tags": ["break_even", "costs"],
    },
]


class FormulaVault:
    """
    Formula Vault — store, retrieve, and execute empire-grade formulas.

    Comes pre-loaded with 7 built-in financial and automation formulas.
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
    ) -> Formula:
        """Add a custom formula to the vault."""
        formula = Formula(
            formula_id=formula_id,
            name=name,
            category=category,
            description=description,
            expression=expression,
            variables=variables,
            example_inputs=example_inputs or {},
            tags=tags or [],
        )
        self._formulas[formula_id] = formula
        return formula

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

        Only numeric inputs are allowed. The expression is evaluated
        using a restricted namespace containing only the inputs and safe
        math builtins (no builtins, no imports).
        """
        f = self._get(formula_id)

        # Validate inputs
        missing = [v for v in f.variables if v not in inputs]
        if missing:
            raise ValueError(f"Missing variables for '{formula_id}': {missing}")

        # Sanitised namespace — only the numeric inputs
        safe_inputs: dict[str, Any] = {}
        for k, v in inputs.items():
            if not isinstance(v, (int, float)):
                raise TypeError(f"Variable '{k}' must be numeric, got {type(v).__name__}.")
            safe_inputs[k] = v

        # Guard expression against non-arithmetic content.
        # Allow: digits, variable names, arithmetic operators, whitespace, parens, dot, star-star.
        import re as _re
        if not _re.fullmatch(r"[A-Za-z0-9_\s\+\-\*\/\(\)\.\%]+", f.expression):
            raise ValueError(f"Formula expression contains unsafe characters: {f.expression!r}")

        result = eval(f.expression, {"__builtins__": {}}, safe_inputs)  # noqa: S307

        f.use_count += 1
        self._execution_log.append({
            "formula_id": formula_id,
            "inputs": inputs,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

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
        """Search formulas by name, description, or tags."""
        q = query.lower()
        results = []
        for f in self._formulas.values():
            if (
                q in f.name.lower()
                or q in f.description.lower()
                or any(q in tag.lower() for tag in f.tags)
            ):
                results.append(_formula_to_dict(f))
        return results

    def get_execution_log(self) -> list:
        """Return the full execution history."""
        return list(self._execution_log)

    def get_stats(self) -> dict:
        """Return vault statistics."""
        return {
            "total_formulas": len(self._formulas),
            "total_executions": len(self._execution_log),
            "most_used": max(self._formulas.values(), key=lambda f: f.use_count).formula_id if self._formulas else None,
            "categories": list({f.category.value for f in self._formulas.values()}),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, formula_id: str) -> Formula:
        if formula_id not in self._formulas:
            raise KeyError(f"Formula '{formula_id}' not found in the vault.")
        return self._formulas[formula_id]


def _formula_to_dict(f: Formula) -> dict:
    return {
        "formula_id": f.formula_id,
        "name": f.name,
        "category": f.category.value,
        "description": f.description,
        "expression": f.expression,
        "variables": f.variables,
        "example_inputs": f.example_inputs,
        "tags": f.tags,
        "use_count": f.use_count,
        "created_at": f.created_at,
    }
