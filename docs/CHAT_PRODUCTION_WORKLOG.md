# DreamCo Production Hardening Worklog

This file records the engineering direction approved during the production-readiness conversation. It is intentionally a worklog/checklist, not a claim that every item is already complete.

## Approved goals

- Make the entire DreamCo/Dreamcobots repository production ready.
- Debug GitHub Actions failures using the current `main` revision as the source of truth.
- Strengthen Buddy orchestration/router and end-to-end validation.
- Validate benchmark reproducibility and expand coverage.
- Integrate and test the Capability Genome.
- Validate the large-model research/registry system with real execution evidence.
- Run teacher-model benchmarks at meaningful scale.
- Productionize experiment, ablation, and distillation pipelines.
- Enforce free-first resource selection with measured resource/cost behavior.
- Measure and regression-test VRAM/RAM/latency behavior.
- Expand regression, security, licensing, and dependency checks.
- Verify Actions page/control-plane behavior end to end.
- Ensure daily autonomous scans publish actionable evidence to the control plane.
- Validate AI-source ingestion freshness and provenance.
- Integrate and test Superbot/module routing.
- Harden deployment, health checks, rollback, and observability.
- Implement measured cost accounting and provider/model attribution.

## Engineering policy

- Do not call architecture production-ready without executable evidence.
- Do not treat historical GitHub failures as current failures without reproducing them.
- Do not bypass security or authorization checks to make CI green.
- Automatic repair must remain bounded and auditable.
- Hardware- or credential-dependent capabilities require tests in the appropriate environment.
- Every production claim should be traceable to a commit, test, artifact, or runtime receipt.

## Current implementation anchor

Production-readiness contract: `config/production-readiness-contract.json`

Evidence gate: `tools/production_readiness_gate.py`

Production readiness workflow: `.github/workflows/production-readiness.yml`

Master plan: `docs/PRODUCTION_READINESS_MASTER_PLAN.md`
