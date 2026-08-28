# DreamCo Model Lab for Users

DreamCo can expose the same research machinery to users with their own eligible AI models.

## Four modes

- **Frontier** — high-compute search, parallel candidates, RL/RLVR, tool-use and extended test-time compute.
- **Efficiency** — resource-aware RL, GRPO experiments, selective distillation, adaptive reasoning budgets and compact retrieval.
- **Compare** — evaluate both strategies against controlled, identical benchmark conditions.
- **Hybrid** — choose strategies conditionally from benchmark evidence and resource budgets.

## Model adapters

The model lab should use adapter interfaces rather than model-specific business logic. Supported adapter families may include OpenAI-compatible, Anthropic-compatible, Google-compatible, DeepSeek-compatible, local/open-weight, Ollama, custom HTTP, and custom inference engines.

Adapters must report capabilities, limits, configuration provenance, and resource usage. Credentials are runtime configuration and must never enter benchmark fixtures, public reports, or source control.

## User isolation

Each workspace owns its models, datasets, benchmarks, experiments, distilled artifacts, and results. Private model or dataset material must not silently cross tenant boundaries or become training data for another user.

## Fair comparison

Compare Mode records a reproducible experiment ID and keeps the benchmark, evaluation rules, held-out tests, and resource budget explicit. Results should report accuracy, tokens, retrieval tokens, latency, cost, compute, memory, reliability, distillation retention, and regression rate.

## Open-source boundary

DreamCo should publish reproducible code, schemas, benchmark definitions, evaluation tooling, and experiment metadata where licensing permits. Third-party model weights, datasets, and outputs remain subject to their licenses. Restricted material is never relabeled as open source.

## Promotion

A model optimization is not promoted merely because a judge prefers it. Promotion requires measurable benchmark evidence, acceptable safety results, and regression checks.
