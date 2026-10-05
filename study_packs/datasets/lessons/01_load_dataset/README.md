# Lesson 01 — `load_dataset`

Pack: `study_packs/datasets` · library: `datasets==5.0.1` · offline by default.

## Run

```bash
python3 study_packs/datasets/lessons/01_load_dataset/example_load_dataset.py          # offline
HF_PACK_ALLOW_NETWORK=1 python3 study_packs/datasets/lessons/01_load_dataset/example_load_dataset.py  # + pinned Hub load
```

The last stdout line is a JSON summary with `"ok": true`.

## What it covers

| Topic | Call |
| --- | --- |
| In-memory data | `Dataset.from_dict({...})` |
| Local files | `load_dataset("csv" \| "json" \| "parquet", data_files=path, split="train")` |
| Named splits from files | `load_dataset("csv", data_files={"train": ..., "test": ...})` → `DatasetDict` |
| Globs | `data_files="dir/*.csv"` |
| Split slicing | `split="train[:3]"`, `split="train[50%:]"` |
| Derived splits | `ds.train_test_split(test_size=0.2, seed=0)` |
| Cache location | `cache_dir=...` (Arrow files land there, not `~/.cache/huggingface`) |
| Hub + pin | `load_dataset("openai/gsm8k", "main", split="test[:8]", revision="<sha>")` |

## Hub loading with a revision pin (network-gated)

```python
from datasets import load_dataset

ds = load_dataset(
    "openai/gsm8k",
    "main",                                   # config name
    split="test[:8]",
    revision="740312add88f781978c0658806c59bc2815b9866",  # full commit sha
    cache_dir="/tmp/hub_cache",
)
```

Rules (see `CARD.md` → revision-pin policy):

- Always pass `revision=` with a **full commit sha**. `main` moves; a sha does not.
- Record `repo_id`, `config`, `revision`, `license`, `split` in `sources.json`.
- Read the dataset card license at that sha before use. `license:unknown` / `other` means
  study-only until reviewed.
- Datasets 3.x+ no longer run Hub loading scripts; prefer repos that ship parquet/json files.

## Offline guard

Without `HF_PACK_ALLOW_NETWORK=1` the example sets `HF_HUB_OFFLINE=1` and
`HF_DATASETS_OFFLINE=1` **before** importing `datasets`, so any accidental Hub call fails
fast instead of downloading. CI never sets the flag.

## Exercises

1. Load `train.jsonl` with `features=` to force `label` to `ClassLabel(names=["neg","pos"])`.
2. Load a folder of parquet shards with `data_dir=` instead of `data_files=`.
3. Find the current sha of a Hub dataset with `huggingface_hub.HfApi().dataset_info(repo_id).sha`
   (network) and explain why you would still keep the old pin until the card is re-reviewed.
