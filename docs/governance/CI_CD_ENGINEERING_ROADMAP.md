# DreamCo CI/CD Engineering Roadmap — 100-Hint Review

This roadmap organizes the 100 proposed CI/CD improvements into delivery waves. It is not a mandate to enable every idea immediately. Every change must have an owner, measurable benefit, rollback path, and bounded permissions.

## Wave 0 — Trust, evidence, and merge safety

Prioritize hints 1–15, 31–33, 36–37, 51–56, 58, 62, 65–68, 71–74, 82, 85, and 88.

- Enforce fail-closed evidence, schema, secret, provenance, dependency, and holdout gates.
- Pin model and dataset revisions and preserve source/license evidence.
- Use safetensors for distributable model weights; do not load untrusted pickle checkpoints.
- Keep holdout data outside training and tuning paths; use hashes plus independent contamination review.
- Add deterministic seeds, gradient clipping, and NaN/Inf loss circuit breakers to training jobs.
- Deduplicate remediation issues and update a single PR audit comment rather than creating ticket spam.
- Require human review and branch protection; automated review is a signal, not an authority to merge.
- Keep audit reports immutable or append-only with report hashes and commit identity.

## Wave 1 — Test quality and maintainability

Prioritize hints 5, 20, 22, 29, 44, 48, 55–70, 74, 76, and 82.

- Add contract/property/fuzz tests and regression comparisons for critical routers and safety policies.
- Track latency percentiles, throughput, memory, and quality by a documented hardware profile.
- Use pedagogical rubrics for teaching style; punctuation checks are not a valid measure of Socratic tutoring.
- Use mutation testing and coverage as diagnostic signals, not as standalone quality guarantees.
- Add Ruff, type checking, actionlint, ShellCheck, Markdown link checks, and dependency review where the repository's toolchain supports them.
- Separate dev tuning from private holdout evaluation and record benchmark fixture versions.
- Enforce conventional commit and release-note conventions only after existing contributor workflows are mapped.

## Wave 2 — Efficient CI and fleet scale

Prioritize hints 16, 18–20, 22, 24–30, 35, 47, 65–67, 78–79, 86–89, and 93–95.

- Cache dependencies with lockfile-based keys and use shallow checkout except where diffs/history are required.
- Use path filters, bounded concurrency, explicit timeouts, and dynamic matrices derived from the canonical 55-division catalog.
- Set fail-fast false for independent division jobs and publish a single reconciliation report.
- Stagger scheduled cohorts within GitHub Actions scheduling limits; do not assume a one-minute cron cadence is available.
- Stream only where appropriate, but preserve exact dataset revisions, snapshots, licenses, and provenance for reproducibility.
- Use job summaries and artifact retention policies appropriate to evidence value and storage cost.
- Add retries with exponential backoff for external APIs, plus request budgets and rate-limit telemetry.

## Wave 3 — Model operations and controlled deployment

Prioritize hints 32–33, 37–43, 46–50, 53–55, 59–60, 90, and 92–100.

- Run model training on explicitly approved compute, not as an accidental side effect of ordinary PR checks.
- Evaluate quantization and ONNX exports against the same independent test suites before release.
- Use hardware-specific memory and latency budgets; 512 MB and 15 ms are targets only when a named target device and workload are specified.
- Canary deployment must be simulation-first for robotics and require safety approval before any physical fleet exposure.
- Cross-division distillation requires source rights, teacher-output provenance, contamination controls, and independent evaluation.
- Quantized/adapter releases must retain links to the parent checkpoint, exact conversion parameters, and regression evidence.
- Use signed release artifacts for credentials; GPA alone cannot mint a credential or establish academic completion.
- Prefer immutable object/artifact storage for large checkpoints over Git branches or ordinary Git LFS workflows.
- Hot swaps require health checks, atomic promotion, rollback evidence, and operator approval for safety-critical systems.

## Recommendations that need correction before adoption

