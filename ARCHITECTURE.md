# DreamCo Architecture

## What this repository is

DreamCo is a governed AI workbench. The repository contains a large bot catalog, a Buddy orchestration layer, a web product, backend services, capability registries, evaluation systems, automation, and research/learning infrastructure.

The goal is not to make 1,000 bots independently clever. The goal is to build **shared intelligence once and reuse it everywhere**.

## Canonical layers

```text
                    ┌─────────────────────────────┐
                    │           USERS             │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │       BUDDY / ROUTER        │
                    │ intent • planning • policy  │
                    └──────────────┬──────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
   ┌─────────▼────────┐  ┌────────▼────────┐  ┌────────▼─────────┐
   │ Capability Layer │  │ Tool/Model Layer │  │ Knowledge Layer  │
   │ skills • tasks   │  │ models • APIs    │  │ sources • memory │
   └─────────┬────────┘  └────────┬────────┘  └────────┬─────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │       SANDBOX / EVAL      │
                    │ tests • benchmarks •       │
                    │ holdouts • regression      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  LEARNING / IMPROVEMENT   │
                    │ failures • experiments    │
                    │ reattempts • promotion    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     GOVERNANCE / AUDIT    │
                    │ permissions • provenance  │
                    │ budgets • rollback       │
                    └───────────────────────────┘
```

## Repository boundaries

| Directory | Responsibility | Rule |
|---|---|---|
| `App_bots/` | Large bot catalog | Profiles/data; do not duplicate runtime logic |
| `bots/` | Curated specialist profiles | Human-readable capability definitions |
| `framework/` | Reusable learning/orchestration primitives | Canonical shared logic belongs here |
| `server/` | Backend/API | Runtime services only |
| `client/` | React application | UI only; use shared contracts |
| `website/` | Static/public web experience | Keep deployable without backend assumptions |
| `shared/` | Cross-runtime types/schemas | Single source of truth for contracts |
| `config/` | Policies, registries, versioned configuration | Generated data must identify its generator |
| `tools/` | Repository generators, audits, validators | Prefer deterministic, idempotent tools |
| `tests/` | Automated verification | Bugs require regression coverage |
| `docs/` | Architecture, operations, contributor guidance | Explain why, not just what |
| `.github/workflows/` | CI/CD and scheduled automation | Small, observable, non-overlapping workflows |

## Golden rules for developers

1. **One canonical owner per capability.** If two systems do the same thing, consolidate rather than adding a third.
2. **Data is not runtime.** A catalog entry does not prove a working capability.
3. **Generated files have a source.** Modify the generator, then regenerate.
4. **Every meaningful bug gets a regression test.**
5. **Sandbox before promotion.** New autonomous behavior must prove itself before production.
6. **Evidence before claims.** Mastery, frontier readiness, and production readiness require measured evidence.
7. **Keep external effects governed.** Credentials, spending, publishing, outreach, destructive actions, and permission changes require explicit policy gates.
8. **Prefer boring interfaces.** JSON/TypeScript/Python contracts should be easy for a new contributor to understand.
9. **Make failures local.** A failure in one subsystem should identify the smallest failing boundary instead of masking unrelated checks.
10. **Delete duplication.** Repository size is not a feature; reusable capability is.

## Change flow

```text
Issue / Goal
    ↓
Find canonical owner
    ↓
Write or update contract
    ↓
Implement smallest change
    ↓
Focused test
    ↓
Repository verification
    ↓
Sandbox / benchmark if capability changes
    ↓
PR review
    ↓
Merge
    ↓
Observe
    ↓
Regression or improvement loop
```

## Developer experience goal

A new contributor should be able to answer these questions in under ten minutes:

- Where does this capability live?
- What contract does it implement?
- What tests prove it works?
- Which workflow verifies it?
- Which configuration controls it?
- What happens if it fails?
- How can I improve it without understanding the whole repository?

If those answers are difficult, the architecture needs improvement.

## Long-term target

Buddy should become the coordination and learning layer rather than a giant pile of duplicated bot code. Specialist bots should increasingly become reusable capability implementations that Buddy can route, compose, evaluate, and improve.
