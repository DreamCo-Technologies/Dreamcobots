# Monetization-ready bot standard

A DreamCo bot is **not complete** merely because it can scrape, classify, or generate an answer.

## Required production contract
1. Source adapter with permitted access.
2. Normalized schema and deduplication key.
3. Freshness timestamp and source URL/identifier.
4. Verification and confidence score.
5. Economics calculation including fees/costs where applicable.
6. Ranking and user-fit logic.
7. Clear user action and handoff.
8. Monetization attribution.
9. Outcome tracking.
10. Revenue reconciliation.
11. Retry/backoff and failure handling.
12. Metrics and health status.
13. Privacy/secret handling.
14. Terms/compliance guardrails.
15. Tests for happy path, stale data, duplicate data, source failure, and zero/negative economics.

## Bot maturity levels
- L0: concept only.
- L1: prototype/data fixture.
- L2: source-connected.
- L3: verified opportunity production.
- L4: monetization-attributed.
- L5: outcome-reconciled and self-monitoring.

Money OS should prioritize upgrading existing L1/L2 bots to L4/L5 before multiplying the number of bots.
