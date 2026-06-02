from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping

@dataclass
class FinancialModel:
    assumptions: Dict[str, float]
    income_statement: Dict[str, Dict[str, float]]
    balance_sheet: Dict[str, Dict[str, float]]
    cash_flow: Dict[str, Dict[str, float]]
    sensitivity_analysis: Dict[str, Dict[str, float]]
    scenarios: Dict[str, Dict[str, Dict[str, float]]]


class FinancialModeler:
    """Builds lightweight three-statement models from business parameters."""

    def build(self, business_params: Mapping[str, float]) -> FinancialModel:
        assumptions = {
            'revenue': float(business_params.get('revenue', 1_000_000)),
            'growth_rate': float(business_params.get('growth_rate', 0.18)),
            'gross_margin': float(business_params.get('gross_margin', 0.72)),
            'opex_ratio': float(business_params.get('opex_ratio', 0.38)),
            'capex_ratio': float(business_params.get('capex_ratio', 0.06)),
            'working_capital_ratio': float(business_params.get('working_capital_ratio', 0.08)),
        }
        scenarios = {name: self._scenario(assumptions, mult) for name, mult in {'base': 1.0, 'bull': 1.25, 'bear': 0.75}.items()}
        sensitivity = self._sensitivity(assumptions)
        return FinancialModel(
            assumptions=assumptions,
            income_statement=scenarios['base']['income_statement'],
            balance_sheet=scenarios['base']['balance_sheet'],
            cash_flow=scenarios['base']['cash_flow'],
            sensitivity_analysis=sensitivity,
            scenarios=scenarios,
        )

    def _scenario(self, assumptions: Dict[str, float], multiplier: float) -> Dict[str, Dict[str, float]]:
        revenue = assumptions['revenue'] * (1 + assumptions['growth_rate'] * multiplier)
        cogs = revenue * (1 - assumptions['gross_margin'])
        gross_profit = revenue - cogs
        opex = revenue * assumptions['opex_ratio'] / max(multiplier, 0.5)
        ebitda = gross_profit - opex
        depreciation = revenue * assumptions['capex_ratio'] * 0.4
        ebit = ebitda - depreciation
        taxes = max(0.0, ebit * 0.21)
        net_income = ebit - taxes
        ar = revenue * 0.12
        cash = max(50_000.0, net_income * 0.6)
        ppe = revenue * assumptions['capex_ratio'] * 2.1
        debt = revenue * 0.18
        equity = cash + ar + ppe - debt
        operating_cf = net_income + depreciation - revenue * assumptions['working_capital_ratio'] * 0.2
        investing_cf = -(revenue * assumptions['capex_ratio'])
        financing_cf = debt * 0.05
        return {
            'income_statement': {
                'period_1': {
                    'revenue': round(revenue, 2), 'cogs': round(cogs, 2), 'gross_profit': round(gross_profit, 2),
                    'opex': round(opex, 2), 'ebitda': round(ebitda, 2), 'ebit': round(ebit, 2),
                    'taxes': round(taxes, 2), 'net_income': round(net_income, 2),
                }
            },
            'balance_sheet': {
                'period_1': {
                    'cash': round(cash, 2), 'accounts_receivable': round(ar, 2), 'ppe': round(ppe, 2),
                    'debt': round(debt, 2), 'equity': round(equity, 2),
                }
            },
            'cash_flow': {
                'period_1': {
                    'operating_cf': round(operating_cf, 2), 'investing_cf': round(investing_cf, 2),
                    'financing_cf': round(financing_cf, 2), 'net_change': round(operating_cf + investing_cf + financing_cf, 2),
                }
            }
        }

    def _sensitivity(self, assumptions: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        output: Dict[str, Dict[str, float]] = {}
        for key in ('growth_rate', 'gross_margin', 'opex_ratio'):
            output[key] = {}
            base_value = assumptions[key]
            for delta in (-0.05, 0.0, 0.05):
                tweaked = dict(assumptions)
                tweaked[key] = max(0.01, base_value + delta)
                scenario = self._scenario(tweaked, 1.0)
                ni = scenario['income_statement']['period_1']['net_income']
                output[key][f'{delta:+.0%}'] = round(ni, 2)
        return output
