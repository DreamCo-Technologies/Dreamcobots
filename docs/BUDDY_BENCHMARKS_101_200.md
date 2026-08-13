# Buddy Benchmark Expansion 101–200

This catalog extends the benchmark program into reliability, autonomy, knowledge, software engineering, security, and business capability.

## Evidence rule

A registered benchmark is a target, not a result. A capability may only become **mastered** after measured evidence satisfies its acceptance criteria and relevant dependent suites pass. Assisted completion by another model is recorded as assisted capability and does not by itself prove Buddy-native mastery.

## Required lifecycle

1. Register the capability.
2. Capture a reproducible baseline.
3. Run Buddy under documented conditions.
4. Compare against an appropriate reference where permitted.
5. Diagnose the root cause of failures.
6. Propose the smallest shared safe repair.
7. Define rollback/fallback.
8. Apply only in sandbox/review scope.
9. Run targeted tests.
10. Rerun the benchmark.
11. Retest dependent suites for shared changes.
12. Record before/after evidence.
13. Promote only if acceptance criteria pass.
14. Retain regression coverage.

## Independence metrics

The benchmark dashboard should track capability independence ratio, teacher dependency rate, capability gap, gap-closure rate, time-to-first-pass, time-to-mastery, regression rate, fallback rate, cost per successful task, and latency to useful result.

## Public transparency

GitHub Pages may expose safe benchmark metadata, scores, trends, statuses and evidence references. It must never expose secrets, credentials, private user data or sensitive raw logs.
