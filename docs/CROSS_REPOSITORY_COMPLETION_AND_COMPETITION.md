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

## Fair compute and anti-cheating protocol

No candidate gets extra resources or more favorable conditions. Every comparison is assigned an immutable run manifest and an equal budget per candidate: wall-clock time, accelerator-active time where measurable, CPU allocation, memory cap, power/energy budget where measurable, warm-up, concurrency, and maximum attempts. The same laptop is one comparison cohort; GitHub runners are a separate cohort. A laptop result must not be directly ranked against a hosted GitHub runner unless hardware and environment equivalence is demonstrated.

Freeze test cases, prompts, scoring, model/tokenizer revisions, context limits, permissions, dataset splits, and benchmark version before execution. Rotate candidate order to reduce cache and thermal bias. Record every attempt, failure, retry, cancellation, environment, cache state, resource measurement, and score. Infrastructure retries must be symmetric; preserve failed attempts. Candidate-specific optimizations must be disclosed and reported as a separate track. Never discard an inconvenient failure or give one runtime a private test-time advantage.

## Division data ownership and controlled sharing

Default to isolated division-owned datasets, database namespaces, access policies, splits, checkpoints, and audit records. Divisions may use a shared, centrally governed corpus only through immutable, versioned manifests after rights, privacy, purpose, retention, and scope approval. Each division receives a separately authorized derived view with source and transformation provenance.

Use four explicit data classes: shared public/licensed corpus, approved sanitized common curriculum, division-private training data, and evaluation-only holdout. Private holdouts never enter training. A division cannot read another division's private raw data or train on it unless the owner has approved compatible rights and purpose. Every dataset version records source/license, rights approval, privacy review, purpose, expiry/revocation, content and split hashes, division access manifest, and transformation provenance. Shared learning should favor approved lessons, synthetic/sanitized examples, and capability metadata rather than copying private raw records across divisions.

## Buddy's model and data access

Buddy uses one canonical, provenance-backed catalog to discover the best eligible model and data source for each task. Model records must include immutable model/revision, provider, capability and modality support, context/tool support, license and output-use rights, data-classification ceiling, region/retention, availability/rate limits, latency/throughput/memory/cost, quality/safety/reliability scores, benchmark provenance, and safe fallbacks.

Routing is a two-stage decision: first enforce hard eligibility (capability, permissions, privacy classification, licensing, safety, region, budget, and availability); then rank eligible candidates using fresh, comparable task-specific benchmark evidence. Missing or stale evidence means unverified, not best. Data selection follows the same rights and privacy gates and returns the best approved dataset/knowledge source for the task, with division boundaries preserved.

## Daily evaluation after readiness

Daily competitive testing starts only after Buddy's end-to-end task execution is verified, Bootcamp coverage and resources are audited, approved model artifacts exist, and benchmark runners are operational. Daily suites include routing accuracy, policy compliance, task quality/completion, p50/p95 latency, throughput, CPU/GPU utilization, accelerator-active time, peak memory, energy/power when measurable, cost, reliability/retries/timeouts/cancellation, safety, privacy leakage, retrieval grounding/provenance, tool-call correctness/recovery, regression, and reproducibility. Also rerun on material model, tokenizer, provider-policy, runtime, dataset, or benchmark changes. Daily results are monitoring evidence, not automatic production promotion.

## Safe Python-to-Swift validation bridge

The Python repository may define a narrow bridge for non-mutating checks against the preserved Swift repository: schema validation, static analysis, fixture-based unit tests, dependency/license inventory, secret scanning, read-only health checks, and shared-contract conformance. It must not run production deployments, paid inference, real training, database writes/migrations, credential changes, publishing, or access private datasets/secrets from untrusted PRs.

A cross-repository GitHub App or dedicated least-privilege token is required to dispatch workflows. Only pinned commit SHA, run URL, contract version, and safe artifact digest may cross the boundary. The bridge is currently specified, not connected: the repository owner must configure the credential as a GitHub secret. The receiver workflow in the Swift repository remains deferred until the Python-first completion gate, except for a separately approved safe-run-only bridge.

## Training resource discovery beyond Hugging Face

Bootcamp resource coverage is not complete merely because Hugging Face categories are indexed. Maintain a source catalog and curriculum map across: core frameworks (PyTorch, TensorFlow/Keras, JAX/Flax); distributed and accelerator training (DeepSpeed, Megatron-LM, FSDP, TorchTitan, Lightning); fine-tuning and alignment (Transformers, PEFT, TRL, Axolotl, LLaMA-Factory, Unsloth); evaluation and observability (lm-evaluation-harness, HELM, Inspect, OpenCompass, EleutherAI evaluation resources); datasets and research repositories (Hugging Face Datasets, BigCode/The Stack, AllenAI, EleutherAI, Common Crawl, Wikipedia/Wikimedia, OpenML, UCI Machine Learning Repository, Kaggle, academic papers and institutional repositories); model and systems research (arXiv, Papers with Code, official framework/model documentation, benchmark leaderboards); and modality-specific resources for vision, audio, speech, video, robotics, retrieval, agents, and tool use.

Every source is only a discovery candidate until its terms, provenance, permitted use, privacy, quality, duplication, and division fit are reviewed. Record canonical URLs, dataset/model IDs, immutable revisions, license evidence, allowed use, owner, refresh cadence, and which Bootcamp lessons and divisions consume it. Never infer training permission from public availability. Include a human-reviewed taxonomy coverage report and unresolved subject-to-division mappings; do not guess an owner when a category spans multiple divisions.

## Python completion and clone gate

Do not clone/rebuild the Apple C or Swift implementations or begin their implementation phases until the Python repository meets the clone gate in config/cross-runtime-contract.json. Every goal must be on track, mastered, or explicitly blocked with an owner and next action. Required workflows must be green on the exact candidate main commit; no unresolved failing required check or unexplained cancelled/skipped run may remain. Historical failures stay visible and need a verified fix plus passing regression evidence. All PRs need reviewed dispositions, Buddy and Bootcamp gates must be verified, training and benchmark evidence must exist, and shared contracts must be frozen. An external blocker can remain only when documented and explicitly accepted; an untracked failure blocks the clone.
