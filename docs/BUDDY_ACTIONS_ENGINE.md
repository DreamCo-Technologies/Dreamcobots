# Buddy Actions Engine

## Objective

Make the Actions page the operational command center for Buddy: a goal-driven execution system that plans, previews, executes, verifies, observes, recovers and learns from work across the 46 Division Superbots, capability registry, device fabric and external tools.

The target is frontier-grade engineering quality, not a claim of literal AGI or singularity.

## Core model

```text
USER GOAL
 ↓
UNDERSTAND
 ↓
CONSTRAINTS + PERMISSIONS
 ↓
PLAN
 ↓
SIMULATE / PREVIEW
 ↓
RISK CLASSIFY
 ↓
APPROVAL GATE (when required)
 ↓
DISPATCH
 ↓
PARALLEL EXECUTION
 ↓
OBSERVE
 ↓
VERIFY
 ↓
RECOVER / REPLAN if needed
 ↓
SYNTHESIZE RESULT
 ↓
USER DELIVERY
 ↓
OUTCOME MEASUREMENT
 ↓
LEARN VALIDATED STRATEGY
```

## Actions page should show

### Mission control

- current mission;
- objective and success criteria;
- plan graph;
- active workers/Superbots;
- tools and devices in use;
- elapsed time;
- cost estimate/actual where available;
- progress;
- blockers;
- risk state;
- approvals required;
- verification state.

### Action graph

Render each mission as a DAG/state graph rather than a flat activity list. Nodes should expose status, dependencies, inputs, outputs, evidence, retries and responsible capability.

### Human control

Users should be able to pause, resume, cancel, approve, reject, retry, reroute and inspect an action. Consequential actions must respect governance gates.

### Explainability

For every consequential action show:

- what Buddy plans to do;
- why the action is needed;
- which capability will perform it;
- what permissions it requires;
- expected side effects;
- evidence/inputs;
- verification method;
- fallback plan.

## Reliability patterns

- idempotency keys;
- checkpoints;
- retries with bounded backoff;
- circuit breakers;
- timeouts;
- cancellation propagation;
- compensating actions;
- dead-letter/recovery queue;
- worker health scoring;
- independent verification;
- immutable/audited action history.

## Parallelism

Execute independent nodes concurrently while respecting dependencies, rate limits, resource constraints, user permissions and provider limits. Prefer the smallest sufficient worker set rather than waking the entire bot fleet.

## Verification

Verification is a first-class state. A task should not be marked successful merely because a worker returned successfully. Verification may use independent workers, deterministic checks, source provenance, test suites or external confirmation depending on risk.

## Learning

Capture outcome data, but do not silently rewrite core behavior. Candidate strategies enter evaluation/simulation before becoming durable strategies.

## Device-aware actions

Actions may use the Buddy Device Fabric. A mission can route video to a verified display, audio to authorized headphones, input to a controller, or combine multiple devices when supported.

## Money-aware execution

Revenue-related actions should expose expected value, actual result, fees/costs, attribution and reconciliation. Financial side effects require the applicable authorization and governance gate.

## Action state machine

`draft → planned → simulated → awaiting_approval → executing → verifying → succeeded | partially_succeeded | failed → recovering → cancelled | quarantined`

## Engineering quality bar

Actions must be observable, testable, replayable and recoverable. Every action should have a stable ID and correlation ID, structured events, timestamps, actor/capability identity, permission context and outcome record.

## Anti-patterns

Do not build an opaque "run everything" button. Do not claim success from a tool invocation alone. Do not silently retry destructive operations. Do not grant a worker permissions it did not already have. Do not create duplicate workers when an existing capability is sufficient.
