# Benchmark-Driven Capability Engine

Benchmarks are not a final report in DreamCo. They are part of the learning loop.

## Core loop

```text
Capability
   ↓
Baseline benchmark
   ↓
Gap measurement
   ↓
Improvement hypothesis
   ↓
Sandbox candidate
   ↓
Benchmark
   ↓
Holdout
   ↓
Transfer
   ↓
Regression suite
   ↓
Compare with baseline
   ↓
Promote winner OR reject
   ↓
Record evidence
   ↓
Schedule revalidation
```

## Why this matters

A capability catalog can become misleading if it only records what a bot claims to do. Benchmark evidence lets DreamCo distinguish:

- what exists on paper
- what is implemented
- what works on known tasks
- what generalizes
- what survives unrelated changes
- what actually improved

## Capability scorecard

Every mature capability should eventually have:

- benchmark IDs
- baseline score
- current score
- threshold
- dataset version
- evaluator version
- model/agent version
- tool configuration
- cost
- latency
- reliability
- failure count
- holdout result
- transfer result
- regression result
- known limitations
- evidence artifacts

## Benchmark gaps become work

If Buddy discovers that a capability scores below its target, the result becomes an improvement task rather than a failure that gets hidden.

Example:

```text
Capability: Python debugging
Baseline: 71%
Target: 90%
Gap: 19 points

Buddy asks:
- Which failure classes dominate?
- Is the problem reasoning, tool use, retrieval, or code execution?
- Which training examples address the failure?
- Can a sandbox experiment improve it?
- Does the improvement generalize?
- Did anything else regress?
```

## Anti-gaming principles

DreamCo should never optimize only for a visible benchmark score.

Use separate holdouts, transfer tasks, regression suites, and real-world task evaluations. Preserve failed experiments and compare every candidate against a baseline.

## Frontier comparison

When comparing Buddy with external models, publish the task definition, model/version, tools, prompts or evaluation conditions where appropriate, dataset version, scoring method, and limitations. The objective is measurable capability improvement, not marketing claims.
