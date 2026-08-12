# DreamCo PR Integration Ledger — 2026-08-12

## Purpose

This ledger records the repository-wide pull-request consolidation pass. It separates changes that were actually merged from changes that remain blocked by conflicts and from older proposals whose ideas need to be preserved without blindly merging stale code.

## Successfully merged in this consolidation pass

- **#471** — production dependency refresh: `lucide-react` and `ws` updates.
- **#473** — DreamPayments sandbox/core architecture, processor routing, fee auditing, benchmark coverage, and real-money safety gates.
- **#475** — civic, real-estate, education, vacancy, and government-services intelligence layer.
- **#468** — DreamCo Lite proof-first MVP roadmap, Proof Mode, and evidence-based upgrade ladder.
- **#470** — continuous innovation policy and library-specialist discovery foundation.
- **#477** — master roadmap, mandatory Global AI Sources Flow specification, revenue operating guide, chat/architecture context, production-bot definition of done, and AI-agent guardrails.

## Open PRs that could not be cleanly merged

### #469 — DreamCo intelligence / routing / benchmark mastery

Status: open, ready for review, merge conflict.

This is a large 184-commit / 133-file change set. It contains substantial unique work including:

- Dream AI Company Base
- 1,051-profile / 45-division preservation
- task-scoped specialist teams
- Personal Data Fabric
- model intelligence and quality-first routing
- provider-neutral model protocol compiler
- lazy task routing
- 32-dimension Model Mastery
- parallel benchmark-gap builders
- benchmark mastery/distillation
- compatibility/security repair lanes
- repository-wide verification and evidence contracts

**Decision:** do not force-merge the conflicting snapshot. Rebase/rebuild this work on the current `main`, then merge the unique capabilities after current CI and generated-artifact checks pass.

### #467 — Universal benchmark / workforce / government / sandbox expansion

Status: open, ready for review, merge conflict.

Unique items to preserve:

- universal expansion program
- O*NET workforce source contract
- 75-stage billable business lifecycle catalog
- shared book-of-associations knowledge graph
- 500 advertising benchmark generator
- every-gap parallel-bot contract
- high-assurance sandbox graduation requirements

**Decision:** rebuild these unique files on current `main` rather than forcing a stale merge commit.

### #476 — GitHub Pages full-page coverage + backend bridge

Status: open, ready for review, merge conflict.

Unique items:

- full React application publication under GitHub Pages
- page-coverage scanner/evidence
- Pages-to-backend bridge for API/WebSocket paths
- CORS configuration
- laptop control-hub bootstrap
- local environment handling
- Pages build/preflight gates

**Decision:** rebuild against current `main`. This overlaps the older #446 Pages proposal, but #476 is the newer and more comprehensive implementation.

### #474 — Actions Control Center repair

Status: open, ready for review, merge conflict.

Unique items:

- truthful task restart behavior
- explicit task-stat styling
- correct loading/error/disconnected states
- complete division filters
- per-task pending state
- explicit GitHub refresh controls
- accurate PR numbering
- truthful Revenue Integrations UI
- no fabricated connection/revenue claims
- health/status panel

**Decision:** reconcile with #469's Actions changes and keep the stronger truth/safety behavior. Do not overwrite the newer Actions implementation blindly.

## Open dependency PRs requiring controlled updates

### #479 — production dependencies

Updates `lucide-react`, `pg`, `react-hook-form`, and `ws`. It was mergeable, but its head moved during the consolidation pass. Refresh/revalidate before merging.

### #480 — development dependencies

Includes major-version upgrades such as Tailwind CSS 3→4, TypeScript 5→7, and Vite 7→8. This must be treated as a migration project, not a blind Dependabot merge. Run the full build, typecheck, visual regression, and browser suite first.

### #450 / #451

Older `actions/setup-python` 6→7 and `actions/setup-node` 6→7 PRs. These conflict with the current workflow strategy and should not be blindly merged. Re-evaluate the actual action versions used by the current `main` workflows before adopting individual upgrades.

### #455

Older grouped development-dependency upgrade. Prefer the newer #480 dependency snapshot after compatibility testing rather than merging two overlapping upgrade sets.

## Older proposals that should not be blindly merged

### #446 — older GitHub Pages landing/docs/blog

Superseded in scope by #476's repository-wide Pages coverage work. Preserve any content that is genuinely missing from the newer Pages implementation, but do not merge the stale branch wholesale.

### #93 — old 83-bot Excel/CSV catalog

The useful idea is preserved as a product/data-catalog requirement: machine-readable bot catalog, industry/function/ROI metadata, filtering, and spreadsheet/CSV export. The old branch is too stale to merge wholesale.

### #16 — DataForge AI Bot

The useful architecture remains important and should be rebuilt on the current framework rather than merged from its old `buddy` base. Preserve:

- synthetic dataset generation
- consent/privacy/licensing controls
- dataset packaging
- user-owned data cooperative concept
- marketplace/publisher adapters
- API registry and lazy connectors
- dataset compliance tests

All future DataForge implementation must use the current canonical DreamCoBot framework and mandatory Global AI Sources Flow.

## Current consolidation rule

Do not resolve conflicts by choosing an entire stale branch over current `main`. For every blocked PR:

1. identify unique files/capabilities;
2. identify overlapping files/capabilities;
3. preserve the strongest current implementation;
4. reapply unique functionality to current `main`;
5. run targeted tests;
6. run repository-wide certification where required;
7. merge only after the new head is conflict-free and green.

## Global architecture rule

All newly rebuilt bots must satisfy `framework/global_ai_sources_flow.py`, the canonical bot contract, governance/security controls, tests, static framework validation, and documentation requirements.

## Truth rule

A PR being described as implemented is not the same as that implementation being present on `main`. This ledger intentionally distinguishes **merged**, **blocked**, **needs rebuild**, and **needs validation**.
