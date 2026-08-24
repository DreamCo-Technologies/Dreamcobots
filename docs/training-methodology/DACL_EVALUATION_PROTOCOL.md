# DACL Evaluation Protocol

## Customer evaluation sequence

### Phase 1 — Baseline
Run a fixed evaluation set and record capability-level scores, latency, cost, and failure categories.

### Phase 2 — Gap map
Rank gaps by severity, business value, transfer potential, and expected improvement per unit of training resource.

### Phase 3 — Intervention
Assign targeted curriculum, sandbox exercises, counterexamples, retrieval practice, and difficulty progression.

### Phase 4 — Verification
Repeat the baseline tasks, add held-out transfer tasks, and run regression checks.

### Phase 5 — Report
Report absolute score, score delta, confidence/variance where available, transfer performance, regressions, compute/time used, and unresolved gaps.

## Success criteria
A customer result is considered a verified improvement only when the post-training evaluation improves against the agreed baseline without unacceptable regression on protected capabilities.

## Recommended commercial report
- Executive capability scorecard
- Top 10 gaps before training
- Training interventions performed
- Benchmark score deltas
- Transfer-test results
- Regression results
- Runtime and cost efficiency
- Remaining gaps
- Recommended next training cycle

## Why this is defensible
The methodology separates **training**, **evaluation**, and **claims**. Customers can audit what changed and reproduce the evaluation rather than relying on a marketing claim that an agent simply became smarter.
