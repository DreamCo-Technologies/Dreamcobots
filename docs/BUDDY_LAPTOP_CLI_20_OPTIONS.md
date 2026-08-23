# Buddy + Laptop: 20 CLI Operating Modes

These are command-level operating modes for a local DreamCo checkout. They should be implemented as guarded actions, not unrestricted shell access.

1. `buddy doctor` — inspect runtime, Git, Node/Python, dependencies, disk, and configuration.
2. `buddy repo scan` — inventory repository structure, code assets, bots, divisions, workflows, and registries.
3. `buddy repo diff` — compare local working tree against `origin/main` before changing anything.
4. `buddy sync` — fetch remotes and report divergence; never overwrite local work automatically.
5. `buddy status` — summarize Git state, active branch, changed files, failing checks, and pending work.
6. `buddy test` — run the safest relevant unit/integration test set.
7. `buddy benchmark` — execute configured local benchmark suites and save evidence.
8. `buddy sandbox` — run generated code in an isolated sandbox with resource/time limits.
9. `buddy train` — run a targeted capability curriculum using the compute-aware scheduler.
10. `buddy learn` — ingest authorized sources and convert them into original study assets with provenance.
11. `buddy assets` — scan existing simulations/apps/websites/libraries and map them to capabilities.
12. `buddy build` — build a selected app, website, package, or service and capture artifacts/logs.
13. `buddy debug` — diagnose a failing build/test/runtime and propose the smallest safe repair.
14. `buddy fix` — apply an approved repair, run tests, and produce an auditable diff.
15. `buddy ci` — inspect or run local CI-equivalent gates before pushing.
16. `buddy actions` — open a unified Actions command/status view backed by the Actions registries.
17. `buddy capabilities` — show capability gaps, mastery evidence, and next-best training actions.
18. `buddy workflows` — inspect, validate, and locally exercise DreamCo workflows.
19. `buddy pr` — prepare a reviewable branch/commit/PR summary; merging remains governed.
20. `buddy release` — run production-readiness checks and prepare a release; deployment/write actions require explicit authorization.

## Safety defaults

- Read-only discovery is the default.
- Sandbox is the default execution environment for generated code.
- Destructive commands require explicit approval.
- Secrets are never printed.
- Production writes require authorization and audit evidence.
- Every action emits an execution/audit record.
- Local work is never silently discarded to make Git clean.
