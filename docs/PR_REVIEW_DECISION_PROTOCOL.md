# DreamCo PR Review Decision Protocol

This protocol is the permanent contract for automated PR review and recovery.

## Decision pipeline

`INTAKE → CONTEXT → DIFF → DEPENDENCIES → SECURITY → TEST IMPACT → ARCHITECTURE → CAPABILITY IMPACT → BENCHMARK IMPACT → DUPLICATE CHECK → MERGEABILITY → FINDINGS → REPAIR PLAN → VERIFICATION → RE-REVIEW → PROMOTION → POST-MERGE MONITORING`

## Decision classes

- `GREEN`: every applicable required gate has current passing evidence.
- `YELLOW`: reviewable, but evidence is incomplete or stale.
- `RED`: a required gate failed or a release-blocking finding exists.
- `BLUE`: the PR cannot merge safely; rebuild from current `main`.
- `PURPLE`: capability overlaps with existing work; compare before importing.
- `GRAY`: not applicable or intentionally not executed.

## Unmergeable PR rule

An unmergeable PR must never be force-merged merely to reduce backlog. The recovery workflow is:

1. Capture the PR's metadata, diff, checks, and changed files.
2. Classify the failure: conflict, failing CI, missing dependency, policy block, stale branch, duplicate, or unknown.
3. Identify unique capabilities and affected contracts.
4. Start a clean repair branch from the current production baseline.
5. Transplant only verified useful capabilities.
6. Run the same review, security, test, benchmark, and regression gates as a normal PR.
7. Publish a replacement PR with lineage back to the original.
8. Re-review the replacement.
9. Promote only when required evidence is green.

## Repair safety

Automated repair must be bounded. It may propose or create changes, but promotion requires independent verification. Secrets, private prompts, hidden chain-of-thought, and protected data must never be copied into reports or artifacts.

## Continuous greenkeeping

Scheduled scans should detect regressions after merge, stale evidence, broken workflows, dependency drift, and benchmark degradation. A repair is complete only when the relevant verification evidence is current.
