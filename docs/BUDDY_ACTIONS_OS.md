# Buddy Actions OS

## Purpose

The Actions page is Buddy's mission-control surface: it turns user goals into observable, verifiable work while keeping execution fast, recoverable and governed.

The design targets frontier-grade engineering characteristics without claiming literal AGI or singularity.

## Core model

```text
GOAL
 ↓
INTENT + CONSTRAINTS
 ↓
PLAN GRAPH
 ↓
CAPABILITY SELECTION
 ↓
RISK / PERMISSION CHECK
 ↓
SIMULATE WHEN USEFUL
 ↓
EXECUTE IN PARALLEL WHERE SAFE
 ↓
OBSERVE
 ↓
VERIFY
 ↓
RECOVER / REPLAN
 ↓
SYNTHESIZE RESULT
 ↓
MEASURE OUTCOME
 ↓
LEARN VALIDATED STRATEGY
```

## Action object

Every action should have:

- `action_id`
- `mission_id`
- `parent_action_id`
- `goal`
- `status`
- `priority`
- `owner_superbot`
- `capability_id`
- `inputs`
- `expected_output`
- `risk_class`
- `permission_scope`
- `dependencies`
- `preconditions`
- `verification_plan`
- `rollback_plan`
- `deadline`
- `cost_budget`
- `confidence`
- `evidence`
- `telemetry`
- `result`
- `created_at`
- `updated_at`

## Action states

`draft → planned → awaiting_approval → ready → running → verifying → completed`

Exceptional states:

`blocked`, `paused`, `retrying`, `degraded`, `failed`, `rolled_back`, `cancelled`, `quarantined`.

## Plan graph

Actions should form a DAG where possible. Independent nodes may run concurrently. Dependent nodes wait for verified prerequisites.

```text
                 MISSION
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      ACTION A    ACTION B    ACTION C
        │           │           │
        └──────┬────┴───────────┘
               ↓
          VERIFICATION
               ↓
          ACTION D
```

## Adaptive execution

Buddy should continuously compare expected versus observed state. If assumptions become invalid, it should pause affected branches, re-plan and resume from the last safe checkpoint rather than restarting the entire mission.

## Reliability patterns

- idempotency keys for repeatable actions;
- checkpoints for long missions;
- bounded retries with backoff;
- circuit breakers for failing dependencies;
- dead-letter/quarantine for poisoned work;
- compensation/rollback where supported;
- independent verification for consequential outcomes;
- immutable audit events;
- cost and time budgets.

## Parallelism

Parallel execution is allowed only when dependencies, permissions, resource contention and side effects permit it. The scheduler should optimize for expected successful completion, not maximum task count.

## Human control

The page must clearly distinguish:

- what Buddy plans to do;
- what is currently executing;
- what requires approval;
- what actually happened;
- what was verified;
- what failed or was skipped;
- what Buddy recommends next.

Consequential actions must pass the applicable governance gate.

## Verification-first completion

A task is not considered successful merely because a tool returned a response. Completion should be based on the action's verification plan and observed outcome.

## Self-improvement lane

The Actions page should surface recurring failures, slow steps, expensive steps, capability gaps and successful reusable strategies to the governed builder/evaluation pipeline. Durable changes require validation.

## UI priorities

The primary screen should optimize for fast comprehension:

1. mission status;
2. current action;
3. next required user decision;
4. progress and blockers;
5. live evidence/results;
6. cost/time;
7. verification state;
8. recovery options;
9. detailed execution trace on demand.

The interface should avoid exposing raw internal complexity unless requested.
