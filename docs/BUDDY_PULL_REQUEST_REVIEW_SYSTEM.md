# Buddy Pull Request Review System

## Goal

Build a developer-grade review system that is useful **before, during, and after** a pull request. Buddy should be able to review every repository it is authorized to inspect, while preserving human control over consequential changes until its evidence supports a higher automation tier.

## Review lifecycle

### 1. Before the PR
- Inspect repository health, branch state, recent regressions, ownership, architecture contracts, dependency policy, security rules, benchmark history and relevant issues.
- Turn the requested change into a review contract: intent, acceptance criteria, affected surfaces, risk class and required tests.
- Select the best specialist(s) for each step rather than assigning every task to one generic reviewer.
- Predict likely failure modes and create targeted tests before implementation when practical.

### 2. During development
- Review commits incrementally instead of waiting for the final diff.
- Detect scope drift, duplicated work, stale assumptions, accidental generated-file edits, API contract changes and missing tests.
- Re-run only relevant checks first, then expand to broader checks based on risk.
- Compare the current change with repository history, similar fixes and prior review lessons.
- Track unresolved findings with stable IDs so a later commit can verify whether each finding was actually fixed.

### 3. At PR submission
Produce a structured review with:
- executive summary
- intent/requirements coverage
- correctness findings
- security/privacy findings
- reliability findings
- performance findings
- dependency/supply-chain findings
- test-quality findings
- API/schema compatibility
- observability/operations impact
- UX/accessibility impact
- documentation/release impact
- benchmark evidence
- changed-file risk map
- suggested fixes with rationale
- confidence and evidence for every material finding

### 4. After changes
- Re-check only changed assumptions and resolved findings.
- Run regression tests for previously related failures.
- Compare before/after benchmark evidence.
- Verify no new high-severity issue was introduced.
- Keep a durable review lesson for future PRs.
- Mark findings resolved only when evidence supports resolution.

## Multi-agent review council

Buddy may route one PR through multiple specialists:

1. Repository Explorer — understand structure and ownership.
2. Requirements Analyst — verify intent and acceptance criteria.
3. Architect — evaluate design and boundaries.
4. Coder — reason about implementation correctness.
5. Tester — identify missing and weak tests.
6. Debugger — investigate failures and regressions.
7. Security Reviewer — threat model and security controls.
8. Dependency Reviewer — packages, versions and supply chain.
9. Performance Engineer — latency, throughput and resource impact.
10. UX/Accessibility Reviewer — usability and accessibility.
11. Data Analyst — data correctness and metric interpretation.
12. Documentation Writer — docs, examples and migration notes.
13. Release Engineer — release readiness and rollback.
14. DevOps/CI Specialist — workflows, environments and deployment.
15. Integration Specialist — external systems and contracts.
16. Benchmark Evaluator — objective evidence and regression comparison.

Buddy should be able to use one specialist, a sequence, or a parallel council. Routing must be evidence-driven and may change when the task changes.

## Finding quality

Every finding should include:

- severity: blocker / critical / high / medium / low / suggestion
- confidence: numeric and calibrated
- evidence: exact file/line/test/log when available
- impact: what can break and who is affected
- reproducibility: how to demonstrate the issue
- recommended fix: smallest safe fix first
- verification: exact test or evidence required to close it
- provenance: which reviewer/model/tool produced it

Avoid noisy comments. Do not report speculative issues as facts. Duplicate findings should be clustered into one canonical finding with linked evidence.

## Better-than-basic review features

- intent-aware review rather than diff-only review
- commit-by-commit early warning
- repository memory of prior incidents
- benchmark-aware review
- change-risk scoring
- dependency blast-radius analysis
- semantic duplicate detection
- test gap generation
- regression test generation
- architecture drift detection
- generated-file awareness
- migration compatibility checks
- security threat modeling
- performance regression detection
- observability readiness checks
- rollback/readiness analysis
- reviewer disagreement detection
- confidence calibration
- false-positive tracking
- false-negative postmortems
- review latency measurement
- developer feedback loop
- personalized explanations for beginners and experts
- machine-readable review artifacts
- immutable evidence trail for important decisions

## Automation ladder

Buddy must not equate confidence with authority. Promotion should require measured evidence.

### Tier 0 — Observe
Read-only analysis. No repository writes.

### Tier 1 — Suggest
Buddy posts proposed findings or recommendations for human review.

### Tier 2 — Assist
Buddy may prepare fixes, tests, replies or review summaries, but humans approve consequential writes.

### Tier 3 — Guarded automation
For explicitly authorized repositories, Buddy may execute narrowly scoped review operations under policy and CI gates.

### Tier 4 — Trusted automation
Only after repeated, task-specific evidence shows high precision, low false-positive rate, reliable regression detection, stable CI outcomes and successful human audits should Buddy automatically perform defined review actions.

### Tier 5 — Scaled review service
For repositories that explicitly authorize it, Buddy can provide the review service continuously across many projects. Repository owners remain in control of permissions, policies, data access and merge authority.

There is **no universal magic score** that proves Buddy can replace human developers. Promotion must be benchmark- and task-specific, with rollback available.

## Review scorecard

Track at least:

- finding precision
- finding recall
- accepted-finding rate
- false-positive rate
- missed-defect rate
- severity calibration
- test-gap detection rate
- regression detection rate
- review latency
- cost per review
- CI pass correlation
- developer acceptance rate
- time-to-resolution
- post-merge incident rate
- security defect escape rate
- performance regression escape rate
- documentation completeness

The dashboard should show trends, not just one percentage.

## Actions-page controls

The Actions page should expose beginner-friendly buttons for:

- Review PR
- Review before coding
- Review latest commit
- Review changed files
- Run review council
- Security review
- Dependency review
- Test-gap review
- Benchmark review
- Performance review
- Architecture review
- Integration review
- Release review
- Explain finding
- Verify fix
- Re-run affected checks
- Compare previous review
- Find duplicate finding
- Generate regression test
- Build repair plan
- Prepare review summary
- Show evidence
- Show confidence
- Show reviewer disagreement
- Audit Buddy review
- Promote automation tier
- Roll back automation tier

## Safety and trust

Buddy should never silently merge code, change branch protection, bypass required checks, weaken security controls, expose secrets, or act outside repository authorization. A review system can be powerful without removing developer ownership.

The objective is not to make Buddy look certain. The objective is to make Buddy **measurably useful, honest about uncertainty, traceable, fast, and increasingly reliable**.
