# HF Day-1 Repeat Runs

```yaml
packet: hf-day1-repeat-runs
claimable: false
mastered: false
drafted: 2026-10-05 16:45 CDT
branch: bench/hf-day1-repeat-runs
base: origin/main @ f1ece6ffa76e6d0230ebefa1daf50523f91c7cf6
promotion: never set true in this packet
```

Rules: numbers below come only from the evidence JSON/log files linked. `claimable: false` and `mastered: false` everywhere. No push / no PR from this work (owner approval pending).

## Summary table

| Benchmark | Run 1 result | Run 2 result | Match / drift | Run1 path | Run2 path |
| --- | --- | --- | --- | --- | --- |
| nlp-tasks harness self-test | ok=true, 5/5 tasks gold_mean=1.0 | ok=true, 5/5 tasks gold_mean=1.0; pytest 4 passed | **MATCH** | `study_packs/nlp-tasks/evidence/harness_selftest_run1.json` | `study_packs/nlp-tasks/evidence/harness_selftest_run2.json` |
| Hub drills 01-05 | 4/5 pass (drill_05 CHECK_FAIL); models 23/ok16/gated5/missing2; datasets 8/ok7/gated1 | same 4/5; same model_summary & dataset_summary; 0 status drift; 0 sha drift | **MATCH** | `study_packs/hub/evidence/hub_drills_run1.json` (+ existing `drill_05_inventory_audit.json`, `run_summary.tsv`) | `study_packs/hub/evidence/hub_drills_run2.json` (+ `drill_05_inventory_audit_run2.json`, `run_summary_run2.tsv`, `*_run2.log`) |
| Datasets pack tests | 6 passed, 3 skipped (no `datasets` lib) | 9 passed, 0 skipped (`datasets==5.0.1` in venv) | **DRIFT (expected env enrichment)** — 3 offline lesson tests un-skipped | `study_packs/datasets/evidence/pack_tests_run1.json` | `study_packs/datasets/evidence/pack_tests_run2.json` |
| Multimodal 5 drills (CPU) | pass_rate **0.4** (2/5); tts ERROR; asr+audio_cls BLOCKED | pass_rate **1.0** (5/5); same CLIP rev `3d74acf9…` | **DRIFT — NOT promotion-eligible**; no new run performed | `study_packs/multimodal/evidence/run_20260928T225019.json` | `study_packs/multimodal/evidence/run_20260928T225217.json` |

Multimodal drift detail: `study_packs/multimodal/evidence/run1_vs_run2_drift.json`.

## Per-benchmark notes

### 1. nlp-tasks harness self-test (smallest; done first)

- Kind: `harness_selftest_not_model_eval` (stdlib scorer; **no model weights**; `model_id` / `model_revision_sha` are null by design).
- Command: `python3 study_packs/nlp-tasks/drill_runner.py --selftest` (+ pytest for run 2).
- Run 1 source: original `harness-selftest-2026-09-28.json` (also on main); wrapped into `harness_selftest_run1.json`.
- Run 2: fresh on this branch worktree @ `f1ece6ffa…`, timestamp America/Chicago in the JSON.
- **Match:** identical per-task gold_mean/wrong_mean/ok.

### 2. Hub drills 01-05

- Metadata API only; `weights_downloaded: false`; anonymous.
- Code on main (originally PR [#12444](https://github.com/DreamCo-Technologies/Dreamcobots/pull/12444), head `15b390a84`); run 2 executed in detached worktree `/workspace/hf-repeat-runs-hub` at that commit.
- drill_05 still `RESULT: CHECK_FAIL` with gated=5 missing=2 (same ids as run 1).
- **Match:** exit codes, model_summary, dataset_summary, per-repo status, and latest_sha all identical vs run 1.

### 3. Datasets pack tests

- Pack + `tests/test_study_pack_datasets.py` on main.
- Dataset pin (same for both runs): `openai/gsm8k` @ `740312add88f781978c0658806c59bc2815b9866` (`study_packs/datasets/sources.json`).
- Run 1: system python without `datasets` → 6 pass / 3 skip (matches Day-1 packet R9).
- Run 2: `/workspace/.venv-hf-datasets` with `datasets==5.0.1` → **9 passed**.
- Drift is environment enrichment, not a scorer change. Still `claimable: false`.

### 4. Multimodal — drift report only (no new run)

- Verified on `origin/main`: both `run_20260928T225019.json` (0.4) and `run_20260928T225217.json` (1.0) present; CLIP revision `3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268` identical across runs (and in `sources.json`).
- Pass-rate jump 0.4 → 1.0 means the two saved runs **do not match**; **not promotion-eligible**.
- No third run was started or committed.

## Not run / blockers

| Item | Status |
| --- | --- |
| New multimodal CPU re-run | **Not run** (conductor: main already has two saved runs; drift-only) |
| Hub weight downloads | Never attempted (drills are metadata-only) |
| Datasets network Hub fetch | Not needed; offline lesson examples + `HF_HUB_OFFLINE=1` |

## Safety confirmations

- Branch: `bench/hf-day1-repeat-runs` (local only).
- **Not pushed. No PR opened. main not touched.**
- Shared checkout `/workspace/Dreamcobots` not used for test execution; only `git fetch` / `git worktree add`.
- Forbidden trees not modified for writes: `/workspace/hf-day1-evidence`, `/workspace/hf-datasets-pack` (read-only / pytest source of truth already on main).
