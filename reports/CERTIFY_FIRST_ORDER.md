# Certify-First Order — DreamCo Master Roadmap (local draft, evidence-only)

- **Prepared:** 2026-10-02 (America/Chicago). Local draft only; nothing pushed, no PRs, no `production_ready` flags changed.
- **Roadmap source:** `docs/DREAMCO_MASTER_ROADMAP_2026.md` read from `origin/main` @ `5ba09f2ea0c1ef49e8e41bbca78c317ad70be8e9` (main tip committed 2026-10-02 12:09 CDT).
- **Status source:** `/home/box/roadmap/coverage_snapshot.json` (reconstructed 2026-09-28 from `reports/PLAN_TO_GROK_BOT_COVERAGE.md`, generated 2026-09-21 16:25 CDT). Statuses below are from that snapshot. Where `origin/main` now has newer evidence, it is listed separately and labeled.
- **Rule:** if something is not in a file or in git history, it is marked **unknown**. Owner bots exist, but having an owner is not evidence.

## 1. The 10-item certify-first order

| # | Plan | Owner (snapshot) | Status (snapshot) | Snapshot evidence | Newer evidence on origin/main | Evidence still missing |
|---:|---|---|---|---|---|---|
| 1 | `plan-buddy-bootcamp` (Buddy Bootcamp) | Grok-Buddy-Bootcamp-Commandant | partial | specs/config/tools; no graduation evidence | `.github/workflows/buddy-sandbox-bootcamp.yml` exists, but only on dispatch/push with no schedule. It runs a sandbox smoke test and validates the curriculum JSON. Also present: `buddy/bootcamp/buddy_bootcamp.yaml`, `buddy/learning/bootcamp.py`, `docs/BUDDY_BOOTCAMP_SANDBOX_SPEC.md` | Any graduation record (a bot completing the bootcamp with scored results). No scheduled runs exist yet. The last green run of the bootcamp workflow is unknown. |
| 2 | `plan-buddy-frontier` (Buddy Frontier) | Grok-Frontier-Loop-Captain | partial | G1–G7 defined; 0/7 evidence-passed | `evidence/frontier/current-status.assessment.json` reports `claimable: false`, `status: incomplete_or_unproven`, `run_count: 0`, `independent_learning_proven: false` (suite_id `buddy-frontier-core-2026-q4`) | Any of G1–G7 passed with evidence. Missing: a Buddy subject, a named frontier reference subject, and a baseline-failure → native-candidate → passing holdout/safety/regression demonstration (from the assessment's `errors`). |
| 3 | `plan-model-access` (Model Access) | Grok-Model-Access-Product-Owner | partial | path stubs; `owner_500_authenticated_live=false` | `buddy_os/actions/paid_model_access_and_resource_import.yaml` exists. No live-auth evidence was found. | An authenticated live check (`owner_500_authenticated_live=true` backed by a run record). Tier/feature-flag enforcement evidence is unknown. |
| 4 | `plan-data-package` (Data Package) | Grok-Data-Package-Merchant | partial | SKU family designed; `populatedDatasetCount 0`; no live sales | `config/data-package-maximal-testing-program.json`, `tools/score_data_package_candidate.py`, `docs/BUDDY_SANDBOX_BOOTCAMP_DATA_PACKAGE.md` | At least one populated dataset with license/provenance. Sales figures are unknown, and no sales evidence exists. |
| 5 | `plan-fleet-capability-gap` (Fleet capability gap) | Grok-Fleet-Gap-Closer | partial | 1101 profiles; `production_ready_profiles=0`; sandbox/adapter/auth/telemetry false for all | `config/generated/universal-capability-gap-workers.json` exists. A newer recount is unknown. | Any profile with sandbox, adapter, auth and telemetry evidenced true. |
| 6 | `plan-prod-readiness-master` (PRC) | Grok-PRC-Certifier | partial | 0/1101 bots `production_ready`; PRC 0 verified / 16 partial / 3 unknown | No newer PRC count found on main | Proof of every PRC item: 0 are verified, 16 are partial and 3 are unknown. The roadmap's Definition of Done needs to be met per bot (canonical interface, `GlobalAISourcesFlow`, `tools/check_bot_framework.py`, tests, docs, health events). |
| 7 | `plan-huggingface-mastery` (Hugging Face mastery) | Grok-HF-Mastery-Coach | partial | inventory + Day-1 plan; study_packs not materialized (at scan time) | **New since snapshot:** `24ca34bd8` (2026-09-28 17:44 CDT) added `study_packs/hub/{DAY1_NOTES.md,day1_audit.py,evidence/day1-inventory.json,evidence/drills.json}`. `drills.json` reports ran 5 / passed 4, and the `inventory` drill **failed**. `tools/build_hf_capability_packs.py` exists and, when run on an export of main, generates 6 packs (code, instruct, reason, research, safety, tools). The output is not committed. | A passing `inventory` drill. Committed or uploaded per-pack evidence. Pinned `repo_id`+`revision`+license in each pack's `sources.json`. |
| 8 | `plan-onet-mastery` (O*NET ingest) | Grok-ONET-Ingest-Lead | stub | pinned O*NET ingest not verified | `config/onet-priority-curriculum.json`, `config/onet-sandbox-dataset-spec.json`, `tools/build_universal_work_ai_catalog.py` (no schedule found in `.github/workflows`) | Pinned O*NET version, an ingest run record, and a license/provenance gate. |
| 9 | `plan-universal-sandbox-programs` (Universal sandbox) | Grok-Universal-Sandbox-Director | partial | 0/1101 `sandbox_test_defined` | **New since snapshot:** `5ba09f2ea` (2026-10-02 12:09 CDT) added `benchmarks/resource_mastery/{sandbox.py,test_sandbox.py}`, and `7ce5b6a2e` (2026-10-02 11:16 CDT) added `benchmarks/america_gov/{sandbox.py,test_sandbox.py,catalog.json}`. It is unknown whether these change the per-bot `sandbox_test_defined` count. | A recount of `sandbox_test_defined` across 1101 bots. Test-run results for the new sandboxes. |
| 10 | `plan-engineering-gap-closure` (Engineering gap closure) | Grok-Eng-Gap-Closure-Pilot | partial | CI Gap Closure noop on tip; not green-certified | `.github/workflows/engineering-gap-closure.yml` (cron `19 14 * * *`), `config/engineering-gap-closure-team.json` | A green, non-noop run linked to closed gaps. Run history is unknown (not in git). |

## 2. Timeline deltas vs `DREAMCO_MASTER_ROADMAP_2026.md`

### 2a. Dated targets in the roadmap
- **None.** The roadmap's Priority Order and 100-idea list give only status words (done / in progress / planned / existing / future). The only date-like text is the "2026" in the title. Every item therefore has **no date in roadmap**, and no "target met by date X" check is possible.
- History of the roadmap file on GitHub `main` (from the GitHub API, because the local clone is shallow):
  - `a57a08200621b6e3fc8d53761c255f3b30ca7478` (2026-08-12 07:54 CDT): created ("docs: consolidate DreamCo roadmap global AI flow and revenue architecture")
  - `2d809d5e9476fdb24fb2838e626407419e4ff5c7` (2026-08-19 09:49 CDT): "docs: remove legacy hosted-provider branding from master roadmap"
  - `9d2f3e7740070e44186de5fbd1958457e93590f0` (2026-09-10 15:24 CDT): "feat: add Buddy laptop test app launcher" (touched the file)
  - The local `git log` shows `2ccd678e5` only because that commit is the shallow-clone graft boundary. It is not a real edit.
- A date-like label exists **outside** the roadmap: the frontier suite id `buddy-frontier-core-2026-q4` (`evidence/frontier/current-status.assessment.json`). That file reports `claimable: false` and `run_count: 0`, so there is no evidence on main that the target was met.

### 2b. Ordering deltas (roadmap Priority Order: Foundation → Intelligence → Commercial → Customer Layer)

| Certify # | Item | Closest roadmap Priority Order slot | Delta |
|---:|---|---|---|
| 1 | Buddy Bootcamp | none (closest: Intelligence → Evaluation/benchmarking; Foundation → Sandbox isolation) | **Missing from roadmap**; placed first |
| 2 | Buddy Frontier | none (closest: Intelligence → Evaluation/benchmarking) | **Missing from roadmap** |
| 3 | Model Access | Commercial → SaaS subscriptions (ideas #30 Feature flags by tier = planned, #41 Tier enforcement = done) | **Moved up** (Commercial tier 3 → #3) |
| 4 | Data Package | Commercial → Marketplace / Lead-generation products (closest) | **Moved up**; not named in roadmap |
| 5 | Fleet capability gap | Foundation → Bot registry and capability graph (Foundation item 1) | **Moved down** (roadmap's first item → #5) |
| 6 | PRC | Foundation → CI/test enforcement + "Definition of Done for a Production Bot" | **Moved down** (Foundation → #6) |
| 7 | Hugging Face mastery | none (closest: Intelligence → Cross-bot learning / Evaluation) | **Missing from roadmap** |
| 8 | O*NET ingest | none | **Missing from roadmap** |
| 9 | Universal sandbox | Foundation → Sandbox isolation (Foundation item 8) | **Moved down** |
| 10 | Engineering gap closure | Foundation → CI/test enforcement; idea #16 "Full CI for all bots — in progress" | **Moved down** |

Roadmap Priority Order items with **no** certify-first slot in the top 10: Canonical DreamCoBot base class, Global AI Sources Flow enforcement, Global configuration, Secrets management, Versioning, Health checks/circuit breakers, Rollback controls (Foundation); Dream Brain, Memory, Anomaly detection, Adaptive scheduling (Intelligence); Revenue attribution, Agency services, Enterprise billing, White-label (Commercial); and the whole Customer Layer. Several of these are covered implicitly through PRC (#6) via the Definition of Done.

## 3. Scheduler-confirmed slots (for the workflow owner; times are UTC as written in cron, with CDT in parentheses)

- **grok-twins-hf-study:** stays at `19 7 * * *` (02:19 CDT). No other workflow fires in that minute.
- **buddy-sandbox-bootcamp:** add `23 8 * * 1-5` (03:23 CDT, weekdays). Caveat: `note-model-hourly.yml` and `system-scan-hourly.yml` (`23 * * * *`) fire in the same minute.
- **pages:** `pages.yml` has no cron (`workflow_dispatch` only, and it calls `deploy-buddy-pages.yml`). The link check runs on push/dispatch only.
- **FLEET_STATUS step:** goes in `self-working-system.yml` at its existing `29 9 * * *` (04:29 CDT) and **must be non-fatal**. No other workflow fires in that minute.
- **repository-scan-update:** if the connectivity audit makes it heavier, move it from Mon `17 6 * * 1` (01:17 CDT) to `53 6 * * 1` (01:53 CDT). On a Monday, 06:17 UTC already has 12 other workflows firing: production-readiness, dreamco-control-plane and benchmark-lessons-daily (daily), five `17 */6` jobs and four `17 * * * *` jobs. Mon 06:53 UTC has none. Note: `bot-production-readiness.yml` is `17 6 * * 0` (**Sunday** only), so it shares 06:17 on Sundays but not on the Monday slot.

## 4. Read-only verification of P0 references on origin/main @ 5ba09f2ea

| Reference | On main? | Note |
|---|---|---|
| `.github/workflows/grok-twins-hf-study.yml` | yes | |
| `tools/build_hf_capability_packs.py` | yes | Runs cleanly on an export of main and writes `study_packs/pack.*`, `study_packs/index.json`, `reports/HUGGINGFACE_CAPABILITY_PACKS.md` |
| `study_packs/hub/drills/run_all.sh` | **MISSING** | The Hub drills on main are `study_packs/hub/day1_audit.py`. It makes anonymous live calls to `huggingface.co/api` and downloads no weights. |
| `.github/workflows/buddy-sandbox-bootcamp.yml` | yes | dispatch + push(paths) only |
| `.github/workflows/pages.yml` | yes | dispatch only; reusable call to `deploy-buddy-pages.yml` |
| website link-check tool | **MISSING** | No broken-link checker on main. `tools/connect_repository_pages.py --check` only checks that pages load the shared nav script; it does not check link targets. |
| `.github/workflows/repository-scan-update.yml` | yes | |
| `tools/audit_repository_connections.py` | yes | Writes `config/generated/repository-system-connections.json` + `reports/REPOSITORY_SYSTEM_CONNECTIONS.md`, **not** `reports/prod-connectivity-scan.json` (a copy/rename step would be needed). Exits 1 if any required reference is missing. On an export of main: ok, 888 refs (753 resolved / 112 generated_at_runtime / 23 missing non-required), 0 blockers. |
| `.github/workflows/self-working-system.yml` | yes | |
| `reports/FLEET_STATUS.md` generator | **MISSING** | No tool on main produces it. A new script or inline step would be needed. |
| `reports/ACTIONS_CONSOLIDATION_PLAN.md` | not checked as P0 | The plan itself says it is absent |

The full cron list is in `/home/box/roadmap/_crons.json` (55 schedules across 90 workflow files on main; all 90 parse with PyYAML).
