# Buddy Repair Orchestrator Implementation Plan

## Principle

Integrate with what already works. Do not create a second control plane when an existing component can be extended safely.

## Phase 1 — Canonical incident contract

Create one incident representation consumed by Issues, Actions and Agents.

Required fields:

- incident_id
- source
- severity
- lifecycle_state
- repository/ref/commit
- symptoms
- evidence
- affected_components
- hypothesis_set
- confidence
- owner
- approval_state
- repair_plan
- verification_plan
- outcome
- learning_record

## Phase 2 — Event bus / event store

Persist append-oriented repair events using the normalized event schema. Support idempotency so duplicate workflow observations do not create duplicate incidents.

Minimum operations:

- append event;
- get incident timeline;
- query active incidents;
- link duplicate observation;
- close/escalate incident;
- record verification.

## Phase 3 — Intake adapters

Connect existing sources:

- GitHub Actions failures;
- repository validation;
- agent failures;
- Actions-page diagnostics;
- monitoring/observability alerts;
- manually created Issues.

Each adapter maps source-specific data into the canonical incident contract.

## Phase 4 — Diagnosis engine

Build deterministic evidence collection first. Add model-assisted hypothesis ranking only after evidence is available.

Required outputs:

- hypotheses;
- evidence for/against each;
- next diagnostic action;
- risk;
- expected information gain;
- confidence.

## Phase 5 — Repair planner

Generate minimal reversible repair plans and attach exact tests and rollback steps.

Plans should be reviewable before consequential execution.

## Phase 6 — Execution adapters

Use existing approved runners/workflows instead of browser-side shell execution.

Every execution produces an action/run ID and links its evidence to the incident.

## Phase 7 — Verification engine

Run only the required evidence gates based on the change surface.

Examples:

- workflow-only change -> workflow validation;
- Python change -> targeted Python tests + dependent checks;
- Actions UI change -> browser smoke + data verification;
- security change -> security gate;
- model behavior change -> benchmark + regression suite.

## Phase 8 — Council integration

Council reviews risk-bearing repairs and disagreements. Council output is itself an event with evidence references.

## Phase 9 — Learning

After verified resolution, produce a learning record. Reuse requires prerequisite checks and revalidation.

## Phase 10 — Actions UI

Expose the live state machine:

- current stage;
- current hypothesis;
- confidence;
- current test;
- evidence;
- risk;
- approval requirement;
- next action;
- final verification.

## Phase 11 — Continuous acceptance

The Actions acceptance suite verifies that every button has a real execution contract and truthful status.

## Safe rollout

Start with read-only observation. Then enable diagnosis. Then bounded low-risk repairs. Only after reliability metrics are established should higher-risk automation be enabled.

## Success gates

Do not promote the orchestrator because it looks impressive. Promote it when measured outcomes show:

- fewer duplicate incidents;
- higher diagnosis accuracy;
- higher verified repair rate;
- lower regression rate;
- lower time to resolution;
- bounded cost;
- correct escalation;
- no unacceptable security regressions.
