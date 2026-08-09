# DreamCo Copilot Instructions

DreamCo is a large multi-bot platform. Treat the canonical repository structure as the source of truth and do not create duplicate parallel architectures without checking for an existing owner first.

## Before editing

- Read `AGENTS.md`.
- For bot/division work, inspect `App_bots/`, the fleet generators, sandbox curriculum, placement audit, and Council career path generators.
- For resource work, inspect the canonical resource contracts and universal resource sandbox.
- For GitHub/CI work, inspect `tools/audit_actions_health.py`, `Buddy Actions Test Lab`, `DreamCo Control Center`, and the failure watcher/sweep.
- For offline work, inspect `config/offline-buddy-repository-engine.json` and `tools/buddy_local_repository.py`.

## Build and validation

Use the smallest focused test first. Then use:

- `python3 tools/buddy_local_repository.py check` for local/offline health.
- `npm run easy:check` for normal repository changes.
- `npm run easy:fleet` for bot/division/fleet changes.
- `npm run easy:resources` for resources/scouts/catalog changes.
- `python3 -m unittest tests.test_offline_generator_universal_sandbox` for offline/generator/universal sandbox changes.
- `npm run test:repository` for broad verification when necessary.

## Repair rules

Fix the first root cause, not cascade errors. Do not weaken tests, hide errors, bypass permissions, or hand-edit generated evidence just to pass CI. Prefer a shared infrastructure fix when many bots share the same failure. Add regression coverage for real defects.

## Capability truth

A config, plan, catalog, generated curriculum, or declared bot capability is not runtime proof. Runtime claims require executable evidence. Planned sandbox cases remain planned until a runner records pass/fail evidence.

## Offline-first rule

Core Buddy build/test/repair/generator behavior must remain usable without GitHub or internet access where technically possible. GitHub-specific features should have a local functional equivalent or a clean optional adapter boundary.

## Safety and side effects

External outreach, publishing, purchases, money movement, applications, contracts, destructive production changes, sensitive-data access, or other consequential actions remain approval-gated. Sandbox and mock execution are preferred.
