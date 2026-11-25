# Benchmark guide and evidence backlog

Run:

```bash
python tools/build_buddy_benchmark_guide_queue.py
pytest -q tests/test_buddy_benchmark_guide_queue.py
```

The builder creates one work item for each canonical benchmark program and each task in the benchmark task registry. It carries forward the existing program IDs, scopes, generators and check commands, and defines a consistent guide contract covering workload, data provenance, environment, baselines, metrics, thresholds, reproducibility, holdouts, safety, evidence, and failure analysis.

All items remain `not_authored_or_not_linked`; all test statuses require execution evidence; measured count remains zero. The queue does not invent benchmark scores, certification, model rankings, or mastery.
