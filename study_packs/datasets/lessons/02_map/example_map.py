#!/usr/bin/env python3
"""Lesson 02: map / filter — batched, num_proc, remove_columns, fingerprint caching, formats.

Fully offline (Dataset.from_dict + a local csv in a temp dir). No Hub access.
Final stdout line is a JSON summary with "ok": true on success.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
from pathlib import Path

# This lesson never needs the network; lock it off before importing datasets.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import datasets  # noqa: E402
import numpy as np  # noqa: E402
from datasets import Dataset, load_dataset  # noqa: E402

datasets.disable_progress_bars()

N = 64
ROWS = {
    "id": list(range(N)),
    "text": [("word " * (1 + i % 7)).strip() for i in range(N)],
    "label": [i % 3 for i in range(N)],
}


# Module-level functions: picklable for num_proc and hashable for stable fingerprints.
def add_length_single(example: dict) -> dict:
    return {"n_words": len(example["text"].split())}


def add_length_batched(batch: dict) -> dict:
    # batch["text"] is a list; return lists of the same length (or a new length).
    return {"n_words": [len(t.split()) for t in batch["text"]]}


def tokenize_batched(batch: dict) -> dict:
    # Toy "tokenizer": fixed-length int ids, padded with 0.
    ids = [[len(w) for w in t.split()][:8] for t in batch["text"]]
    return {"input_ids": [row + [0] * (8 - len(row)) for row in ids]}


def explode_batched(batch: dict) -> dict:
    # Batched map may change the row count: one output row per word.
    out = {"id": [], "word": []}
    for i, t in zip(batch["id"], batch["text"]):
        for w in t.split():
            out["id"].append(i)
            out["word"].append(w)
    return out


def keep_long(example: dict) -> bool:
    return example["n_words"] >= 4


def keep_label_batched(batch: dict) -> list[bool]:
    return [lbl != 0 for lbl in batch["label"]]


def main() -> int:
    summary: dict = {"lesson": "map", "datasets_version": datasets.__version__}
    ds = Dataset.from_dict(ROWS)

    # 1. Row-wise vs batched map give the same result; batched is the fast path.
    single = ds.map(add_length_single)
    batched = ds.map(add_length_batched, batched=True, batch_size=16)
    assert single["n_words"] == batched["n_words"]
    summary["n_words_sum"] = int(sum(batched["n_words"]))

    # 2. num_proc shards the work across processes; output order is preserved.
    parallel = ds.map(add_length_batched, batched=True, num_proc=2)
    assert parallel["n_words"] == batched["n_words"]
    assert parallel["id"] == ROWS["id"]
    summary["num_proc_rows"] = parallel.num_rows

    # 3. remove_columns drops inputs you no longer need (e.g. raw text after tokenizing).
    tok = ds.map(tokenize_batched, batched=True, remove_columns=["text"])
    assert tok.column_names == ["id", "label", "input_ids"], tok.column_names
    summary["tokenized_columns"] = tok.column_names

    # 4. Batched map can change row count if you remove the old columns.
    exploded = ds.map(explode_batched, batched=True, remove_columns=ds.column_names)
    assert exploded.num_rows == summary["n_words_sum"]
    summary["exploded_rows"] = exploded.num_rows

    # 5. filter: row-wise and batched predicates.
    long_rows = batched.filter(keep_long)
    no_zero = ds.filter(keep_label_batched, batched=True)
    assert all(n >= 4 for n in long_rows["n_words"])
    assert 0 not in no_zero["label"]
    summary["filter_rows"] = {"n_words>=4": long_rows.num_rows, "label!=0": no_zero.num_rows}

    # 6. Fingerprint caching: file-backed datasets write map results to cache files and a
    #    second identical map (same fn + args) reuses them instead of recomputing.
    with tempfile.TemporaryDirectory(prefix="hf_pack_map_") as tmp:
        work = Path(tmp)
        csv_path = work / "rows.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "text", "label"])
            for row in zip(ROWS["id"], ROWS["text"], ROWS["label"]):
                writer.writerow(row)
        disk = load_dataset("csv", data_files=str(csv_path), split="train", cache_dir=str(work / "cache"))
        first = disk.map(add_length_batched, batched=True)
        second = disk.map(add_length_batched, batched=True)
        assert first._fingerprint == second._fingerprint
        assert first.cache_files == second.cache_files and first.cache_files
        forced = disk.map(add_length_batched, batched=True, load_from_cache_file=False)
        assert forced["n_words"] == first["n_words"]
        # Different function / args -> different fingerprint.
        other = disk.map(add_length_batched, batched=True, batch_size=8)
        assert other._fingerprint != first._fingerprint
        summary["fingerprint_reused"] = True
        summary["cache_file_count"] = len(first.cache_files)

    # 7. Formats: with_format returns a new view; set_format mutates in place.
    np_view = tok.with_format("numpy", columns=["input_ids", "label"])
    batch = np_view[:4]
    assert isinstance(batch["input_ids"], np.ndarray) and batch["input_ids"].shape == (4, 8)
    assert tok.format["type"] is None  # original untouched
    tok.set_format("numpy", columns=["input_ids"])
    assert isinstance(tok[0]["input_ids"], np.ndarray)
    tok.reset_format()
    assert isinstance(tok[0]["input_ids"], list)
    summary["numpy_shape"] = list(batch["input_ids"].shape)

    try:
        import torch  # noqa: F401
    except ImportError:
        summary["torch_format"] = "skipped (torch not installed)"
    else:
        tview = tok.with_format("torch", columns=["input_ids", "label"])
        t = tview[:4]["input_ids"]
        assert isinstance(t, torch.Tensor) and tuple(t.shape) == (4, 8)
        summary["torch_format"] = list(t.shape)

    summary["ok"] = True
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
