# Superbot Cognitive Maturity Model

The maturity model measures demonstrated capability rather than marketing claims.

## M0 — Reactive

- Handles a single request.
- Limited context.
- Deterministic tool routing.

## M1 — Contextual

- Maintains task state.
- Retrieves relevant knowledge.
- Uses multiple tools in one task.
- Cites/retains source provenance.

## M2 — Planning

- Decomposes goals into subtasks.
- Selects tools dynamically.
- Tracks dependencies and blockers.
- Recovers from ordinary failures.

## M3 — Reflective

- Verifies its own outputs.
- Detects uncertainty.
- Critiques plans before execution.
- Compares results against benchmarks.

## M4 — Adaptive

- Runs controlled experiments.
- Learns successful strategies from evidence.
- Replans when conditions change.
- Shares reusable capabilities through contracts.

## M5 — Frontier Candidate

- Demonstrates sustained improvement against strong baselines.
- Performs complex multi-step domain work reliably.
- Builds/tests new capability proposals through the builder cell.
- Maintains strong reliability, security and cost characteristics.
- Produces reproducible evaluation evidence.

## Promotion rule

A Superbot advances only when its evidence bundle satisfies the required gates. A larger model, more tools, more prompts, or more tokens alone does not qualify it for promotion.

## Division-specific specialization

Every Superbot should combine the common cognitive stack with deep division-specific knowledge, tools, workflows, benchmarks and commercial outcome metrics. The goal is general reasoning plus expert execution—not a collection of narrow scripts.
