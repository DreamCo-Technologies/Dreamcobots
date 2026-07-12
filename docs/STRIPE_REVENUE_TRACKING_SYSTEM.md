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

## Revenue rescue command

Run the local rescue scan whenever Stripe is connected but revenue is still zero:

```bash
npm run report:stripe-rescue
```

This generates:

- `reports/STRIPE_REVENUE_RESCUE_REPORT.md`
- `reports/stripe_revenue_rescue_report.json`

The rescue report checks:

- whether offers are live/published;
- whether each offer has a Stripe price ID and payment link ID;
- whether local webhook events are being recorded;
- whether successful payments or paid invoices are tracked;
- whether customer-facing checkout buttons appear to use verified live payment links;
- whether this runtime has Stripe secret and webhook variables configured.

The report never prints secret values. Keep Stripe keys in environment variables, GitHub secrets, Hostinger secrets, or the hosting provider's secure secret store.

## Current likely blocker pattern

If `checkout_ready_offers` is `0`, customers do not have a verified live Stripe offer to buy through this system. Fix that before changing prices or adding more bots:

1. Create or confirm live Stripe Products and Prices.
2. Create live Stripe Payment Links for the top offers.
3. Store live price/payment link IDs in a private production offer catalog or environment-backed config.
4. Update customer-facing CTA buttons to use those verified live payment links.
5. Deploy the Stripe webhook endpoint over HTTPS.
6. Subscribe the webhook to checkout, payment, invoice, subscription, and payout events.
7. Run one low-dollar live checkout test you control.
8. Confirm the report shows `checkout_completed > 0` and `gross_revenue_cents > 0`.
