# Lesson 02 — `map`, `filter`, formats

Pack: `study_packs/datasets` · library: `datasets==5.0.1` · fully offline (no Hub calls).

## Run

```bash
python3 study_packs/datasets/lessons/02_map/example_map.py
```

The last stdout line is a JSON summary with `"ok": true`. The torch step runs only if
`torch` is installed; otherwise it reports `skipped`.

## What it covers

| Topic | Call | Note |
| --- | --- | --- |
| Row-wise map | `ds.map(fn)` | `fn(example) -> dict` |
| Batched map | `ds.map(fn, batched=True, batch_size=16)` | `fn(batch_of_lists) -> dict of lists`; much faster |
| Parallel map | `ds.map(fn, batched=True, num_proc=2)` | fn must be picklable (module-level); order is preserved |
| Drop inputs | `remove_columns=["text"]` | e.g. after tokenizing |
| Change row count | batched fn + `remove_columns=ds.column_names` | one-to-many / many-to-one |
| Filter | `ds.filter(pred)` / `ds.filter(pred_batched, batched=True)` | batched pred returns `list[bool]` |
| Fingerprint cache | repeat the same `map` on a file-backed dataset | reuses `cache-*.arrow`; `load_from_cache_file=False` forces recompute |
| Formats | `with_format("numpy", columns=[...])` | returns a new view |
| | `set_format(...)` / `reset_format()` | mutates in place |
| | `with_format("torch")` | tensors for a `DataLoader` |

## Fingerprint caching, briefly

Every transform gets a fingerprint = hash(previous fingerprint, function, arguments).
For datasets backed by Arrow cache files (e.g. from `load_dataset`), `map` writes its
result to `cache-<fingerprint>.arrow` next to the source cache; the same transform again
is a cache hit. In-memory datasets (`Dataset.from_dict`) are not written to disk by default.

Gotchas:

- Lambdas/closures that capture changing state can hash differently each run → cache misses.
- Changing `batch_size`, `remove_columns`, or the function body changes the fingerprint.
- Use `datasets.disable_caching()` or `load_from_cache_file=False` when debugging.

## Exercises

1. Add `with_indices=True` to a map and store the index as a column.
2. Time `batched=False` vs `batched=True` on 100k rows.
3. Use `ds.cleanup_cache_files()` and confirm the next `map` recomputes.
