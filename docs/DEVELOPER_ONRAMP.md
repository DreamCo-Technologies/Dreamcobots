# Developer On-Ramp

Welcome to DreamCo. You do **not** need to understand the entire repository before making a useful contribution.

## First 10 minutes

1. Read `ARCHITECTURE.md`.
2. Read `CONTRIBUTING.md`.
3. Inspect `package.json` for the supported verification commands.
4. Find the canonical owner of the capability you want to change.
5. Run the smallest relevant test before changing anything.

## Choose your lane

### Buddy / AI behavior

Start with `framework/`, `config/`, `tests/`, and the Buddy-related generators in `tools/`.

### Bot catalog

Start with `App_bots/`, `bots/`, capability registries, and their generators/tests. Do not implement runtime behavior inside thousands of individual bot profiles.

### Backend

Start with `server/` and `shared/`. Keep API contracts explicit and validate inputs at the boundary.

### Frontend

Start with `client/` and `shared/`. Prefer reusable components and typed contracts instead of page-specific copies.

### Website

Start with `website/`. Static pages should remain usable independently of optional backend services.

### CI / automation

Start with `.github/workflows/` and `tools/audit_actions_health.py`. Before adding a workflow, check whether an existing workflow already owns the same responsibility.

## The smallest safe change

```text
1. Identify the canonical owner.
2. Change one boundary at a time.
3. Add a regression test.
4. Run focused verification.
5. Run repository checks relevant to the change.
6. Inspect the diff.
7. Open a PR with evidence.
```

## What a good PR looks like

A strong DreamCo PR tells the reviewer:

- **Problem:** what was broken or missing?
- **Decision:** why was this implementation chosen?
- **Scope:** which canonical subsystem owns the change?
- **Evidence:** which tests/benchmarks passed?
- **Risk:** what could regress?
- **Rollback:** how can the change be safely reversed?
- **Next step:** what remains intentionally out of scope?

## Avoid these traps

- Adding another bot when a shared capability should be improved.
- Editing generated output instead of its generator.
- Making a catalog claim without executable evidence.
- Creating a new workflow for an existing CI responsibility.
- Mixing credentials into source files, logs, browser storage, or test fixtures.
- Making external side effects automatic just because a local test passes.
- Removing a failing test instead of fixing the underlying behavior.

## Contribution philosophy

DreamCo should become **easier to improve as it gets larger**. If a contribution makes the next contribution harder, add documentation, tests, interfaces, or consolidation work before declaring the job finished.
