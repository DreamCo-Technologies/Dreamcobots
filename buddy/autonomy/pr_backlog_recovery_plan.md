# Buddy PR Backlog Recovery Plan

## Objective

Recover useful capabilities from stale or unmergeable pull requests without force-merging old branches or overwriting current `main`.

## Procedure

1. Treat current `main` as the source of truth.
2. Inventory open PRs and classify them as valuable, duplicate, obsolete, conflicting, or blocked.
3. For valuable PRs, port the capability—not the stale branch history—onto a fresh branch from current `main`.
4. Preserve existing DreamCo architecture, including the protected original model catalog.
5. Run focused tests and repository validation.
6. Open small, current-base pull requests.
7. Merge only validated changes.
8. Close obsolete duplicates after their useful capabilities are preserved.

## Priority capabilities identified in the backlog

- 65-MasterBot training OS and bounded training lanes.
- 20-MasterBot homepage/routing architecture.
- Evidence-based model benchmark scorecards.
- Buddy repository-scan evidence reporting.
- Actions Control Center reliability and truthfulness.

## Buddy autonomy rule

Backlog recovery should feed Buddy's capability-mastery system. External models and bots may teach or validate a capability, but the objective is to make the capability increasingly Buddy-native. Existing models/bots are not deleted merely because a capability has been reproduced once.

## Protected model-fleet rule

The original DreamCo model catalog remains intact. OpenRouter is supplemental and may contribute additional models, providers, benchmarks, and fallbacks, but it must not remove or replace the original catalog.
