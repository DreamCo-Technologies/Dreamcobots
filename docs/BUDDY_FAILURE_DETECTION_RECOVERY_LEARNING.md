# Buddy Failure Detection, Recovery, and Learning System

## Objective

Make failure handling a permanent platform capability shared by Issues, Actions,
Agents, runtime services, integrations, deployments, and all canonical MasterBots.
This extends the Repair Orchestrator, Three-Queue Operating Model, and Greenkeeper;
it does not create a competing incident system.

## Required operating loop

`OBSERVE -> NORMALIZE -> FINGERPRINT -> DEDUPLICATE -> PRIORITIZE -> DIAGNOSE
-> REPRODUCE -> PLAN -> APPROVAL_GATE -> REPAIR -> VERIFY -> LEARN -> MONITOR`

Every observation is retained or linked to a canonical incident. A retry is not
a repair. A code edit is not a repair. Resolution requires evidence that the
original failure and required regression checks pass.

## Coverage

- GitHub Actions workflow and job failures, cancellations, timeouts, and skipped gates.
- Unit, integration, end-to-end, security, dependency, build, and benchmark checks.
- Buddy/MasterBot task failures, model/tool routing failures, and adapter outages.
- Deployment, public Pages, runtime health, scheduled jobs, and webhook processing.
- Recurrence after a previously resolved incident.

## Learning memory

Each incident stores a stable fingerprint, failure class, affected component,
first/last seen, recurrence count, linked runs/commits/PRs, root cause, attempted
repairs, failed alternatives, verification evidence, and a reusable lesson.
Fingerprints exclude run IDs and commit SHAs so repeated manifestations can be
recognized. Similarity matching may suggest links, but must not auto-merge
different incidents without corroborating evidence.

Lessons enter reusable memory only after the original failure and regression
checks pass. Failed repairs are recorded as failed alternatives and must not be
recommended as successful fixes. Every lesson is versioned and traceable to its
verification run and source commit.

## Automatic repair boundaries

**Allowed without additional approval:** read-only diagnostics; incident
normalization/deduplication; reproducible low-risk fixes limited to generated
indexes, formatting, documentation links, and deterministic test fixtures;
creating an isolated repair branch/PR; running bounded tests.

**Approval required:** production code behavior, authentication/authorization,
security controls, secrets, permissions, dependency major upgrades, database
schema/data migrations, billing, paid compute, deployment, destructive changes,
and any action with uncertain blast radius.

**Never allowed:** disabling required checks to obtain green status, weakening
the 52 MiB Pages budget, deleting evidence, rewriting tests to mask failures,
exposing secrets/private data, or self-merging an unreviewed production change.

## Verification contract

1. Reproduce the original failure or document why reproduction is impossible.
2. Run the exact failed check against the repair.
3. Run targeted tests for changed components.
4. Run dependent integration/regression tests.
5. Run security and policy checks when relevant.
6. Compare benchmark behavior when functionality or performance changes.
7. Confirm no new failures were introduced.
8. Monitor at least one subsequent scheduled or relevant workflow cycle.

A repair is `VERIFIED` only when all required checks have current successful
evidence. Otherwise its state remains `BLOCKED`, `ESCALATED`, or `REPAIRING`.

## Learning and recurrence policy

- Repeated fingerprints increase priority and recurrence score.
- A previously verified lesson may be proposed again, but must be checked against
  current code, dependencies, and environment before reuse.
- A previously failed repair is excluded from automatic recommendation unless
  new evidence explains why it is now applicable.
- Regression reopens the incident and invalidates stale green evidence.
- Root-cause clusters create durable engineering work rather than endless
  retries or duplicate tickets.

## Operational cadence

- Ingest failures immediately from workflow completion events where available.
- Reconcile recent workflow history on a scheduled cadence to recover missed events.
- Run read-only health checks continuously within GitHub Actions scheduling limits.
- Use bounded concurrency, timeouts, backoff, and idempotency keys.
- Do not claim a five-minute or 24x7 SLA: GitHub scheduled workflows are best-effort.

## Success metrics

Track time to detect, time to diagnose, time to verified repair, recurrence rate,
repair success rate, regression rate, false-positive rate, escalations, unresolved
age, and verification coverage. Report unknown values as unknown, never zero.

## Current implementation status

The deterministic fingerprinting, risk policy, recurrence recommendation, and
verified-lesson storage helper are implemented in `tools/buddy_failure_learning.py`
with unit tests. GitHub-wide event ingestion, durable cross-run incident storage,
bounded repair execution, and live monitoring remain integration gates until
connected to the repository's Issues/Actions/Agents control plane and verified
by CI. This document does not assert that those integrations are deployed.
