# Home Screen Dashboard

Main dashboard screen for the DreamCo Money OS mobile-style interface, showing profit summary and top deals.

## Features

- Daily profit estimate
- Active alert count
- Top deals list (up to 3 displayed)
- Tier-aware display (FREE / PRO / ENTERPRISE)
- Demo mode for rapid prototyping

## Source

Implementation: [`frontend/screens/home_dashboard.py`](../../frontend/screens/home_dashboard.py)

## Usage

```python
from frontend.screens.home_dashboard import HomeDashboardScreen

# Live usage
screen = HomeDashboardScreen(
    user_tier="PRO",
    daily_profit=247.80,
    top_deals=[
        {"name": "PS5 Clearance", "profit": 85.0},
        {"name": "Dyson Refurb", "profit": 42.5},
    ],
    alerts=[{"urgency": "HIGH", "message": "Deal expiring in 30 min"}],
)
print(screen.render())

# Quick demo
print(HomeDashboardScreen.demo().render())
```
