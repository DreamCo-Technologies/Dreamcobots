# DreamCo Production Readiness Master Plan

## Purpose

This document is the canonical checklist for turning DreamCo/Dreamcobots into a production-grade platform. It consolidates the engineering goals identified during the current production-readiness review.

## Release rule

A capability is production-certified only when the current `main` revision has executable evidence for implementation, tests, security, observability, failure handling, and deployment/recovery where applicable. Documentation alone is not proof.

## Workstreams

1. **Buddy orchestration** — route tasks to capabilities/models/bots, enforce policy, preserve correlation IDs, handle failures and fallbacks, and prove end-to-end execution.
2. **Benchmarking** — deterministic datasets, versioned schemas, environment metadata, repeated runs, baselines, regression thresholds, and persisted receipts.
3. **Capability Genome** — canonical capability IDs, ownership, dependencies, interfaces, health, versions, tests, and routing integration.
4. **Model research** — versioned model registry, official-source provenance, adapters, capability probes, resource measurements, and safe execution boundaries.
5. **Teacher-model evaluation** — reproducible teacher baselines, student comparisons, quality floors, and promotion/rollback rules.
6. **Experiment/ablation** — isolated experiments, controlled variables, automatic matrix execution, artifact retention, statistical summaries, and reproducibility metadata.
7. **Distillation** — teacher/student contracts, dataset lineage, evaluation gates, regression protection, and rollback.
8. **Resource optimization** — free-first policy, measured VRAM/RAM/latency, quotas, timeouts, provider fallback, and cost/performance tracking.
9. **Regression/security** — unit/integration/E2E suites, dependency and secret scanning, licensing/provenance checks, input validation, authz, and release blockers.
10. **Actions control plane** — stable action IDs, authorization, UI/backend contract tests, execution receipts, status propagation, retries, and error visibility.
11. **Autonomous scanning** — scheduled scans, freshness/provenance checks, bounded repair, artifact publication, and escalation when automatic repair is unsafe.
12. **Superbot/fleet** — canonical module registry, dependency graph, conflict serialization, health checks, routing tests, and fleet accounting.
13. **Deployment** — reproducible production build, environment validation, health/readiness checks, smoke tests, rollback, and deployment evidence.
14. **Observability** — structured logs, traces, metrics, correlation IDs, agent/model/tool spans, benchmark telemetry, alerts, and retention.
15. **Cost accounting** — provider/model attribution, token/resource usage, request ledger, budget enforcement, reconciliation, and reporting.

## Debugging loop

`current main SHA -> failing check -> logs -> root cause -> minimal safe fix -> commit -> Actions -> evidence -> regression check`

Never mark an old failure as a current blocker without reproducing it on the current revision. Never mark an undocumented runtime assumption as verified.

## Completion criteria

The platform may be called production-ready only after the certification workflow reports no release-blocking failures on a stable revision and the required external/runtime integrations have passed their live smoke tests. External credentials and hardware-dependent behavior must be tested in the appropriate environment rather than simulated as green.
