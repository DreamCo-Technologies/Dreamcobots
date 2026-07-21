"""Finance Bot - Budgeting, portfolio analysis, cash flow forecasting, and tax optimization."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class FinanceBot(BaseBot):
    """AI bot for financial planning, portfolio analysis, and tax optimization."""

    def __init__(self):
        """Initialize the FinanceBot."""
        super().__init__(
            name="finance-bot",
            description="Provides budgeting, portfolio analysis, cash flow forecasting, ROI calculations, and tax optimization.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the finance bot main workflow."""
        self.start()
        return self.get_status()

    def build_budget(self, income: float, expenses_dict: dict) -> dict:
        """Build a detailed budget plan based on income and expenses."""
        total_expenses = sum(expenses_dict.values())
        surplus = income - total_expenses
        savings_rate = (surplus / income * 100) if income > 0 else 0
        expense_breakdown = {k: {"amount": v, "percent_of_income": round(v / income * 100, 1)}
                             for k, v in expenses_dict.items()} if income > 0 else {}
        recommendations = []
        if savings_rate < 10:
            recommendations.append("⚠️ Savings rate below 10% - aim for 20%+ for financial security")
        if "entertainment" in expenses_dict and expenses_dict["entertainment"] / income > 0.10:
            recommendations.append("Entertainment spending is above 10% of income - consider reducing")
        if surplus > 0:
            recommendations.append(f"Invest ${surplus * 0.5:.2f} in index funds (50% of surplus)")
            recommendations.append(f"Build emergency fund with ${surplus * 0.3:.2f} (30% of surplus)")
        return {
            "monthly_income": income,
            "total_expenses": total_expenses,
            "net_surplus": round(surplus, 2),
            "savings_rate_percent": round(savings_rate, 1),
            "expense_breakdown": expense_breakdown,
            "budget_health": "Good" if savings_rate >= 20 else "Fair" if savings_rate >= 10 else "Needs Improvement",
            "recommendations": recommendations,
            "50_30_20_rule": {
                "needs_50_percent": round(income * 0.50, 2),
                "wants_30_percent": round(income * 0.30, 2),
                "savings_20_percent": round(income * 0.20, 2),
            },
        }

    def analyze_portfolio(self, holdings_dict: dict) -> dict:
        """Analyze an investment portfolio for diversification and risk."""
        total_value = sum(holdings_dict.values())
        allocations = {asset: round(value / total_value * 100, 1)
                       for asset, value in holdings_dict.items()} if total_value > 0 else {}
        is_diversified = len(holdings_dict) >= 5
        largest_position_pct = max(allocations.values()) if allocations else 0
        return {
            "total_portfolio_value": round(total_value, 2),
            "number_of_holdings": len(holdings_dict),
            "allocations_percent": allocations,
            "diversification_score": "Good" if is_diversified and largest_position_pct < 30 else "Needs Improvement",
            "largest_position_percent": largest_position_pct,
            "risk_assessment": "Moderate" if is_diversified else "High - concentrated",
            "recommendations": [
                "Rebalance quarterly to maintain target allocations",
                "Ensure international exposure (20-30% of equity)",
                "Add bond allocation for stability if nearing retirement",
                "Consider low-cost index funds (VTI, VXUS, BND)",
            ],
        }

    def forecast_cash_flow(self, current_balance: float, monthly_income: float,
                           monthly_expenses: float, months: int) -> dict:
        """Forecast cash flow over a specified number of months."""
        monthly_net = monthly_income - monthly_expenses
        projections = []
        balance = current_balance
        for month in range(1, months + 1):
            balance += monthly_net
            projections.append({
                "month": month,
                "balance": round(balance, 2),
                "cumulative_net": round(monthly_net * month, 2),
            })
        return {
            "current_balance": current_balance,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_net": round(monthly_net, 2),
            "forecast_months": months,
            "ending_balance": round(projections[-1]["balance"], 2) if projections else current_balance,
            "break_even_month": next((p["month"] for p in projections if p["balance"] > 0), None) if current_balance < 0 else "Already positive",
            "projections": projections,
            "trend": "Positive" if monthly_net > 0 else "Negative - expenses exceed income",
        }

    def calculate_roi(self, investment: float, returns: float, time_years: float) -> dict:
        """Calculate ROI, annualized return, and related metrics."""
        if investment <= 0:
            return {"error": "Investment must be greater than 0"}
        simple_roi = (returns - investment) / investment * 100
        annualized_roi = ((returns / investment) ** (1 / time_years) - 1) * 100 if time_years > 0 else 0
        return {
            "investment": investment,
            "total_returns": returns,
            "net_profit": round(returns - investment, 2),
            "simple_roi_percent": round(simple_roi, 2),
            "annualized_roi_percent": round(annualized_roi, 2),
            "time_years": time_years,
            "rating": "Excellent (>15%)" if annualized_roi > 15 else "Good (8-15%)" if annualized_roi > 8 else "Below average (<8%)",
            "comparison": {
                "sp500_avg_annual": "10.5%",
                "treasury_bonds": "4.5%",
                "savings_account": "4.8%",
            },
        }

    def optimize_taxes(self, income: float, deductions_dict: dict) -> dict:
        """Provide tax optimization suggestions based on income and deductions."""
        total_deductions = sum(deductions_dict.values())
        standard_deduction = 14600  # 2024 single filer
        best_deduction = max(total_deductions, standard_deduction)
        taxable_income = max(0, income - best_deduction)
        tax_brackets_2024 = [
            (11600, 0.10), (47150, 0.12), (100525, 0.22),
            (191950, 0.24), (243725, 0.32), (609350, 0.35), (float("inf"), 0.37)
        ]
        tax = 0
        prev_limit = 0
        for limit, rate in tax_brackets_2024:
            if taxable_income <= prev_limit:
                break
            taxable_at_rate = min(taxable_income, limit) - prev_limit
            tax += taxable_at_rate * rate
            prev_limit = limit
        return {
            "gross_income": income,
            "total_deductions": total_deductions,
            "itemized_vs_standard": "Itemize" if total_deductions > standard_deduction else "Standard deduction",
            "taxable_income": round(taxable_income, 2),
            "estimated_federal_tax": round(tax, 2),
            "effective_tax_rate_percent": round(tax / income * 100, 1) if income > 0 else 0,
            "optimization_strategies": [
                f"Max 401(k) contribution: $23,000 (2024) saves ~${23000 * 0.24:.0f} in taxes",
                "HSA contribution: $4,150 single / $8,300 family (triple tax advantage)",
                "Harvest tax losses in brokerage accounts before year-end",
                "Consider QBI deduction if you have pass-through business income",
                "Bunch charitable donations to itemize every other year",
            ],
        }

    def compare_loans(self, loan_options: list) -> list:
        """Compare multiple loan options and rank by true cost."""
        compared = []
        for loan in loan_options:
            principal = loan.get("amount", 0)
            annual_rate = loan.get("rate_percent", 0) / 100
            months = loan.get("term_months", 60)
            monthly_rate = annual_rate / 12
            if monthly_rate > 0:
                payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
            else:
                payment = principal / months
            total_cost = payment * months
            compared.append({
                "lender": loan.get("lender", "Unknown"),
                "amount": principal,
                "rate_percent": loan.get("rate_percent", 0),
                "term_months": months,
                "monthly_payment": round(payment, 2),
                "total_cost": round(total_cost, 2),
                "total_interest": round(total_cost - principal, 2),
            })
        compared.sort(key=lambda x: x["total_cost"])
        for i, loan in enumerate(compared):
            loan["rank"] = i + 1
        return compared

    def track_crypto(self, portfolio_dict: dict) -> dict:
        """Track and analyze a cryptocurrency portfolio."""
        mock_prices = {
            "BTC": 67000, "ETH": 3500, "SOL": 180, "ADA": 0.45,
            "DOT": 7.20, "MATIC": 0.85, "LINK": 14.50, "AVAX": 38.0,
        }
        holdings = []
        total_value = 0
        for coin, amount in portfolio_dict.items():
            price = mock_prices.get(coin.upper(), 1.0)
            value = amount * price
            total_value += value
            holdings.append({
                "coin": coin.upper(),
                "amount": amount,
                "price_usd": price,
                "value_usd": round(value, 2),
            })
        for h in holdings:
            h["portfolio_percent"] = round(h["value_usd"] / total_value * 100, 1) if total_value > 0 else 0
        return {
            "total_portfolio_value_usd": round(total_value, 2),
            "holdings": holdings,
            "disclaimer": "Crypto prices are illustrative mock data. Use a real-time API for live prices.",
            "risk_note": "Cryptocurrency is highly volatile. Never invest more than you can afford to lose.",
        }

    def financial_health_score(self, assets: float, liabilities: float,
                               income: float, expenses: float) -> dict:
        """Calculate a financial health score from 1-100."""
        net_worth = assets - liabilities
        debt_to_income = (liabilities / (income * 12)) if income > 0 else 1
        savings_rate = ((income - expenses) / income) if income > 0 else 0
        net_worth_score = min(40, max(0, 40 * (1 - debt_to_income)))
        savings_score = min(30, savings_rate * 100)
        income_score = min(30, min(income / 1000, 30))
        total_score = int(net_worth_score + savings_score + income_score)
        total_score = max(1, min(100, total_score))
        return {
            "assets": assets,
            "liabilities": liabilities,
            "net_worth": round(net_worth, 2),
            "monthly_income": income,
            "monthly_expenses": expenses,
            "debt_to_income_ratio": round(debt_to_income, 2),
            "savings_rate_percent": round(savings_rate * 100, 1),
            "financial_health_score": total_score,
            "rating": "Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Fair" if total_score >= 40 else "Needs Work",
            "top_recommendations": [
                "Pay down high-interest debt first (avalanche method)",
                "Build 3-6 month emergency fund",
                "Increase savings rate to 20%+",
                "Invest surplus in diversified index funds",
            ],
        }
