# DreamCo Global Reconciliation System

## Purpose
Create one evidence-backed view across every repository Markdown/MDX source, approved DreamCo conversation export, and GitHub pull request. Convert requirements into durable, deduplicated work records linked across:

`Source → Checklist → Requirement ID → Workstream → Issue → PR → Code → Test → Runtime Evidence → Benchmark Evidence → Status`

## Components
- `tools/dreamco_global_reconciliation.py`: inventories tracked Markdown/MDX, approved chat exports, and all PR states via paginated GitHub API.
- `governance/dreamco-chat-sources/`: explicit intake for approved ChatGPT exports.
- `governance/dreamco-requirement-evidence.json`: curated evidence map. Empty means unmapped, not complete.
- `artifacts/dreamco-reconciliation/`: generated inventories and summary.
- `.github/workflows/dreamco-global-reconciliation.yml`: scheduled and change-triggered inventory.

## PR review and merge policy
Every PR must be evaluated against current base and head refs. Capture changed paths, merge base, overlapping upstream paths, conflict state, changed workflows, tests, security impact, Pages impact, and deployment impact. Use three-way Git merge/rebase in a real checkout; never simulate conflict resolution by replacing files from one side. Re-run required checks on the reconciled head. Merge only when GitHub reports mergeable, required checks pass, reviews/branch protections are satisfied, and production/deployment boundaries are verified. Never force-push or auto-merge a PR merely because it is old or approved in a chat.

The first release inventories PR metadata. Full patch-level reconciliation and automated repair must run in a checked-out runner and produce an inspectable patch/PR for human review.

## Markdown and requirement policy
Inventory every tracked `.md` and `.mdx` file. Extract actionable checklist/list items with stable IDs. Preserve source path, line, section, and exact source text. Curate mappings to implementation, tests, runtime route, benchmark, and evidence artifact. A file existing is not proof that a capability works.

## Conversation policy
ChatGPT does not expose all private project chats to a repository workflow. Only explicitly exported/approved conversation files are ingested. Keep source identity and provenance. Deduplicate requirements without deleting original source statements. Preserve approvals, constraints, decisions, code snippets, issue/PR references, blockers, and unresolved questions.

## Evidence states
`SOURCE_ONLY → REQUIREMENT_CAPTURED → MAPPED → IMPLEMENTED → TESTED → RUNTIME_VERIFIED → BENCHMARK_VERIFIED`; use `BLOCKED`, `REGRESSED`, and `SUPERSEDED` with explicit reasons. Do not infer later states from earlier ones.

## Cadence
- On PR and Markdown/chat source changes: inventory and validate.
- Daily: full repository/PR inventory.
- Weekly: deeper cross-source deduplication and evidence-map review.
- Before merge: fresh branch comparison, three-way conflict check, focused tests, full required suite, deployment preflight.
- Five-minute MasterBot rotation remains separate; it must not create a noisy full-repository PR scan every five minutes.

## Safety
Read-only inventory by default. No force pushes, destructive cleanup, secret handling, production writes, merges, or deployments in this workflow. Repair suggestions and candidate patches must be reviewable. High-impact actions require explicit human approval and repository protections.
