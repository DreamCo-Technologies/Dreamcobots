# Stripe Revenue Rescue Report

- Generated: 2026-07-17T14:23:28Z
- Rescue ready: False
- Checkout-ready offers: 0/2
- Tracked Stripe events: 0
- Gross tracked revenue: $0.00
- Refund events: 0
- Refunded amount tracked: $0.00
- Disputes created: 0
- Disputed amount tracked: $0.00
- Payouts paid: 0
- Payouts failed: 0
- Payment email recipients configured: 0
- Payment email notices tracked: 0
- GitHub payment notifications enabled: False
- GitHub payment issues created: 0
- Blockers: 9

## Revenue Blockers

- No checkout-ready live Stripe offers with price and payment link IDs.
- No Stripe webhook events are recorded locally.
- No successful payment or paid invoice revenue is tracked.
- Customer CTA buttons are not mapped to verified live Stripe Payment Links.
- STRIPE_SECRET_KEY is not configured in this runtime.
- STRIPE_WEBHOOK_SECRET is not configured in this runtime.
- Payment alert email recipients are not configured.
- Payment email provider is not configured.
- GitHub payment notifications are not enabled.

## Priority Fixes

1. Set STRIPE_PAYMENT_ALERT_EMAILS or PAYMENT_ALERT_EMAILS to the owner email list that should receive every payment notice.
2. Configure PAYMENT_EMAIL_PROVIDER=resend plus RESEND_API_KEY and PAYMENT_EMAIL_FROM, or connect another production email provider.
3. For GitHub payment alerts, set PAYMENT_GITHUB_NOTIFICATIONS=true, PAYMENT_GITHUB_REPOSITORY=DreamCo-Technologies/Dreamcobots, and PAYMENT_GITHUB_TOKEN or GITHUB_TOKEN with issue-write access.
4. Create or confirm two live Stripe Payment Links for the starter audit and monthly command center offers.
5. Put the live Stripe price/payment link IDs in a private production offer catalog or environment-backed config.
6. Update customer-facing CTA buttons to use verified live Stripe Payment Links, not generic placeholder checkout routes.
7. Deploy the webhook endpoint over HTTPS and subscribe it to checkout, payment, invoice, subscription, and payout events.
8. Send one $1 live-mode internal checkout test, then confirm the rescue report shows checkoutCompleted > 0 and grossRevenueCents > 0.
9. Review the Stripe Dashboard for failed payments, disabled payouts, test-mode products, and broken success/cancel URLs.

## Offer Readiness

- `dreamco-starter-audit`: status=draft, price_id=False, payment_link=False, ready=False
- `dreamco-monthly-command-center`: status=draft, price_id=False, payment_link=False, ready=False

## Payment Email Notifications

- Provider: missing
- Recipients configured: 0
- Outbox notices: 0
- Sent notices: 0
- Queued notices: 0
- Blocked notices: 0
- GitHub notifications enabled: False
- GitHub repository configured: False
- GitHub token configured: False
- GitHub issues created: 0
