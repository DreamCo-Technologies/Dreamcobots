# Buddy Repair Orchestrator Specification

## Objective

Connect the existing Issues, Actions, Agents, Council, benchmark and verification systems into one evidence-driven repair loop.

## Incident state machine

`DETECTED -> TRIAGED -> REPRODUCING -> HYPOTHESIZING -> DIAGNOSING -> PLANNED -> APPROVAL_GATE -> REPAIRING -> TESTING -> COUNCIL -> CANARY -> VERIFYING -> RESOLVED`

Alternative terminal states:

- `ESCALATED`
- `BLOCKED`
- `WONT_FIX`
- `DUPLICATE`
- `INVALID`

A terminal state requires evidence and an explanation.

## Intake normalization

Every incident receives a canonical record containing:

- incident ID;
- source queue: Issue / Action / Agent / monitor;
- repository/ref/commit;
- workflow/job/agent identifiers when applicable;
- timestamps;
- symptoms;
- logs/evidence references;
- affected components;
- severity;
- user impact;
- security impact;
- recurrence history;
- suspected causes;
- confidence;
- owner;
- current state.

## Deduplication

Before creating new repair work, compare the incident against open and historical incidents using exact identifiers plus semantic/symptom similarity.

If a canonical incident already exists, link the new observation rather than creating another independent repair task.

## Prioritization

Priority considers:

`severity + user impact + security impact + recurrence + blast radius + confidence + repair cost`

Critical safety/security incidents outrank convenience features.

## Diagnosis strategy

Buddy should choose the smallest safe action expected to provide useful information.

Examples:

- inspect dependency/runtime versions;
- inspect changed files;
- run targeted test;
- reproduce in sandbox;
- inspect workflow logs;
- run browser smoke test;
- compare against last known-good commit.

## Repair planner

Plans must contain:

1. hypothesis;
2. supporting evidence;
3. counter-evidence;
4. exact files/components likely affected;
5. minimal repair;
6. tests;
7. regression checks;
8. rollback;
9. risk classification;
10. approval requirement;
11. success criteria.

## Execution policy

### Automatic
Read-only diagnostics and bounded, low-risk operations may run automatically.

### Gated
Production code, permissions, dependencies with compatibility risk, data/schema, authentication, security controls, deployments and user-memory behavior require the appropriate approval policy.

### Forbidden
Never bypass security controls, expose secrets, destroy user work, rewrite tests merely to hide failures, or claim a repair succeeded without verification.

## Verification hierarchy

1. original failing test;
2. targeted affected tests;
3. dependent regression tests;
4. integration tests;
5. Actions/workflow validation;
6. security checks;
7. benchmark if behavior/performance changed;
8. browser/end-user smoke test;
9. canary/production health where applicable.

Stop when the required evidence gate is satisfied; do not run unnecessary high-cost checks.

## Learning output

A resolved incident creates a learning record only after verification. It stores:

- root cause;
- successful repair;
- failed alternatives when useful;
- evidence;
- environment;
- regression results;
- confidence calibration;
- reusable prerequisites;
- recurrence watch.

## Feedback loop

```text
incident
 -> repair
 -> verification
 -> outcome metrics
 -> strategy update
 -> future diagnosis
```

The orchestrator should optimize for fewer repeated failures, faster verified repairs, lower unnecessary work, lower cost, and stable safety.

## UI requirements

The Actions page should expose the current incident stage, not merely a spinner. Users should be able to see:

- what Buddy believes is happening;
- what it is testing now;
- why it selected that test;
- what evidence it found;
- what it plans to do next;
- whether approval is required;
- what changed;
- what passed;
- what remains unresolved.

## Success definition

The orchestrator is successful when the system can take a real failure from detection through verified resolution with traceable evidence, while preserving user control and avoiding false-green status.
