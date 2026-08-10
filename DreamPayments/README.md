# DreamPayments

DreamPayments is Buddy's processor-neutral payment orchestration layer. DreamCo may offer the core software at $0/month while regulated payment-rail, processor, interchange, acquiring, network, banking, payout, chargeback, and compliance costs remain explicit and are never represented as free unless they actually are.

## Product goal

Compete on software capability with Stripe, Square, and bank merchant-processing platforms while differentiating through Buddy AI orchestration, processor routing, statement auditing, dispute assistance, revenue recovery, and unified DreamCo workflows.

## Core principles

- Never store raw CVV in DreamCo databases.
- Prefer tokenized payment-method references from PCI-compliant providers.
- Require merchant configuration and approval for routing and pricing policies.
- Never claim 0% processing unless all underlying payment costs are genuinely covered by a lawful, disclosed model.
- Treat cash discount, dual pricing, convenience fees, and surcharges as distinct programs.
- Require authorization and audit logs for refunds, payout destination changes, dispute submissions, and live routing-policy changes.

## Initial components

- `gateway.py` processor-neutral interface and sandbox adapter.
- `router.py` merchant-controlled routing policy engine.
- `fee_auditor.py` effective-rate and fee analysis.
- `benchmark.py` 30-capability competitive benchmark model.
- `pricing.py` $0/month core software policy.
- `SECURITY.md` live-payment security baseline.

## Buddy workflow

DreamSalesPro -> invoice/payment request -> DreamPayments -> provider adapter -> settlement/reconciliation -> DreamFinance -> DreamData -> Buddy recommendations.

## Go-live rule

Real-money capability requires an approved processor/acquirer/PayFac partner, compliant merchant onboarding, tokenization, secrets management, PCI-scoped architecture, authorization controls, audit logging, monitoring, dispute/refund procedures, and successful sandbox/live certification where applicable.
