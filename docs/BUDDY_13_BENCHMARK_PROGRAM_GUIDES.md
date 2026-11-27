# 13 canonical benchmark program guides

This pack adds one original guide for each program in `config/buddy-benchmark-index.json`. Each guide carries forward its canonical ID, scope, generator, check command, cadence, and current status, then defines a reproducible methodology, evaluation dimensions, baseline, environment, holdout policy, safety gates, evidence artifacts, and remediation loop.

## No invented results

All guides remain drafts. Numerical thresholds are left pending unless they already exist in a canonical benchmark contract. The generator does not run the benchmark and does not assign scores.

## Scope limitation

The repository contains additional benchmark suites, configs, workflows, and scripts outside the 13 programs in the canonical index. This pack does not claim that every repository benchmark reference has been exhaustively catalogued or individually documented. Further discovery and reconciliation remain required.

## Validate

```bash
python -m pytest -q tests/test_buddy_benchmark_program_guides.py
python tools/validate_buddy_benchmark_program_guides.py
```
