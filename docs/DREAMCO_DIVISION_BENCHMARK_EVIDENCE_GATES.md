# DreamCo division benchmark evidence gates

This package separates benchmark planning from benchmark execution and certification.

## Required evidence

Every division model benchmark plan pins the canonical MasterBot ID, division model name/version, immutable trained-weight SHA-256, training dataset hash, and a different evaluation-only holdout dataset hash. It also requires a rights-review reference and explicit evaluation approval.

A complete evidence bundle contains at least three independent runs with unique run IDs and seeds. Each run is tied to a commit SHA, workflow run ID, evaluator identity, exact weight hash, and exact holdout hash. The required suites are:
- domain-task quality;
- general capability;
- safety critical-violation count;
- privacy leakage count;
- robustness;
- regression;
- performance, including p95 latency and cost per 1,000 tokens.

Default acceptance floors are domain 0.90, general 0.80, robustness 0.85, zero critical safety violations, zero privacy leaks, passing regression, p95 latency at or below 10 seconds, and cost at or below $5 per 1,000 tokens. These are starter gates, not universal production SLOs; divisions must set stricter domain-appropriate limits before certification.

## Promotion behavior

The validator returns `BENCHMARKED_READY_FOR_INDEPENDENT_REVIEW` only when all required evidence passes. It never marks a model certified or deployed. Independent reviewer sign-off, model-card review, runtime health evidence, rollback readiness and a separate production approval remain mandatory.

## Truth boundary

The validator does not run inference or generate benchmark scores. A fabricated JSON evidence object can pass structural validation, so evidence must be collected by trusted benchmark runners and linked to immutable workflow artifacts. CI tests only the validator logic. The real benchmark execution phase must bind this contract to model inference, protected holdout access controls, and durable evidence storage.
