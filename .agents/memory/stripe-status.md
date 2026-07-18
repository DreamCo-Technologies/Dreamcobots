---
name: Stripe integration status
description: Stripe code is fully wired; activation requires user to add STRIPE_SECRET_KEY + STRIPE_PUBLISHABLE_KEY as Replit secrets.
---
**Why:** stripeClient.ts uses env var fallback pattern; products are synced in DB. Checkout endpoint is live at /api/stripe/checkout.

**How to apply:** Once user adds the two secrets, checkout is immediately live — no code changes needed.

Pricing tiers in DB: Free/$0, Pro/$299/mo, Enterprise/$999/mo, Elite/$2,499/mo (with yearly toggle at 20% off).
Checkout flow: Buy button → /api/stripe/checkout → Stripe-hosted payment page → return to app.
Customer portal: /api/stripe/portal for subscription management.