| Proposed hint | Decision | Engineering correction |
|---|---|---|
| 17 — CPU-only PyTorch install | Adapt | Use the official PyTorch CPU wheel index/selector for the pinned version; the generic pytorch.org URL shown in the example is not a valid wheel index. |
| 21 — add [skip ci] to telemetry commits | Avoid by default | Use path filters and concurrency. Skipping CI can bypass required checks if the commit changes protected content. |
| 23 — self-hosted GPU runners | Restricted | Use ephemeral, isolated runners with no long-lived secrets; never expose privileged self-hosted runners to untrusted PR code. |
| 27 — four-minute timeout for a five-minute loop | Reject as written | Choose timeouts from measured workload duration; a four-minute timeout contradicts a five-minute task. |
| 34 — streaming external data | Adapt | Streaming does not establish license rights, revision pinning, offline reproducibility, or holdout separation. |
| 36 — hard-code tokenizer vocabulary to 32,000 | Reject as a universal rule | Tokenizer vocabulary must match the versioned architecture and trained tokenizer; changing it changes the model contract. |
| 41 — route 5% to a canary | Restricted | Begin in simulation/shadow mode; physical robotics deployment requires safety case, human approval, and rollback readiness. |
| 45 — nightly cross-division distillation | Restricted | Teacher outputs are training data and need provenance, rights, leakage controls, and holdout separation. |
| 46 — universal 512 MB RAM limit | Adapt | Define memory budgets per hardware class, context length, runtime, and batch size. |
| 48 — chosen response must score higher | Adapt | Pairwise scores alone do not prove preference quality; audit pair provenance, annotator policy, ties, and disagreement. |
| 52 — 13-gram overlap as zero-contamination proof | Reject as sufficient | Combine exact hashes, normalized duplicate checks, n-gram/fuzzy matching, semantic review, and independent holdout governance. |
| 53 — call the four DreamCo lanes O*NET lanes | Correct terminology | Treat Human-Only, AI-Assisted, Autonomous-Robot, and Full-AI as DreamCo routing lanes; map them to occupational taxonomies without misattribution. |
| 57 — require question marks for Socratic style | Reject | Evaluate question quality, learner reasoning, feedback, and transfer using a rubric and human-calibrated examples. |
| 61 — universal 85% coverage floor | Adapt | Set risk-based coverage thresholds for critical modules and test behavior, not merely lines executed. |
| 73 — automatically close issues on one passing scan | Restrict | Close only when all linked findings are resolved and required CI is green; preserve the audit trail. |
| 75 — close inactive drafts after 14 days | Avoid by default | Notify owners and request confirmation; inactivity alone does not make a draft obsolete. |
| 77 — release when all divisions pass | Restrict | Require release owner approval, provenance/license checks, signed artifacts, and production readiness beyond benchmark scores. |
| 80 — webhook alerts | Restrict | Store secrets securely, minimize payloads, and notify only on actionable incidents. |
| 83 — reset a corrupt curriculum cursor to zero | Adapt | Quarantine the corrupt state and recover from a verified checkpoint; silently resetting can repeat data or hide corruption. |
| 87 — five cron cohorts every minute | Reject as written | GitHub scheduled workflows have a minimum interval; stagger cohorts on supported schedules or use a queue. |
| 90 — diploma at GPA >= 3.75 | Reject as sufficient | Registrar requirements, independent assessment, thesis/practicum, review, and credential signing must all pass. |
| 94 — query remaining Actions billing minutes | Investigate | Use documented billing/usage data where available; do not make job scheduling depend on an assumed universal remaining-minutes API. |
| 96 — checkpoint per branch | Adapt | Store large immutable artifacts in a model/artifact registry with hashes and retention policy, not ordinary Git branches. |
| 97 — prune by validation perplexity alone | Reject as sufficient | Preserve rare safety and edge cases; require multi-objective review and rollback before curriculum removal. |

## Non-negotiable operating rules

1. No paid training, external downloads, deployment, public publishing, or physical robot actuation without the applicable explicit authorization.
2. No untrusted PR code executes in a workflow holding write-capable tokens or privileged self-hosted runner access.
3. No private holdout is generated, tuned, or promoted by the training-resource harvester.
4. No benchmark, performance, safety, or accreditation claim is published without matching evidence.
5. No automated fixer commits to a contributor branch without a scoped patch, tests, and a reviewable PR.
6. No workflow is added solely to increase workflow count; consolidate checks and use a canonical source of truth.
