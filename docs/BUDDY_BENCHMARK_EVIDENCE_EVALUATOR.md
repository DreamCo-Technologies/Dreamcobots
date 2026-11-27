# Buddy benchmark evidence packet evaluator

This deterministic evaluator scores submitted evidence packets against the 11 core capability benchmark definitions. It checks exact rubric dimensions, 0–4 dimension scores, critical gates, evidence hashes, ISO-8601 timestamps, and distinct training/holdout fixture hashes.

Run `python -m pytest -q tests/test_buddy_benchmark_evidence_evaluator.py` and `python tools/evaluate_buddy_benchmark_packet.py --input packet.json --output result.json`.

A candidate pass is not an independently verified benchmark run. The evaluator does not execute model code, inspect fixture contents, validate provider logs, or certify mastery. Results remain `independent_verification: pending` and `benchmark_execution_verified: false` until a separately governed execution adapter and independent verification path are implemented. Critical-gate failure blocks a pass regardless of numeric score. Preserve failed runs and regressions.
