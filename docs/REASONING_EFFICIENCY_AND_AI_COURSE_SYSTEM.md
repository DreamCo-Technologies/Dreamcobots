# DreamCo Reasoning Efficiency and AI Course System

## Goal

Build Buddy as a resource-aware learning system that maximizes verified capability per token, compute unit, dollar, and unit of retrieved context.

## Benchmark lifecycle

`fixture -> generate -> evaluate -> trace inversion -> distill -> retest -> promote`

Trace inversion analyzes authorized observable execution evidence after a benchmark. It extracts the minimum sufficient sequence of actions, tool selections, checks, outcomes, and failure patterns needed to reproduce the capability. It does not attempt to expose or reconstruct private model chain-of-thought.

## Distillation

Successful benchmark behavior can become compact, reusable artifacts:

- strategy
- skill
- example
- verification rule
- failure pattern

A distilled artifact is promoted only after held-out regression tests meet its configured retention threshold.

## AI-native courses

Courses should be normalized into prerequisite-aware learning units:

`course -> module -> concept -> prerequisite -> example -> exercise -> assessment -> mastery`

Repeated concepts are deduplicated. Retrieval should select the smallest relevant verified context rather than repeatedly presenting entire courses. Every learned unit retains source provenance and requires assessment evidence for mastery.

## Efficiency scoreboard

Every learning or benchmark strategy can be compared using:

- accuracy
- input/output tokens
- retrieval tokens
- latency
- monetary cost
- training compute
- distillation retention
- regression rate

The objective is not merely lower token usage. A strategy that saves tokens but loses capability should fail promotion.

## RL research registry

GRPO, PPO, DPO, RLAIF, and rule-based RL are treated as interchangeable experimental pathways. Buddy should select or compare them using benchmark evidence and the available resource budget rather than assuming one algorithm is universally superior.

## Protected reasoning artifacts

Sensitive artifacts may be encrypted at rest with controlled access and integrity hashes. Public prospectuses must never contain credentials, secrets, private data, or restricted prompts. The system stores verifiable outcome evidence and compact authorized strategy abstractions rather than private hidden reasoning.

## Scaling principle

There is no architectural bot-count ceiling. Modules and capabilities scale according to resources and registry capacity. Counts such as 1,051 or 500 are inventory/prospectus scopes, not system limits.
