# DreamCo three-runtime traceability ledger

Snapshot: 2026-11-23 local time (GitHub API timestamps may be 2026-11-24 UTC). This is a point-in-time inventory, not a claim that the listed work is complete.

## Runtime candidates

| Candidate | Repository | Canonical responsibility | Current evidence | Remaining gate |
|---|---|---|---|---|
| Python reference | `DreamCo-Technologies/Dreamcobots` | Buddy orchestration, division registry, provider policy, data, tokenizers, training, evaluation, benchmark definitions and release evidence | Main repository; multiple Python contract and training PRs merged | Complete remaining PR reconciliation; verify live DB/storage/queue/compute integrations; run actual approved tokenizer/weight training; private holdout and release gates |
| Apple C | `ireanjordan24/dreamcobots` | Portable native runtime and later Apple Silicon execution adapter | `core-c/` CMake project, public header, source, C tests and `.github/workflows/dreamco-c-runtime.yml`; C workflow has successful runs on `main` and `feat/dreamco-c-runtime-foundation`; an earlier run failed on both OS matrix jobs | Reconcile branch/main history; investigate old Build failure; add shared contract fixtures, runtime implementation and benchmark evidence only after Python completion |
| Apple Swift | `ireanjordan24/dreamcobots` | Existing macOS UI/provider/orchestration candidate | `dreamco/ContentView.swift`, `dreamco/OpenRouterService.swift`, `dreamco/dreamcoApp.swift`, Xcode project, unit tests and UI tests exist | Preserve app and provider path; add a dedicated Xcode build/test workflow and shared task/provider contract conformance after Python completion |

## Python-first work reconciliation

| PR | Scope | Snapshot status | Traceability / next action |
|---|---|---|---|
| #18157 | Private holdout benchmarking | Merged | Verify benchmark artifacts and holdout isolation on current main; a merge alone is not a completed benchmark campaign |
| #18161 | Per-division PostgreSQL catalog identities | Merged | `buddy/datasets/postgres_catalog.py`, `tests/test_buddy_postgres_catalog.py`; verify real DSNs, grants, schema isolation and integration evidence |
| #18168 | Buddy Bootcamp curriculum for all 65 divisions | Merged | Verify curriculum coverage and that each learning path is backed by approved data/resources, not just catalog entries |
| #18169 | Release-gate-compatible training evidence | Merged | Verify evidence is emitted by real training jobs and binds exact code/data/model/checkpoint revisions |
| #18170 | Canonical per-division model identities | Merged | Verify identities are backed by actual checkpoints/tokenizers and execution evidence; specification-only models are not trained models |
| #18158 | Model-provider data classification and output-use policy | Open | Review `buddy/models/provider_runtime.py`, `config/buddy-model-serving-policy.json`, tests and generated artifacts. Verify provider-specific classification ceilings, model allowlists, output-training permission semantics, request audit evidence and fail-closed behavior. Reconcile stale base before merge |
| #18159 | S3 object storage health and backup/restore evidence | Open | Review `buddy/storage/object_store.py`, tests and workflow. Test credential-chain behavior, encryption/versioning/retention, isolated healthcheck prefix, backup/restore integrity and real service evidence. Mocks do not prove live S3 connectivity. Reconcile stale base before merge |
| #18167 | Five-minute planning versus actual training | Open | Verify the scheduler cannot claim training from planning events; real worker execution must produce job IDs, resource allocation, checkpoints, logs and benchmark evidence. Reconcile stale base before merge |

## Apple repository workflow evidence

- C workflow: `.github/workflows/dreamco-c-runtime.yml`.
- Successful run on Apple repository `main`: [run 45334180626](https://github.com/ireanjordan24/dreamcobots/actions/runs/45334180626).
- Successful run on `feat/dreamco-c-runtime-foundation`: [run 45333790023](https://github.com/ireanjordan24/dreamcobots/actions/runs/45333790023).
- Earlier failed C matrix run: [run 45333715060](https://github.com/ireanjordan24/dreamcobots/actions/runs/45333715060); both Ubuntu and macOS Build steps failed. Preserve and diagnose this evidence; later success does not erase the failure.
- The inspected C workflow builds/tests CMake on Ubuntu and macOS. It does not establish Swift compilation or Xcode UI-test execution.
- The private Apple repository has no open PRs in the inspected query. Its default branch is `main`; inspect branch history and submodule pins before any synchronization.

## Shared three-runtime release gates

1. Python remains the source of truth for task packets, division/model identities, provider policy, dataset rights/manifests, tokenizer/model artifacts, benchmark cases and release evidence.
2. Complete and verify Python services, approved tokenizer/weight training, private holdout, regression/safety tests, backup/restore and release gates before promoting either Apple candidate.
3. Freeze versioned JSON schemas and conformance fixtures.
4. Keep C and Swift as separate candidates with independent builds/tests and a shared task/provider interface.
5. Compare only parity-controlled workloads: same task packet, model/tokenizer revisions, prompts, tool permissions, data splits, benchmark version and gates. Record hardware/OS/compiler/runtime/environment. Separate incomparable hardware cohorts.
6. Select the best eligible implementation per task only after capability, rights, privacy, safety, quality and reproducibility hard gates. Keep fallback and rollback evidence.
7. Do not infer training from scheduled jobs, model quality from parameter count, or performance from language choice.

## Operational truth and safety boundaries

- A merged PR means its code is in the target branch; it does not prove live external services, training, model quality, or production readiness.
- A green C build does not prove a complete inference runtime; a Swift UI test does not prove model inference parity.
- No Mac runner execution is claimed by this ledger. Use it only when runner registration and actual job execution are observable.
- Do not commit credentials or raw private ChatGPT conversations. Export only explicitly approved requirements and decisions.
- Do not rewrite history, delete old branches, bulk-update the submodule, cancel productive workflows, enable Cloudflare, or weaken macOS security controls.
