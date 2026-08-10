# DreamPayments Competitive Benchmark

This is a benchmark specification, not a claim that every target is production-ready.

## Benchmark peers

- Stripe: APIs, subscriptions, marketplace payments, global payments, developer tooling, fraud/risk, issuing.
- Square: POS, Tap to Pay, retail workflows, invoices, inventory, CRM, small-business usability.
- Bank merchant processing: settlement, banking integration, relationship-based merchant services, deposits, support.
- Buddy / DreamPayments: target is equivalent software coverage plus processor-neutral orchestration and AI automation.

## 30 capability scorecard

Use 0 = missing, 1 = partial, 2 = strong. Every Buddy score needs automated tests, integration evidence, or telemetry before being promoted from target to verified.

1. Online card payments
2. In-person POS
3. Tap to Pay
4. Payment links
5. Invoices
6. Recurring billing
7. Subscriptions
8. Marketplace/split payments
9. Developer APIs
10. Webhooks
11. Refunds
12. Disputes/chargebacks
13. Fraud detection
14. Inventory
15. Customer CRM
16. Employee management
17. Multi-location
18. Digital wallets
19. Fast deposits
20. Business banking
21. Card issuing
22. International payments
23. Processor routing
24. Statement fee auditing
25. AI dispute assistance
26. AI revenue recovery
27. AI payment assistant
28. Reconciliation
29. Analytics
30. Sandbox testing

## Buddy differentiation requirements

- Processor-neutral adapter layer.
- Merchant-controlled routing by cost, reliability, latency, geography, payment method, and risk.
- Fee Auditor for effective-rate and statement-cost analysis.
- Buddy workflows for invoices, links, refunds, dispute evidence, and reporting with authorization gates.
- Unified DreamSalesPro -> DreamPayments -> DreamFinance -> DreamData -> Buddy workflow.
- $0/month core DreamCo software option with third-party rail costs disclosed separately.
- ComplianceGuard preventing raw CVV storage and misleading free-processing claims.
- Continuous status labels: VERIFIED, PARTIAL, DISCONNECTED, TARGET-ONLY.

## Production verification gates

A capability is not production-ready because a class or UI exists. Real-money processing requires approved regulated partners, compliant merchant onboarding, tokenization, secrets management, PCI-scoped architecture, authorization controls, audit logging, monitoring, incident response, dispute/refund procedures, and sandbox/live certification where applicable.
