# Three-month open PR merge audit — 2026-11-06

Scope: open PRs returned by GitHub search `is:open created:>=2026-08-06`. Search returned **57** PRs. Search results are not proof that every PR was individually reviewed. This report covers the first four PRs whose Actions were inspected.

| PR | Changed files | Observed failed workflow(s) | Decision |
| --- | ---: | --- | --- |
| #15342 | 1 | Keep Green | HOLD: inspect failing job and whether baseline failure |
| #15406 | 4 | Frontier Claim Trust Gate; Fleet runtime truth | HOLD: do not disable fail-closed claims gate |
| #15487 | 4 | Fleet runtime truth | HOLD: verify read-only behavior and fleet baseline |
| #16559 | 1 | Keep Green; Dependabot auto-merge | HOLD: validate dependency compatibility and failing jobs |

PR #15406's Frontier Claim Trust Gate failed specifically at **Strict require-all-gates (hard-fail until claimable)**; its vanity-copy check and unit tests passed. This appears intentionally fail-closed. Never make that gate green by weakening production evidence requirements.

PR #16600 is a draft integration PR; it must not be merged until its own tests, code review, security review and required checks pass. PR #16757 is another open feature PR and needs overlap/conflict review before integrating.

## Merge criteria
1. Verify current head SHA and exact changed files, not title-only triage.
2. Inspect every failed required check and determine whether the failure is PR-introduced, baseline, environmental or intentionally fail-closed.
3. Never bypass branch protection, security checks, training-data rights, billing limits or exact-action approvals.
4. Test the combined result and Pages paths, not only individual PRs.
5. Merge only independently safe and reviewed changes using expected-head-SHA protection.
6. Record each merge SHA or explicit hold reason; never report a draft or mergeable PR as merged.

**Current audit outcome:** No PR is certified merge-ready by this limited review. No merges performed.
