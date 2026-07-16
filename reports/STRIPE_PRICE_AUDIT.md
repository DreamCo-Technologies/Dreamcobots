# Stripe Price Audit

- Repository prices: 1402
- Generated Stripe offers: 1402
- Paid Stripe offers: 109
- Free offers: 1293
- Live-ready paid offers: 0
- Missing live Stripe ID offers: 109
- Prices match generated Stripe catalog: True
- Secret values stored in repo: False

## Policy

Every repository sellable price must have a generated Stripe draft offer with the same amount in cents.

Generated draft offers are not live until Stripe Price IDs and Payment Link IDs are added from a secure Stripe account setup.

## Catalog Files

- price_map: data/stripe/repository-price-map.json
- generated_offers: data/stripe/offers.generated.json
- template_offers: data/stripe/offers.template.json
