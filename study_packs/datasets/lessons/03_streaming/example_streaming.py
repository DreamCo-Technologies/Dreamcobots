#!/usr/bin/env python3
"""Lesson 03: streaming — IterableDataset, take/skip, shuffle(buffer_size), interleave, conversion.

Runs fully offline by default (local jsonl/parquet files streamed from a temp dir).
Set HF_PACK_ALLOW_NETWORK=1 to also stream a few rows from the pinned Hub dataset.
Final stdout line is a JSON summary with "ok": true on success.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ALLOW_NETWORK = os.environ.get("HF_PACK_ALLOW_NETWORK") == "1"
if not ALLOW_NETWORK:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"

import datasets  # noqa: E402
from datasets import Dataset, IterableDataset, interleave_datasets, load_dataset  # noqa: E402

datasets.disable_progress_bars()

# Pinned Hub source; must match study_packs/datasets/sources.json.
HUB_REPO_ID = "openai/gsm8k"
HUB_CONFIG = "main"
HUB_REVISION = "740312add88f781978c0658806c59bc2815b9866"

N = 100


def write_shards(root: Path, n_shards: int = 4) -> list[str]:
    """Write N rows across several jsonl shards (streaming reads shard by shard)."""
    paths = []
    per = N // n_shards
    for s in range(n_shards):
        p = root / f"shard-{s:02d}.jsonl"
        with p.open("w", encoding="utf-8") as fh:
            for i in range(s * per, (s + 1) * per):
                fh.write(json.dumps({"id": i, "text": f"row {i}", "source": "local"}) + "\n")
        paths.append(str(p))
    return paths


def add_upper(example: dict) -> dict:
    return {"upper": example["text"].upper()}


def main() -> int:
    summary: dict = {"lesson": "streaming", "datasets_version": datasets.__version__}
    with tempfile.TemporaryDirectory(prefix="hf_pack_stream_") as tmp:
        work = Path(tmp)
        shards = write_shards(work)

        # 1. streaming=True returns an IterableDataset: lazy, no Arrow cache written.
        stream = load_dataset("json", data_files=shards, split="train", streaming=True)
        assert isinstance(stream, IterableDataset)
        assert stream.num_shards == len(shards)
        first = next(iter(stream))
        assert first["id"] == 0
        summary["num_shards"] = stream.num_shards

        # 2. take / skip slice the stream without materializing it.
        head = [r["id"] for r in stream.take(5)]
        tail = [r["id"] for r in stream.skip(95)]
        window = [r["id"] for r in stream.skip(10).take(3)]
        assert head == [0, 1, 2, 3, 4]
        assert tail == [95, 96, 97, 98, 99]
        assert window == [10, 11, 12]
        summary["take_skip"] = {"head": head, "window": window}

        # 3. shuffle(buffer_size) is approximate: a buffer plus shard-order shuffling.
        #    Same seed -> same order; set_epoch(n) reshuffles deterministically per epoch.
        shuf_a = [r["id"] for r in stream.shuffle(seed=42, buffer_size=16)]
        shuf_b = [r["id"] for r in stream.shuffle(seed=42, buffer_size=16)]
        assert shuf_a == shuf_b
        assert sorted(shuf_a) == list(range(N)) and shuf_a != list(range(N))
        epoch_ds = stream.shuffle(seed=42, buffer_size=16)
        epoch_ds.set_epoch(1)
        assert [r["id"] for r in epoch_ds] != shuf_a
        summary["shuffle_first5"] = shuf_a[:5]

        # 4. Lazy map/filter on streams run while iterating.
        mapped = stream.map(add_upper).filter(lambda r: r["id"] % 10 == 0)
        got = list(mapped)
        assert [r["id"] for r in got] == list(range(0, N, 10))
        assert got[0]["upper"] == "ROW 0"
        summary["lazy_map_filter_rows"] = len(got)

        # 5. interleave_datasets mixes sources by probability (seeded) or round-robin.
        other = Dataset.from_dict(
            {"id": list(range(1000, 1020)), "text": [f"extra {i}" for i in range(20)], "source": ["extra"] * 20}
        ).to_iterable_dataset()
        robin = list(interleave_datasets([stream, other]).take(6))
        assert [r["source"] for r in robin] == ["local", "extra"] * 3
        mixed = list(
            interleave_datasets([stream, other], probabilities=[0.8, 0.2], seed=0, stopping_strategy="first_exhausted")
        )
        sources = {r["source"] for r in mixed}
        assert sources == {"local", "extra"}
        summary["interleave"] = {
            "round_robin": [r["source"] for r in robin],
            "prob_rows": len(mixed),
            "prob_extra_rows": sum(r["source"] == "extra" for r in mixed),
        }

        # 6. Dataset.to_iterable_dataset(num_shards=...) turns an in-memory/Arrow dataset
        #    into a stream (useful for DataLoader workers); streams can be collected back.
        mem = Dataset.from_dict({"id": list(range(12)), "text": [f"m{i}" for i in range(12)]})
        it = mem.to_iterable_dataset(num_shards=3)
        assert isinstance(it, IterableDataset) and it.num_shards == 3
        back = Dataset.from_list(list(it))
        assert back["id"] == mem["id"]
        summary["to_iterable_shards"] = it.num_shards

        # 7. Streaming parquet works the same way.
        pq = work / "rows.parquet"
        mem.to_parquet(str(pq))
        pq_stream = load_dataset("parquet", data_files=str(pq), split="train", streaming=True)
        assert [r["id"] for r in pq_stream.take(3)] == [0, 1, 2]

        # No Arrow cache files were produced by streaming.
        assert not list(work.rglob("*.arrow"))
        summary["arrow_cache_files"] = 0

    if ALLOW_NETWORK:
        hub = load_dataset(HUB_REPO_ID, HUB_CONFIG, split="test", streaming=True, revision=HUB_REVISION)
        rows = list(hub.take(3))
        assert len(rows) == 3 and "question" in rows[0]
        summary["hub"] = {"repo_id": HUB_REPO_ID, "revision": HUB_REVISION, "rows": len(rows)}
    else:
        summary["hub"] = "skipped (set HF_PACK_ALLOW_NETWORK=1 to run)"

    summary["ok"] = True
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
