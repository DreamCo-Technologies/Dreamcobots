# CRM Automation Bot

A tier-aware AI-powered CRM contact management and pipeline automation bot for the Dreamcobots platform. Manages contacts, tracks pipeline stages, and provides pipeline analytics based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.crm_automation_bot.bot import CRMAutomationBot
from bots.crm_automation_bot.tiers import get_crm_automation_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)                  | Pro ($49/mo)                             | Enterprise ($299/mo)                          |
|--------------------------|-------------------------------|------------------------------------------|-----------------------------------------------|
| Contacts                 | 100                           | 10,000                                   | Unlimited                                     |
| Pipeline stages          | 3 (lead, prospect, customer)  | 7 full stages                            | 7 full stages + AI insights                   |
| Email templates          | ✅                            | ✅                                       | ✅                                            |
| Automated sequences      | ❌                            | ✅                                       | ✅                                            |
| Integrations             | ❌                            | ✅                                       | ✅                                            |
| AI insights              | ❌                            | ❌                                       | ✅                                            |
| Custom CRM integration   | ❌                            | ❌                                       | ✅                                            |
| Team collaboration       | ❌                            | ❌                                       | ✅                                            |

## Usage

### Initialize the bot

```python
from bots.crm_automation_bot.bot import CRMAutomationBot
from tiers import Tier

bot = CRMAutomationBot(tier=Tier.PRO)
```

### Add a contact

```python
contact = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "company": "Acme Corp"
}

result = bot.add_contact(contact)
print(result)
# {
#   "contact_id": "uuid-...",
#   "name": "Alice Johnson",
#   "email": "alice@example.com",
#   "pipeline_stage": "lead",
#   "tier": "pro"
# }
```

### Update pipeline stage

```python
result = bot.update_pipeline("uuid-...", "qualified")
print(result)
# {
#   "contact_id": "uuid-...",
#   "previous_stage": "lead",
#   "new_stage": "qualified",
#   "tier": "pro"
# }
# Note: "qualified" is only available on PRO/ENTERPRISE
```

### Get pipeline statistics

```python
stats = bot.get_pipeline_stats()
print(stats)
# {
#   "total_contacts": 5,
#   "stages": {"lead": 3, "qualified": 1, "customer": 1},
#   "tier": "pro",
#   "buddy_integration": True
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 6,
#   "requests_remaining": "994",
#   "contact_count": 5,
#   "buddy_integration": True
# }
```

## License

MIT
