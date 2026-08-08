# DreamCo Notes and Documentation Organization

## Goal

Keep all useful ideas and history while preventing Markdown notes, pasted updates, generated reports, issue plans, and architecture documents from becoming competing sources of truth.

## Document classes

### 1. Canonical
Current source of truth. There should normally be one canonical document per subject.

### 2. Active plan
Approved work that is not fully verified or shipped. Active plans should link to canonical owners, acceptance criteria, benchmarks, and issues/gaps.

### 3. Implementation guide
Instructions for building, running, testing, upgrading, migrating, or operating a system. Guides must identify which canonical system they apply to.

### 4. Generated report
Evidence created by tooling. Reports should include generated/retrieved dates and should not become architecture truth automatically.

### 5. Historical note / pasted update
Old ideas, conversation exports, pasted implementation plans, experiments, and prior status snapshots. Preserve them for provenance, but builders must compare them against current code and canonical plans before acting.

### 6. Archive candidate
A file whose useful requirements are already represented in canonical plans/code and whose historical value is low. Archive candidates should be moved only after review; do not delete automatically.

## Folder policy
- `docs/` — canonical human-readable architecture, plans, guides, governance, user/developer documentation.
- `docs/archive/` — reviewed historical docs retained for provenance.
- `reports/` — generated/datestamped evidence and system reports.
- `config/` — canonical machine-readable policies/programs/contracts.
- `config/generated/` — generated machine-readable evidence; regenerate instead of hand editing.
- `tools/` — document inventory, validation, generation and reconciliation scripts.
- `attached_assets/` — raw pasted/source material; not canonical by default.
- `.agents/` — agent-operating context/memory; not product roadmap truth.

## Naming standard
Canonical docs use clear stable names such as `MASTER_PLAN.md`, `ARCHITECTURE.md`, and `SECURITY.md`.

Active plans use `PLAN_<SUBJECT>.md` only when a separate plan is genuinely needed.

Generated reports should use `<SUBJECT>_<YYYY-MM-DD>.md` where practical, or clearly state a generation date inside the file.

Historical docs preserve original names when provenance matters; add an archive header after review rather than rewriting history.

## Consolidation workflow
1. Inventory all `.md`, `.mdx`, and relevant `.txt` plan/update/note files.
2. Compute path, size, hash, headings, and likely class.
3. Group files by subject using path/title/heading similarity.
4. Compare each group against current canonical code/config.
5. Extract requirements that are still active and not already represented.
6. Merge active requirements into the canonical plan/config/issue owner.
7. Mark outdated claims as historical rather than silently deleting them.
8. Move reviewed low-value duplicates to `docs/archive/` only after owner review.
9. Never hand-edit generated reports that have a generator.
10. Re-run inventory after major planning bursts or large imports.

## Builder-bot rule
Before implementing a requirement from any note or Markdown file, builders must:
1. identify the canonical owner;
2. search existing code/config/tests/issues;
3. determine whether the requirement is already verified, partially implemented, missing, obsolete, or conflicting;
4. implement only the remaining verified gap;
5. update tests/benchmarks/evidence;
6. close the issue/gap only after verification.

## Duplicate-document rule
Two documents discussing the same subject are not automatically duplicates. They may represent history, requirements, implementation guidance, or generated evidence. Consolidate meaning first; move/archive files second.

## Truth rule
A note saying “built,” “live,” “passing,” “autonomous,” or “production-ready” is not sufficient evidence. Runtime/tests/deployment evidence controls current status.
