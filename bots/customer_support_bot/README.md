# Customer Support Bot

A tier-aware AI-powered customer support automation bot for the Dreamcobots platform. Handles support tickets, performs sentiment analysis, and routes inquiries based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

Ensure the `bots/` directory is on your Python path, then import directly:

```python
from bots.customer_support_bot.bot import CustomerSupportBot
from bots.customer_support_bot.tiers import get_customer_support_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)          | Pro ($49/mo)                        | Enterprise ($299/mo)                          |
|--------------------------|-----------------------|-------------------------------------|-----------------------------------------------|
| Support categories       | 3 (billing, technical, general) | 15 categories              | Unlimited categories                          |
| Sentiment analysis       | ❌                    | ✅                                  | ✅                                            |
| Priority routing         | ❌                    | ✅                                  | ✅                                            |
| CRM integration          | ❌                    | ✅                                  | ✅                                            |
| Custom AI training       | ❌                    | ❌                                  | ✅                                            |
| White-label              | ❌                    | ❌                                  | ✅                                            |
| SLA guarantees           | ❌                    | ❌                                  | ✅                                            |
| API webhooks             | ❌                    | ❌                                  | ✅                                            |
| Ticket escalation        | ❌                    | ✅ (support_team)                   | ✅ (dedicated_agent)                          |

## Usage

### Initialize the bot

```python
from bots.customer_support_bot.bot import CustomerSupportBot
from bots.customer_support_bot.tiers import get_customer_support_tier_info
from tiers import Tier  # from ai-models-integration

# Free tier (default)
bot = CustomerSupportBot()

# Pro tier
bot = CustomerSupportBot(tier=Tier.PRO)

# Enterprise tier
bot = CustomerSupportBot(tier=Tier.ENTERPRISE)
```

### Handle a support ticket

```python
ticket = {
    "id": "TICKET-001",
    "message": "My billing statement is incorrect and I'm very frustrated.",
    "category": "billing"
}

result = bot.handle_ticket(ticket)
print(result)
# {
#   "ticket_id": "TICKET-001",
#   "response": "Thank you for reaching out...",
#   "category": "billing",
#   "sentiment": "negative",    # PRO/ENTERPRISE only
#   "escalated": True,          # PRO/ENTERPRISE only
#   "tier": "pro"
# }
```

### Escalate a ticket

```python
# Requires PRO or ENTERPRISE
result = bot.escalate("TICKET-001")
print(result)
# {
#   "ticket_id": "TICKET-001",
#   "escalated": True,
#   "assigned_to": "dedicated_agent",  # "support_team" on PRO
#   "tier": "enterprise"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 5,
#   "requests_remaining": "995",
#   "buddy_integration": True
# }
```

### Get tier information

```python
info = get_customer_support_tier_info(Tier.PRO)
print(info)
# {
#   "tier": "pro",
#   "name": "Pro",
#   "price_usd_monthly": 49,
#   "requests_per_month": 1000,
#   "platform_features": [...],
#   "bot_features": ["15 support categories", "sentiment analysis", ...],
#   "support_level": "email"
# }
```

## License

MIT
