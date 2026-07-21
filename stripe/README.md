# Dreamcobots Stripe Integration

This directory contains Stripe SDK setup files for every supported language so that any Dreamcobots bot can accept payments, manage subscriptions, issue refunds, and handle webhooks.

---

## Quick Start (Python)

```bash
# Install the Python Stripe library
pip install stripe python-dotenv

# Copy the environment template and fill in your keys
cp ../.env.example ../.env
# Edit .env and set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET
```

```python
from bots.stripe_integration import StripeBot, WebhookHandler, PaymentLinks

# StripeBot auto-reads STRIPE_SECRET_KEY from the environment
bot = StripeBot()

# Create a customer
customer = bot.create_customer("buyer@example.com", "Jane Doe")

# Start a checkout session
session = bot.create_checkout_session(
    amount_cents=4999,        # $49.99
    currency="usd",
    customer_email="buyer@example.com",
    success_url="https://yourdomain.com/success",
    cancel_url="https://yourdomain.com/cancel",
)
print(session["checkout_url"])

# Create a shareable Payment Link
pl = PaymentLinks()
link = pl.create_link(2500, "usd", "Real Estate Lead Report")
print(link["url"])
```

---

## Environment Variables

Set these in your `.env` file (never commit real keys):

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | `sk_live_...` or `sk_test_...` from [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| `STRIPE_PUBLISHABLE_KEY` | `pk_live_...` or `pk_test_...` — safe for client-side code |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` — from Stripe Dashboard → Developers → Webhooks |

---

## Directory Structure

```
stripe/
├── node/           Node.js (stripe@14) — index.js, webhook.js
├── python/         Python (stripe>=5) — stripe_client.py
├── ruby/           Ruby (stripe ~10) — stripe_client.rb + Gemfile
├── php/            PHP (stripe-php ^13) — stripe_client.php + composer.json
├── go/             Go (stripe-go v76) — stripe_client.go + go.mod
├── java/           Java (stripe-java 25) — StripeClient.java + pom.xml
├── dotnet/         .NET 8 (Stripe.net 45) — StripeClient.cs + .csproj
├── ios/            iOS Swift (Stripe ~23) — StripeClient.swift + Podfile
└── android/        Android Kotlin (stripe-android 20+) — StripeClient.kt
```

---

## Webhook Setup

### 1. Expose your local server (development)
```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:4242/webhook
```

### 2. Register your handler (Python)
```python
from bots.stripe_integration import WebhookHandler

handler = WebhookHandler()  # reads STRIPE_WEBHOOK_SECRET from env

@handler.on("payment_intent.succeeded")
def on_payment(event):
    pi = event["data"]["object"]
    print(f"Payment succeeded: {pi['id']} — {pi['amount']} {pi['currency'].upper()}")

# In your Flask/FastAPI route:
# result = handler.handle_event(request.get_data(), request.headers["Stripe-Signature"])
```

### 3. Register your endpoint in Stripe
Go to **Stripe Dashboard → Developers → Webhooks → Add endpoint** and point it at `https://yourdomain.com/webhook`.

Recommended events to subscribe to:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `payout.paid`

---

## Node.js Setup

```bash
cd stripe/node
npm install
# Start webhook server (forwarded by Stripe CLI)
node webhook.js
```

---

## Testing

```bash
# Python tests
python -m pytest tests/test_stripe_integration.py -v

# Trigger test events with Stripe CLI
stripe trigger payment_intent.succeeded
stripe trigger checkout.session.completed
```

---

## Language-Specific Setup

### Ruby
```bash
cd stripe/ruby && bundle install
```

### PHP
```bash
cd stripe/php && composer install
```

### Go
```bash
cd stripe/go && go mod tidy
```

### Java
```bash
cd stripe/java && mvn package
```

### .NET
```bash
cd stripe/dotnet && dotnet restore && dotnet run
```

### iOS
```bash
cd stripe/ios && pod install
# Then open the generated .xcworkspace in Xcode
```

### Android
Add to your `app/build.gradle`:
```groovy
implementation 'com.stripe:stripe-android:20.+'
```

---

## Security Notes

- **Never** commit your `.env` file or any file containing `sk_live_...` keys.
- The `.gitignore` is configured to exclude `.env` and language-specific dependency directories.
- On iOS and Android, only use the **publishable key** (`pk_live_...`) — fetch client secrets from your backend.
- Validate every webhook using the `STRIPE_WEBHOOK_SECRET` to prevent spoofed events.
