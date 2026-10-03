# GOALS_TO_PRODUCTION_GATES

Main checked: `2ccd678e5` (2026-09-28 5:28 PM CT). Readiness report on main generated from `0a496c5b1`. Verdict: **NOT production-ready**. Nothing here is MET.

Goal source: `docs/PRODUCTION_READINESS_MASTER_PLAN.md` (15 workstreams + completion criteria), statuses from `data/production-readiness-report.json`, gate runs from GitHub Actions on `main`.

## P0 gaps (evidence)

1. Dependency audit fails in both `code-trust-gate` (run 36492623176) and `full-system-certification` (run 36492623235). `buddy/media/{connectors,core,image,memory_guard,voice}.py` and `tests/test_buddy_media.py` import PIL, chatterbox, diffusers, f5_tts, kokoro, openvoice, psutil, scipy, soundfile, which are not in any Python manifest (`requirements-tools.txt`, `requirements-buddy-learning.txt`, `huggingface/dreamco-router/requirements.txt`). Last green code-trust-gate was run 36377227740 on `0a496c5b1` (Sep 27, 11:19 PM CT). Fix: add a `requirements-buddy-media.txt` (or optional-extras manifest) and register it with the audit, or guard imports as optional.
2. Static site is 60.96 MiB, over the 52 MiB deployment-cost cap (run 36492623235). Fix: prune or externalize large Pages assets.
3. Full certification last passed on `e49446d44` (run 35386383194, Sep 18, 2:31 PM CT). It has not been green for 10 days; current run is 27 passed, 3 failed.
4. Live environment checks remain `external_config_required`. Only the owner can supply live production env/secrets for smoke tests.

## Truthfulness flags

- `production-readiness.yml` is green on `2ccd678e5` while full certification is red. Its green means the evidence-first report built, not that production is certified. Nobody should cite it as certification.
- `reports/PRODUCTION_READINESS_REPORT.md` on main (from `0a496c5b1`) lists 12 `pass` runtime rows, but most are "documented" checks (env var names in `.env.example`, files existing), not live runtime proof. It is honest about this in its note, but readers should not treat those rows as runtime evidence.
- `config/generated/bot-production-readiness.json` correctly shows `production_ready_true: 0` across 1,101 bots. Good.

## Goal table

| Goal | Status | Priority | Required evidence | Current failure |
|---|---|---|---|---|
| 1 Buddy orchestration | PARTIAL | P1 | buddy router source, router tests, routing evidence |  |
| 2 Benchmarking | PARTIAL | P1 | benchmark schema, benchmark tests, reproducibility metadata |  |
| 3 Capability Genome | PARTIAL | P1 | capability registry, capability validation, integration evidence |  |
| 4 Model research | PARTIAL | P1 | model registry, official-source provenance, execution adapter evidence |  |
| 5 Teacher-model eval | UNVERIFIED | P1 | teacher benchmark contract, baseline evidence, repeat-run evidence |  |
| 6 Experiment | PARTIAL | P1 | experiment lifecycle, isolated execution, result persistence |  |
| 6 Ablation | UNVERIFIED | P1 | ablation matrix, controlled fixtures, automated results |  |
| 7 Distillation | UNVERIFIED | P1 | teacher/student contract, quality floor, rollback evidence |  |
| 8 Free-first | PARTIAL | P1 | resource policy, budget enforcement, fallback tests |  |
| 8 Resource optimization | PARTIAL | P1 | resource measurements, hardware profile, regression thresholds |  |
| 9 Regression | FAILING | P0 | regression suite, failure fixtures, release gate | governed-tests FAIL: tests/test_repository_dependencies.py (run 36492623235) |
| 9 Security | FAILING | P0 | secret scan, dependency audit, license/provenance audit | code-trust-gate + full-system-certification dependency audit FAIL on main 2ccd678e5 (undeclared PIL, chatterbox, diffusers, f5_tts, kokoro, openvoice, psutil, scipy, soundfile from buddy/media/*) |
| 10 Actions control plane | PARTIAL | P1 | stable action IDs, UI tests, source-to-UI evidence |  |
| 11 Autonomous scanning | PARTIAL | P1 | scheduled workflow, evidence artifact, Actions ingestion |  |
| 11 Source ingestion | PARTIAL | P1 | provenance, freshness, refresh failure handling |  |
| 12 Superbot/fleet | PARTIAL | P1 | module registry, routing tests, conflict serialization |  |
| 13 Deployment | FAILING | P0 | production build, health endpoint, rollback procedure | full-system-certification deployment-cost FAIL: static site 60.96 MiB > 52 MiB cap (run 36492623235) |
| 14 Observability | PARTIAL | P1 | correlation IDs, structured telemetry, benchmark/agent traces |  |
| 15 Cost accounting | PARTIAL | P1 | usage ledger, provider/model attribution, budget reconciliation |  |
| Completion criteria: platform production-ready | FAILING | P0 | certification with no release-blocking failures, live external smoke tests | cert 27 pass / 3 fail on 2ccd678e5; last green 35386383194 on e49446d44 (Sep 18); live env = external_config_required |
