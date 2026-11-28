# DreamCo Master Completion Plan
Updated: 2026-11-28
Repository: DreamCo-Technologies/Dreamcobots
Observed main SHA: 38751893b8299239fdf054463a61c06bead3d097

This is a consolidated execution plan, not a claim that the work is already complete.

## Completion rules
1. Preserve existing bot IDs, divisions, pages, working workflows, and merged work. Prefer additive, narrow changes.
2. Never claim implemented, verified, trained, mastered, production-ready, or revenue-generating without reproducible evidence.
3. Queued, skipped, cancelled, stale, or missing checks are not passes.
4. Keep production deployment, external account actions, paid compute, live outreach, payments, model training, and promotion behind explicit approval and documented prerequisites.
5. Keep credentials and private signing keys out of source control, generated artifacts, URLs, logs, and browser storage.
6. Clean-room reverse engineering only: authorized inputs, metadata/structure extraction, no copied proprietary source or protected content, rights review, redaction, sandboxing, and human approval.
7. Split large generated diffs into reviewable slices, targeting under 1,500 changed lines and under 5 MiB per PR where practical.

## Workstreams and exit criteria

### 0. Repository baseline, PR inventory, evidence ledger
Reconcile every open PR against current main: head/base SHA, age and behind count, changed paths, checks, review threads, overlap, dependencies, and disposition. Reconcile closed-unmerged PRs separately. Preserve merged work and verify current-main checks. Maintain evidence states: found, proposed, changed, verified, blocked, unknown. Exit: every PR has a documented merge/rebase/split/supersede/close/owner-review decision.

### 1. Stabilize newest CI and feature PRs
Review #18814 safe-repair assertions and generated credential guard; #18815 rights/catalog integrity; #18817 safe AST rewrites; #18818 Actions schedule reduction; #18819 Media Foundry; #18820 C++/CUDA clean-room parsers; #18816 Foundry holdout/signing hardening; #18829 Markdown inventory; #18830 65-division capability gaps; #18831 curriculum import fix; #18832 Watchtower DNS test fix. Confirm latest head checks and review threads. #18816 depends on #18815 and was previously reported 98 commits behind; recheck and rebase before merge. Reconcile recently merged #18798, #18803, #18808, #18809, #18811, #18812 against main and verify post-merge checks. Exit: exact-head required checks pass, reviews resolved, dependencies respected, and only safe PRs merged.

### 2. Actions / CI reliability and cost
Inventory workflows, triggers, permissions, concurrency, schedules, runners, secrets, artifacts, duration, failures, and duplicate coverage. Fix root causes before consolidation. Preserve unique safety/release coverage and manual/PR/push triggers. Pin third-party actions, use least privilege, cache only explicitly permitted public data, and measure improvements against a baseline. Exit: required CI green on main with no missing safety coverage and improved measured reliability/runtime.

### 3. Sentinel / repository self-repair
Keep AST consolidation conservative: dry-run diffs, ambiguity detection, symlink/path-traversal/out-of-root protection, backups, atomic writes, rollback, idempotency, and bounded scope. Integrate FreeCodeCamp delta sync as metadata/catalog refresh with pinned source identity, rate limits, hashes, and diffs. Catalog lag may open a proposed refresh PR; it must not silently overwrite reviewed content. Exit: fixtures, adversarial path tests, rollback/idempotency tests, and human review pass.

### 4. Bootcamp / 65 divisions / proprietary learning
Complete source catalog, rights gate, curriculum generation, learner progress, sandbox, assessments, teach-back, and mastery evidence. Preserve 45 original core divisions plus 10 supplemental profiles; distinguish the canonical 65 MasterBots from 55 domain profiles and 20 shared platform services. Resolve owner identity and exact O*NET mappings; never infer mappings. Produce original course materials/books; third-party content requires documented rights. Exit: each division has reviewed curriculum, cleared sources, capability-specific tests, unseen evaluation, teach-back, and traceable mastery. Missing evidence remains blocked.

### 5. Model Foundry / Buddy training / teacher benchmarks
Complete dataset authorization, source hashes, split isolation, tokenizer/shard provenance, reproducible recipes, evaluation, safety regression, and checkpoint provenance. Holdout data must never be used for training, tuning, tokenizer fitting, or prompt optimization. Require pinned base-model revisions and commercial-use rights. Build teacher/student task benchmarks with quality, safety, latency, cost, and independent holdouts. Run GPU training only with signed data/model authorization and an approved isolated runner. Exit: real checkpoint plus exact provenance hashes, full holdout report, no-regression evidence, and owner-approved promotion. Otherwise training/mastery claims remain false.

