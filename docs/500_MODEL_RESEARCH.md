# 500-Model Research Matrix

DreamCo uses the 500-model prospectus as a research scope, not a permanent system limit.

## What gets benchmarked

For every catalogued model/provider and every applicable suite, record evidence for:

- quality
- correctness
- completeness
- speed
- efficiency
- reliability
- safety
- independence

## Comparison axes

`provider -> model -> version -> capability -> benchmark suite -> task -> Buddy result -> reference result -> gap -> status -> evidence -> last verified`

## Status lifecycle

`not_catalogued -> catalogued -> ready -> running -> passed/failed/blocked/stale -> needs_review`

A model is not considered evaluated until applicable benchmark evidence exists. Missing data is never inferred.

## Research modes

Each model can be evaluated through:

1. **Frontier** — high-compute search, parallel candidates, RL/RLVR, tools, and extended test-time compute.
2. **Efficiency** — resource-aware RL, GRPO experiments, selective distillation, adaptive reasoning budgets, and compact retrieval.
3. **Compare** — controlled head-to-head evaluation using the same task fixtures and evaluation rules.
4. **Hybrid** — conditionally combine strategies according to measured evidence and resource budgets.

## Learning and reasoning study

DreamCo studies publicly documented, legally usable, and reproducible model techniques including training methods, RL/RLVR, distillation, inference optimization, retrieval, tool use, verification, architecture, data efficiency, and evaluation methodology. The research record distinguishes reported claims from techniques independently reproduced by DreamCo.

We study observable behavior and documented methods rather than attempting to expose private hidden chain-of-thought.

## Fairness and reproducibility

Comparisons should record the benchmark version, task fixture, rubric, model/version, execution conditions, resource budget, and experiment ID. Paid or private models may remain blocked/unverified when an approved evaluation adapter is unavailable.

## History

Prior verified snapshots are preserved so users can see progress over time.

## Public safety

Public pages never expose credentials, private prompts/data, encryption keys, restricted endpoints, or other secrets. Third-party model and dataset licenses remain authoritative.
