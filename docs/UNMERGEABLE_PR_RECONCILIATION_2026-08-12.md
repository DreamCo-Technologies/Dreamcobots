# Unmergeable PR Reconciliation — 2026-08-12

This branch is intentionally based on current `main`. It does **not** merge stale/conflicting branches wholesale. It carries forward capabilities from blocked PRs only where they are missing from `main` and can be added without replacing newer work.

## Source PRs compared

- #469 — intelligence routing, model mastery, Personal Data Fabric, benchmark mastery, sandbox fleet, repository intelligence, autonomous builder patterns
- #467 — benchmark-gap acceleration, universal workforce/business capability expansion, association knowledge graph, advertising/business lifecycle benchmarks
- #474 — Actions Control Center correctness and truthfulness
- #476 — GitHub Pages full application coverage, backend bridge, laptop control hub, deployment preflight

## Added on this reconciliation branch

### Benchmark gap acceleration

`config/benchmark-gap-acceleration-policy.json`

Preserves the strongest missing ideas from #467:

- 32 safe parallel benchmark lanes
- serialized edits per canonical owner
- explicit gap state machine
- stagnation timers
- priority preemption
- dedicated benchmark/builder/integration/QA/security/value/review roles
- evidence-based closure
- no fake completion claims

### Shared Book of Associations

`config/book-of-associations.json`

Preserves #467's shared organization graph for:

- trade/professional associations
- chambers and merchant groups
- standards/certification bodies
- workforce and economic-development organizations
- partnerships, sponsorships, procurement and grants
- events and training
- provenance and verification dates

### Canonical Bot Business Blueprint

`config/bot-blueprint-standard.json`

Preserves #467's requirement that bots become measurable products/business units with customer, pricing, sales, marketing, support, KPI and verification metadata while also requiring the current Global AI Sources Flow and framework checks.

### GitHub Pages backend bridge

`client/src/lib/runtimeBackend.ts`

Preserves the core #476 Pages capability of routing browser `/api`, `/ws`, and `/socket` traffic to a configured HTTPS/WSS backend while leaving normal local development behavior unchanged.

## Capabilities intentionally NOT copied blindly

### #469

The branch contained many overlapping changes to workflows, Actions UI, benchmark registries, model routing and generated artifacts. Those areas are intentionally left for targeted follow-up because copying the stale snapshots would risk overwriting current `main` changes.

The unique requirements still tracked for follow-up are:

- task-scoped model routing and model-quality registry
- Personal Data Fabric contracts
- 32-dimension model mastery evidence
- benchmark mastery/distillation workers
- all-bot sandbox campaign and repair loop
- compatibility repair automation
- repository-wide connection graph and builder backlog
- autonomous PR creation with bounded governance

### #474

The Actions page contains a large UI rewrite. It is not copied wholesale because it removes functionality and overlaps with newer Actions work. The desired behavior is retained as a reconciliation target: truthful status, explicit loading/error/disconnected states, per-task pending state, refresh controls, correct PR numbers, and no fabricated revenue/integration claims.

### #476

The full Pages workflow and laptop bootstrap are not copied wholesale because they also modify routing, deployment, backend CORS, service-worker behavior, and generated website artifacts. Those need a coordinated current-main implementation. The backend bridge is carried forward because it is isolated and additive.

## Required next integration wave

1. Rebase/rebuild #469's unique model-intelligence and benchmark systems onto this branch.
2. Rebuild #467's generated benchmark artifacts and universal business/advertising catalogs against current schemas.
3. Apply #474's Actions truthfulness requirements to the current Actions page rather than replacing it.
4. Integrate #476's Pages build preflight, hash routing, CORS, deployment and laptop bootstrap as one tested deployment change.
5. Run repository-wide framework certification and tests.
6. Run the Pages browser verification suite.
7. Run benchmark/sandbox evidence generation.
8. Merge only after conflicts are resolved and the resulting branch passes current CI.

## Non-negotiable architecture

Every newly added or rebuilt bot must comply with `framework/global_ai_sources_flow.py`, including all required stages and governance/security controls. No credentials are copied from PRs or chat into source control.
