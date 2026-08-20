# Buddy Benchmark + Pull Request Review Standard

## Design principle
If this were my own long-lived software project, I would optimize for **truth before confidence**. Buddy should earn trust by repeatedly finding real defects, avoiding false alarms, explaining evidence, surviving adversarial tests, and learning from what happens after merge.

## Benchmark lifecycle
1. Define the exact task and success contract.
2. Build a representative dataset, including normal, boundary, adversarial and regression cases.
3. Establish deterministic tests where possible.
4. Run multiple candidate models/agents.
5. Score correctness, quality, completeness, safety, speed, cost and reproducibility separately.
6. Compare against a baseline and the best verified candidate.
7. Inspect failures rather than hiding them in an aggregate score.
8. Generate targeted training/repair work.
9. Re-run the same benchmark plus a holdout set.
10. Promote only when the improvement is repeatable.
11. Keep the benchmark as a regression suite.

### Mastery is multidimensional
A benchmark is not "passed" merely because an answer looks good. A mastered capability needs task-specific thresholds for correctness, safety, quality, latency and reproducibility, plus enough repeated evidence to establish confidence. If a dimension is not measured, it is reported as unknown rather than silently treated as passing.

## PR review benchmark
Buddy PR review is evaluated on:
- true-positive defect precision
- true-negative precision
- defect recall
- false-positive rate
- false-negative rate
- severity calibration
- actionable-fix rate
- duplicate suppression
- requirements coverage
- security detection
- dependency/supply-chain detection
- performance-regression detection
- test-gap detection
- accessibility detection
- adversarial robustness
- reviewer agreement/disagreement quality
- review latency
- cost
- post-merge incident correlation
- developer acceptance

## Before / during / after review

### Before
Repository Explorer and Requirements Analyst build context. Architect maps affected contracts. Tester and Benchmark Evaluator identify the validation plan. Buddy flags missing requirements and likely regression surfaces before code is written.

### During
Buddy selects specialists per exact step. Deterministic checks run first. Semantic reviewers then analyze correctness and risks. Adversarial reviewers attempt to disprove important assumptions. Findings are deduplicated and tied to evidence.

### During revision
Each new commit invalidates only findings made obsolete by the change. Still-valid findings remain linked. Targeted tests and benchmarks rerun. Buddy produces a change-since-last-review summary.

### Before merge
Buddy produces a merge-readiness decision with explicit blockers, evidence, unresolved uncertainty, benchmark results and required human approvals.

### After merge
Buddy monitors regressions, incidents, reverts, flaky tests, security findings and performance changes. Review findings are scored against later reality so the reviewer itself can improve.

## Trust ladder
- **Observe:** read-only analysis.
- **Assist:** comments, tests and plans prepared for humans.
- **Collaborate:** patches/branches prepared for human review.
- **Guarded automation:** explicitly authorized low-risk actions.
- **Trusted automation:** only after repository-specific evidence, policy approval, rollback and monitoring requirements are satisfied.

No level bypasses GitHub permissions, branch protection, secrets controls, security policy or user authorization.

## Money-opportunity benchmark
Money ideas must also be evidence-driven. Buddy should distinguish:
- opportunity discovered
- opportunity researched
- economics estimated
- legality/policy checked
- customer demand validated
- supplier/platform constraints checked
- pilot launched
- revenue observed
- profit observed
- repeatability demonstrated

Never label an opportunity "profitable" solely because a model predicts it will be profitable.
