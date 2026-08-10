# DreamPayments Security Baseline

DreamPayments must treat payment credentials as high-risk regulated data.

- Never accept or persist raw CVV.
- Avoid storing raw PAN; use provider tokenization, hosted fields, or certified terminal SDKs.
- Encrypt secrets using the deployment platform's secret manager; never commit keys.
- Require idempotency keys for money-moving API calls.
- Require explicit authorization for refunds, payout destination changes, dispute submissions, and live routing changes.
- Maintain append-only audit events for sensitive operations.
- Separate sandbox and live credentials and prevent accidental cross-mode use.
- Add rate limits, fraud/velocity rules, webhook signature verification, replay protection, and least-privilege service credentials before live payments.
- Complete PCI scope review and processor certification before claiming production readiness.
