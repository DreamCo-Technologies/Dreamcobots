# HF Day-1 Evidence Packet

```yaml
packet: hf-day1-evidence
claimable: false   # stays false until certification
mastered: false    # stays false until certification
drafted: 2026-10-02 (CT), local draft, not committed
base: origin/main @ 5ba09f2ea
```

Rules for this packet: an item counts as evidence only if a file, PR, or command output below backs it.
"Uncommitted" means the file exists only in a local checkout/worktree on the shared box, not on any pushed branch.

## Where each item lives

| Item | origin/main | Open PR | Uncommitted only |
| --- | --- | --- | --- |
| Hub Day-1 audit (`study_packs/hub/day1_audit.py`, `evidence/drills.json`, `evidence/day1-inventory.json`) | yes, commit `24ca34bd8` | n/a | n/a |
| Hub drills 01-05 (`study_packs/hub/drills/`, `evidence/drill_0*.log`) | no | [#12444](https://github.com/DreamCo-Technologies/Dreamcobots/pull/12444) (head `15b390a84`) | also a byte-identical copy in `/workspace/Dreamcobots` |
| Multimodal pack (`study_packs/multimodal/`, `tests/test_study_pack_multimodal.py`) | no | [#12433](https://github.com/DreamCo-Technologies/Dreamcobots/pull/12433) (head `af364e345`) | also a byte-identical copy in `/workspace/Dreamcobots` |
| nlp-tasks zoo (`study_packs/nlp-tasks/`, `tests/test_nlp_task_zoo_drills.py`) | no | none found | yes, `/workspace/Dreamcobots` only |
| Datasets pack (`study_packs/datasets/`, `tests/test_study_pack_datasets.py`) | no | none found | yes, `/workspace/hf-datasets-pack` (branch `study-pack-datasets`) only |
| Capability-pack builder changes (`tools/build_hf_capability_packs.py`, its test) | older version on main | none found | modified, `/workspace/Dreamcobots` (+353/-47 lines) |

## Studied

- `study_packs/hub/DAY1_NOTES.md` (on main; a different, untracked version is in `/workspace/Dreamcobots`): Day-1 topic "License, provenance, and exact checkpoint inventory". Covers `revision=` pins, model cards, license metadata, gated repos, safetensors vs pickle. Inventory: 23 model ids, 8 dataset ids.
- `study_packs/nlp-tasks/README.md` (uncommitted): 5 tasks (classification, ner, qa, summarization, translation), 24 drills total. Stdlib scorer only, no weights.
- `study_packs/multimodal/README.md`, `sources.json` (PR #12433): CLIP, ViT, MMS-TTS, Whisper-tiny, AST. Revisions are pinned to 40-char SHAs.
- `study_packs/datasets/` lessons 01_load_dataset, 02_map, 03_streaming (uncommitted, `/workspace/hf-datasets-pack`).

## Ran

| # | What | Source / command | Observed result |
| --- | --- | --- | --- |
| R1 | Hub drills 01-05, anonymous (`huggingface_hub 2.0.0`), 2026-09-28 17:32-17:33 CDT | `study_packs/hub/evidence/run_summary.tsv` (PR #12444) | drill_01-04 exit 0 (`RESULT: PASS`), drill_05 exit 1. **4/5 passed.** |
| R2 | drill_05 inventory audit | `study_packs/hub/evidence/drill_05_inventory_audit.json` / `.log` (PR #12444) | models: total 23, ok 16, **gated 5**, **missing 2**, error 0. datasets: total 8, ok 7, gated 1. `weights_downloaded: false`, `claimable: false` |
| R3 | Hub Day-1 audit on main | `study_packs/hub/evidence/drills.json`, `day1-inventory.json` (main, `24ca34bd8`) | `ran: 5, passed: 4` (failed: "inventory"). checked 31: public 23, gated 7, missing 0, not_a_model_id 1. `token_used: false`, `downloaded: false` |
| R4 | Multimodal drills, CPU (py 3.13.5, transformers 5.17.0, torch 2.14.0+cpu), 2026-09-28 22:52Z (17:52 CT) | `study_packs/multimodal/evidence/latest.json` = `run_20260928T225217.json` (PR #12433) | **5/5 PASS**, pass_rate 1.0: clip_zero_shot_shapes 3/3 hits, vit_imagenet_smoke, tts_generate (3.94 s wav), asr_roundtrip WER 0.333 (floor <=0.5), audio_cls_smoke |
| R5 | nlp-tasks harness self-test (recorded) | `study_packs/nlp-tasks/evidence/harness-selftest-2026-09-28.json` (uncommitted) | `ok: true`, all 5 tasks gold_mean 1.0 / wrong_mean 0.0. Kind: `harness_selftest_not_model_eval` |
| R6 | nlp-tasks self-test (re-run 2026-10-02) | `python3 study_packs/nlp-tasks/drill_runner.py --selftest` (stdout only) | `ok: True`, all 5 tasks ok |
| R7 | nlp-tasks tests (re-run 2026-10-02) | `python3 -m pytest -p no:cacheprovider -q tests/test_nlp_task_zoo_drills.py` in `/workspace/Dreamcobots` | **4 passed** in 0.03s |
| R8 | Multimodal structure tests (re-run 2026-10-02) | `python3 -m pytest -p no:cacheprovider -q tests/test_study_pack_multimodal.py` in `/workspace/Dreamcobots` | **4 passed** in 0.03s (offline schema checks only, no model run) |
| R9 | Datasets pack tests (re-run 2026-10-02) | `python3 -m pytest -p no:cacheprovider -q -rs tests/test_study_pack_datasets.py` in `/workspace/hf-datasets-pack` | **6 passed, 3 skipped**. Skip reason: "datasets library not installed; offline lesson examples skipped" (load_dataset, map, streaming) |
| R10 | Capability-pack builder tests (re-run 2026-10-02) | `python3 -m pytest -p no:cacheprovider -q tests/test_build_hf_capability_packs.py` | uncommitted version in `/workspace/Dreamcobots`: **5 passed**. main version: **1 passed** |

## Failed

- **F1 drill_05_inventory_audit**: `RESULT: CHECK_FAIL (2 inventory model id(s) missing on the Hub)`, exit 1.
  - Gated (anonymous 401, `gated=manual`): meta-llama/Llama-3.1-70B-Instruct, google/gemma-2-27b-it, meta-llama/Llama-3.1-8B-Instruct, google/gemma-2-9b-it, meta-llama/Llama-Guard-3-1B.
  - Missing (HTTP 401, repo not found or private): mistralai/Mistral-Large-Instruct, openai-community/gpt-oss-study-only-if-license-allows.
  - Gated dataset: bigcode/the-stack-smol (`gated=auto`).
- **F2 main's Day-1 audit, "inventory" drill**: `passed: false`. The same ids are classified differently here. Mistral-Large-Instruct is counted as `gated` (code 401), gpt-oss-... as `not_a_model_id`, and gated totals 7 (6 models + 1 dataset). The two audits disagree on 5-vs-6 gated models and 2-vs-0 missing. This needs a single source of truth.
- **F3 first multimodal run** `run_20260928T225019.json`: 2/5. tts_generate ERROR `TypeError: BatchEncoding.to() got an unexpected keyword argument 'dtype'`, so asr_roundtrip and audio_cls_smoke were BLOCKED. The second run fixed this with the "VitsModel direct (pipeline bug workaround)" method.
- **Weak pass (not a failure, but flag it)**: in R4, audio_cls_smoke passes only on `len(out) > 0`. `top1_is_yes: False` (top-1 was "visual", 0.9834). Its PASS does not show correct classification.
- **Not exercised**: the 3 datasets lesson tests (R9) skipped because `datasets` is not installed in system python or `/workspace/hf-venv`.
- **CI**: `trusted-code` = FAILURE on #12444 and #12433. #12433 also fails "Typecheck, tests, build, fleet and security". Root cause not investigated here.

## Reported, not yet verified

Reported by another agent (via the parent agent's handoff, 2026-10-02). Each line says what the files confirm and what they don't:

- "Hub drills 4/5 passed; drill_05: 5 gated, 2 missing": **verified** against PR #12444 evidence files (R1, R2). It is **not on main**. Main's own audit says 4/5 but 7 gated (6 models) / 0 missing (F2).
- "Multimodal 5/5 on CPU": **verified** from the recorded evidence (R4) only. It was not re-run here (that would need model downloads). It is in PR #12433, not on main.
- "nlp-tasks harness self-test": **verified** (R5-R7). It is a harness check, not model evidence, and is uncommitted only.
- "datasets pack tests": **partially verified**. 6 structural tests pass, but the 3 offline lesson tests were skipped (R9). There is no recorded run evidence: `study_packs/datasets/evidence/README.md` says "Nothing is recorded yet." It is uncommitted only.
