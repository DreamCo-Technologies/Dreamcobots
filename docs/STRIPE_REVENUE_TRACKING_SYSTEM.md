# DreamCo Stripe Revenue Tracking System

This system makes Stripe accountable to DreamCo bots, offers, workflows, and reports. It does not guarantee revenue; it shows exactly whether payments, subscriptions, invoices, failures, and payouts are happening.

## Why this exists

Having a Stripe account is not enough. DreamCo needs to know:

- Which bot created the offer.
- Which offer got paid.
- Which workflow brought the customer.
- Which payments failed.
- Which subscriptions started or canceled.
- Whether webhooks are delivering.
- Whether payouts are happening.

## Required Stripe metadata

Every Stripe checkout session, payment link, price, subscription, refund, and invoice path should carry:

| Metadata key | Example | Purpose |
| --- | --- | --- |
| `bot_id` | `buddy_bot` | Shows which bot owns the money path |
| `offer_id` | `dreamco-starter-audit` | Shows which offer is selling |
| `workflow_id` | `audit_and_repair` | Shows which workflow produced the sale |
| `source` | `checkout_session` | Shows where the Stripe object came from |

## Files added

| File | Purpose |
| --- | --- |
| `stripe/node/revenue-ledger.js` | Records Stripe events into JSON summaries |
| `stripe/node/revenue-report.js` | Generates a Markdown revenue report |
| `data/stripe/offers.template.json` | Starter offer catalog for bots |
| `reports/stripe-revenue-report.md` | Generated report output |

## Webhook events tracked

- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `payout.paid`

## Commands

```bash
cd stripe/node
npm install
node webhook.js
node revenue-report.js
```

## Production checklist

1. Confirm Stripe is in live mode.
2. Confirm live products and prices exist.
3. Confirm every bot offer has an `offerId` in `data/stripe/offers.template.json` or the production offer catalog.
4. Confirm all checkout/payment links include DreamCo metadata.
5. Add the webhook endpoint in Stripe Dashboard.
6. Subscribe the webhook to all tracked events.
7. Confirm webhook deliveries in Stripe Dashboard.
8. Confirm `reports/stripe-revenue-report.md` updates after test events.
9. Review failed payments weekly.
10. Review payout status weekly.

## No-money diagnosis

If revenue is zero after months, check these in order:

1. Are links live, published, and reachable by customers?
2. Are products/prices in live mode or only test mode?
3. Did any checkout sessions complete?
4. Are webhook events arriving?
5. Are invoices failing?
6. Are customers being sent to a broken success/cancel URL?
7. Is the bank account verified for payouts?
8. Are bots actually creating offers and sending payment links?
9. Are offers clear enough for customers to buy?
10. Is every bot tied to a measurable sales workflow?
