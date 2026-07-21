# Profit Calculator Bot

Tier-aware financial analysis bot for gross profit, break-even, P&L, and pricing optimisation.

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Gross profit calc | ✓ | ✓ | ✓ |
| Break-even analysis | ✓ | ✓ | ✓ |
| Single product | ✓ | ✓ | ✓ |
| Full P&L statement | ✗ | ✓ | ✓ |
| Multi-product | ✗ | ✓ | ✓ |
| Pricing optimisation | ✗ | ✓ | ✓ |
| What-if scenarios | ✗ | ✓ | ✓ |
| Financial modelling | ✗ | ✗ | ✓ |
| Monte Carlo simulation | ✗ | ✗ | ✓ |

## Usage

```python
from bots.profit_calculator_bot import ProfitCalculatorBot
from bots.ai-models-integration.tiers import Tier

bot = ProfitCalculatorBot(tier=Tier.PRO)
gp = bot.calculate_gross_profit(revenue=500_000, cogs=300_000)
be = bot.calculate_break_even(fixed_costs=50_000, variable_cost_per_unit=20, selling_price=50)
pl = bot.build_pl_statement(revenue=500_000, cogs=300_000, operating_expenses=80_000)
pricing = bot.optimize_pricing(cost=30, target_margin=0.4, competitor_price=55)
```
