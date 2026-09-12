# Buddy Frontier Evidence Plan — September through December 2026

## Current factual status

Buddy has repository contracts, generated benchmark catalogs, and test coverage. It has **no claimable live frontier comparison**, **no measured model calls in the model lab**, and **no independent-learning promotion evidence** as of this plan's creation. Catalog size, provider references, and passing interface tests do not change that status.

## Proof standard

The executable validator `tools/verify_frontier_evidence.py` accepts a claim only when a pinned suite has three or more comparable repetitions for Buddy and at least one named frontier reference, with fixture hashes, exact subject versions, grader versions, timestamps, latency, cost, safety, regression, and assistance data. Simulated rows are rejected.

Independent learning additionally requires a measured Buddy baseline failure, a native (not teacher-completed) candidate that passes safety and regression, and a passing separate holdout. Owner review is required before release.

## Delivery sequence

### September 11–30: establish the measurement floor

1. Put the hidden task prompts and expected checks in a private evaluation store, separate from training/retrieval material.
2. Connect approved Buddy, OpenAI, Anthropic, Gemini, and local-model adapters through server-side credentials; pin exact model IDs and prices for every run.
3. Implement deterministic graders for the five Q4 lanes in `config/frontier-evidence-suite.json`.
4. Run three baseline repetitions for each subject/task and publish every pass, failure, timeout, cost, and latency result.

Exit evidence: signed result bundles are accepted by the validator; no model receives holdout answers in prompts, retrieval, or training data.

### October: targeted reliability and tool-use parity

1. Focus on property/resource routing, source-grounded research, permission correctness, and provider-timeout recovery.
2. Fix only measured gaps through routing, retrieval, tools, or code; do not tune to hidden holdouts.
3. Re-run baseline, candidate, regression, and holdout suites after each bounded change.

Exit evidence: Buddy reaches the suite threshold on at least two lanes with three repeat runs and no new critical safety regression.

### November: repository repair and long-horizon workflows

1. Run sandboxed repository-repair fixtures with hidden regression tests.
2. Run real but owner-approved workflows such as rental research to annotated visit list and 211 need to source-attributed map plan.
3. Measure completion, recovery, permission correctness, factual support, latency, cost, and human acceptance.

Exit evidence: end-to-end tasks have reproducible traces and holdout performance, not only unit-test success.

### December: independent-learning demonstration and limited beta

1. Choose one safe, bounded failed capability such as provider-timeout recovery.
2. Allow Buddy to retrieve only a source allowlist, propose a review-branch change, and run it in a sandbox.
3. Require owner review, regression, safety, and separate holdout pass before a canary.
4. Publish the before/after result bundle, retained failure, changed source list, rollback, and a plain-language scorecard.

Exit evidence: one claimable independent-learning record; any broader frontier claim remains lane-specific and confidence-qualified.

## No-go rules

- Never call a result frontier-competitive without the same fixture, grader, timeout, and assistance policy for each subject.
- Never report a single "AGI percentage."
- Never treat a provider catalog, mocked result, or passing harness test as model performance.
- Never place credentials, raw user data, hidden answers, or copyrighted/private training data in an evidence bundle.
