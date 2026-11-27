# DreamCo Free GitHub Execution Plan

**Operating target:** $0 in required subscriptions and paid model/API calls.

**Scope:** GitHub-hosted CI validates repository code and evidence contracts. Real model inference and weight downloads run only on an explicitly approved local/self-hosted machine or another separately approved compute source. This plan does not promise unlimited free compute.

## Free-first operating model

| Workload | Default execution location | Cost control |
|---|---|---|
| Python unit tests, JSON/schema checks, static validation | GitHub Actions hosted runner | Standard CI only; no model downloads or paid APIs |
| Pull request checks and evidence validation | GitHub Actions hosted runner | Read-only token permissions; no secrets exposed to fork PRs |
| Model inference and 500-model sweeps | User-controlled local machine / self-hosted runner | Off by default; explicit job and compute approval required |
| Open-weight model storage | Local disk or user-selected free storage | Pin revisions and verify licenses; no automatic bulk downloads |
| Failure replay and learning records | Repository fixtures for tests; local SQLite for operational history | Redact secrets and personal data; do not commit private traces |
| Reports and leaderboard snapshots | Small JSON/Markdown artifacts | Retain only compact, reproducible evidence |
| Bootcamp lessons | Clean-room JSONL fixtures | Only verified, rights-cleared and human-reviewed lessons can be promoted |

## What the free CI workflow does

`.github/workflows/dreamco-free-ci.yml` runs on relevant pull requests or manual dispatch. It:

1. Compiles the evidence-first benchmark modules.
2. Runs the standard-library unit tests.
3. Confirms that the 10-pillar roadmap contains 100 uniquely identified planned upgrades.
4. Checks the generated 65-division model lifecycle manifest against its canonical sources.
5. Executes the 500-model readiness recorder and asserts that it makes zero provider calls, starts no execution, and reports zero verified results.
6. Checks patch whitespace.

The workflow deliberately does **not** download model weights, invoke external inference APIs, train models, or manufacture benchmark scores. It is a low-cost engineering gate, not a 500-model benchmark run.

## How to run it

- Open the repository's **Actions** tab.
- Select **DreamCo Free CI and Benchmark Safety Gate**.
- Choose **Run workflow** on the intended branch.
- Review every job result before merging the pull request.

A pull request from an untrusted fork must never receive secrets or write permissions. Keep workflow permissions at the minimum required level.

## Local model execution without paid APIs

For actual open-weight model tests, use a computer you control:

1. Install a local runtime such as Ollama or llama.cpp.
2. Download only models whose licenses and revisions have been reviewed.
3. Create a benchmark manifest through DreamCo's existing dataset hub and benchmark-job tools.
4. Record an explicit compute approval ID and a resource budget.
5. Run the existing benchmark runner with its explicit execution flags.
6. Preserve per-model results, failures, resource use, model revision, dataset revision, and evidence hashes.
7. Upload only reviewed, redacted summary evidence to the repository.

A self-hosted GitHub Actions runner can automate this later. Register it only on a machine you control, isolate it from sensitive personal files, and do not let untrusted pull-request code execute on it. Do not leave a privileged self-hosted runner online for arbitrary public PRs.

## 500-model execution policy

The number **500** is a target capacity, not proof that 500 runnable models are currently available. Before a shard is assigned, every candidate must have:

- a canonical inventory record and immutable model revision;
- verified license and usage evidence;
- an approved benchmark dataset and isolated evaluation split;
- an explicit compute approval and resource ceiling;
- a runner that produces measured inference results and an evidence receipt.

Ten shards of 50 candidates are only valid after the canonical inventory contains 500 eligible candidates. Missing, gated, unlicensed, unavailable, or unapproved candidates remain visibly blocked; they are never replaced with invented model IDs or synthetic pass scores.

## Free operating rules

- No paid API keys are required by the free CI workflow.
- No automatic model downloads in hosted CI.
- No scheduled full-model sweeps on GitHub-hosted runners.
- No workflow may silently spend money or exceed a compute budget.
- No secrets in source control, artifacts, traces, or failure replay.
- No benchmark result without execution evidence.
- No production deployment, certification, or PR merge by the benchmark system itself.
- Keep large model weights and raw private datasets out of Git history.

## Current implementation boundaries

The repository already contains an approval-gated cross-model benchmark manifest and runner in `buddy/datasets/benchmark_jobs.py`, `buddy/datasets/benchmark_runner.py`, and `tools/run_buddy_model_benchmark.py`. Reuse those controls rather than building a competing runner. The separate `tools/run_500_model_benchmarks.py` currently records a fail-closed readiness state; this workflow verifies that boundary and does not claim that the 500-model execution engine is complete.

The adaptive spaced-repetition implementation is documented in `docs/learning/BUDDY_ADAPTIVE_SPACED_REPETITION.md`. Reuse the shared scheduler and its evidence ledger rather than creating a second curriculum scheduler.

## Next engineering gates

1. Extend the canonical model inventory with real, rights-reviewed candidates and measured availability.
2. Build a sharding planner that assigns only eligible inventory records and emits blocked reasons for the rest.
3. Connect the existing approved benchmark runner to local/self-hosted execution with strict resource budgets.
4. Aggregate signed or otherwise independently verifiable per-model receipts; keep signing keys outside the repository.
5. Connect only verified repair evidence to failure learning and human-reviewed Bootcamp distillation.
6. Add leaderboard updates only after comparable head-to-head or same-suite measurements exist.

**Status:** This document and the free CI workflow define a free-first operating path. They do not certify the full 10-pillar system, prove that 500 models have been executed, or imply that Buddy's model weights have been trained.
