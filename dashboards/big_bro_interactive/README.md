# Big Bro AI — Interactive Gamified Dashboard

Gamified experience layer for the Big Bro AI platform with XP progression, achievements, and live simulations.

## Features

- **XP & Level System** — earn experience points for completing tasks
- **Achievement Badges** — unlock milestones (First Bot, Revenue Milestone, Code Gladiator, etc.)
- **Bot Idea Manager** — generate, rank, and track bot ideas
- **Hustle Simulator** — simulate revenue/profit scenarios
- **Code Gladiator** — challenge-based skill games
- **Bot Speed Control** — dynamic throttle and turbo modes
- **Big Bro Commentary** — motivational messages from Big Bro AI
- **ASCII Progress Bars** — visual progress rendering

## Source

Implementation: [`bots/big_bro_ai/interactive_dashboard.py`](../../bots/big_bro_ai/interactive_dashboard.py)

## Usage

```python
from bots.big_bro_ai.interactive_dashboard import InteractiveDashboard

dash = InteractiveDashboard(username="DreamBuilder")
dash.earn_xp(500)
dash.unlock_achievement("first_bot")
print(dash.render_hud())
```
