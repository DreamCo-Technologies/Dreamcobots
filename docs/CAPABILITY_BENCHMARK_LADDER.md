# Capability Benchmark Ladder

Benchmarks are a first-class part of DreamCo capability development.

## Evidence ladder

1. **Claimed** — the bot/capability says it can do something.
2. **Documented** — the behavior has a clear specification and examples.
3. **Unit tested** — isolated implementation behavior passes tests.
4. **Task tested** — the capability completes representative tasks.
5. **Benchmarked** — standardized evaluation produces a measurable score.
6. **Holdout tested** — unseen evaluation data confirms the result.
7. **Transfer tested** — the capability generalizes to related tasks.
8. **Regression tested** — improvement does not break previously mastered behavior.
9. **Mastered** — all required evidence gates pass.
10. **Improving** — a mastered capability is actively being optimized against a measurable baseline.

## What this changes

A bot with 300 documented capabilities can still have 0 mastered capabilities. That is acceptable and useful information.

The system's job is to turn claims into evidence over time.

## Benchmark gap loop

```text
Capability
   ↓
Baseline benchmark
   ↓
Gap detected
   ↓
Improvement hypothesis
   ↓
Sandbox experiment
   ↓
Standard benchmark
   ↓
Holdout
   ↓
Transfer
   ↓
Regression suite
   ↓
Better than baseline?
  ↙             ↘
 NO             YES
 ↓                ↓
learn/retry     promote
                   ↓
              record evidence
                   ↓
              find next improvement
```

## Benchmark categories

DreamCo should maintain evaluations for:

- reasoning
- coding
- debugging
- research
- tool use
- planning
- writing
- data analysis
- mathematics
- retrieval
- long-context work
- multimodal tasks
- agent reliability
- business workflows
- personal productivity
- safety
- security
- cost efficiency
- latency
- recovery from failure

## Golden rule

> **A capability is only as good as the evidence behind it.**

Benchmarks are not decoration. They are the feedback mechanism that tells Buddy what to learn next.
