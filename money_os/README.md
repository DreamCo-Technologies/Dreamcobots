# DreamCo Money OS

Revenue orchestration layer for the existing DreamCo bot fleet. It does not pretend that a data source is live: adapters must provide current, attributable data before an opportunity is published.

## Coverage

- Deals: price drops, coupons, clearance and penny-price alerts.
- Receipts: OCR/matching adapter interface and reward tracking.
- Legal money: class actions, settlements and unclaimed-money discovery with eligibility verification and user confirmation before submission.
- Work: leads, Fiverr/job opportunities and application tracking.
- Government: grants and contracts.
- Property: real-estate opportunity scoring.
- Resale: marketplace/auction opportunity scoring.
- Revenue: affiliate attribution, subscriptions, qualified leads and marketplace fees.

## Existing bot integration

The repository already contains a large bot fleet, including the named bots supplied by the product owner. This layer is an integration contract rather than a destructive rewrite: each existing bot should register an adapter that emits the normalized opportunity shape consumed by `money_os/core.js`.

Required adapter contract:

```js
export async function scan(context) {
  return [{
    id, category, title, source, url,
    price, coupon, cashback, fees, shipping, resale,
    confidence, effort, freshness
  }];
}
```

## Monetization loop

`discover -> verify -> score -> rank -> publish -> click/claim -> conversion -> revenue reconciliation -> learning`

Never label estimated savings, resale value, settlement amounts, or affiliate commissions as guaranteed income.

## Deploy

1. Use Node 20+.
2. `cd money_os && npm install`.
3. `npm start`.
4. Configure real source adapters and secrets outside Git.
5. Run the repository's validation/CI suite before production promotion.

The frontend should consume `/health`, `/bots`, and `/opportunities`; a FlutterFlow project can be generated from this API contract, but FlutterFlow's proprietary project export is not fabricated in this repository.

## Security

Keep API keys, affiliate credentials, payout credentials and OCR credentials in environment/secret storage. Do not commit secrets. Legal claims require explicit user confirmation and should link to the authoritative settlement administrator/court notice.
