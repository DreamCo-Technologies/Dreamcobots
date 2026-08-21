# Buddy Actions Execution Matrix

This is the operational checklist for turning the Actions page from a catalog into a trustworthy control system.

## Control lifecycle

Every action follows:

`VISIBLE -> EXPLAINED -> PRECHECKED -> EXECUTED -> EVIDENCE -> VERIFIED -> LINKED -> LEARNED`

If an execution step is unavailable, the UI must say so instead of pretending it ran.

## Core controls

| Action | Precheck | Execution | Evidence | Pass condition | Failure route |
|---|---|---|---|---|---|
| Doctor | runner/config available | health audit | health report | no critical foundation blocker | Issue |
| Tests | dependencies available | approved test suite | test report | required suite passes | Issue + Action |
| Lint/Type | project scripts available | lint/type checks | diagnostics | required checks pass | Issue |
| Security | scanners/config available | security suite | findings report | required security gate passes | Security incident |
| Benchmark | benchmark dataset/config available | benchmark run | score/cost/latency report | threshold met | Capability gap |
| Repair Plan | failure evidence exists | generate bounded plan | plan + rollback | plan is reproducible/reversible | Escalate |
| Pages Verify | page/data sources available | data + browser verification | verification report | UI agrees with source evidence | Issue |
| Device Bundle | build config available | package + smoke test | artifact metadata | install/launch checks pass | Build incident |
| Refresh Runs | GitHub access available | read run evidence | run snapshot | current data displayed | Integration incident |
| Workflow Run | workflow dispatch permission | dispatch approved workflow | run URL/status | required workflow passes | Action incident |
| Full Certification | all prerequisites | complete certification suite | certification artifact | all required gates pass | Master incident |

## Full certification order

1. repository integrity
2. dependency/runtime compatibility
3. lint/type/static checks
4. unit tests
5. integration tests
6. workflow validation
7. security
8. Actions page data validation
9. agent health
10. end-to-end smoke
11. performance/cost benchmark
12. deployment/canary verification
13. rollback readiness
14. Council certification

A failed prerequisite should stop dependent stages when continuing would create misleading results.

## Repair policy

### Safe automatic
- read-only diagnostics
- deduplication
- metadata/status repair
- retry of known transient jobs within a bounded budget
- generation of repair plans
- creation/linking of regression tests where tooling explicitly supports it

### Review required
- source-code changes affecting production
- workflow permission changes
- dependency upgrades with compatibility risk
- database/schema changes
- authentication/security changes
- deployment changes
- user-data/memory behavior changes

### Never blind-automate
- destructive deletion
- secret extraction/printing
- disabling security gates to obtain green
- rewriting tests to accept known-bad behavior
- force-pushing over user work
- closing failures without evidence

## Button result contract

Every result should show:

- started time
- finished time
- action ID
- commit/ref
- execution class
- status
- evidence link
- affected components
- failures
- recommended next action
- whether code/production changed
- rollback information when applicable

## Health score

Do not use a single opaque score as certification. Show the underlying gates.

Recommended summary:

`GREEN = all required gates pass`
`YELLOW = no critical gate failure, but work/blockers remain`
`RED = one or more required gates fail`
`UNKNOWN = current evidence unavailable/stale`

## Parent-grade behavior

Buddy should act like a careful senior engineer responsible for the system:

- protect the repository;
- protect user work;
- fix root causes;
- explain failures in plain language;
- avoid unnecessary complexity;
- measure improvement;
- escalate when confidence is low;
- never claim a result without evidence.
