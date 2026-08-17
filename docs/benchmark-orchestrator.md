# Buddy Benchmark Orchestrator

The benchmark system is a continuous workload manager, not a single test runner.

## Parallel queues

- **Benchmark:** execute capability tests.
- **Gap closure:** research, build, and test weak capabilities.
- **Regression:** protect capabilities that already work.
- **Discovery:** find better benchmarks and reference implementations.
- **Evidence:** validate sources and benchmark claims.

## Failure behavior

A failed benchmark is classified, its artifacts are captured, a gap record is created, an alternate path may be tried, and the task can be deferred while unrelated queues continue.

The orchestrator resumes from checkpoints and uses bounded retries. This prevents one broken benchmark, unavailable dependency, flaky test, or resource limit from freezing Buddy's entire learning program.

## Actions command center

The dashboard should expose queue state, capability score, confidence, gap, active worker, sandbox state, latest run, failure classification, recovery path, regression state, and promotion state.

All results remain evidence-backed and reproducible where possible. Offline operation is supported.
