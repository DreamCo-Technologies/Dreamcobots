# Buddy Learning

Buddy's learning system separates **evidence collection** from **mastery claims**.

## Pipeline

- `action_failure_learning.py` — stable signatures and failure taxonomy.
- `benchmark_progress.py` — pass-rate/native-pass-rate calculations and mastery gating.
- `benchmark_learning_policy.json` — repeated-pass, holdout, regression, and dependency policy.
- `LEARNING_FROM_FAILURES.md` — failure-to-retest evidence contract.
- `record_buddy_benchmark_learning.py` — converts deterministic benchmark output into durable evidence.

The benchmark runner remains the source of truth for benchmark execution. The recorder only serializes its result for later comparison; it does not execute untrusted output or alter production code.

## Mastery

A passing run is not automatically mastery. Buddy's policy requires repeated native passes, an independent holdout, and regression protection before a capability is promoted.
