# Benchmark runner truth boundary

The lightweight benchmark runner is a deterministic execution/reporting scaffold. Its configured baseline score and optional `--score` override are not outputs from a model, task evaluator, independent reviewer, or held-out test.

The runner therefore labels results as simulated threshold outcomes and always records:
- `simulation_only: true`;
- `mastery_awarded: false`;
- `mastery_eligible: false`;
- `mastery_state: discovered`; and
- a result type distinguishing a configured placeholder from an explicit score override.

The numeric `passed` field and aggregate `pass_rate` remain for compatibility, but the report states that they are simulated threshold rates, not measured model pass rates. Real benchmark adapters must supply reproducible task inputs, evaluator versions, execution traces, result artifacts, independent holdout evidence, and regression results before a mastery workflow can promote a capability.
