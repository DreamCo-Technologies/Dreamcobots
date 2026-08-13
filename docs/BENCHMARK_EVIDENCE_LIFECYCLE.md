# Buddy Benchmark Evidence Lifecycle

Every registered benchmark is evaluated as a measurable capability, not a checklist item.

## Lifecycle

1. Register the target and acceptance criteria.
2. Establish a reproducible baseline.
3. Run Buddy and record quality, performance, efficiency, reliability, safety and independence evidence applicable to the task.
4. Compare with the documented baseline and, where appropriate, a comparable approved reference.
5. Diagnose the root cause of any gap.
6. Design the smallest safe shared repair.
7. Define rollback and fallback behavior.
8. Apply only within review/sandbox scope.
9. Run targeted verification.
10. Rerun the benchmark.
11. Retest dependent suites whenever shared behavior changed.
12. Compare before/after evidence.
13. Iterate while measurable improvement remains and safety/regression gates remain satisfied.
14. Mark mastered only when the benchmark's repeated acceptance criteria are actually met.

## Four-dimensional interpretation

A benchmark should answer at least:

- **Can Buddy do it?** — capability/correctness.
- **How good is the result?** — quality.
- **How fast is it?** — latency/throughput.
- **How efficiently does it do it?** — resource, tool, model and cost efficiency where measurable.

Reliability, safety, recovery, regression resilience and independence are additional gates where applicable.

## No false mastery

The following do not constitute mastery by themselves:

- registration of a benchmark;
- a model-routing path existing;
- a frontier model completing the task for Buddy;
- a single lucky pass;
- an evaluator saying an answer looks good without required evidence;
- a faster result that is less correct;
- a cheaper result that is unsafe;
- a passing test obtained by weakening the test.

## Evidence states

`unknown → registered → baselined → testing → passed/failed/blocked → repair → retest → mastered_candidate → mastered`

A regression moves a previously accepted capability back into investigation.

## Dashboard contract

GitHub Pages may show safe aggregate benchmark status, quality, performance, efficiency, reliability, independence, trends and evidence references. Secrets, credentials, private user data and sensitive raw logs must remain excluded.
