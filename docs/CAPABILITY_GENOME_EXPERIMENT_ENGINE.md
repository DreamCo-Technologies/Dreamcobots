# DreamCo Capability Genome Experiment Engine

## Purpose

Convert research across the growing model/lab registry into independently testable capabilities and reusable modules.

## Pipeline

`lab -> model -> technique -> capability -> hypothesis -> baseline -> experiment -> ablation -> holdout -> distillation -> regression -> promotion`

## Technique families

- architecture and expert routing
- attention and memory efficiency
- training objectives
- SFT and post-training
- RL/RLVR/GRPO/PPO and related methods
- synthetic data
- distillation
- reasoning and adaptive compute
- tool use and agents
- retrieval and memory
- quantization and compression
- speculative/inference optimization
- multimodality
- verification and evaluation
- hardware/software co-design

## Experiment record

Every experiment should identify the source, license/usage basis, hypothesis, baseline, variables, benchmark version, task fixture, resource budget, execution environment, result, uncertainty, and reproducibility state.

## Ablation

When multiple techniques are combined, isolate important variables before attributing gains to the whole stack. Use controlled comparisons and held-out tests where practical.

## Capability ROI

Evaluate improvements using a multidimensional profile rather than one score:

- capability gain
- correctness
- reliability
- generalization
- tokens
- latency
- VRAM
- RAM
- compute
- energy
- dollars
- safety
- reproducibility

A capability may be Pareto-efficient even when it does not have the highest absolute benchmark score.

## Promotion states

`observed -> reported -> reproduced -> benchmarked -> verified -> promoted`

Alternative terminal states: `rejected`, `blocked`, `stale`, `needs_review`.

## Composition

Promoted capabilities become reusable modules. Superbots and Buddy can compose modules without requiring one permanent bot per capability.

## Scaling

Registry counts are dynamic. There is no fixed architectural ceiling on labs, models, techniques, modules, capabilities, or agents.

## Reasoning boundary

Trace inversion and reasoning analysis use authorized observable execution evidence, outcomes, tool traces, and evaluation artifacts. Do not attempt to reconstruct or publish private hidden chain-of-thought.
