# Buddy Green-by-Tonight Runbook

## Objective

Drive the repository toward the strongest possible verified state in one operating window without hiding failures or using blind retries.

**Green means:** required checks pass, production smoke passes, authoritative generated artifacts are current, and unresolved failures are either fixed or explicitly escalated. It does not mean every issue is magically closed.

## Operating loop

```text
DISCOVER -> SNAPSHOT -> TRIAGE -> DEDUP -> PRIORITIZE
        -> REPRODUCE -> REPAIR -> TEST -> COUNCIL
        -> DEPLOY/CANARY -> VERIFY -> CLOSE/ESCALATE
```

## Queues

### Issues
Work on critical/security/data-loss/production blockers first, then regressions, user blockers, correctness, performance and enhancements.

### Actions
Fingerprint failing workflow/job/step combinations. Group repeated failures. Retry only transient failures with a bounded budget. Persistent failures become repair incidents.

### Agents
Classify failures as model, tool, code, data, policy, permission, environment or integration. Retry only safe classes. Repeated or low-confidence failures escalate.

## Hard rules

1. Never mark a failure fixed because a retry passed once.
2. Never close an issue without verification evidence.
3. Never let an agent certify its own consequential production change.
4. Never expose secrets in logs or diagnostics.
5. Never use destructive cleanup without a reversible plan.
6. Never create a duplicate bot when a shared service can handle the job.
7. Never hide blocked work; show the blocker and next action.
8. Every repair should add regression protection when practical.
9. Generated status is rebuilt from source-of-truth evidence before certification.
10. Production readiness is a claim that must be continuously re-earned.

## Priority score

`severity x blast_radius x recurrence x dependency_centrality x user_impact x age`

Security, data loss and production outages outrank normal feature work.

## Required evidence package

Every repaired incident records:

- canonical incident ID
- original failure
- reproduction evidence
- root-cause hypothesis
- change/diff
- tests executed
- regression test
- Council decision when required
- deployment result
- runtime verification
- rollback plan/result
- final status

## End-of-window gates

- no known critical production smoke failure;
- required certification workflow is passing;
- generated status is fresh;
- all new failures are routed into Issues/Actions/Agents;
- unresolved blockers have owners and explicit next actions;
- repeated failures are grouped instead of multiplying;
- dashboard accurately reports green/yellow/red state.

If any gate fails, report it honestly. The objective is **verified green**, not cosmetically green.
