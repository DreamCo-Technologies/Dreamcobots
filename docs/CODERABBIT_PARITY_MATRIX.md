# DreamCo PR Review vs CodeRabbit Parity Matrix

DreamCo uses CodeRabbit as an external benchmark, not as a dependency or claim of equivalence. The goal is to make every important review capability measurable and continuously improve DreamCo against the same classes of work.

## Reference capabilities

CodeRabbit publicly documents automated PR review, bug detection, refactor suggestions, summaries, security/quality analysis, repository context, code-graph analysis, incremental reviews, issue/acceptance-criteria context, interactive conversations, IDE/CLI reviews, agent handoff, triage/prioritization, pre-merge checks, post-merge actions, and configurable review behavior. See the official documentation for the current feature set.

## DreamCo parity targets

| Capability | DreamCo target | Evidence required |
|---|---|---|
| Automatic PR review | Required | PR-triggered Guardian run |
| Incremental review | Required | synchronize-event delta evidence |
| Bug/logic detection | Required | finding + reproducible test/evidence |
| Security review | Required | security scanner + contextual review |
| Dependency review | Required | dependency graph + vulnerability evidence |
| Performance review | Required | benchmark/profile evidence where applicable |
| Maintainability/refactor review | Required | actionable finding + rationale |
| Repository-wide context | Required | capability/dependency graph |
| Code graph / blast radius | Required | affected-node map |
| Issue/requirements alignment | Required | PR ↔ issue/acceptance-criteria evidence |
| PR summary / walkthrough | Required | generated review artifact |
| Inline findings | Required | line/path anchored findings |
| Severity classification | Required | severity taxonomy + confidence |
| Triage/prioritization | Required | risk/reward/effort/complexity score |
| Reviewer routing | Required | capability-based reviewer selection |
| Conversational review | Required | review-thread interaction contract |
| Suggested fixes | Required | patch proposal + validation |
| One-click/automated fixes | Target | isolated patch branch + gates |
| Agent handoff | Required | structured context package |
| Review learning | Required | feedback → policy/benchmark evidence |
| Pre-merge checks | Required | production gate |
| Post-merge verification | Required | deployment/regression evidence |
| Stale-risk monitoring | Required | scheduled review sweep |
| Conflict recovery | DreamCo extension | clean-branch rebuild workflow |
| Benchmark validation | DreamCo extension | capability benchmark + regression |
| Multi-model ensemble review | DreamCo extension | independent reviewer evidence |
| Free/local reviewer route | DreamCo extension | cost/resource evidence |
| 500-model comparison | DreamCo extension | normalized model benchmark ledger |
| Capability-gap closure | DreamCo extension | gap worker + retest evidence |
| Evidence ledger/mastery | DreamCo extension | immutable run/result references |

## Review decision contract

Every PR should end in one of:

- `merge-ready`
- `merge-after-fixes`
- `needs-human-review`
- `needs-benchmark`
- `needs-security-review`
- `needs-dependency-review`
- `conflicted-rebuild`
- `duplicate-or-obsolete`
- `blocked`
- `unknown`

`unknown` is never treated as pass.

## DreamCo's comparison score

For each PR, the review engine should record:

1. defect detection recall/precision on seeded known issues
2. security finding coverage
3. dependency finding coverage
4. test-gap detection
5. architecture/blast-radius accuracy
6. issue/acceptance-criteria alignment
7. false-positive rate
8. actionable-fix acceptance rate
9. regression prevention rate
10. review latency
11. compute/time cost
12. reviewer agreement
13. mergeability prediction accuracy
14. conflict-rebuild success rate
15. post-merge incident/regression rate

The score must be benchmark evidence, not marketing. DreamCo should be allowed to lose a comparison when the measured result says it lost.

## Continuous comparison loop

`PR → DreamCo review → reference review (when available) → independent tests → compare findings → classify disagreements → human adjudication → regression case → update reviewer policy → retest`

The system should compare categories and evidence, not copy proprietary prompts, private reasoning, or protected implementation details from another product.
