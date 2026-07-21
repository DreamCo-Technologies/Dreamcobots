# Lead Generation Bot

A tier-aware AI-powered lead capture and scoring bot for the Dreamcobots platform. Captures leads, scores them using domain intelligence, and exports them in various formats based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.lead_generation_bot.bot import LeadGenerationBot
from bots.lead_generation_bot.tiers import get_lead_generation_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)     | Pro ($49/mo)                         | Enterprise ($299/mo)                      |
|--------------------------|------------------|--------------------------------------|-------------------------------------------|
| Leads per month          | 50               | 1,000                                | Unlimited                                 |
| Lead scoring             | Basic (0.5 fixed)| AI scoring (domain-based)            | Predictive analytics (+0.1 bonus)         |
| Export formats           | CSV only         | CSV, JSON                            | CSV, JSON, XML                            |
| CRM sync                 | ❌               | ✅                                   | ✅                                        |
| Email sequences          | ❌               | ✅                                   | ✅                                        |
| A/B testing              | ❌               | ❌                                   | ✅                                        |
| Custom integrations      | ❌               | ❌                                   | ✅                                        |

## Usage

### Initialize the bot

```python
from bots.lead_generation_bot.bot import LeadGenerationBot
from tiers import Tier

bot = LeadGenerationBot(tier=Tier.PRO)
```

### Capture a lead

```python
lead = {
    "name": "Jane Smith",
    "email": "jane@acme.io",
    "source": "referral"
}

result = bot.capture_lead(lead)
print(result)
# {
#   "lead_id": "uuid-...",
#   "name": "Jane Smith",
#   "email": "jane@acme.io",
#   "score": 0.9,   # .io domain (0.8) + referral bonus (0.1)
#   "tier": "pro"
# }
```

### Re-score a lead (PRO/ENTERPRISE)

```python
result = bot.score_lead("uuid-...")
print(result)
# {
#   "lead_id": "uuid-...",
#   "score": 0.9,
#   "tier": "pro"
# }
```

### Export leads

```python
# CSV available on all tiers
export = bot.export_leads(format="csv")
print(export)
# {"format": "csv", "count": 3, "data": [...], "tier": "pro"}

# JSON available on PRO+
export = bot.export_leads(format="json")
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 3,
#   "requests_remaining": "997",
#   "leads_captured": 3,
#   "buddy_integration": True
# }
```

## License

MIT
