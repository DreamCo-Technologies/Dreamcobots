# Repo Autonomous Systems Plan (draft, 2026-09-28)

Goal: every recurring Grok-bot job also runs inside the repo (GitHub Actions + scripts), so the repo keeps working without agents.
Rules: evidence-first, no deletes, never auto-flip `production_ready`, fold into existing workflows before adding new ones.

## Bot job -> existing repo automation
| Bot job family | Already scheduled in repo | Gap |
|---|---|---|
| Repo/connectivity scan | `repository-scan-update.yml` (Mon 06:17 UTC), `tools/audit_repository_connections.py` | add connectivity audit step + write `reports/prod-connectivity-scan.json` |
| Fleet health / System Watch | `repository-system-watch.yml` (hourly) | fix stale 1051/45 baselines (PR #9573) |
| Gap closure | `engineering-gap-closure.yml` (daily 14:19 UTC) | same as above |
| Goals -> gates / prod readiness | `production-readiness.yml` (daily), `self-working-system.yml` (daily) | add goals-to-gates regen step |
| Cert gate | `full-system-certification.yml` (daily) | keep fail-closed (#9575) |
| Benchmarks / evidence | `benchmark-evidence-loop.yml` (hourly), benchmark-* family | wire vs500 T0 card output |
| Branch readiness | `branch-health-daily.yml` (daily) | report-only, no deletes |
| HF study | `grok-twins-hf-study.yml` (daily 07:19 UTC) | add `tools/build_hf_capability_packs.py` + `study_packs/hub/drills/run_all.sh` (anonymous, no training) |
| Bootcamp | `buddy-sandbox-bootcamp.yml` (dispatch only) | add weekday off-peak cron |
| Pages | `pages.yml`, `actions-page-gate.yml` (no cron) | add link check for website/ nav + missing pages |
| Bot orchestration | `grok-owner-systems.yml`, `autonomous-systems-builder.yml` (every 8h) | publish fleet status report consumed by check-ins |
| O*NET / data packages | `tools/build_universal_work_ai_catalog.py` (no schedule found) | weekly build + license/provenance gate |

## P0: first 5 conversions
1. `grok-twins-hf-study.yml`: add HF pack build + hub drills, upload `study_packs/**/evidence` as artifact.
2. `buddy-sandbox-bootcamp.yml`: add `schedule: cron "23 8 * * 1-5"`.
3. `pages.yml`: add website link-check job (fail on broken nav links).
4. `repository-scan-update.yml`: add `tools/audit_repository_connections.py` step writing the connectivity json.
5. `self-working-system.yml`: add a `reports/FLEET_STATUS.md` step (PR states, CI, pack counts) so status exists without agents.

Note: `reports/ACTIONS_CONSOLIDATION_PLAN.md` is not present in this checkout; fold these into the durable buckets once it is restored.
