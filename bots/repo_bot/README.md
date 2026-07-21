# DreamCo Repo Bot — Repository Activity Tracker

Monitors GitHub repository activity (issues and pull requests) and converts
detected needs into prioritised action items for the DreamCo autonomous system.

## Overview

The Repo Activity Tracker:
- Scans open issues and pull requests (tier-limited).
- Categorises each item (bug, feature, bot_request, security, …).
- Generates a prioritised action plan.
- Can auto-create bot template stubs for bot-request issues (ENTERPRISE).

## Tiers

| Tier | Price | Features |
|------|-------|----------|
| FREE | $0/mo | Last 10 issues, last 5 PRs, basic action items |
| PRO | $49/mo | Last 50 issues, last 25 PRs, full categorisation, workflow suggestions |
| ENTERPRISE | $199/mo | Unlimited scanning, auto bot-stub creation, API |

## Quick start

```python
from bots.repo_bot.repo_activity_tracker import RepoActivityTracker
from bots.repo_bot.tiers import Tier

tracker = RepoActivityTracker(tier=Tier.PRO, repo_name="ireanjordan24/Dreamcobots")
result = tracker.scan_activity()

for item in result["action_items"]:
    print(f"[{item['priority'].upper()}] #{item['number']} {item['title']} → {item['action']}")
```
