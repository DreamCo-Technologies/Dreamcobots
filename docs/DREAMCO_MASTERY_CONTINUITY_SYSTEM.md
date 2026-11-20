# DreamCo Mastery Continuity System

## Mission

Keep every historical DreamCo/Buddy goal, approved plan, requirement, and unfinished task visible and progressing until it reaches evidence-backed mastery or the user explicitly pauses, replaces, or retires it.

The canonical seed registry is `config/dreamco-mastery-continuity-registry.json`. It is a starting inventory, not a claim that historical reconciliation is complete.

## Never lose a goal

Reconcile historical ChatGPT conversations, repository branches, pull requests (open and closed), issues, workflow definitions, documentation, registries, and generated reports. Create a stable goal ID for each requirement. Preserve source references and approvals. Deduplicate implementation, not intent: overlapping requirements may share one implementation while retaining links to every source.

Every goal record must map:
- Original source and approval
- Requirement and acceptance criteria
- Implementation files and runtime route
- Tests and reproducible commands
- Benchmark definition, baseline, result, and threshold
- Dependencies, blockers, risk, owner, and next safe action
- Current lifecycle state and evidence references

## Mastery is an evidence gate

Lifecycle: `catalogued → specified → implemented → sandbox_verified → benchmark_verified → regression_verified → production_verified → mastered`.

A stage cannot be skipped. A file existing is not proof that a feature works. A passing unit test is not proof of end-to-end runtime behavior. Production verification requires an approved release, live health evidence, rollback plan, and human release approval. Mastery additionally requires a sustained success window, monitoring owner, and no open critical findings.

Reopen a mastered item if monitoring, regression tests, security review, or new requirements show it has drifted.

## Continuous operating loop

1. Inventory new and changed requirements, PRs, workflows, tests, and failures.
2. Reconcile them with canonical goal IDs and preserve historical provenance.
3. Recalculate dependencies and identify the highest-priority safe, unblocked task.
4. Run read-only audits and deterministic tests.
5. Repair the smallest safe failure in a reviewable pull request.
6. Run targeted tests, then regression and integration tests.
7. Update evidence and status; never convert unknown into passed.
8. Publish a daily master queue: completed with evidence, next actions, blocked decisions, stale evidence, regressions, and newly discovered requirements.
9. Repeat. A mastered goal remains monitored and can be reopened.

## Priority order

1. Security, data loss, production isolation, and real Actions blockers.
2. Smallest safe repair, targeted verification, and regression.
3. Historical requirement traceability.
4. Buddy OS end-to-end execution and Dream Brain.
5. Bot contracts, MasterBot/division registry, capability certification.
6. Model/provider routing, benchmarks, and governed learning lanes.
7. User data controls, integrations, command centers, and operational recovery.
8. Marketplace/revenue, robotics, and other approved expansion.

Dependencies can change this ordering, but safety gates cannot be bypassed.

## Operating boundaries

- Read-only audits and local/CI tests may run automatically.
- Keep the production safety hold. No automatic merge, production deployment, destructive migration, credential/permission change, paid compute, billing action, or external data action.
- User approval of a plan authorizes work in the approved scope; it is not blanket approval for spending, merging, deployment, or weakening safeguards.
- Do not collect raw user conversations into shared learning. Personal memory, product improvement, cross-user learning, and foundation-model training remain separate consent purposes.
- User data study requires source ownership/authority, explicit scopes, rights review, expiry, and revocation. No access-control bypass.
- External company opt-out, deletion, or subscription cancellation is not complete until the provider confirms it.
- If a task is blocked, retain it in the master queue with the exact blocker and the decision/evidence needed.

## Current honest status

This system adds a canonical seed registry and an automated validator/reporting workflow. Historical import, full repository traceability, live end-to-end execution, benchmarks, and production verification remain open until evidence is attached. Scheduled automation runs only after the workflow is merged into the default branch; a pull-request run validates the change but does not activate the schedule on the default branch.
