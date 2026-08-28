# DreamCo Reasoning Efficiency and AI Course System

## Goal

Build Buddy as a resource-aware learning system that maximizes verified capability per token, compute unit, dollar, and unit of retrieved context.

## Benchmark lifecycle

`fixture -> generate -> evaluate -> trace inversion -> distill -> retest -> promote`

Trace inversion analyzes authorized observable execution evidence after a benchmark. It extracts the minimum sufficient sequence of actions, tool selections, checks, outcomes, and failure patterns needed to reproduce the capability. It does not attempt to expose or reconstruct private model chain-of-thought.

## Distillation

Successful benchmark behavior can become compact, reusable artifacts: strategy, skill, example, verification rule, and failure pattern. A distilled artifact is promoted only after held-out regression tests meet its configured retention threshold.

## AI-native courses

Normalize learning as `course -> module -> concept -> prerequisite -> example -> exercise -> assessment -> mastery`. Deduplicate repeated concepts, preserve provenance, retrieve minimal relevant context, and require assessment evidence for mastery.

## Efficiency scoreboard

Track accuracy, input/output tokens, retrieval tokens, latency, monetary cost, training compute, distillation retention, and regression rate. Token savings alone are not an improvement if capability is lost.

## RL research registry

Treat GRPO, PPO, DPO, RLAIF, and rule-based RL as experimental pathways selected using benchmark evidence and resource budgets rather than assuming one universal recipe.

## Protected reasoning artifacts

Sensitive artifacts may be encrypted at rest with controlled access and integrity hashes. Public prospectuses never contain credentials, secrets, private data, or restricted prompts. Store verifiable outcome evidence and compact authorized strategy abstractions rather than private hidden reasoning.

## Scaling principle

There is no architectural bot-count ceiling. Modules and capabilities scale according to resources and registry capacity. Counts such as 1,051 or 500 are inventory/prospectus scopes, not system limits.
