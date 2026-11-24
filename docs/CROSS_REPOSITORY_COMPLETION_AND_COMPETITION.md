# DreamCo three-runtime completion and competition

## Decision

Preserve all three implementations as independent candidates: the canonical Python system, the Apple C runtime, and the existing Apple Swift implementation. Complete and verify the Python system first. The C and Swift implementations are then brought into conformance with the frozen shared contracts and benchmarked against Python and each other. No language is presumed faster, safer, or better.

## Repository responsibilities

- **DreamCo-Technologies/Dreamcobots (Python):** canonical source of truth for the division registry, Buddy orchestration, task routing, model/provider policy, dataset and tokenizer lineage, training, evaluation, benchmark definitions, governance, shared schemas, conformance fixtures, and release evidence.
- **ireanjordan24/dreamcobots — C candidate:** preserve the existing `core-c/` implementation, including its CMake project, public runtime header, C source, tests, and `.github/workflows/dreamco-c-runtime.yml`. Treat the existing C branch and main-branch work as history to inspect and reconcile, not as disposable stale code.
- **ireanjordan24/dreamcobots — Swift candidate:** preserve the existing macOS app and its SwiftUI shell, including `dreamco/ContentView.swift`, `dreamco/OpenRouterService.swift`, app entry point, Xcode project, unit tests, and UI tests. Keep its provider path working while adapting its task execution/provider layer to the shared contracts.
- **Shared contracts:** versioned JSON schemas and conformance fixtures are owned by the Python repository. Both Apple candidates consume reviewed versions and run the same fixtures. The Apple repository is not an independent source of truth.

The C and Swift candidates may live in the same private Apple repository; they remain distinct implementations with separate build/test results and runtime identities. Do not move or delete the Swift application merely to make room for C.

## Completion before either Apple candidate is promoted

1. Inventory both repositories, all relevant branches, open and merged PRs, workflows, app capabilities, submodules, and unique features. Produce a source-to-destination traceability ledger; no PR or feature is discarded because it is old.
2. Reconcile existing Python PR work. Inspect divergence and conflicts before updating branches. Preserve distinct changes; do not merge merely because a PR is open or reports mergeable.
3. Resolve owner-review items and mappings; document unknowns instead of guessing.
4. Connect real PostgreSQL identities, object storage, durable queue/task runners, and monitoring. Verify actual grants, isolation, encryption, backup, and restore. A mock test is not a live connection.
5. Execute approved tokenizer training and weight training with pinned source revisions, licensed datasets, compute budgets, checkpoint/resume, and artifact hashes. The five-minute planner remains planning unless a real worker execution is recorded.
6. Run private holdout, safety, regression, latency, throughput, memory, and cost benchmarks. Training output remains pending review until all required gates pass.
7. Release-gate the Python implementation and freeze versioned shared contracts before either Apple candidate is declared compatible or promoted.

## Apple C candidate

Use C for the portable runtime core and stable ABI. Preserve the SwiftUI app as the native application shell. Keep provider SDKs and model-specific backends behind adapters. Use Metal/MLX or another supported Apple Silicon backend only through a measured, maintainable adapter; C itself does not magically provide Metal acceleration.

Required C subsystems include task protocol, model/provider capability registry, policy and eligibility checks, tokenizer adapter, inference backend interface, bounded worker queue, cancellation and deadlines, telemetry/evidence writer, checkpoint metadata validation, benchmark harness, and safe local resource governor. Training kernels may remain in the Python/MLX training stack initially; the C runtime consumes verified tokenizer/model artifacts. Port training components only where a measured requirement justifies it.

## Apple Swift candidate

Keep the existing SwiftUI/macOS app and its current provider integration functional. Separate UI presentation from task execution so the Swift candidate can consume the same task packets, provider manifests, tokenizer/model artifacts, policy decisions, and evidence schema as Python and C. Add conformance tests around the Swift provider/orchestration layer; do not count a UI-only test as proof of model inference parity. Swift can remain the app shell while its runtime adapter is independently benchmarked.

## Three-way competition and best-model-per-task routing

All three candidates receive identical task packets, model and tokenizer revisions, prompts, tool permissions, dataset splits, benchmark versions, quality/safety gates, and equivalent hardware constraints. Record hardware, OS, compiler/runtime versions, power mode, thermal state when available, and all relevant configuration. If hardware differs, report the results in separate cohorts or normalize with a documented method; do not claim a direct winner from incomparable runs.

A candidate is ineligible if it fails capability, licensing, privacy, safety, quality-floor, shared-contract conformance, or reproducibility gates. Rank eligible candidates using measured quality, reliability, safety, latency, throughput, memory, and cost. Maintain per-task leaderboards, confidence intervals where appropriate, fallback routes, and rollback history. Buddy selects the best eligible implementation/model per task, not one global winner and not a language winner by assumption.

## Training and artifact ownership

The Python training pipeline remains authoritative for tokenizer and model training until a separate training implementation is explicitly certified. Every trained artifact must identify its base model, tokenizer, dataset manifest and rights, recipe, compute environment, checkpoint hash, and evaluation evidence. C and Swift may load approved artifacts; neither gets credit for training merely because a schedule or workflow ran.

## Chat continuity

Approved requirements, decisions, and completion status from ChatGPT conversations can be exported into repository issues/PRs and the traceability ledger. Do not commit raw private chat transcripts, secrets, credentials, or personal data. A repository cannot automatically read every ChatGPT conversation unless a supported, explicitly authorized integration is configured.

## Operational safeguards

- Keep existing GitHub Actions workflows running; do not cancel useful jobs to force a green dashboard.
- Five-minute jobs may plan, reconcile, and monitor. They must not launch unbounded GPU training.
- Use protected environments, pinned actions, least-privilege credentials, runner isolation, job timeouts, resource budgets, cancellation, and audit logs.
- A self-hosted Mac runner is used only when its registration and job execution are verified. Never expose an unrestricted host runner to untrusted pull-request code.
- Do not enable Cloudflare or weaken macOS security protections as part of this work.
- Do not rewrite history, delete stale branches, replace the Swift app, or bulk-update the submodule without inventory and compatibility evidence.

## Current state

This contract records the intended three-candidate architecture and ordering. It does not claim that all three implementations are complete, that live services are connected, that model training has run, that a Mac runner is executing jobs, or that runtime competition has occurred. A passing contract validator proves only that the specification is structurally consistent.
