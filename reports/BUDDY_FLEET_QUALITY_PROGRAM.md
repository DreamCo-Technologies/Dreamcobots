# Buddy Fleet Quality Program

This report separates repository contract evidence from live end-to-end and competitor evidence. It does not claim permanent rankings, perfection, or production readiness without deployed proof.

## Coverage

- Bot build plans: 1051
- Unique bot learning paths: 1051
- Unique competitor benchmark suites: 1051
- Capability benchmark plans: 8408
- Repository capability contracts passed: 8408
- Live competitor benchmarks completed: 0
- Live end-to-end profiles passed: 0
- Production-ready profiles evidenced: 0

## Release Pipeline

| Phase | Evidence gate |
| --- | --- |
| catalog_and_route | Profile schema, stable ID, Buddy route, and governed runtime evidence exist. |
| repository_contract | Every declared capability passes its repository-controlled fixture. |
| dependency_closure | Manifests, lockfiles, imports, licenses, runtime versions, and vulnerabilities are checked. |
| adapter_contract | Every required API has a mock, failure, timeout, retry, and secret-handling test. |
| live_end_to_end | Authenticated staging proves the full user flow without production writes. |
| competitor_baseline | Current competitors run the same approved fixtures with cost and version evidence. |
| release_candidate | Build, tests, accessibility, security, performance, and regression checks pass on a review branch. |
| owner_review | A human owner reviews scope, evidence, cost, permissions, and rollback before merge. |
| production_observation | Deployment health, errors, latency, costs, and rollback are verified after release. |

## Continuous Improvement Boundary

Buddy may prepare evidence, issues, review branches, and draft pull requests. It may not self-merge, silently change models, spend money, or perform production actions without the configured approval gate.
