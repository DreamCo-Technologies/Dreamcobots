#!/usr/bin/env python3
"""Lesson 01: load_dataset — local files, data_files, splits, cache_dir, Hub revision pins.

Runs fully offline by default. Set HF_PACK_ALLOW_NETWORK=1 to also run the pinned Hub example.
Final stdout line is a JSON summary with "ok": true on success.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
from pathlib import Path

ALLOW_NETWORK = os.environ.get("HF_PACK_ALLOW_NETWORK") == "1"
if not ALLOW_NETWORK:
    # Must be set before `import datasets` so nothing can reach the Hub.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"

import datasets  # noqa: E402
from datasets import Dataset, DatasetDict, load_dataset  # noqa: E402

datasets.disable_progress_bars()

# Pinned Hub source; must match study_packs/datasets/sources.json.
HUB_REPO_ID = "openai/gsm8k"
HUB_CONFIG = "main"
HUB_REVISION = "740312add88f781978c0658806c59bc2815b9866"  # full commit sha, never "main"
HUB_SPLIT = "test[:8]"

ROWS = {
    "id": list(range(10)),
    "text": [f"example sentence number {i}" for i in range(10)],
    "label": [i % 2 for i in range(10)],
}


def write_local_files(root: Path) -> dict[str, Path]:
    """Write the same rows as csv, jsonl and parquet (train) plus a small test csv."""
    paths = {}
    csv_path = root / "train.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "text", "label"])
        for i, t, l in zip(ROWS["id"], ROWS["text"], ROWS["label"]):
            writer.writerow([i, t, l])
    paths["csv"] = csv_path

    jsonl_path = root / "train.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as fh:
        for i, t, l in zip(ROWS["id"], ROWS["text"], ROWS["label"]):
            fh.write(json.dumps({"id": i, "text": t, "label": l}) + "\n")
    paths["json"] = jsonl_path

    parquet_path = root / "train.parquet"
    Dataset.from_dict(ROWS).to_parquet(str(parquet_path))
    paths["parquet"] = parquet_path

    test_path = root / "test.csv"
    with test_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "text", "label"])
        writer.writerow([100, "held out one", 1])
        writer.writerow([101, "held out two", 0])
    paths["test_csv"] = test_path
    return paths


def offline_examples(work: Path) -> dict:
    cache_dir = work / "hf_cache"  # explicit cache_dir keeps Arrow files out of ~/.cache
    paths = write_local_files(work)
    summary: dict = {}

    # 1. In-memory dataset: no files, no cache, no network.
    mem = Dataset.from_dict(ROWS)
    assert mem.num_rows == 10 and mem.column_names == ["id", "text", "label"]
    summary["from_dict_rows"] = mem.num_rows

    # 2. Local files via the packaged builders: "csv", "json", "parquet".
    for builder in ("csv", "json", "parquet"):
        ds = load_dataset(builder, data_files=str(paths[builder]), split="train", cache_dir=str(cache_dir))
        assert ds.num_rows == 10, (builder, ds.num_rows)
        assert sorted(ds["id"]) == ROWS["id"], builder
        summary[f"{builder}_rows"] = ds.num_rows

    # 3. data_files as a mapping -> named splits in a DatasetDict.
    dd = load_dataset(
        "csv",
        data_files={"train": str(paths["csv"]), "test": str(paths["test_csv"])},
        cache_dir=str(cache_dir),
    )
    assert isinstance(dd, DatasetDict)
    assert set(dd.keys()) == {"train", "test"}
    assert dd["test"].num_rows == 2
    summary["splits"] = sorted(dd.keys())

    # 4. Split slicing syntax works on local files too.
    head = load_dataset("csv", data_files=str(paths["csv"]), split="train[:3]", cache_dir=str(cache_dir))
    pct = load_dataset("csv", data_files=str(paths["csv"]), split="train[50%:]", cache_dir=str(cache_dir))
    assert head.num_rows == 3 and pct.num_rows == 5
    summary["slice_rows"] = {"train[:3]": head.num_rows, "train[50%:]": pct.num_rows}

    # 5. Glob data_files + train_test_split for a derived split.
    globbed = load_dataset("csv", data_files=str(work / "*.csv"), split="train", cache_dir=str(cache_dir))
    assert globbed.num_rows == 12  # train.csv (10) + test.csv (2)
    split = mem.train_test_split(test_size=0.2, seed=0)
    assert split["train"].num_rows == 8 and split["test"].num_rows == 2
    summary["glob_rows"] = globbed.num_rows

    # 6. cache_dir really holds the Arrow cache.
    arrow_files = list(cache_dir.rglob("*.arrow"))
    assert arrow_files, "expected Arrow cache files under cache_dir"
    assert all(str(cache_dir) in f["filename"] for f in dd["train"].cache_files)
    summary["cache_arrow_files"] = len(arrow_files)
    return summary


def hub_example(work: Path) -> dict:
    """Pinned Hub load. Only runs with HF_PACK_ALLOW_NETWORK=1."""
    ds = load_dataset(
        HUB_REPO_ID,
        HUB_CONFIG,
        split=HUB_SPLIT,
        revision=HUB_REVISION,
        cache_dir=str(work / "hub_cache"),
    )
    assert ds.num_rows == 8
    assert {"question", "answer"} <= set(ds.column_names)
    return {"repo_id": HUB_REPO_ID, "revision": HUB_REVISION, "rows": ds.num_rows}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hf_pack_load_") as tmp:
        work = Path(tmp)
        result = {"lesson": "load_dataset", "datasets_version": datasets.__version__}
        result["offline"] = offline_examples(work)
        if ALLOW_NETWORK:
            result["hub"] = hub_example(work)
        else:
            result["hub"] = "skipped (set HF_PACK_ALLOW_NETWORK=1 to run)"
        result["ok"] = True
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
