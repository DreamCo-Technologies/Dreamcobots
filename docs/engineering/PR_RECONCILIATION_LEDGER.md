# DreamCo Pull Request Reconciliation Ledger

**Repository:** `DreamCo-Technologies/Dreamcobots`  
**Baseline branch:** `main`  
**Baseline commit inspected:** `9cfca37fbd16748c02d9a8a6e03fc17b1e28b8d2`  
**Initial inventory date:** 2026-11-18  
**Status:** Initial inventory and targeted first-pass review; NOT a complete forensic review or merge-readiness certification.

## Purpose

Preserve the engineering value of historical and active pull requests while preventing duplicate implementation, unsafe merges, lost decisions, and false completion claims. Every source PR must remain traceable to its original number, branch, commit SHA, changed files, review discussion, checks, and resulting integration.

## Repository-wide inventory snapshot

The paginated GitHub pull-request listing returned 699 PR records across seven non-empty pages:

| State at inventory time | Count |
|---|---:|
| Open | 61 |
| Merged | 423 |
| Closed, not merged | 215 |
| Total | 699 |

These are a point-in-time metadata inventory only. They do not mean 699 PRs have been read, diff-reviewed, tested, or reconciled. The listing was sorted by updated time; a durable historical pass must retain page/cursor and PR-number coverage, and re-check PRs whose heads or checks change.

## Targeted first-pass candidates

### PR #17411 — GPT-5.4 mini catalog and generated-data CI

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/17411
- State: Open; branch `feat/gpt-5-4-mini-model-catalog-and-ci-repair-20261118`
- Head SHA inspected: `02931c77e1a908fe0b21a8d76d8532153cc2dd88`
- Base: `main`; metadata reported mergeable at inspection time.
- Files: `.github/workflows/command-center-index.yml`, `config/buddy-model-selection-registry.json`, `tests/test_buddy_resource_registry.py`.
- Useful work: records GPT-5.4 mini as configuration-required and unverified; paid calls require per-request approval; explicitly does not claim fine-tuning or weight modification; adds regression tests; regenerates derived command-center data before freshness check.
- Limitations: catalog entry is not a live connection, production route, benchmark, or trained model. PR description reported one Command Center Data Contract run passing and other checks still running at its stated update; current-head check status must be fetched again before merge.
- Preliminary disposition: **NEEDS_FRESH_CHECKS**; retain as a focused PR and verify exact-head CI plus model registry consumer compatibility.

### PR #17173 — Conversation checklists and master requirements registry

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/17173
- State: Open; branch `codex/per-conversation-tracking-20261108`
- Head SHA inspected: `2e6e24f04ac78dcdb53bce9e9cb956646fc2d0e1`
- Files include `.github/workflows/keep-green.yml`, `docs/DREAMCO_CONVERSATION_CHECKLISTS.md`, `docs/DREAMCO_MASTER_REQUIREMENTS_REGISTRY.md`, and per-conversation checklists.
- Useful work: requirement traceability, independent conversation checklists, evidence-based completion rules, and regeneration of a derived Pages connection index before JSON validation.
- Limitations: metadata reported non-mergeable; the PR body describes 14 conversations/196 requirement pairs while generated review text mentions 15 conversations. Source conversation/message-level mapping is explicitly pending and checklist items remain unverified. The PR states no application code changed and no tests were run for its documentation-only changes.
- Preliminary disposition: **NEEDS_REBASE_AND_CONTENT_RECONCILIATION**; resolve conversation-count discrepancy, validate all links/targets, verify generated artifacts and current checks.

### PR #17170 — Full Markdown inventory and Pages checklist

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/17170
- State: Open; branch `audit/full-markdown-and-branch-readiness-20261109`
- Head SHA inspected: `6b5e00cc2aacd1aece99f35efc6dc40755feed72`
- Files: 15 changed files; includes Markdown audit/checklist data, Pages audit UI, registry/config, validator/tests, navigation, generated repository inventory/readiness report.
- Useful work: branch snapshot reports 1,624 Markdown files, each with an eight-point checklist; adds a searchable Pages Markdown Audit and validation gate; explicitly distinguishes inventory completeness from content review completion.
- Limitations: all checklist items were pending in the PR description; 475-branch compare had not been run fresh; browser checklist edits are local until exported/committed; metadata reported non-mergeable. Snapshot counts and generated artifacts need refresh against current main.
- Preliminary disposition: **NEEDS_REBASE_AND_FRESH_INVENTORY**; high priority because it directly supports the requested all-Markdown scan, but do not mistake file inventory for file-content review.

