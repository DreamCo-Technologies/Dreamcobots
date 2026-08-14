# Buddy Bank-Agnostic Best-Deal Policy

Buddy should help a merchant choose among **any supported bank, processor, acquirer, or payment account** rather than steering the merchant to a preferred institution merely because DreamCo earns more from it.

## Policy

1. Merchant chooses or authorizes eligible financial institutions/providers.
2. Buddy collects only the minimum data required to compare offers.
3. Normalize pricing, APY/fees where relevant, payment-processing costs, limits, settlement timing, and service terms.
4. Calculate total economic value, not headline rate alone.
5. Show the merchant the top options and the assumptions behind each result.
6. Separate projected savings from verified savings.
7. Disclose commissions/referral economics before enrollment.
8. Require explicit merchant approval before opening, switching, routing, or enrolling in a financial service.
9. Keep provider integrations modular so the merchant is not locked to one bank.
10. Re-run comparisons periodically because pricing and eligibility change.

## Best-deal score

`total merchant value = savings + operational value + reliability value - fees - switching costs - risk adjustments`

The highest DreamCo commission must never automatically win.

## Provider-neutrality test

For every recommendation, the benchmark system should be able to answer:

- Which providers were eligible?
- Which providers were actually compared?
- What data was used?
- What fees were included?
- What assumptions were made?
- What does the merchant save?
- What does DreamCo earn?
- Would the recommendation change if DreamCo's commission were zero?

That last question is a core conflict-of-interest test.

## Scope

This policy supports bank-agnostic merchant tooling. It does not itself make Buddy a bank, lender, money transmitter, card network, or regulated financial institution. Live financial-product enrollment and movement of funds must use appropriately authorized providers and comply with applicable law and contractual requirements.
