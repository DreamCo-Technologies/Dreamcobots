# Consolidated PR Integration Manifest

## Purpose
This branch is the clean integration ledger for the remaining open DreamCo PR portfolio. Current `main` is the source of truth. No legacy PR should be blindly merged. Every change is classified as **integrate**, **already present**, **duplicate**, **conflict requiring rewrite**, or **defer**.

## Core integration groups

### Actions Control Center
- PR #474 — focused Actions behavior/status-truth repair. **INTEGRATE/REBASE REQUIRED**. Changes only `client/src/pages/ActionsPage.tsx`; it is currently non-mergeable because its base is stale.
- PR #469 — broad Actions/control-center and orchestration expansion. **SELECTIVE INTEGRATION**. It overlaps heavily with current main and PR #474; do not merge wholesale.
- PR #476 — Pages coverage, backend bridge, laptop bootstrap. **INTEGRATE AFTER COMPATIBILITY REVIEW**.

### 65 MasterBots
- PR #3682 — canonical 65-MasterBot registry, 65 training lanes, Bootcamp/Sandbox and Actions manifest. **HIGH PRIORITY INTEGRATION**.
- PR #3684 — 20 MasterBots homepage extension/routing audit. **INTEGRATE UNIQUE HOMEPAGE/Routing pieces**; avoid duplicate registry definitions.

### Benchmark / learning
- PR #682 — model benchmark scorecard. **INTEGRATE UNIQUE SCORECARD CONTRACT**.
- PR #1961 — universal benchmark scanner, video/multimodal learning, evidence/update contracts. **SELECTIVE INTEGRATION**; remove duplicate/repeated scope files.
- PR #469 — model mastery, distillation, gap builders and sandbox/research infrastructure. **SELECTIVE INTEGRATION**.
- PR #730 — O*NET Bootcamp and evidence-driven routing. **SELECTIVE INTEGRATION**.

### Business / payments
- PR #928 — Money OS revenue integration. **SELECTIVE INTEGRATION** after checking current revenue architecture.
- PR #730 — DreamPayments/merchant value/agent routing/equipment compatibility. **SELECTIVE INTEGRATION**; never merge duplicate payment systems.

### Expansion
- PR #467 — universal expansion, workforce sources, billable lifecycle catalog, associations and advertising benchmark generation. **SELECTIVE INTEGRATION**.
- PR #830 — frontier growth/navigation architecture. **SELECTIVE INTEGRATION**; architecture only where it does not duplicate current systems.

### Repository/laptop integration
- PR #2999 — personal `ireanjordan24/dreamcobots` Xcode/Swift integration. **HIGH PRIORITY BUT REQUIRES FILE-BY-FILE COMPARISON**. GitHub-pushed work only; laptop-only work must first be pushed.

## Dependency-only PRs
- PR #451 — `actions/setup-node` update.
- PR #450 — `actions/setup-python` update.
- PR #2402 — `actions/checkout` update.
- PR #4222 — Vite/plugin-react development dependency update.

These should be evaluated as normal dependency maintenance, not mixed into the architectural consolidation unless compatible with the repository's supported Node/Python versions and CI.

## Non-negotiable consolidation rules
1. Preserve valuable source ideas; do not preserve duplicate implementations merely because they are in separate PRs.
2. One canonical registry for the 65 MasterBots.
3. One canonical Actions status contract.
4. One benchmark evidence model.
5. One sandbox/training queue architecture.
6. One local Buddy model configuration/runtime contract.
7. One revenue/payment architecture with provider adapters, not competing payment engines.
8. No claim of mastery without reproducible evidence.
9. No claim of a trained 500M checkpoint until an actual checkpoint exists and is benchmarked.
10. Do not delete or close legacy PRs until their useful changes have been accounted for here.

## Integration order
1. Canonical 65-MasterBot registry/training contracts.
2. Actions status-truth repair.
3. Benchmark scorecard/evidence contracts.
4. Bootcamp/sandbox and gap-closure lanes.
5. Homepage routing and division dashboards.
6. Repository/laptop integration.
7. Pages/backend bridge.
8. Selective business/payment/expansion modules.
9. Dependency upgrades after compatibility tests.
10. Full CI and browser verification.

## Current limitation
This manifest prevents loss of intent and identifies the merge order, but it does **not** falsely claim that every PR's source code has already been imported. The next commits must import the actual unique files from the listed PR heads and resolve conflicts against current `main`.
