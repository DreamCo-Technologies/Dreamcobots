# Repository benchmark artifact discovery

Run:

```bash
python -m pytest -q tests/test_repository_benchmark_artifact_scanner.py
python tools/scan_repository_benchmark_artifacts.py --output benchmark-artifact-inventory.json
```

The scanner inventories repository paths containing the word `benchmark`, classifies likely workflows, tests, documentation, configuration, suites, builders, and runtime artifacts, and creates an individual guide/test/evidence work queue.

## Discovery boundary

This first pass is path-name based. It does not parse every source file for textual references, discover benchmark names hidden in unrelated files, or prove that an artifact is an active benchmark. The output is a candidate inventory requiring content review and reconciliation with canonical benchmark IDs.

Every item remains unmeasured. The scanner does not execute tests, benchmarks, models, or workflows and does not claim scores, certification, or mastery.
