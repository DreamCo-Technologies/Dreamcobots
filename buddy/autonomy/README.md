# Buddy Autonomy Roadmap

Buddy's long-term objective is **capability self-sufficiency**: use external models and DreamCo bots as teachers, specialists, validators, and fallbacks while progressively learning the capabilities it uses most often.

## The loop

1. **Discover** a task/capability that needs outside help.
2. **Delegate** to an approved DreamCo bot or model.
3. **Capture** the task, solution, tool trace, tests, quality, cost, and latency.
4. **Reproduce** the capability with Buddy-native code/skills.
5. **Evaluate** the native result against the same benchmark.
6. **Repeat** until the evidence threshold is met.
7. **Promote** the capability to Buddy-native.
8. **Shadow-test** the old dependency instead of immediately deleting it.
9. **Retire** only after sustained regression-free performance and policy approval.

## What "self-training" means here

Buddy should continuously create useful training/evaluation examples from work it is legitimately allowed to process. It should not blindly train on private client data, bypass provider restrictions, or modify production behavior without tests and policy checks.

The system should optimize for:

- capability coverage
- correctness
- reliability
- tool-use success
- latency
- cost
- security
- privacy
- reproducibility

## Desired end state

External models and bots become increasingly **teachers and fallbacks**, while Buddy accumulates a growing internal capability library. The goal is not to eliminate every external model immediately; it is to eliminate unnecessary dependencies without sacrificing quality or safety.

A capability is considered replaceable only when Buddy passes repeated independent evaluations and maintains a reserve/fallback path.

## Metrics

Track at minimum:

- `external_dependency_ratio`
- `native_capability_coverage`
- `native_success_rate`
- `teacher_calls_per_task`
- `cost_per_successful_task`
- `regression_rate`
- `capabilities_ready_for_migration`

The autonomy engine should make these metrics visible to the existing DreamCo control/observability systems.