### PR #16600 — Open-PR unified control-plane inventory

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/16600
- State: Open; branch `integration/open-pr-unified-control-plane-20261102`
- Head SHA inspected: `ee149b959ef325e6cfaf9bb0f338d4410770f47f`
- Files: 68; 33 commits; 2,333 additions and 1,127 deletions. Metadata reported mergeable at inspection time.
- Useful work: machine-readable inventory of PRs returned by its open-PR search and a fail-closed standard-library inventory validator.
- Limitations: scope is a historical open-PR search snapshot, not all historical PRs; its own body says individual diff/review/check inspection and integration remain future work.
- Preliminary disposition: **NEEDS_SCOPE_ALIGNMENT_AND_REVIEW**; compare its inventory/schema with this all-state ledger and consolidate rather than create competing sources of truth.

### PR #13176 — Buddy model route identity and allowlist gate

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/13176
- State: Open; branch `plan-model-access/route-gate-allowlist`
- Head SHA inspected: `b83e6146c15ac26c10256c5c092b30a9a0c0a250`
- Files: 36; 9 commits; 1,241 additions and 98 deletions. Metadata reported non-mergeable.
- Useful work: proposes caller identity checks on 14 model routes, plan-policy enforcement, allowlist-only model selection, owner-only discovery, paid-use approval, and UI fallback/sign-in notices with tests.
- Limitations: no provider call or deployment is claimed. The large cross-cutting route/security change requires full diff, review-thread, auth/session, endpoint-coverage, test, and rebase analysis before integration.
- Preliminary disposition: **NEEDS_REBASE_AND_SECURITY_REVIEW**; high-risk/high-value. Preserve fail-closed behavior and verify every route and caller.

### PR #15255 — Buddy Training Methods Hub

- URL: https://github.com/DreamCo-Technologies/Dreamcobots/pull/15255
- State: Open; branch `feat/buddy-training-methods-hub-20261022`
- Head SHA inspected: `271cfc24de5f2e9ee2215e736f319433ed06e21e`
- Files: `.github/workflows/buddy-training-methods-hub.yml`, `buddy/bootcamp/training_methods_hub.py`, `tests/test_buddy_training_methods_hub.py`. Metadata reported mergeable.
- Useful work: read-only catalog of RAG, prompting, SFT, LoRA/QLoRA, DPO, GRPO, distillation, continued pretraining, tokenizer/embedding/reward training and evaluation; compute/provider discovery; rights/approval gates; targeted unit tests.
- Limitations: explicitly does not claim live provider availability, account access, compute entitlement, or an executed training job; should integrate with the canonical Buddy resource registry and training manifest.
- Preliminary disposition: **REVIEW_FOR_SMALL_SAFE_INTEGRATION**; verify imports, schema overlap, targeted workflow, rights gates, and current-head tests before deciding whether to rebase or port.

## Cross-PR architecture findings

