# Buddy PR Review System

## Mission
Buddy should become an evidence-driven pull-request review system that developers can trust before, during, and after a change. The goal is not to imitate one existing reviewer. The goal is to combine repository understanding, specialist routing, deterministic checks, adversarial testing, historical learning, human judgment, and measurable review quality.

Buddy must never claim to be the best in the world without benchmark evidence. The system therefore treats "world-class" as a measurable engineering target.

## Review lifecycle

### 0. Before the PR
- Understand repository architecture, conventions, ownership, dependencies, security boundaries and active work.
- Build a change-risk map before code is written.
- Identify likely files, tests, contracts and benchmark suites affected by the planned change.
- Recommend a minimal implementation and validation plan.

### 1. PR intake
- Read title, description, linked issues, labels, changed files, commits and branch/base context.
- Compare the PR against the current base, not stale cached assumptions.
- Detect missing context, oversized scope, generated files, risky permissions and dependency changes.
- Classify the change by language, framework, subsystem, risk and expected test surface.

### 2. Specialist routing
Buddy selects one or more specialists for each exact step. Candidate selection uses task-specific benchmark evidence, correctness, review precision, recall, historical performance, repository familiarity, speed, cost, safety and tool compatibility.

Core reviewer roles:
1. Repository Explorer
2. Requirements Analyst
3. Architect
4. Coder
5. Tester
6. Debugger
7. Security Reviewer
8. Dependency Reviewer
9. Performance Engineer
10. UX/Accessibility Reviewer
11. Data Analyst
12. Documentation Writer
13. Release Engineer
14. DevOps/CI Specialist
15. Integration Specialist
16. Benchmark Evaluator

The router may use several reviewers for one change and may re-route after new evidence appears.

### 3. Static and deterministic evidence
Run applicable linters, formatters, type checks, unit tests, integration tests, build checks, dependency audits, secret scans, SAST, license/policy checks and repository-specific validators.

Deterministic failures outrank speculative model comments.

### 4. Semantic review
Review:
- correctness
- requirements coverage
- architecture
- API contracts
- error handling
- concurrency/state
- data integrity
- security/privacy
- dependency risk
- performance
- accessibility/UX
- observability
- tests
- documentation
- release readiness
- migration/rollback safety

### 5. Adversarial review
Buddy creates targeted counterexamples for important changes:
- malformed inputs
- boundary values
- retries and duplicate events
- partial failures
- race conditions
- permission failures
- dependency outages
- rollback scenarios
- compatibility problems
- unexpected user behavior

It should prefer small, reproducible demonstrations over vague warnings.

### 6. Review synthesis
Every finding receives:
- severity
- confidence
- evidence
- affected path/line when available
- why it matters
- minimal fix
- validation command/test
- whether it blocks merge
- whether it is a duplicate of another finding

Findings are deduplicated across specialists.

### 7. Developer experience
The default review should be concise and actionable. Developers can expand any finding into:
- Teach Me
- Show the evidence
- Show a safer alternative
- Generate a test
- Generate a fix plan
- Explain the architecture
- Compare alternatives
- Re-review after changes

### 8. During revision
Buddy watches new commits, invalidates stale findings when appropriate, preserves still-valid findings, re-runs targeted checks, and explains what changed since the previous review.

### 9. Pre-merge gate
Buddy produces a merge-readiness report containing:
- requirements coverage
- deterministic checks
- benchmark results
- unresolved high-confidence findings
- risk summary
- changed-scope summary
- reviewer agreement/disagreement
- human approvals required

Default policy: Buddy may recommend approval, but it does not silently approve or merge consequential changes.

### 10. After merge
Buddy continues reviewing:
- post-merge failures
- regressions
- production incidents
- rollback events
- reverted commits
- flaky tests
- security findings
- performance regressions
- developer feedback

It links incidents back to the review that missed or correctly identified the issue and updates reviewer benchmarks.

## Review-quality benchmarks

Buddy should maintain separate benchmark scores for:
- defect precision
- defect recall
- false-positive rate
- false-negative rate
- severity calibration
- duplicate suppression
- actionable-fix rate
- test-generation usefulness
- regression detection
- security detection
- dependency detection
- performance detection
- accessibility detection
- review latency
- token/tool cost
- developer acceptance
- post-merge incident correlation

A reviewer is not promoted to "mastered" based on one good PR. Promotion requires repeated, task-specific evidence across representative repositories and regression suites.

## Review memory

Buddy stores structured lessons rather than blindly copying previous reviews:
- repository conventions
- confirmed defects
- accepted exceptions
- recurring failure patterns
- false positives
- false negatives
- successful fixes
- tests that caught regressions
- reviewer/model benchmark history

Sensitive or proprietary source code must remain subject to repository permissions and configured retention rules.

## Human control levels

### Observe
Read-only analysis and suggestions.

### Assist
Generate comments, tests and fix plans for human approval.

### Collaborate
Prepare patches or branches; human reviews the changes before publication.

### Guarded automation
Perform explicitly authorized low-risk actions under repository policy.

### Trusted automation
Only available after measurable evidence, policy approval, rollback capability and repository-specific trust requirements are satisfied.

No global "take over" switch should bypass repository permissions, branch protections, security policy or human authorization.

## What makes Buddy different

1. Repository-wide context before line-by-line review.
2. Dynamic specialist routing per exact task.
3. Deterministic evidence before speculative reasoning.
4. Multi-agent disagreement analysis.
5. Adversarial test generation.
6. Historical false-positive/false-negative learning.
7. Review quality measured after merge.
8. Beginner and expert views of the same finding.
9. Change-aware re-review rather than repeating the entire review blindly.
10. Explicit evidence for every blocking finding.
11. Repository-specific standards and benchmarks.
12. Human-control levels that can increase only with evidence.

## Actions page controls

The Buddy Actions page should expose:
- Review a PR
- Pre-PR architecture review
- Re-review latest commit
- Review only changed files
- Security review
- Dependency review
- Performance review
- Test-gap review
- Accessibility review
- Requirements review
- Adversarial review
- Compare reviewers
- Explain a finding
- Generate regression test
- Generate fix plan
- Check stale findings
- Review merge readiness
- Post-merge regression review
- View reviewer benchmark history
- Run review benchmark suite
- Configure repository trust level

## Success condition

Buddy is ready to take a larger role only when measured review quality demonstrates that it is reliable for the exact repository and review class, with transparent evidence and safe rollback. The system should continuously attempt to disprove its own confidence rather than rewarding itself for agreeing with humans.