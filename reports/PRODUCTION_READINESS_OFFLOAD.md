# Production readiness work done without CodeRabbit

Date: 2026-09-27
Base: `main` @ `b47233f4d912674549f4735c333a10fe2eaa99d5`

Goal: do the expensive review/CI-truth work here so CodeRabbit minutes stay off.

## Already done on GitHub

| Item | Where |
| --- | --- |
| Unmerged PR inventory + SHAs | `reports/UNMERGED_PR_VAULT.md` and PR #12057 |
| Efficient Dependabot | `.github/dependabot.yml` on #12057 |
| CodeRabbit cheap config | `.coderabbit.yaml` on this branch |
| Stop auto-filing failure issues | `.github/workflows/actions-failure-watch.yml` on this branch |

## Do not spend CodeRabbit on

- Regenerating PR summaries for vault PRs (inventory exists)
- Reviewing `config/generated/**` or lockfiles (path-filtered)
- Poems, docstrings, unit-test finishing touches (disabled)
- Fix-CI agent loops on Full System Certification (4h kitchen-sink job; fix the job list first)
- 192 `ci-failure` issues one-by-one (same workflows, same root keys)

## Human / Grok reviews already completed

### PR #12057 — vault + Dependabot
Safe to merge after this branch lands or rebase. No runtime code. Does not discard feature branches.

### PR #9573 — System Watch + Gap Closure
~198k additions. Treat as a data dump, not a CI hotfix. Do not squash onto main until catalog generator is isolated. Head `ff801e286f2e2a6ecc5baa488e39cea112ce23bf` is vaulted.

### PRs #9575 / #9576
Fail-closed observability/trust tiles. Smallest real product slices. Rebase onto current main one at a time after #12057.

### Draft #8847 and stale #467–#830, #3682, #3684, #5123, #7973
Do not merge. Recover files from vault SHAs only if a current-main PR needs that slice.

### Dependabot majors
#10115 Gradio 4→6, #2402 checkout 4→7, personal-repo Vite 5→8: close after efficient Dependabot is on main.

## CI truth

| Workflow | Latest observed | Action |
| --- | --- | --- |
| Full System Certification run [36327308406](https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/36327308406) | failure on schedule, ~2 minutes (not 240) | Job is a kitchen sink; do not pay an agent to “fix certification.” Narrow or disable schedule. |
| Grok Owner Systems | failure on `*/8` cron | Isolated to `tools/grok_run_owner_systems.py` + test; cheapest real fix if you want one agent task. |
| Actions Failure Watch | success that **opens issues** | This branch stops issue create/close. |
| Repository System Watch | recent success | Leave alone. |

## Workflows that should stay after a later cleanup (not done in this PR)

Keep: one CI, CodeQL, dependency-review, Pages deploy, one health job.
Disable later (do not delete in this PR): Run Everything Now, Keep Green, Failure Sweep, Command Center fan-out, Parallel Benchmark Gap Builders, 500-Model Benchmark on a tight cron.

## CodeRabbit budget if you still use it

1. One `@coderabbitai review` on this PR and on #9575/#9576 after rebase.
2. Nothing else until GitHub App write is accepted on the org.
3. Never `@coderabbitai full review` on #9573 or other 100k-line PRs.