1. The Markdown/Pages audit work (#17170) and conversation traceability work (#17173) are complementary but must converge on one canonical requirements/coverage registry. Avoid competing checklists or duplicated generated data.
2. The open-PR inventory (#16600) is useful but does not cover merged and closed history; extend or replace its scope with the all-state ledger rather than presenting it as complete history.
3. Model governance work (#13176) and the newer model catalog work (#17411) must be checked together: a catalog row must not become an executable route unless identity, allowlist, approval, fallback, and exact-model verification gates are satisfied.
4. Training discovery (#15255) is a catalog/planning capability, not training execution. Connect it to dataset rights, training manifests, compute approval, run IDs, checkpoints, and independent evaluation only after those systems exist and pass tests.
5. Generated artifacts should have a single canonical generator and deterministic CI order. Validate that regeneration is reproducible and does not mask stale or unintended source changes.

## Required next review passes

For every PR, including merged and closed PRs:

- Fetch current PR metadata and record source/base/head SHAs.
- Read full description, all changed files and complete patches, commit list, issue comments, reviews, inline review comments/threads, and linked issues.
- Fetch workflow runs and job logs for the exact current head SHA; stale checks are not evidence.
- Compare changed paths and symbols against main and other PRs to identify already-integrated or duplicate work.
- Check dependency/security changes, secrets, licenses/provenance, migrations, auth boundaries, generated files, tests, docs, and production impact.
- Assign one disposition: `ALREADY_INTEGRATED`, `READY_FOR_INTEGRATION`, `NEEDS_FIXES`, `NEEDS_REBASE`, `DUPLICATE_OR_SUPERSEDED`, `BLOCKED`, `REJECTED_WITH_REASON`, or `REQUIRES_OWNER_DECISION`.
- Record exact evidence and preserve unique useful work from closed/unmerged PRs.

## Integration safety

- Use focused feature branches and traceable PRs. Never mass-merge, force-push, bypass branch protections, or push unreviewed code directly to `main`.
- Merge only after exact-head required checks pass, conflicts and blocking reviews are resolved, and security/production impact is assessed.
- Preserve source PR numbers, authorship, commits, and rationale in integration PR descriptions.
- No paid compute/API spend, production deployment, destructive migration, secret exposure, or production data changes as part of this reconciliation.
- A PR being open, mergeable, or approved does not by itself prove its code is correct or production-ready.

## Progress accounting

- PRs discovered in initial listing: **699**
- PRs fully forensic-reviewed in this initial pass: **0**
- PRs targeted for first-pass detailed follow-up: **6**
- Integration PRs created by this ledger commit: **0** (this document is a tracking artifact, not code integration)
- Full historical reconciliation: **IN PROGRESS**

Update this document incrementally with exact evidence. Never mark a PR reconciled based only on its title, description, inventory row, or old CI result.


## Daily update — 2026-11-24

**Main snapshot inspected:** `adc02c1ed95e225d33870ff696808bf95de67234`  
**Pull-request listing:** 8 non-empty API pages, 795 PR records; page 9 was empty. This is a complete metadata listing, not a complete forensic review.

| State | Count |
|---|---:|
| Open | 72 |
| Merged | 498 |
| Closed, not merged | 225 |
| Total | 795 |

The prior 2026-11-18 inventory contained 699 records. The current listing therefore adds 96 PR records. The listing is sorted by descending PR number. **Fully forensic-reviewed PRs remain 0 / 795.** Targeted triage below does not satisfy the full forensic standard (complete diff, commits, issue history, review threads, exact-head checks/logs, dependency/security/licensing, and base-branch reconciliation).

### Targeted triage updates

- **PR #18207 — freeCodeCamp Buddy Bootcamp integration:** `NEEDS_FIXES` + `NEEDS_REBASE`. Current head `197e8897ccb35263a8938bc70095f68576920e22`; base `9c1a7e109bc26bc5adc3bd4766baa547a6ac2c7c`; GitHub reports `mergeable_state=dirty`. Eleven review threads were returned; eight remain unresolved. Current-head checks include successful curriculum generation and Python analysis, but the weekly transcript audit fails closed with `approved_transcript_manifest_missing`, `transcript_count=0`, and no actual Buddy transcript evaluation. Run: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45417978166 . The run's catalog log reports 1,740 video metadata entries across 22 categories, 65 division queues, 1,950 queue items, and 6,421 specialty routes; these are metadata/routing counts, not downloaded media, completed lessons, training examples, or model learning. The five-per-division planner creates 325 daily slots, not 325 authored/verified lesson contents. Unresolved review risks include unconditional `inventory_status=complete` despite partial enumeration, position-derived resource IDs, evidence URLs not checked against the registered catalog, checking the catalog only after sync overwrites it, and the weekly transcript policy's `training_permission_is_separate=false` contradiction. Cloudflare Workers reports a build under a `production/builds` path; actual live rollout was not independently verified.
- **PR #18204 — Buddy Continuous Repair permission fallback:** draft, overlapping fix for the same `.github/workflows/buddy-continuous-repair.yml` failure. Head `aaed2ea64348e99075a70bc3f57c691a4b6db4fd`; base SHA `f5277d556d826e34719ff12d6f6a103468340cc1` (older than this main snapshot). It removes automatic PR creation, reduces permissions, and proposes a patch artifact. It has no review submissions; CodeRabbit explicitly skipped it because it is a draft. Keep as an integration candidate, not proof of closure.
- **PR #18209 — artifact-only Continuous Repair alternative:** created from current main to remove the same failing automatic PR-creation step and add a regression guard. It overlaps #18204, so it was converted to draft to prevent accidental merging of both alternatives. Current head `1ca513975d1dcc49d6922f22f686633585271efd`; only Python analysis is green on this head while the Cloudflare Workers build is in progress. A GitHub Actions generated-artifact repair commit added unrelated generated outputs; current-head checks must be rerun. **Do not merge #18204 and #18209 together; owner must choose/consolidate.**
- **PR #18210 — MDX inventory fix:** adds `*.mdx` to `tools/audit_markdown_implementation_gaps.py` and a temporary-Git-repository regression test. Current head `93fa9fcc426cd951af430d238e4a238755a56a52`. An earlier `validate` check failed because generated Markdown audit outputs were stale; the allowlisted generated-artifact workflow refreshed them, changing the PR from two code/test files to 15 total files. The current head has no completed full test suite yet. Keep open for exact-head validation; do not treat generated-artifact refresh as semantic Markdown review.
- **PR #18202 / #18198 — training data factory:** overlapping proposals. #18202 is a draft and has a CodeRabbit duplicate-`source_registry`-key finding in `tools/build_dreamco_training_factory.py`; #18198 is dirty and appears to be the older overlapping variant. Neither is verified training execution.
- **PR #18205 / #18203:** both are drafts with no submitted reviews or inline review threads; CodeRabbit says draft review was skipped. Their reported check suites (33 and 48 checks respectively) do not replace human review or exact-head forensic inspection.
- **PR #17170:** older all-Markdown/Pages audit proposal remains open and dirty. Its purpose overlaps the current Markdown audit work, but its files implement a separate checklist/dashboard system; compare and consolidate rather than blindly duplicate.

### Repository blockers and acceleration evidence

- Main run [#45413830493](https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45413830493) failed at automatic PR creation. The log shows `peter-evans/create-pull-request@v7` force-updating `bot/buddy-continuous-repair` with `--force-with-lease`, then GitHub rejecting PR creation because Actions is not permitted to create or approve PRs. PR #18204 already proposes a fix; PR #18209 is a test-enhanced overlapping alternative.
- The current static `website/` tree is 55.16 MiB across 655 files, exceeding the 52 MiB deployment policy. Largest files include `website/data/buddy-technology-radar.json` (9.11 MiB), `website/data/dreamco-search-index.js` (3.32 MiB), `website/data/bot-fleet-catalog.json` (3.13 MiB), `website/data/command-center/capabilities.json` (2.38 MiB), and `website/data/bot-calculators.json` (2.32 MiB). The cost-policy failure is a real merge/deployment blocker; preserve content and investigate deterministic sharding/lazy loading rather than deleting features.
- The GitHub Pages workflow builds and uploads the site, and its deploy job is gated to `main`; no current successful Pages deployment or live-site health was independently verified in this run. Cloudflare Workers PR build notifications are separate and must not be conflated with GitHub Pages.
- Latest 100 main-branch workflow runs: 11 success, 88 skipped, 1 failure (#45413830493). Skipped runs are not failures; this sample is not an all-history health claim.

### Next deterministic review batch

Continue full forensic review from the newest unreviewed PRs, prioritizing #18207, #18204, #18202, #18198, #18205, #18203, #18209, and #18210. Record complete patches, commits, issues, all review threads, exact-head logs, and branch/base comparison before assigning a final disposition. No PR was merged by this pass.
