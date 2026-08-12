# Buddy Benchmarks 201–250

These targets cover human collaboration, communication, teaching, preference handling, delegation, multi-agent coordination, and safe human takeover.

## Evaluation principle

A benchmark target is not a mastery claim. The system must capture reproducible baseline evidence, execute under documented conditions, diagnose failures, apply only a bounded review/sandbox repair, run targeted tests, rerun the benchmark, retest dependent suites, and preserve rollback/fallback evidence.

## Independence states

- `assisted`: another approved model or external capability completes material work.
- `learning`: Buddy is being improved and has not yet demonstrated independent acceptance.
- `independent`: Buddy completes the defined task without teacher-model completion for the evaluated task.
- `mastered`: repeated accepted benchmark evidence plus required regression protection.
- `blocked`: required fixture, permission, environment, or dependency is unavailable; this is never a pass.

## Parallelization

Independent targets may execute concurrently. Shared-state writes, conflicting environment mutations, and dependency-sensitive repairs must be serialized. A shared repair should fan out into dependent-suite retesting only after the repair itself passes targeted verification.

## Public evidence

GitHub Pages may display target status, benchmark scores, trends, independence state, evidence references, and blockers. Secrets, credentials, private user data, and sensitive raw logs remain excluded.
