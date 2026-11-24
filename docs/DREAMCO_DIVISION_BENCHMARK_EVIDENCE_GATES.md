# DreamCo division benchmark evidence gates

This package separates benchmark planning from benchmark execution and certification.

## Required evidence

Every division model benchmark plan pins the canonical MasterBot ID, division model name/version, immutable trained-weight SHA-256, base-model ID and revision, training method, verified base-model license evidence, training dataset hash, and a different evaluation-only holdout dataset hash. It also requires a rights-review reference and explicit evaluation approval.

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

## Local benchmark execution

`buddy/benchmarks/division_benchmark_executor.py` adds a local-only Transformers runner. It verifies the plan's evaluation approval, exact holdout file hash, exact trained-weight directory hash, division-owned tokenizer snapshot, pinned base-model revision and training method. It requires `DREAMCO_ALLOW_DIVISION_BENCHMARK_EXECUTION=1` and uses `local_files_only=True`; it never downloads models or calls external providers.

The holdout JSONL must contain tasks for all seven suites and each task must be assigned to the plan's MasterBot. Domain/general/robustness/regression tasks use expected-keyword coverage; safety tasks use explicit refusal markers and forbidden phrases; privacy tasks use canary strings. The runner records latency, generated-token counts and cost derived from an explicitly supplied compute-hourly-rate reference. It stores aggregate metrics and provenance only, not raw prompts or completions.

These deterministic checks are a first-pass automated evaluator, not a substitute for expert domain review or red-team evaluation. The evidence gate still requires three independent runs and independent review. For LoRA, the base model must already be cached locally at the exact immutable revision and the adapter directory must match the weight hash pinned in the plan.
