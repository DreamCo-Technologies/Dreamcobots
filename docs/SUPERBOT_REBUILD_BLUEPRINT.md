# DreamCo Superbot Rebuild Blueprint

## Objective

Turn the existing large bot ecosystem into a coherent engineering platform while preserving useful knowledge and capability.

## Phase 0 — Freeze proliferation

- New feature requests become capabilities, not standalone bots.
- Existing production behavior remains available through compatibility aliases.
- No destructive cleanup.

## Phase 1 — Inventory

Create a complete repository inventory and legacy recovery manifest. Record path, hash, ownership signal, dependencies, consumer hints, bot identity signals and review state.

**Exit:** every eligible repository artifact has a migration record.

## Phase 2 — Domain ownership

Assign every capability to exactly one Division Superbot. Assign divisions to one Cluster Superbot. Ambiguity goes to review rather than silent reassignment.

**Exit:** ownership conflicts are explicit and resolved or blocked.

## Phase 3 — Capability normalization

Convert names such as `foo_bot`, `fooBot`, `FooAgent`, `foo_worker` and duplicated implementations into stable outcome-based capability IDs. Preserve old names as aliases/provenance.

**Exit:** no competing canonical implementation for the same capability.

## Phase 4 — Runtime consolidation

Route capability execution through the governed fleet runtime. Remove independent worker creation where the capability does not require isolation. Keep dedicated workers only with documented engineering justification.

**Exit:** duplicate runtime check passes.

## Phase 5 — Product integration

Connect web, dashboard, APIs and automation to Superbot contracts. Product code must not reach directly into legacy bot implementations once an equivalent capability route exists.

**Exit:** website/API route parity and E2E pass.

## Phase 6 — Reliability

Add contract, unit, integration, sandbox and E2E coverage proportional to risk. Add structured telemetry and failure/recovery behavior.

**Exit:** Code Trust and reliability gates pass.

## Phase 7 — Commercial certification

For money-producing divisions, distinguish opportunity, eligibility, user action, provider confirmation and realized revenue. Every revenue workflow receives attribution and reconciliation events.

**Exit:** revenue attribution parity passes.

## Phase 8 — Legacy retirement

Only after parity: mark legacy implementations deprecated, retain aliases during a defined compatibility period, then remove unreachable duplicate implementations with a rollback manifest.

## Phase 9 — Continuous architecture governance

Every new capability requires:

1. Division owner.
2. Capability contract.
3. Dependency declaration.
4. Policy declaration.
5. Tests/benchmark plan.
6. Observability plan.
7. Rollback strategy.

A new standalone bot is an exception, not the default.

## Quality principle

The goal is not the fewest files. The goal is the **fewest canonical implementations required to preserve the maximum verified capability**.
