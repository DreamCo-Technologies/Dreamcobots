# Stripe Integration Guide

This document explains how to configure and use the Stripe payment integration
in Dreamcobots.

---

## Overview

Dreamcobots integrates Stripe through two complementary modules:

| Module | Purpose |
|--------|---------|
| `bots/stripe_payment_bot/` | Tier-aware payment bot — checkout sessions, subscriptions, coupons, invoices, Connect split payments, fraud radar, analytics |
| `saas/stripe_billing.py` | SaaS subscription lifecycle management (create, upgrade, cancel, webhooks) |

Both modules operate in **simulation mode** when the Stripe SDK is not
configured, so the rest of the system keeps working in development without
live credentials.

---

## Environment Variables

Set the following secrets in GitHub Actions (Settings → Secrets → Actions)
and in your local `.env` file (never commit the `.env` file):

| Variable | Description | Example |
|----------|-------------|---------|
| `STRIPE_API_KEY` | Secret API key — server-side only | `paste-your-stripe-secret-key` |
| `STRIPE_PUBLISHABLE_KEY` | Publishable key — safe for client-side use | `pk_live_…` / `pk_test_…` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret from Stripe dashboard | `whsec_…` |
| `STRIPE_PRICE_PRO` | Stripe Price ID for the PRO plan | `price_pro_monthly` |
| `STRIPE_PRICE_ENTERPRISE` | Stripe Price ID for the ENTERPRISE plan | `price_enterprise_monthly` |

> **Security note:** Never commit API keys or webhook secrets to source
> control. Use GitHub Actions secrets or a secrets manager (e.g. AWS
> Secrets Manager, HashiCorp Vault).

---

## Local Setup

1. **Install the Stripe SDK** (included in `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the repo root (already in `.gitignore`):

   ```dotenv
   STRIPE_API_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_PRO=price_...
   STRIPE_PRICE_ENTERPRISE=price_...
   ```

3. **Load the environment** before running the app:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## GitHub Actions Secrets

Add the secrets via the GitHub UI or the `gh` CLI:

```bash
gh secret set STRIPE_API_KEY       --body "sk_test_..."
gh secret set STRIPE_WEBHOOK_SECRET --body "whsec_..."
gh secret set STRIPE_PRICE_PRO     --body "price_..."
gh secret set STRIPE_PRICE_ENTERPRISE --body "price_..."
```

The CI workflow (`.github/workflows/ci.yml`) passes these secrets as
environment variables to the test runner so integration tests can exercise
real Stripe sandbox calls when credentials are available, and fall back to
simulation mode when they are not.

---

## Key Features

### Payment Capture (one-time checkout)

```python
from bots.stripe_payment_bot.stripe_payment_bot import StripePaymentBot
from bots.stripe_payment_bot.tiers import Tier

bot = StripePaymentBot(tier=Tier.STARTER)
session = bot.create_checkout_session(
    amount=99.0,
    currency="USD",
    product_name="DreamCo Bot Access",
    customer_email="customer@example.com",
)
# session["url"] → redirect the customer here
```

### Subscription Management

```python
from bots.stripe_payment_bot.stripe_payment_bot import StripePaymentBot
from bots.stripe_payment_bot.tiers import Tier

bot = StripePaymentBot(tier=Tier.GROWTH)

# Create subscription
sub = bot.create_subscription(customer_id="cus_xxx", plan_id="lead_generator_pro")

# Cancel subscription
result = bot.cancel_subscription(subscription_id=sub["id"])
```

### Webhook Handling

Register your webhook endpoint with Stripe, then verify and process events:

```python
from saas.stripe_billing import StripeBillingService

billing = StripeBillingService()

# In your Flask/FastAPI route handler:
result = billing.handle_webhook(
    payload=request.get_data(),          # raw bytes
    sig_header=request.headers.get("Stripe-Signature"),
)
if not result["success"]:
    return {"error": result["error"]}, 400
```

Supported webhook events:
- `customer.subscription.updated` — tier change
- `invoice.payment_succeeded` — logs revenue
- `customer.subscription.deleted` — cancellation

### SaaS Billing Lifecycle

```python
from saas.stripe_billing import StripeBillingService

billing = StripeBillingService()

# Create customer
customer = billing.create_customer(user_id="usr_001", email="user@example.com")

# Subscribe to a tier
sub = billing.create_subscription(
    customer_id=customer["customer_id"],
    tier="pro",
    user_id="usr_001",
)

# Upgrade tier
billing.upgrade_subscription(
    subscription_id=sub["subscription_id"],
    new_tier="enterprise",
    user_id="usr_001",
)

# Revenue report
summary = billing.revenue_summary()
```

---

## Running the Tests

```bash
# Stripe payment bot tests (94 tests, simulation mode)
python -m pytest tests/test_stripe_payment_bot.py -v

# SaaS / Stripe billing tests
python -m pytest tests/test_stripe_billing.py -v

# Full test suite
python -m pytest tests/ \
  --ignore=tests/test_backend.py \
  --ignore=tests/test_web_dashboard.py \
  -q
```

---

## Tier Capabilities

| Feature | STARTER ($29/mo) | GROWTH ($99/mo) | ENTERPRISE ($299/mo) |
|---------|:-:|:-:|:-:|
| Checkout sessions | ✓ | ✓ | ✓ |
| Refunds | ✓ | ✓ | ✓ |
| Subscriptions | — | ✓ | ✓ |
| Webhooks | — | ✓ | ✓ |
| Coupons | — | ✓ | ✓ |
| Invoices | — | ✓ | ✓ |
| Analytics | — | ✓ | ✓ |
| Stripe Connect | — | — | ✓ |
| Split payments | — | — | ✓ |
| Fraud Radar | — | — | ✓ |
| White-label | — | — | ✓ |
| SLA guarantee | — | — | ✓ |