### 6. Media Foundry
Complete Stage 10 production packet, storyboard, keyframe/shot plan, timeline, asset manifest, renderer adapters, and quality gate. Enforce rights for every asset, voice, character, music track, model, and dependency; code license is not model/asset license. Add reproducible render tests, provenance, output validation, and rights ledger. Exit: end-to-end sample render using rights-cleared assets with validated manifest.

### 7. Universal Watchtower / Opportunity Engine
Complete declarative rules, provider-neutral fetch/normalize adapters, scheduling, deduplication, freshness, attribution, alert routing, retries/backoff, and audit trail. Bound and allowlist network access; respect source terms, authentication boundaries, and rate limits. Test DNS/network failures, redirects, SSRF, stale data, duplicates, and provider outages. Exit: deterministic offline tests and approved live-source smoke tests; no unauthorized transactions or execution.

### 8. Buddy OS / runtime / persistence / integrations
Complete authenticated task lifecycle, user-scoped persistence, append-only audit, explicit approval state machine, tool routing, memory boundaries, and recovery. Build a beginner-friendly connection center with permissions/cost explanations, secure credential references, connection tests, diagnostics, and free/local alternatives. Model routing must use measured quality, safety, latency, availability, and cost; fail closed without identity/policy. Exit: authenticated end-to-end workflows, isolation/contract tests, audit evidence, and recovery.

### 9. Security, privacy, reverse engineering
Resolve API authentication and owner-only administrative routes; explicitly allowlist public endpoints. Complete secret/generated-artifact scanning, dependency/supply-chain checks, CodeQL, SBOM/provenance, least privilege, redaction, and retention. Complete forensic review and validated lessons before audit closure. Reverse engineering requires authorized samples, redaction, clean-room functional specs, sandbox execution, and human/legal review. Exit: no unresolved critical/high findings without documented owner-approved exception; tests pass on exact commit.

### 10. Pages, deployment, operational truth
Validate public pages, navigation, links, assets, API contracts, health checks, deployment isolation, rollback, and production configuration. Separate static Pages success from backend health and real deployment. Verify runtime evidence ledger, actual schedule execution, and service health before claiming 300-second scheduling or hourly training. Exit: reproducible deployment, smoke tests, observability, rollback drill, secrets/config review, and owner sign-off.

### 11. Bot fleet, revenue, marketplace
Preserve executable bot IDs; do not create duplicate bots for proposals. Verify each bot family has manifest, runtime contract, tools, memory boundaries, learning policy, sandbox, tests, observability, security, and owner approval. Keep revenue adapters simulation/read-only until separately authorized; verify economics and source data. Exit: task-level tests and independent performance evidence; revenue only from reconciled real outcomes.

## Dependency order
1. Capture baseline and reconcile PR inventory.
2. Stabilize focused CI/security/rights fixes (#18814, #18815, #18817, #18831, #18832).
3. Merge dependent feature work only after prerequisites and exact-head checks pass; #18816 follows #18815.
4. Complete Sentinel and Watchtower validation and safe delta sync.
5. Complete Bootcamp curriculum, rights, mastery, and teacher benchmarks.
6. Complete Foundry evaluation/training and Media Foundry rights/render validation.
7. Complete Buddy runtime, persistence, integrations, security, deployment, and operational evidence.
8. Complete fleet/revenue verification and final certification.

## Known blockers to revalidate
- Prior review identified 36 open PRs; recount from the live inventory before claiming a current count.
- #18816 previously 98 commits behind; verify current state and rebase.
- Legacy #14014, #13176, #474, and #730 were previously thousands of commits behind; do not merge blindly. Extract/split unique changes or close after comparison.
- #17173 needs privacy sanitization and completed conversation-checklist evidence.
- #18211 contains an inventory but zero completed forensic reviews/validated lessons; inventory is not audit completion.
- #13195 remains a draft requiring owner security review and full auth regression validation.
- #15189 persistence foundation still needs authenticated API, dashboard, and supervised runtime integration.
- Revalidate dataset hashes when reusing signed manifests.
- Prior full certification had a supply-chain vulnerability gate failure; remediate and rerun.

## Definition of done
Every open PR has a documented disposition. Required checks pass on the exact commit to be merged. Security, rights, privacy, and owner approval gates are closed or block release. Promised features have tests and observable evidence. Training, deployment, schedules, integrations, and revenue are claimed only when actual artifacts/runs prove them. Final certification includes commit SHA, run IDs, artifacts, test results, unresolved risks, and owner sign-off.

## Per-task evidence fields
Owner; PR/issue; dependency; status; exact commit SHA; workflow/run ID and attempt; artifact/evidence URI; test result; security/rights review; blocker; next action; completion approver.
