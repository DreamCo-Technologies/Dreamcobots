# DreamCo Automation Consolidation

## Goal

Reduce overlapping GitHub Actions schedules and keep DreamCo's many logical bots behind shared orchestration. The target is approximately 8–12 durable workflows rather than dozens of overlapping scheduled jobs.

## Target workflow groups

1. **DreamCo Core Health** — typecheck, focused regression tests, build, fleet contracts, dependency audit, and basic repository health.
2. **Actions Health & Failure Sweep** — static/live workflow health and failure reporting.
3. **Repository System Watch** — generated contracts, inventory, and repository map validation.
4. **Full System Certification** — manual + nightly end-to-end certification.
5. **Buddy Verification Suite** — Buddy contracts, routing, fleet, and success-program validation.
6. **Security** — CodeQL and dependency review.
7. **Deploy Buddy Pages** — website/pages deployment.
8. **Problem Registry** — lightweight evidence and issue tracking.
9. **Benchmarks** — scheduled benchmark/model evidence generation.
10. **Revenue & Entitlements** — pricing, checkout configuration, plan access, and webhook smoke tests.

## Consolidation rules

- Prefer one canonical generator or validator per artifact.
- Generated files must not be hand-maintained when a source generator exists.
- Scheduled workflows should be consolidated before adding another scheduled workflow for the same concern.
- Heavy benchmark/certification work must not run on every pull request.
- Logical bots are configuration/specialization; shared execution belongs in Buddy/fleet services.
- External side effects require explicit approval and must be represented as governed tasks.
- A failed generator should report the failure without causing unrelated generators to race or cascade.

## Current first step

`dreamco-core-health.yml` provides a single CI contract for the most important source changes. It runs on pull requests, pushes to `main`, manual dispatch, and a daily health schedule.

Existing workflows should be retired or converted to manual-only execution **after** their functionality is verified as covered by a consolidated workflow. Do not delete workflow definitions merely to make the count smaller; preserve historical behavior until replacement coverage is proven.

## Fleet model

DreamCo can maintain hundreds or thousands of logical specialist profiles without launching one heavyweight process per profile. Buddy should select the required specialists, place work into a queue, and activate a bounded worker pool. The initial production target is approximately 20–50 active services/processes, with horizontal/vertical scaling available later.

## Production inference

Large-model inference remains API-based through OpenRouter and existing DreamCo model providers. The VPS is an orchestration and application-compute layer, not a large-model inference host.
