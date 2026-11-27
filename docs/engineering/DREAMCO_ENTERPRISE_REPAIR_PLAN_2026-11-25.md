# DreamCo Enterprise Repair Plan — 2026-11-25

## Operating standard

Every repair is delivered through a scoped pull request, with a reproducible test, explicit acceptance criteria, and evidence from the exact PR head. A green inventory or catalog is not runtime proof. Do not claim a division, bot, tokenizer, model, connector, or deployment is working unless its execution and evidence are present.

No direct push to `main`, production deployment, credential creation, paid compute, external data download, financial action, or model-weight promotion is authorized by this plan.

## Baseline observed during the audit

- Canonical business-domain crosswalk: 45 divisions.
- MasterBot registry: 65 lanes.
- Generated runtime division manifests: 57 entries, including shared-workforce/support records.
- App bot portfolio: 56 source divisions, plus generated/shared routing.
- Full generated bot manifest: 1,232 bot profiles.
- Division model manifest: 65 planned records; status is `inventory_only_not_trained`.
- The Division Superbot manifest builder initializes user jobs, capabilities, tools, connectors, dependencies, workflows, benchmarks, and commercial outcome metrics as empty arrays. Its own notes say the generated records require enrichment before production certification.
- Byte-level BPE tokenizer implementation and regression tests exist. The repository currently has no registered authorized training corpora, so no real corpus-backed tokenizer run is evidenced.
- A model-foundry trainer and separate authorization workflow exist. The actual division-training workflow requires a self-hosted GPU runner, owner approval, local rights-cleared data, and a training evidence artifact. No successful checkpoint/holdout/promotion evidence was established in this audit.
- Latest PR run history included 33 skipped Actions Failure Watch runs and 24 skipped Buddy CI Safe Generated-Artifact Repair runs among the 100 most recent workflow runs. This indicates workflow-run fan-out/no-op overhead, not by itself an infinite loop.
- PR #18407 exposed three concrete issues in its first check run: missing top-level proposed owner metadata, stale division/runtime evidence, and a Code Trust evidence requirement. The proposed-owner correction and regression test have since been added to the PR; the updated checks must be re-read before merge.
- PR #18406 duplicates the proposed-owner edit and has a malformed PyYAML install line nested under `run: npm ci`. A warning was posted; do not merge it as written.
- PR #18405 changes source provenance and dual-learner curriculum contracts but is currently not mergeable. Reconcile its branch/base conflicts and test its source provenance changes independently.

## Repair waves and acceptance criteria

### Wave 0 — Protect the merge queue and establish the baseline
1. Inventory every open PR, branch head, base SHA, changed paths, merge conflicts, and required checks.
2. Group overlapping PRs by changed file and contract; identify duplicate or superseded PRs before merging.
3. Re-run current PR checks after each commit and use job logs to find root causes. Do not merge on `mergeable=true` alone.
4. Keep the main branch as the canonical base and preserve all source artifacts.

**Done when:** each active PR has a disposition (merge-ready, repair-needed, conflict-blocked, duplicate/superseded) and current check evidence.

### Wave 1 — CI reliability and Actions efficiency
1. Fix dependency declarations in workflows (including the PyYAML dependency used by Repository System Watch).
2. Validate every workflow file with a YAML 1.2-aware parser and a workflow schema/lint pass.
3. Map all `workflow_run` dependencies as a directed graph; identify fan-out, repeated no-op events, circular chains, missing conclusion filters, and workflows that trigger expensive downstream jobs unnecessarily.
4. Keep failure evidence capture, but reduce unnecessary workflow-run subscriptions and add branch/event filters where supported.
5. Make scheduled health jobs read-only and idempotent; separate report-only checks from required CI gates.
6. Standardize permissions to least privilege, timeouts, concurrency, caching, and artifact retention.
7. Pin third-party actions to immutable SHAs where policy requires; upgrade deprecated action runtimes through a tested batch.

**Done when:** workflow graph is acyclic by design, routine PRs do not create avoidable cascades, YAML/schema checks pass, and required checks finish with useful evidence.

### Wave 2 — Fleet routing and generated-contract correctness
1. Keep the proposed division owner on every fleet bot record while leaving canonical owner null until approval.
2. Reconcile the 45-domain crosswalk, 65 MasterBot lanes, 56 App_bots portfolios, and 57 runtime manifest entries with an explicit mapping and no silent drops.
3. Regenerate and verify bot manifests, division manifests, fleet execution maps, Pages prospectuses, search indexes, and production evidence in dependency order.
4. Fix runtime truth semantics: `IMPLEMENTED` means generic offline smoke only; `TESTED` requires bot-specific unit and division smoke evidence. Tests must assert the state actually proven.
5. Investigate the learning-task external fallback regression and ensure explicit opt-in only occurs after internal gap detection.
6. Reconcile file-prospectus and Actions-prospectus drift without weakening freshness checks.
7. Add crosswalk tests for missing, extra, duplicate, and unassigned domain records.

