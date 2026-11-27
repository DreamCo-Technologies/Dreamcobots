# Repository branch, pull-request, documentation, and Pages readiness audit

**Snapshot:** 2026-11-09  
**Repository:** `DreamCo-Technologies/Dreamcobots`  
**Default branch:** `main`  
**Main snapshot:** `8896319d73cdc138a4643c68a27bed16ae8bedf6`

## Executive findings

This is a live inventory and first-pass requirements audit, not a claim that every branch, PR, Markdown file, or runtime has passed verification.

| Area | Observed state | Assessment |
| --- | ---: | --- |
| Branches | 475 across five API pages | Inventory complete for this snapshot |
| Unique branch head commits | 369 | Many branches share commit heads |
| Branch protection flags | 0 of 475 marked protected by the branches endpoint | Detailed protection/ruleset read returned HTTP 403; effective rules are unverified |
| Open pull requests | 63 | Inventory complete for this snapshot |
| Workflow definitions | 111 | Far above the 8–12 workflow target in `CONSOLIDATION.md`; consolidation remains a goal, not current state |
| Markdown files on main snapshot | 1,622 | Per-file checklist inventory created in the audit PR |
| Markdown files on this audit branch | 1,624 after this report | The checklist registry is updated with this file |
| Pages connection index | 5,426 tracked paths in the main tree; 800,108-byte JSON artifact | Tracks repository paths and page reachability, not runtime behavior |
| Branch-health public report | Last scan 2026-09-19; 373 branches, 14 open PRs | Stale; must be regenerated from current Git state |

## Fresh full branch-health scan

The existing `branch-health-daily.yml` workflow was triggered through the approved Buddy control plane with fixed input `resolve=false`. Run: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/42549780199. It completed successfully and published a fresh report at `2026-11-09T02:16:10Z`.

- 476 total branches including `main` (475 non-default branches).
- 64 open PRs; 63 branch records were linked to an open PR.
- 414 branches classified blocked, 60 watch, and 1 healthy by the current scanner's freshness/completeness/mergeability/safety/scope heuristics.
- 28 PR conflicts reported; money/payment PRs #730 and #928 were skipped for automatic conflict work.
- The scan did not run the conflict team and did not merge PRs.

**Important limitation:** This run used the current `main` scanner, which did not check for a common merge base before counting commits. Earlier GitHub compare checks found unrelated histories for `gaming-engine` and `add-index-html`; local Git can count both entire histories and present huge ahead/behind numbers. The current 414/60/1 classifications are useful triage, not final branch certification. The audit PR changes the scanner to mark no-common-ancestor and comparison failures unavailable/blocked, and adds regression tests. A new scan must run after that repair is merged.

The branch API reported `protected=false` for all 475 branches. The detailed branch-protection endpoint returned HTTP 403 for this connection, so effective branch protection and ruleset requirements remain unverified.

## Branch comparison evidence

The repository branch list was paginated through five pages. A sample of eight distinct branch heads was compared with `main`; the results already show very old or unrelated histories:

- `dreamco/conflict-resolve/5123`: 38 commits ahead and 989 behind.
- `feat/actions-control-plane-batch-01`: 0 ahead and 989 behind.
- `agent/buddy-live-civic-realestate-education-v3`: 0 ahead and 1,754 behind.
- `agent/dream-ai-company-library-intelligence`: 184 ahead and 1,760 behind.
- `agent/fix-actions-control-center`: 1 ahead and 1,754 behind.
- `agent/github-pages-full-page-coverage`: 12 ahead and 1,754 behind.
- `gaming-engine` and `add-index-html`: GitHub compare reports no common ancestor.

**Important:** This sample is not a complete 475-branch comparison. The existing daily branch-health workflow is designed to perform the full local-Git scan, but its published report is stale. The scanner was found to convert comparison failures into zero ahead/behind and no missing files; this audit branch changes that behavior to fail closed and adds regression tests. The full scan still needs a successful fresh Actions run.

## Pull-request inventory and merge policy

