# Buddy Learning

Buddy's learning system separates **evidence collection** from **mastery claims**.

## Pipeline

- `action_failure_learning.py` — stable signatures and failure taxonomy.
- `benchmark_progress.py` — pass-rate/native-pass-rate calculations and mastery gating.
- `benchmark_learning_policy.json` — repeated-pass, holdout, regression, and dependency policy.
- `LEARNING_FROM_FAILURES.md` — failure-to-retest evidence contract.
- `record_buddy_benchmark_learning.py` — converts deterministic benchmark output into durable evidence.
- `study_resource_scheduler.py` — selects the next study source from unresolved capability gaps.
- `study_data_schema.json` — categorizes study evidence for authorized future training/reuse.

The benchmark runner remains the source of truth for benchmark execution. The recorder only serializes its result for later comparison; it does not execute untrusted output or alter production code.

## Mastery

A passing run is not automatically mastery. Buddy's policy requires repeated native passes, an independent holdout, and regression protection before a capability is promoted.

## Adaptive study loop

`benchmark failure -> capability gap -> rank resources -> study authorized material -> sandbox practice -> targeted retest -> holdout -> regression -> mastery`

The Top-1000 study curriculum is separate from the protected DreamCo model catalog. Resources are ranked by relevance to failures, technical authority, hands-on value and freshness. Study evidence is categorized by source, capability, material type, benchmark and provenance so authorized learning artifacts can later support other users/models without exposing private/client data.