**Done when:** all generated artifacts are current, every expected division has a smoke result, all 1,232 bot profiles have consistent route metadata, and the fleet runtime gate passes without downgrading truth standards.

### Wave 3 — Division completeness and Superbot quality
1. Replace the empty-array-only division generator with source-backed extraction from bot manifests, capability charters, connector registries, workflow registry, benchmark registry, and dependency metadata.
2. Preserve source paths and provenance for every synthesized capability.
3. Add a domain-specific gap report for missing missions, users/jobs, inputs/outputs, tools, connectors, dependencies, policies, workflows, benchmarks, and outcome metrics.
4. Create per-division smoke and acceptance suites, including negative tests for permissions and external side effects.
5. Keep cross-division collaboration as links, not duplicate ownership.
6. Do not mark a generated division production-ready until its required evidence passes.

**Done when:** each of the 45 canonical divisions has a reviewable, non-empty operational blueprint where evidence exists; unknown fields remain explicitly unknown rather than fabricated.

### Wave 4 — Buddy learning, tokenizer, and model factory
1. Keep tokenizer training separate from neural model-weight training in UI, job names, logs, and metrics.
2. Add a repeatable tokenizer job that accepts only local, rights-cleared, hashed corpora; records vocabulary size, merges, source provenance, deterministic output hash, and round-trip regression results.
3. Add a small synthetic, first-party corpus fixture for CI tests only; never promote it as a production training corpus.
4. Connect tokenizer artifacts to the model registry with immutable version/hash metadata and compatibility tests.
5. Validate the existing CPU model-foundry CLI, architecture profiles, manifest checks, resume/checkpoint behavior, and deterministic smoke training on a synthetic test fixture.
6. Keep production weight updates blocked until the owner authorization profile, dataset rights, compute approval, and explicit run approval are all present.
7. For GPU training, require pinned base model/revision, verified license, train/validation/holdout separation, checkpoint hashes, loss curves, baseline comparisons, safety/regression evaluation, and cost records.
8. Add distillation only where teacher license/output-use terms and human-reviewed target provenance permit it.
9. Keep Dream Brain retrieval/memory improvements distinct from model weight changes; measure retrieval quality and regression separately.
10. Do not claim model mastery from course completion, tokenizer training, synthetic unit tests, or catalog presence.

**Done when:** a tokenizer artifact can be reproduced and evaluated from approved local data; a synthetic CPU training smoke produces a real checkpoint in test-only scope; production training remains gated; no model is promoted without holdout and regression evidence.

### Wave 5 — Runtime, integration, and security
1. Test server/client/shared TypeScript contracts, API routes, database migrations, queue semantics, and runtime adapter boundaries.
2. Test connector health, missing-secret diagnostics, permission scopes, cost visibility, retries, idempotency, and safe fallback.
3. Verify secret values never enter logs, generated manifests, browser bundles, or artifacts.
4. Test user consent and approval gates for external writes, money, publishing, communications, destructive operations, and deployment.
5. Run dependency, static-analysis, secret-scan, CodeQL, and supply-chain checks.
6. Add end-to-end journeys for Buddy task intake → plan → approval → execution → evidence → learning record → regression.

**Done when:** integration tests pass and all consequential actions remain approval-gated.

### Wave 6 — Production certification and operations
1. Build a division-by-division and workflow-by-workflow certification matrix.
2. Run unit, contract, integration, offline smoke, end-to-end, security, performance, accessibility, and recovery tests.
3. Verify backups, rollback, queue draining, rate limits, health endpoints, alerting, and incident records.
4. Establish cost budgets and run-frequency limits; prevent duplicate scheduled/triggered work.
5. Produce a final report separating passed, failed, blocked, untested, and owner-approval-required items.

**Done when:** every production claim links to a current passing run and artifact, all failures are fixed or explicitly blocked with an owner/action, and no unresolved critical/high issue is hidden.

## Current scoped pull-request queue

| PR | Scope | Current disposition |
|---|---|---|
| #18407 | Fleet proposed-owner field, Repository System Watch dependency, rights-gated tokenizer workflow | Updated; re-check exact latest head before merge |
| #18406 | Duplicate fleet/dependency repair | Do not merge as written; malformed YAML and duplicate field |
| #18405 | Study-plan source provenance and dual-learner contract | Conflict-blocked; rebase/reconcile separately |
| New PRs | Actions trigger graph/fan-out, fleet truth/evidence drift, division blueprint enrichment, model-factory reproducibility | Create as separate bounded waves after source/test inspection |

## Rules for each repair PR

- One coherent subsystem per PR; no unrelated generated-file churn.
- Include a root cause, affected contracts, tests, expected evidence, and rollback notes.
- Run targeted tests first, then dependent regression checks, then full required CI.
- Inspect logs from every failed job; do not repeat a run without changing code or identifying a transient failure.
- Never lower test expectations, alter baselines, or mark readiness as tested merely to make CI green.
- Merge only after current checks pass and conflicts are resolved; use auto-merge only if repository rules and checks explicitly allow it.
