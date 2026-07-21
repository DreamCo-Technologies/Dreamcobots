# DreamCo Payments Bot

A tier-aware payment processing bot for the DreamCo ecosystem. Handles
one-time payments, subscriptions, currency conversion, fraud detection,
API key management, and a Discount Dominator settings dashboard.

## Tiers

| Feature | Starter ($29/mo) | Growth ($99/mo) | Enterprise ($299/mo) |
|---|---|---|---|
| Transactions/month | 1,000 | 10,000 | Unlimited |
| Payment processing | ✅ | ✅ | ✅ |
| Basic subscriptions | ✅ | ✅ | ✅ |
| Refunds | ✅ | ✅ | ✅ |
| API key management | ✅ | ✅ | ✅ |
| Currency conversion | ❌ | ✅ | ✅ |
| Recurring billing | ❌ | ✅ | ✅ |
| Fraud detection | ❌ | ✅ | ✅ |
| Analytics dashboard | ❌ | ✅ | ✅ |
| Discount Dominator | view only | view + update | view + update |
| Custom user limits | ❌ | ❌ | ✅ |
| Advanced exports (CSV/PDF) | ❌ | ❌ | ✅ |
| Real-estate automation | ❌ | ❌ | ✅ |
| Auto-dealer automation | ❌ | ❌ | ✅ |
| Support | Community | Email 24h SLA | Dedicated 24/7 |

## Quick Start

```python
from bots.dreamco_payments import DreamcoPaymentsBot, Tier

# Create a Growth-tier bot
bot = DreamcoPaymentsBot(tier=Tier.GROWTH)

# Process a payment
result = bot.process_payment(99.99, "USD", "card_visa_4242", "cust_001")
print(result["transaction_id"])

# Convert currency
conv = bot.convert_currency(100.0, "USD", "EUR")
print(f"100 USD = {conv['converted_amount']} EUR")

# Create a subscription
sub = bot.create_subscription("cust_001", "plan_growth", 99.0, "USD", "monthly")

# Detect fraud
risk = bot.detect_fraud({"amount": 50_000, "currency": "USD"})
print(risk["risk_level"])  # "high"

# Describe your current tier
print(bot.describe_tier())
```

## Supported Currencies

USD, EUR, GBP, CAD, AUD, JPY, MXN — suitable for real-estate and
car-flipping markets worldwide.

## Business Types

When onboarding users, set `business_type` to unlock specialist hints:

- `"standard"` — General merchant
- `"real_estate"` — Real-estate flipping automation hints
- `"auto_dealer"` — Car-flipping automation hints

```python
bot.onboard_user("u1", "Jane Doe", "jane@re.com", business_type="real_estate")
```

## Discount Dominator Settings (401–600)

| Group | IDs | Count |
|---|---|---|
| analytics | 401–450 | 50 |
| in_store | 451–500 | 50 |
| online | 501–550 | 50 |
| enterprise | 551–580 | 30 |
| behavioral | 581–600 | 20 |

```python
# View a setting (all tiers)
setting = bot.get_discount_dominator_settings(401)

# Update a setting (Growth+ only)
bot.update_discount_dominator_setting(401, False)
```

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.dreamco_payments import DreamcoPaymentsBot, Tier

buddy = BuddyBot()
payments_bot = DreamcoPaymentsBot(Tier.GROWTH)
payments_bot.register_with_buddy(buddy)

# Route a message directly
response = buddy.route_message("dreamco_payments", "What currencies do you support?")
print(response["response"])
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DREAMCO_STRIPE_KEY` | `sk_test_placeholder_dreamco_stripe_key` | Stripe integration key (placeholder only) |

## Running Tests

```bash
cd /path/to/Dreamcobots
python -m pytest tests/test_dreamco_payments.py -v
```
