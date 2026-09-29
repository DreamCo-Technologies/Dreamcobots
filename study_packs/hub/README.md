# study_packs/hub: HF Hub Day-1 Literacy Pack

```json
{"claimable": false, "weights_downloaded": false, "anonymous_run": true, "committed": false}
```

Phase 1 "hub literacy" deliverable for `docs/HUGGINGFACE_MASTERY_PLAN.md`, Day 1 of `config/huggingface-two-week-study.json`.
This is study material plus runnable evidence. It does **not** prove mastery, frontier parity, or any trained weights.

## Index

| Path | What |
| --- | --- |
| `DAY1_DRILL_NOTES.md` | Hub literacy notes tied to Dreamcobots inventory ids, with source-file citations and `[observed]` markers |
| `drills/DRILLS.md` | Drill catalogue, exit codes, how to run, last-run table |
| `drills/_common.py` | Inventory loader (reads the two configs), exit codes, weight-extension guard |
| `drills/drill_01_model_info_card.py` | model_info + card YAML + license |
| `drills/drill_02_pin_revision.py` | refs → pin SHA → config.json at revision → 6 verifications |
| `drills/drill_03_gated_probe.py` | accessible / needs-token / needs-accept / missing classifier |
| `drills/drill_04_snapshot_patterns.py` | snapshot_download(allow_patterns) + cache layout |
| `drills/drill_05_inventory_audit.py` | every inventory id: exists / gated / license / latest sha → JSON |
| `drills/run_all.sh` | runs all 5 anonymously with an isolated HF_HOME, writes logs |
| `evidence/drill_0N_*.log` | full stdout/stderr of each run, ending with `exit_code=N` |
| `evidence/run_summary.tsv` | drill, exit code, local start time |
| `evidence/drill_05_inventory_audit.json` | per-id audit evidence (schema `dreamco.hf_hub_inventory_audit.v1`) |

## Status (run 2026-09-28 ~17:33 CDT, huggingface_hub 2.0.0, venv `/workspace/hf-venv`, HF_TOKEN unset)

| Drill | Ran | Exit | Status | Evidence |
| --- | --- | --- | --- | --- |
| 01 model_info + card | yes | 0 | PASS | `BAAI/bge-small-en-v1.5` license `mit`, sha `5c38ec7c…` |
| 02 pin revision | yes | 0 | PASS | `openai/whisper-tiny` pinned `169d4a43…`, 6/6 checks ok |
| 03 gated probe | yes | 0 | PASS | 1 accessible, 3 needs-token (401), 1 missing. `needs-accept` path not exercisable without a token |
| 04 snapshot allow_patterns | yes | 0 | PASS | 9 files, 716,270 B, 0 weight files |
| 05 inventory audit | yes | 1 | CHECK_FAIL (finding) | models 23 = 16 ok + 5 gated + 2 missing. datasets 8 = 7 ok + 1 gated |

Missing ids: `mistralai/Mistral-Large-Instruct`, `openai-community/gpt-oss-study-only-if-license-allows`.
Gated models: `meta-llama/Llama-3.1-70B-Instruct`, `meta-llama/Llama-3.1-8B-Instruct`, `meta-llama/Llama-Guard-3-1B`,
`google/gemma-2-27b-it`, `google/gemma-2-9b-it`. Gated dataset: `bigcode/the-stack-smol`.
Duplicate: `gsm8k` resolves to `openai/gsm8k`.

## Not done / limits

- No config files under `config/` or `study_packs/<pack>/sources.json` were changed. Pins and license fixes are listed in `DAY1_DRILL_NOTES.md` as follow-ups.
- `latest_sha` values are main-branch heads at audit time. They are not reviewed pins.
- Nothing committed or pushed.
