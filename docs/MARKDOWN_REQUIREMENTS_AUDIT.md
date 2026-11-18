# Markdown requirements audit

This checklist inventory covers **1622 tracked Markdown files** found on `main` at source tree `8896319d73cdc138a4643c68a27bed16ae8bedf6` (2026-11-09). It includes every Markdown path in the repository tree, not just the `docs/` folder.

## Per-file checklist

Every entry in [`config/markdown-requirements-audit.json`](../config/markdown-requirements-audit.json) has its own eight-point checklist. The GitHub Pages view is [Markdown Requirements Audit](https://dreamco-technologies.github.io/Dreamcobots/markdown-audit.html).

| Check | What must be proven |
| --- | --- |
| Read and studied | The complete file was read, including code blocks, tables, links, and appendices. |
| Requirements extracted | Purpose, intended behavior, constraints, and acceptance criteria are explicit. |
| Implementation traced | Each factual capability claim is mapped to the actual source/configuration. |
| Tests verified | Relevant test cases and actual GitHub Actions results are inspected. |
| Pages verified | Relevant data is visible on Pages and controls behave as claimed. |
| Links verified | Internal and external references resolve and remain relevant. |
| Conflicts resolved | Stale, duplicate, or contradictory claims are documented and reconciled. |
| Owner reviewed | Reviewer, date, evidence links, and remaining risks are recorded. |

## Current status

The initial inventory is complete, but the content review is intentionally **not started** for every file until it has actually been read and traced. A file being present, linked, or listed is not a completed review. Do not promote an item to completed without evidence.

## Editing and persistence

The Pages checklist supports filtering, local checkbox updates, notes, and exporting the updated JSON. Exported changes must be committed through GitHub (or an approved authenticated backend) to persist. No GitHub token is embedded in the static site.

## Audit rules

- Preserve historical Markdown and record conflicts instead of deleting inconvenient claims.
- Separate planned, catalogued, implemented, tested, deployed, and production-verified states.
- For code or feature claims, record exact source paths and relevant CI run links.
- Rebuild the inventory whenever Markdown files are added, renamed, or removed.
