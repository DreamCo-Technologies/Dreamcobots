# Car Flipping Bot

Tier-aware car deal finder and flip profit estimator. Searches vehicles, evaluates flip potential, estimates profit, and surfaces top opportunities.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Makes | 1 at a time | Any | All |
| Results | 5 | 20 | 50 |
| Vehicle history | ✗ | ✓ | ✓ |
| Market prediction | ✗ | ✗ | ✓ |

## Usage

```python
from bots.car_flipping_bot.car_flipping_bot import CarFlippingBot
from tiers import Tier

bot = CarFlippingBot(tier=Tier.PRO)
cars = bot.search_cars("Toyota", budget=25000)
evaluation = bot.evaluate_car(cars[0])
profit = bot.estimate_flip_profit(cars[0])
best = bot.get_best_opportunities(limit=5)
```

## Methods

- `search_cars(make, budget)` — returns cars under budget for a make
- `evaluate_car(car)` — returns condition score, market value, flip potential
- `estimate_flip_profit(car)` — returns estimated profit after costs and fees
- `get_best_opportunities(limit)` — returns top flip opportunities sorted by profit

## Directory Structure

```
bots/car_flipping_bot/
├── car_flipping_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
