# Buddy Agent Routing Engine

Buddy uses dynamic specialist routing rather than a fixed one-bot-per-task mapping.

## Route

`Goal → Decompose → Capability Match → Team Selection → Execute → Verify → Synthesize → Benchmark → Learn`

A task can use one specialist or several. Independent subtasks can run in parallel; dependent steps wait for their prerequisites.

## Selection rule

An agent is eligible only when its capability is backed by measured evidence. Evidence tracks quality, speed, efficiency, reliability, safety and sample count. Agent names, descriptions or self-reported skills are not sufficient.

## Verification

Important steps may request an independent verifier. Disagreement becomes a new evidence task rather than a hidden tie-break.

## Learning

Every completed route should record the task type, selected agents, tools, duration, resource usage, benchmark outcome, failures, reviewer outcome and regression result. Routing can then be optimized against observed outcomes.

## Safety

The routing layer chooses and plans work; it does not silently grant permissions, expose secrets, deploy production, or bypass repository review gates. High-impact operations remain explicitly gated.
