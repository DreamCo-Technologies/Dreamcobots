# DreamCo cross-repository completion and runtime competition

## Decision

Complete and verify the existing Python DreamCo system first. Only after the Python work is reconciled, connected to real services, trained, benchmarked, and release-gated should the Apple implementation be rebuilt in C. The two implementations then compete; neither is presumed faster or better.

## Repository responsibilities

- **DreamCo-Technologies/Dreamcobots (Python):** canonical source of truth for the 65-division registry, Buddy orchestration, task routing, model/provider policy, dataset and tokenizer lineage, training, evaluation, benchmark definitions, governance, and release evidence.
- **ireanjordan24/dreamcobots (Apple app):** native macOS user interface and, after the completion gate, the C runtime implementation for Apple Silicon. Preserve existing SwiftUI functionality while introducing C behind stable interfaces. Do not replace the app or its working OpenRouter path during the port.
- **Shared contracts:** versioned JSON schemas and conformance fixtures are owned by the main repository. The Apple repository pins a reviewed contract release/commit and runs the same fixtures.

## Completion before the C rebuild

1. Inventory both repositories, every relevant branch, all open and merged PRs, workflows, app capabilities, submodules, and unique features. Produce a source-to-destination traceability ledger; no PR or feature is discarded because it is old or inconvenient.
2. Reconcile existing Python PR work. Rebase/update only after inspecting divergence and conflicts. Preserve all distinct changes; do not merge merely because a PR is open or reports mergeable.
3. Resolve owner-review items and mappings; document unknowns instead of guessing.
4. Connect real PostgreSQL identities, object storage, durable queue/task runners, and monitoring. Verify actual grants, isolation, encryption, backup and restore. A mock test is not a live connection.
5. Enable approved tokenizer training and weight training with pinned source revisions, licensed datasets, compute budgets, checkpoint/resume, and artifact hashes. The five-minute planner remains planning unless a real worker execution is recorded.
6. Run private holdout, safety, regression, latency, throughput, memory, and cost benchmarks. Training output remains pending review until all required gates pass.
7. Release-gate the Python implementation and freeze shared contracts.

## Apple C implementation after the completion gate

Use C for the portable runtime core and stable ABI. Keep Swift/SwiftUI as the native application shell and use Metal/MLX or another supported Apple Silicon backend only through a measured, maintainable adapter; C itself does not magically provide Metal acceleration. Keep provider SDKs and model-specific backends behind adapters.

Required C subsystems: task protocol, model/provider capability registry, policy and eligibility checks, tokenizer adapter, inference backend interface, bounded worker queue, cancellation and deadlines, telemetry/evidence writer, checkpoint metadata validation, benchmark harness, and safe local resource governor. Training kernels may remain in the Python/MLX training stack initially; the C runtime consumes verified tokenizer/model artifacts. Port training components only where a measured requirement justifies it.

## Model competition and best-model-per-task routing

Both runtimes receive identical task packets, model revisions, prompts, tool permissions, datasets, benchmark versions, and hardware constraints. A candidate is ineligible if it fails capability, licensing, privacy, safety, quality-floor, or reproducibility gates. Rank eligible candidates using measured quality, reliability, safety, latency, throughput, memory, and cost. Maintain per-task leaderboards, confidence intervals where appropriate, fallback routes, and rollback history. Never choose solely on speed or provider marketing claims.

## Chat continuity

Approved requirements, decisions, and completion status from ChatGPT conversations can be exported into repository issues/PRs and the traceability ledger. Do not commit raw private chat transcripts, secrets, credentials, or personal data. A repository cannot automatically read every ChatGPT conversation unless a supported, explicitly authorized integration is configured.

## Operational safeguards

- Keep existing GitHub Actions workflows running; do not cancel useful jobs to force a green dashboard.
- Five-minute jobs may plan, reconcile, and monitor. They must not launch unbounded GPU training.
- Use protected environments, pinned actions, least-privilege credentials, runner isolation, job timeouts, resource budgets, cancellation, and audit logs.
- A self-hosted Mac runner is enabled only after the device is connected and explicitly configured. Never expose an unrestricted host runner to untrusted pull-request code.
- Do not enable Cloudflare or weaken macOS security protections as part of this work.

## Current state

This document and `config/cross-runtime-contract.json` establish the intended contract and completion order. They do not claim that repository reconciliation, live service connections, model training, Mac access, C implementation, or runtime competition has already happened. The contract validator checks structure only.
