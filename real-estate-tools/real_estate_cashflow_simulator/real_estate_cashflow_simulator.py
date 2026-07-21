# GLOBAL AI SOURCES FLOW
"""Real Estate Cashflow Simulator - property investment cashflow and ROI analysis."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


class RealEstateCashflowSimulator:
    """Simulate real estate investment cashflow, ROI, cap rate, and amortization."""

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])

    def simulate_cashflow(self, property_data: dict) -> dict:
        """
        Simulate monthly and annual cashflow for a rental property.

        property_data keys:
          - purchase_price: float
          - down_payment_pct: float (e.g. 0.20)
          - interest_rate: float (annual, e.g. 0.065)
          - loan_term_years: int
          - monthly_rent: float
          - vacancy_rate: float (e.g. 0.05)
          - monthly_expenses: float (taxes, insurance, maintenance)
          - property_management_pct: float (e.g. 0.08)
        """
        price = property_data.get("purchase_price", 200000)
        down_pct = property_data.get("down_payment_pct", 0.20)
        rate = property_data.get("interest_rate", 0.065)
        term = property_data.get("loan_term_years", 30)
        rent = property_data.get("monthly_rent", 1500)
        vacancy = property_data.get("vacancy_rate", 0.05)
        expenses = property_data.get("monthly_expenses", 400)
        mgmt_pct = property_data.get("property_management_pct", 0.08)

        loan_amount = price * (1 - down_pct)
        monthly_rate = rate / 12
        n_payments = term * 12

        if monthly_rate > 0:
            mortgage = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** n_payments)
                / ((1 + monthly_rate) ** n_payments - 1)
            )
        else:
            mortgage = loan_amount / n_payments

        effective_rent = rent * (1 - vacancy)
        mgmt_fee = effective_rent * mgmt_pct
        total_monthly_costs = mortgage + expenses + mgmt_fee
        monthly_cashflow = round(effective_rent - total_monthly_costs, 2)
        annual_cashflow = round(monthly_cashflow * 12, 2)
        annual_rent = round(effective_rent * 12, 2)
        noi = round((effective_rent - expenses - mgmt_fee) * 12, 2)
        cap_rate = round((noi / price) * 100, 2) if price else 0.0
        cash_on_cash = round((annual_cashflow / (price * down_pct)) * 100, 2) if (price * down_pct) else 0.0

        return {
            "purchase_price": price,
            "loan_amount": round(loan_amount, 2),
            "monthly_mortgage": round(mortgage, 2),
            "effective_monthly_rent": round(effective_rent, 2),
            "monthly_cashflow": monthly_cashflow,
            "annual_cashflow": annual_cashflow,
            "annual_rent": annual_rent,
            "noi": noi,
            "cap_rate_pct": cap_rate,
            "cash_on_cash_return_pct": cash_on_cash,
            "tier": self.tier,
        }

    def generate_amortization(self, property_data: dict, years: int = 5) -> list:
        """Generate an amortization schedule (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Amortization schedule requires Pro tier or higher.")
        price = property_data.get("purchase_price", 200000)
        down_pct = property_data.get("down_payment_pct", 0.20)
        rate = property_data.get("interest_rate", 0.065)
        term = property_data.get("loan_term_years", 30)

        loan = price * (1 - down_pct)
        monthly_rate = rate / 12
        n_payments = term * 12
        payment = (
            loan
            * (monthly_rate * (1 + monthly_rate) ** n_payments)
            / ((1 + monthly_rate) ** n_payments - 1)
            if monthly_rate else loan / n_payments
        )

        schedule = []
        balance = loan
        for year in range(1, years + 1):
            year_interest = 0
            year_principal = 0
            for _ in range(12):
                interest = balance * monthly_rate
                principal = payment - interest
                balance -= principal
                year_interest += interest
                year_principal += principal
            schedule.append({
                "year": year,
                "annual_payment": round(payment * 12, 2),
                "principal_paid": round(year_principal, 2),
                "interest_paid": round(year_interest, 2),
                "remaining_balance": round(max(0, balance), 2),
            })
        return schedule

    def portfolio_summary(self, properties: list) -> dict:
        """Summarize cashflow across multiple properties (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Portfolio analysis requires Pro tier or higher.")
        results = [self.simulate_cashflow(p) for p in properties]
        total_cashflow = sum(r["annual_cashflow"] for r in results)
        total_invested = sum(
            p.get("purchase_price", 0) * p.get("down_payment_pct", 0.20) for p in properties
        )
        avg_cap_rate = sum(r["cap_rate_pct"] for r in results) / len(results) if results else 0.0
        return {
            "property_count": len(properties),
            "total_annual_cashflow": round(total_cashflow, 2),
            "total_capital_invested": round(total_invested, 2),
            "portfolio_coc_return_pct": round((total_cashflow / total_invested) * 100, 2) if total_invested else 0.0,
            "avg_cap_rate_pct": round(avg_cap_rate, 2),
            "properties": results,
        }
