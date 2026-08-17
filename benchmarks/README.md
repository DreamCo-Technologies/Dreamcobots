# Buddy Benchmarks

This directory is the execution layer for DreamCo's universal benchmark program.

## Free-first rule
Local/open/free execution is the default. Paid models or paid services require explicit user authorization. Every result records the route and cost.

## Lifecycle
1. Discover a source or capability.
2. Ingest permitted material.
3. Normalize and preserve provenance.
4. Package the knowledge into machine-readable data.
5. Generate independent tasks.
6. Create an isolated sandbox.
7. Execute the task.
8. Validate against objective criteria.
9. Score quality, reliability, time, cost and human intervention.
10. Diagnose failures.
11. Run targeted remediation.
12. Retest and run regressions.
13. Promote only after the configured mastery threshold is repeatedly passed.

## Current executable smoke test

```bash
python3 benchmarks/buddy_benchmark_runner.py benchmarks/tasks/universal_1000_smoke.json
```

The runner uses only the Python standard library and does not require an external model or paid API. It provides the deterministic evaluation shell that model/tool adapters can plug into later.

## Important distinction
A source being listed or downloaded does not mean Buddy mastered it. Mastery requires benchmark evidence. Production-proven requires successful authorized use in a real workflow with measurable results.
