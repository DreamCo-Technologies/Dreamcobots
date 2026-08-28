# DreamCo Production Greenkeeper

DreamCo's Actions and pull-request review systems use a persistent evidence-first lifecycle.

## Lifecycle

1. Detect change or scheduled health check.
2. Validate workflow configuration and repository contracts.
3. Run tests and static checks available to the project.
4. Inspect security and dependency risk.
5. Run relevant benchmark/evaluation gates.
6. Check regressions against the known-good baseline.
7. Evaluate PR mergeability.
8. If mergeable, continue through required gates.
9. If unmergeable, create a clean branch from current `main` and selectively rebuild verified unique capabilities.
10. Publish artifacts and a decision report.
11. Never claim green without evidence from the actual run.

## Permanent guardrails

- Do not force-merge conflicted PRs.
- Do not automatically copy private model reasoning or protected content.
- Do not expose secrets in Actions artifacts or Pages.
- Do not spend paid compute merely because a scan exists.
- Prefer free/local resources when they satisfy the test.
- Preserve rejected approaches as evidence rather than silently deleting them.
- Treat `main` as the production source of truth.

## Green means

A subsystem is green only when its applicable checks pass. Repository-wide green is a measured state, not a label that the automation can invent.
