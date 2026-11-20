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


## Division-wide mastery engine

The division engine reads `config/masterbot-65-registry.json` and refuses to build a fleet if the canonical count is not exactly 65 or if IDs/names are duplicated. It builds one isolated logical lane per MasterBot and assigns shared platform goals plus domain-relevant workstreams. The keyword routing is an initial routing heuristic; it must be reconciled against the authoritative 45-division taxonomy and actual capability ownership before it can be treated as final.

Each lane has:
- Stable MasterBot/division identity and assigned canonical goal IDs
- Explicit goal dependency map and ordered task DAG
- Traceability anchors for implementation files, tests, runtime routes, and benchmark definitions
- A visible missing-evidence list; anchor paths are not treated as verified completion
- A bounded task runner that executes registry validation, shared regression tests, and the existing sandbox-first lane planner
- A run record with commit SHA, task outcomes, evidence hash, and next actions

The scheduled division workflow runs twice daily and uses a bounded matrix (maximum five concurrent lanes). GitHub schedules are best-effort, not a 24/7 compute guarantee. A separate division contract benchmark is retained as JSON evidence. That existing benchmark checks structural contracts; it is not a per-division model-quality benchmark and does not prove that weights changed.

Goal dependencies currently encode a proposed execution order. Historical reconciliation and repository health precede orchestration, bot registry, model routing, learning, privacy/integration, and expansion work. The dependency map must be reviewed as implementation evidence becomes available.

## Promotion requirements

A candidate is only eligible for human review when numeric baseline and candidate scores exist, candidate score does not regress, held-out and regression checks pass, provenance and data rights are verified, a tested commit SHA is recorded, and a reviewer approves. Eligibility does not deploy or change production weights. Production release continues to require separate human approval and rollback evidence.

## Current implementation boundary

The new engine connects all 65 registry entries to logical lanes, goal routing, dependency metadata, shared regression execution, the existing lane planner, benchmark execution, and evidence artifacts. It does **not** yet implement every domain capability, execute every historical requirement, prove every runtime route, run domain-specific held-out benchmarks for all 65 divisions, or train/merge model weights. Those remain explicit gaps in each lane's traceability record. No division should be described as mastered until its own capability-level evidence is complete.