There are 63 open PRs in the current API listing. At least one PR targets a feature branch rather than `main` (#17121 targets `bootcamp/hf-ollama-training-curriculum`), and multiple training PRs form a dependency chain. They must be reviewed in dependency order, not treated as one flat merge queue.

A PR is not merge-ready merely because GitHub reports `mergeable: true`. The review must include:

1. Exact base/head revisions and full changed-file list.
2. Conflict status and whether the PR is up to date with its actual base.
3. All required checks passing on the current head.
4. File-by-file review for security, authorization, data loss, generated files, and production side effects.
5. Tests for changed behavior and downstream contracts.
6. No unapproved secrets, spending, provider calls, deployment, payment changes, or destructive actions.
7. Dependency order and post-merge verification.

PR #17169 (category systems) was still draft and had multiple failing gates in the observed run, including Command Center Data Contract, Keep Green, Frontier Claim Trust Gate, Fleet runtime truth, DreamCo Core Health, Repository Test Matrix, and Parallel Benchmark Gap Builders. Its category-registry validation itself passed. It is not safe to merge on that evidence.

PR #17170 (Markdown checklist and Pages audit) was opened as a draft. Its first observed run had Command Center Data Contract, Frontier Claim Trust Gate, Keep Green, and DreamCo Core Health failures while other jobs were still running. Its latest checks must be refreshed after the scanner and checklist changes; it is not yet merge-ready.

## Documentation contradictions and stale snapshots found

- `README.md` describes 1,051 specialist profiles across 45 divisions.
- `SYSTEM_ARCHITECTURE.md` describes 875+ bots across 45 divisions.
- `docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md` explicitly says not to hardcode 45 or 65 and to read the current registry.
- `config/masterbot-65-registry.json` has 65 division entries; the placement audit and README use 45, while the legacy lineage map says 46. The 65-entry list has 20 names not present in the 45-division audit. This remains an owner-reconciliation issue.
- `docs/REPOSITORY_OWNER_GUIDE.md` uses a September 22, 2026 baseline of 3,420 tracked paths, 94 top-level HTML pages, 226 tests, and 214 tools. The current tree has 5,426 entries and 111 workflow definitions; the guide's inventory counts are stale.
- `docs/BUDDY_RESOURCE_MAP.md` records a scan date of October 5, 2026. It correctly states that a listed resource is not a live integration, but its status must be refreshed before being used as current connection evidence.
- `website/data/branch-health.json` is dated September 19, 2026 and materially undercounts current branches and PRs.
- `CONSOLIDATION.md` describes an 8–12-workflow target; 111 workflow YAML files currently exist. This does not mean all 111 are active or redundant, but it proves the target has not been reached.

## Pages monitoring and edit boundary

The repository already has a tracked-file connection index, a Pages feature audit, a branch-health page, an Actions page, Command Center data, and a governed Buddy control plane. These are useful foundations.

The Pages connection index is generated from `git ls-files` and classifies every tracked path as a page, site asset, or repository source. It explicitly does not prove runtime behavior. The existing control-plane documentation says Pages is static and read-only: it builds GitHub URLs and does not hold tokens or write directly to the repository. GitHub-signed-in editing or an approved backend/workflow is required to persist changes safely.

The new Markdown Audit page follows that boundary: checkboxes and notes can be edited locally and exported as JSON; persistent changes must be committed through GitHub. Do not place a personal access token in browser code.

## Current corrective work in this branch

- Added a per-file Markdown requirements checklist and Pages view.
- Added validation that the checklist covers every tracked Markdown file and that the Pages copy matches the canonical config file.
- Added Keep Green coverage for the Markdown audit and branch-health fail-closed behavior.
- Changed branch-health comparison errors from false zeroes to explicit unavailable/blocked evidence.
- Added a visible warning when the published branch-health report is older than 24 hours.

## Remaining gates

- Run the new Markdown audit validator and tests in GitHub Actions.
- Run the branch-health scanner across all 475 branches and publish a fresh report; confirm that compare failures remain blocked/unverified.
- Reconcile the 45/46/65 division conflict with an owner-approved source-of-truth decision.
- Read and study every Markdown file; the checklist is a tracking scaffold and all content-review statuses remain pending.
- Review all 63 open PRs file-by-file, resolve conflicts and failing checks, and merge only safe, current, dependency-ordered PRs.
- Verify actual branch protection/rulesets with an authorized GitHub permissions context.
- Refresh Command Center generated artifacts using the repository's real generator in CI; do not fabricate them by hand.
- Add explicit source/generator/validator/Pages links for every generated data family, and keep edit actions behind authenticated GitHub or backend controls.

## Evidence policy

Every completion claim must include the exact source revision and relevant test, workflow run, artifact, or production observation. A plan, Markdown description, branch name, registry entry, static page, or green unrelated workflow is not sufficient evidence.
