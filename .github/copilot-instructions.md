# DreamCo Copilot Instructions

DreamCo is a large multi-bot platform. Treat the canonical repository structure as the source of truth and do not create duplicate parallel architectures without checking for an existing owner first.

## Before editing

- Read `AGENTS.md`.
- Read `config/trusted-code-delivery-program.json` for executable code changes.
- For bot/division work, inspect `App_bots/`, the fleet generators, sandbox curriculum, placement audit, and Council career path generators.
- For resource work, inspect the canonical resource contracts and universal resource sandbox.
- For GitHub/CI work, inspect `tools/audit_actions_health.py`, `Buddy Actions Test Lab`, `DreamCo Control Center`, `Code Trust Gate`, and the failure watcher/sweep.
- For offline work, inspect `config/offline-buddy-repository-engine.json` and `tools/buddy_local_repository.py`.

## Trusted code delivery

Treat new or changed executable code as **draft until verification passes**. Never call code bug-free. A trustworthy delivery means the required evidence passed for the tested commit and conditions, known limitations are disclosed, and no known release-blocking defect remains.

- Generate or strengthen tests whenever executable behavior changes.
- For a real bug fix, add a regression test or smallest reliable fixture that would have failed before the fix whenever reasonably reproducible.
- Test happy paths, error paths, empty/missing values, boundaries, malformed inputs, permissions and recovery where applicable.
- Shared/core changes require dependent-system regression tests.
- API/schema changes require compatibility/contract tests.
- Authentication, authorization, payment, privacy, security, migration and destructive-action changes require stronger negative tests, permission checks and rollback evidence.
- Do not silently swallow exceptions, hide failed checks, delete meaningful tests, weaken thresholds, or mark failures skipped merely to get green CI.
- Suspicious patterns such as broad ignores, empty catches, TODO/FIXME/HACK markers and blanket lint disables require review; context determines whether they are defects.
- Run `python3 tools/audit_trusted_code_delivery.py` and use **Trusted Code Reviewer** for significant executable changes.
- Code intended for release should pass the **Code Trust Gate** in addition to relevant focused tests.

## Build and validation

Use the smallest focused test first. Then use:

- `python3 tools/buddy_local_repository.py check` for local/offline health.
- `npm run easy:check` for normal repository changes.
- `npm run easy:fleet` for bot/division/fleet changes.
- `npm run easy:resources` for resources/scouts/catalog changes.
- `python3 -m unittest tests.test_offline_generator_universal_sandbox` for offline/generator/universal sandbox changes.
- `python3 -m unittest tests.test_trusted_code_delivery` for trusted-code policy changes.
- `npm run test:repository` for broad verification when necessary.
- `npm run buddy:fleet:e2e` when shared fleet behavior or bot routing could be affected.

## Repair rules

Fix the first root cause, not cascade errors. Do not weaken tests, hide errors, bypass permissions, or hand-edit generated evidence just to pass CI. Prefer a shared infrastructure fix when many bots share the same failure. Add regression coverage for real defects.

## Capability truth

A config, plan, catalog, generated curriculum, or declared bot capability is not runtime proof. Runtime claims require executable evidence. Planned sandbox cases remain planned until a runner records pass/fail evidence.

## Offline-first rule

Core Buddy build/test/repair/generator behavior must remain usable without GitHub or internet access where technically possible. GitHub-specific features should have a local functional equivalent or a clean optional adapter boundary.

## Safety and side effects

External outreach, publishing, purchases, money movement, applications, contracts, destructive production changes, sensitive-data access, or other consequential actions remain approval-gated. Sandbox and mock execution are preferred.
