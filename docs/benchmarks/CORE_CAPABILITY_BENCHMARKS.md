# Core capability benchmark definitions

This registry defines one benchmark specification for every capability currently listed in `config/buddy-benchmark-task-registry.json`: reasoning, coding, SQL, Python, spreadsheets, tool use, retrieval, long context, agentic completion, factuality, and safety.

Each definition includes an objective, dimensions, task difficulty, independent holdout policy, weighted scoring rubric, pass threshold, and critical safety/quality gates.

## Validation

```bash
python -m pytest -q tests/test_core_capability_benchmarks.py
python tools/validate_core_capability_benchmarks.py
```

## Implementation status

These are benchmark definitions, not completed execution adapters. Each record is marked `definition_ready_adapter_pending` until a deterministic task generator, evaluator, fixture set, and regression test are implemented and run. Scores remain unknown without evidence. Holdout data must remain separate from training data, and failed attempts must be preserved.

This registry is a core foundation; it does not claim to cover every benchmark mentioned elsewhere in DreamCo or the broader industry. The wider benchmark inventory still needs discovery, mapping, and per-benchmark implementation.
