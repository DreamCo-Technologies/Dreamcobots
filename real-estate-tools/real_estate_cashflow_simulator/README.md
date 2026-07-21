# Real Estate Cashflow Simulator

Analyze rental property cashflow, cap rate, cash-on-cash return, and portfolio performance.

## Tiers
- **Free** ($0/mo): Single property cashflow, basic metrics
- **Pro** ($34/mo): Multi-property portfolio, IRR calculation, amortization schedule
- **Enterprise** ($129/mo): Multi-entity analysis, tax projection, API access

## Usage
```python
import sys
sys.path.insert(0, "real-estate-tools/real_estate_cashflow_simulator")
from real_estate_cashflow_simulator import RealEstateCashflowSimulator

sim = RealEstateCashflowSimulator(tier="pro")
result = sim.simulate_cashflow({
    "purchase_price": 250000, "down_payment_pct": 0.20,
    "interest_rate": 0.065, "loan_term_years": 30,
    "monthly_rent": 1800, "vacancy_rate": 0.05,
    "monthly_expenses": 450, "property_management_pct": 0.08
})
```
