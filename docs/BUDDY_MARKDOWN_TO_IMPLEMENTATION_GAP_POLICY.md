# Buddy Markdown-to-Implementation Gap Policy

## Purpose

Every actionable Markdown plan, requirement, architecture note, bot specification, and operating directive must be traceable to implementation paths, tests, workflows, and evidence. Markdown is a specification or proposal; it is never proof that a feature exists.

## Living inventory

- Scan every Git-tracked Markdown file, not a fixed filename list.
- Discover referenced repository paths from Markdown links and inline code.
- Separate implementation references, test references, workflow references, configuration references, and missing paths.
- Recompute all totals from the current Git tree. No document, claim, category, or reference count is a permanent ceiling.
- Preserve older documents and historical claims; supersede them with explicit, dated decisions instead of silently deleting history.

## Gap states

- `broken_path_references`: referenced paths are missing.
- `implementation_reference_missing`: actionable requirements have no linked implementation path; manual code discovery is required.
- `test_reference_missing`: code is referenced but no test path is linked.
- `implementation_and_test_paths_referenced_not_verified`: code and test paths are linked, but execution and results remain unverified.
- `reference_only`: no actionable implementation claim was detected.

## Closure pipeline

`discover document → extract claims and references → identify missing code → deduplicate against existing systems → assign owner → implement → add tests → run CI → benchmark → regression verify → production verify`

A code reference or test filename does not promote a claim. The relevant test must run, results must be retained, and production claims require runtime evidence. Reuse or extend existing capabilities before creating another bot or subsystem.

## Generated outputs

- Policy: `config/buddy/markdown-implementation-gap-policy.json`
- Collector: `tools/audit_markdown_implementation_gaps.py`
- Current JSON: `config/generated/markdown-implementation-gap-audit.json`
- GitHub Pages data: `website/data/markdown-implementation-gap-audit.json`
- Report: `reports/MARKDOWN_IMPLEMENTATION_GAP_AUDIT.md`
- Dashboard: `website/markdown-gap-audit.html`

Run `python3 tools/audit_markdown_implementation_gaps.py --write` to refresh. Run with `--check` to detect stale generated outputs.

## Truth boundary

This audit finds references and likely gaps; it does not understand every semantic claim and does not prove that linked code satisfies the requirement. Human review and executable evidence remain mandatory.
