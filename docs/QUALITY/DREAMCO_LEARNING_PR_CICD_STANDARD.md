# DreamCo Learning, Pull Request, and CI/CD Quality Standard

## Purpose

Apply a consistent, evidence-led quality bar to every DreamCo division, specialist bot, learning pathway, pull request, and delivery workflow. The learning approach is inspired by publicly available freeCodeCamp practices: structured curriculum, progressive hands-on challenges, projects, automated tests, practical feedback, and demonstrable outcomes. This is not a freeCodeCamp standard or endorsement.

## 1. Division learning contract

Every canonical division must have a verified registry identity, owner, mission, capability map, prerequisites, learning resources, original lessons, exercises, practical projects, sandbox plan, assessments, regression tests, and evidence history.

Each division must be able to:
1. Discover authorized resources and record provenance and rights.
2. Map each resource to a capability and division with a defensible rationale.
3. Select study based on a measured skill gap.
4. Produce original notes and original DreamCo-authored instruction.
5. Complete guided and independent exercises.
6. Build a practical project with explicit acceptance criteria.
7. Run targeted tests and an unseen holdout assessment.
8. Run regression checks and record versioned evidence.
9. Route failures back to prerequisite review or targeted practice.
10. Report progress truthfully.

A queued resource is not studied. A studied resource is not mastery. Metadata discovery is not video viewing. A sandbox contract test is not proof of a live external integration. Rights to view a resource do not automatically grant rights to copy, redistribute, scrape, or train on it.

## 2. Learning and mastery states

Use explicit states: discovered, queued_not_studied, rights_pending, studied, practiced, sandbox_tested, assessed, verified, mastered, blocked, and reopened.

Mastery requires an authorized study basis, original learner notes or work, a completed practical exercise, a passed targeted assessment, a separate unseen holdout, passing regression checks, and inspectable run/version evidence. Consequential capabilities require appropriate human review. Any later regression reopens the capability.

## 3. Lesson package requirements

Every original lesson should contain:
- audience, level, prerequisites, and measurable learning objectives
- plain-language explanation and glossary
- original worked examples
- guided practice with graduated hints
- independent practice without answer leakage
- stretch challenge
- practical project and acceptance criteria
- knowledge check with explanations
- sandbox/test instructions
- accessibility guidance
- source links, provenance, license/terms, and permitted-use status

Do not copy course transcripts, proprietary exercises, answer keys, or paid course material. Link to original resources and create independent explanations and tasks.

## 4. Pull request review gates

Every PR description must state the problem, expected outcome, approach, scope, tests run, results, risks, migration/configuration impact, and rollback approach.

Reviewers must assess:
- correctness and acceptance criteria
- architecture, ownership, and division routing
- tests for happy paths, boundaries, failures, and security
- privacy, secrets, authorization, and least privilege
- dependency and supply-chain changes
- generated artifacts and reproducibility
- accessibility and user experience where applicable
- documentation and accuracy of completion claims
- observability, cost, deployment, and rollback

Comments must identify file/line, impact, and a concrete remediation. Separate blockers from suggestions. Independent review is required where repository policy requires it; authors must not self-approve. Never merge solely to clear a queue or turn a status green.

## 5. CI/CD workflow review gates

Review both workflow configuration and actual run evidence. Required checks should be appropriate to the change and include reproducible dependency installation, formatting/lint, type checks, unit/integration/end-to-end tests, schema and registry validation, generated-artifact freshness, secret/dependency scanning, production build, and deployment smoke tests where relevant.

Workflow security:
- grant least-privilege token permissions
- do not expose secrets to untrusted fork pull requests
- pin and review third-party actions according to repository policy
- protect deployment environments and require approvals for consequential releases
- use concurrency and caches without allowing stale or untrusted artifacts to bypass validation
- retain actionable logs, test reports, and artifacts
- support rollback and post-deployment verification

## 6. Failure handling

For every failure, capture workflow, run ID, commit SHA, branch, job, step, first causal error, log excerpt, environment, root-cause category, repair, regression test, rerun ID, and observed conclusion.

Classify defects: source-code bug, test/assertion bug, flaky test, missing file/artifact, stale generated output, dependency drift, permission/token scope, missing secret, provider outage, quota/rate limit, configuration/environment drift, or infrastructure issue.

Never manufacture success by deleting meaningful tests, weakening assertions, broadly skipping checks, suppressing errors, or treating cancelled/skipped jobs as passed. Fix root causes and preserve regression coverage.

## 7. Completion reporting

Dashboards and reports must distinguish planned, implemented, sandbox-tested, verified, production-ready, blocked, failed, and not-tested states. Show denominators, timestamps, commit/run identifiers, and evidence links. A green workflow means only that the checks actually configured and executed passed for that run; it is not a blanket certification of every division or feature.

## 8. Release checklist

- [ ] PR scope and acceptance criteria are clear.
- [ ] Independent review is complete where required.
- [ ] Relevant tests and security checks pass.
- [ ] Full required CI suite passes on the proposed merge commit.
- [ ] Generated outputs are reproducible and current.
- [ ] No secret or private data exposure is present.
- [ ] Required approvals and deployment protections are active.
- [ ] Smoke checks and rollback plan are documented.
- [ ] User-facing claims match the evidence.
- [ ] Completion status links to inspectable evidence.
