# HF Hub Day-1 Drills

Five runnable drills. Each one works **without a token** and downloads **only cards, configs, or tokenizers, never weights**.
Inventory ids are read live from `config/huggingface-two-week-study.json` and `config/hf-capability-download-map.json`
(see `_common.py:inventory()`).

## Setup and run

```bash
python3 -m venv /workspace/hf-venv && /workspace/hf-venv/bin/pip install -U huggingface_hub
cd study_packs/hub/drills
bash run_all.sh /workspace/hf-venv/bin/python    # isolated HF_HOME, unsets HF_TOKEN, logs to ../evidence/
# or run one drill:  /workspace/hf-venv/bin/python drill_02_pin_revision.py openai/whisper-small
```

## Exit codes (shared, `_common.py`)

| code | meaning |
| --- | --- |
| 0 | PASS: every check held |
| 1 | CHECK_FAIL: drill ran, but a verification or finding failed (details in log) |
| 2 | HUB_ERROR: network, Hub unreachable, or unexpected HTTP error |
| 3 | USAGE: bad args, or repo not in the Dreamcobots inventory |

## Drills

| # | File | Default target (inventory source) | What it proves | Downloads |
| --- | --- | --- | --- | --- |
| 1 | `drill_01_model_info_card.py` | `BAAI/bge-small-en-v1.5` (`seed_models.pack.embed`) | `model_info` + card YAML: license, pipeline_tag, base_model, sha. Fails if license or sha is missing | README.md only |
| 2 | `drill_02_pin_revision.py` | `openai/whisper-tiny` (`seed_models.pack.speech`) | `list_repo_refs`, `list_repo_commits`, pin main-head SHA, `hf_hub_download(config.json, revision=sha)`. 6 checks: snapshot dir == sha, `model_info(revision)` sha, JSON parses, blob name == git SHA-1, `refs/main` == sha, main and pin share a blob | config.json → temp cache |
| 3 | `drill_03_gated_probe.py` | MiniLM (open), Llama-Guard-3-1B, Llama-3.1-8B-Instruct, gemma-2-9b-it (gated), Mistral-Large-Instruct (missing) | classifies each repo as `accessible` / `needs-token` (401) / `needs-accept` (403 with token) / `missing`, plus `whoami`. Never crashes | HEAD metadata only |
| 4 | `drill_04_snapshot_patterns.py` | `sentence-transformers/all-MiniLM-L6-v2` (`seed_models.pack.embed`) | `snapshot_download(allow_patterns=[configs, tokenizer, vocab, README])` into a temp cache. Prints blobs/refs/snapshots layout and `scan_cache_dir`. Fails if any weight file lands or size > 10 MB | ~0.7 MB → temp cache (deleted) |
| 5 | `drill_05_inventory_audit.py` | all 23 model ids + 8 dataset ids | exists, gated, license, latest sha, last_modified, pipeline_tag, base_model, rename detection. Writes `../evidence/drill_05_inventory_audit.json`. Exits 1 if any model id is missing | none (metadata API) |

## Last run (2026-09-28 ~17:33 CDT, anonymous, huggingface_hub 2.0.0)

| Drill | Exit | Result | Evidence line |
| --- | --- | --- | --- |
| 1 | 0 | PASS | `card.license  : mit` / `sha (main)    : 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` |
| 2 | 0 | PASS | `PINNED revision = 169d4a4341b33bc18d8881c4b69c2e104e1cc0af`, 6/6 checks `[ok]` |
| 3 | 0 | PASS | 1 accessible, 3 `needs-token http=401 gated=manual`, 1 missing |
| 4 | 0 | PASS | `total blob bytes: 716270 (0.72 MB); weight files: []` |
| 5 | 1 | CHECK_FAIL (expected finding) | `model_summary: {'total': 23, 'ok': 16, 'gated': 5, 'missing': 2, 'error': 0}` |

Drill 5's exit 1 is a real inventory finding: two `student_shortlist` ids do not exist on the Hub. The drill itself completed and wrote its evidence.
