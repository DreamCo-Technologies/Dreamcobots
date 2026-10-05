# Lesson 03 — streaming and `IterableDataset`

Pack: `study_packs/datasets` · library: `datasets==5.0.1` · offline by default.

## Run

```bash
python3 study_packs/datasets/lessons/03_streaming/example_streaming.py          # offline
HF_PACK_ALLOW_NETWORK=1 python3 study_packs/datasets/lessons/03_streaming/example_streaming.py  # + pinned Hub stream
```

The last stdout line is a JSON summary with `"ok": true`.

## What it covers

| Topic | Call | Note |
| --- | --- | --- |
| Stream local files | `load_dataset("json", data_files=[...], split="train", streaming=True)` | returns `IterableDataset`, no Arrow cache |
| Shards | `stream.num_shards` | one per file; shard order is what gets shuffled |
| Slice | `stream.take(5)`, `stream.skip(95)`, `stream.skip(10).take(3)` | lazy |
| Approximate shuffle | `stream.shuffle(seed=42, buffer_size=16)` | buffer + shard shuffle; not a full permutation guarantee |
| Epochs | `ds.set_epoch(n)` | deterministic reshuffle per epoch |
| Lazy transforms | `stream.map(fn).filter(pred)` | run during iteration |
| Mix sources | `interleave_datasets([a, b])` | round-robin |
| | `interleave_datasets([a, b], probabilities=[0.8, 0.2], seed=0, stopping_strategy=...)` | `first_exhausted` / `all_exhausted` |
| Convert | `Dataset.to_iterable_dataset(num_shards=3)` | e.g. for `DataLoader(num_workers=3)` |
| Collect | `Dataset.from_list(list(stream))` | only for small streams |

## Hub streaming with a revision pin (network-gated)

```python
from datasets import load_dataset

stream = load_dataset(
    "openai/gsm8k", "main", split="test", streaming=True,
    revision="740312add88f781978c0658806c59bc2815b9866",
)
for row in stream.take(3):
    print(row["question"][:60])
```

Streaming avoids downloading whole datasets, which is the right default for exploring
large Hub datasets. It still makes network requests, so it is gated behind
`HF_PACK_ALLOW_NETWORK=1` here and never runs in CI.

## Exercises

1. Compare the first 10 ids for `buffer_size=1` vs `buffer_size=1000`. What does `buffer_size=1` still shuffle (hint: shard order)?
2. Interleave three streams with `stopping_strategy="all_exhausted"` and count rows per source.
3. Wrap `mem.to_iterable_dataset(num_shards=4)` in a `torch.utils.data.DataLoader(num_workers=2)`.
