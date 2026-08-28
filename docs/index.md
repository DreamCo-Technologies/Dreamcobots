# DreamCo AI Research Observatory

Welcome to the public-facing DreamCo AI research portal.

## Research modes

- **U.S. Frontier Mode** — high-compute search, parallel candidates, RL/RLVR, tool use, and extended test-time compute.
- **Efficiency Mode** — GRPO experiments, selective distillation, adaptive reasoning budgets, and compact retrieval.
- **Compare Mode** — run both strategies under controlled benchmark conditions.
- **Hybrid Mode** — select strategies conditionally using benchmark evidence and resource budgets.

## 500-model benchmark

DreamCo's 500-model prospectus is the comparison backbone for Buddy and catalogued models/providers. Each applicable benchmark must have evidence before a model is considered evaluated. Results track quality, correctness, completeness, speed, efficiency, reliability, safety, and independence.

See: `../config/500-model-full-matrix-prospectus.json`

## Global AI source learning

Buddy's source-learning system continuously prioritizes authorized AI sources by authority, freshness, benchmark relevance, capability-gap coverage, transfer value, and cost efficiency. It extracts transferable capabilities, creates original lessons, runs exercises, tests mastery, and regression-tests prior capabilities.

See: `BUDDY_1000_SOURCE_BOOTCAMP.md`

## Reasoning efficiency

The learning lifecycle is:

`benchmark -> generate -> evaluate -> trace inversion -> distill -> retest -> promote`

Trace inversion uses authorized observable execution evidence. It does not attempt to expose or reconstruct private model chain-of-thought.

See: `REASONING_EFFICIENCY_AND_AI_COURSE_SYSTEM.md`

## User AI Model Lab

Users can evaluate eligible models through model adapters and the four research modes. Workspaces isolate private models, datasets, experiments, distilled artifacts, and results.

See: `MODEL_LAB_FOR_USERS.md`

## Public research principles

DreamCo aims to publish reproducible code, schemas, benchmarks, evaluation tooling, and experiment metadata where licensing permits. Third-party model weights, datasets, and outputs remain subject to their licenses. Credentials, private data, encryption keys, restricted prompts, and other secrets are never published.

## Evidence states

`Observed -> Reported -> Reproduced -> Benchmarked -> Verified -> Adopted`

A research claim does not become a DreamCo capability merely because a source reports it. Promotion requires reproducible evidence, acceptable safety results, and regression checks.

## Scaling

Model, bot, and capability counts are inventory values rather than architectural limits. Independent benchmark cases can be batched and parallelized while dependencies preserve ordering.

## Navigation

- [Actions recovery and benchmark dashboard](ACTIONS_RECOVERY_AND_BENCHMARK_DASHBOARD.md)
- [Benchmark-driven capability engine](BENCHMARK_DRIVEN_CAPABILITY_ENGINE.md)
- [Benchmark evidence lifecycle](BENCHMARK_EVIDENCE_LIFECYCLE.md)
- [Buddy source bootcamp](BUDDY_1000_SOURCE_BOOTCAMP.md)
- [Reasoning efficiency and AI course system](REASONING_EFFICIENCY_AND_AI_COURSE_SYSTEM.md)
- [Model Lab for users](MODEL_LAB_FOR_USERS.md)
