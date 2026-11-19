# DreamCo Rotating Operations, AI/ML Lifecycle and User Training

## Operating contract

DreamCo's five-minute Actions scheduler performs a deterministic rotation. Every tick inventories **all tracked Markdown and MDX specifications** by path, byte count and SHA-256 digest, then executes one bounded workstream. The inventory is a lossless source manifest, not a claim that each requirement is implemented. A separate requirement-to-code/test/evidence audit must determine implementation status.

The scheduler rotates through 12 workstreams. Each lane receives one scheduled slot every hour under a five-minute cadence. GitHub-hosted schedules are best-effort and may be delayed; they are not real-time timers. A run is considered complete only when its command evidence is uploaded and its failures remain visible.

## Rotating workstreams

1. Specifications and master goals
2. Buddy OS and Dream Brain learning architecture
3. Model catalog, routing and benchmark integrity
4. Training queues, datasets and distillation governance
5. User bootcamp, learning paths and model-lab education
6. Divisions, bot fleet, profiles and capability contracts
7. Repository tests and regression registration
8. Provider integrations and connection graph
9. Security, privacy, approvals and release safeguards
10. Command center and operational telemetry
11. Performance, cost and reliability
12. Release readiness and evidence reconciliation

The scheduler computes its lane from the UTC five-minute slot, so a retry in the same slot repeats the same lane and the next slot advances. Failed lanes are not silently marked complete. The uploaded artifact records the exact commit, Markdown inventory, selected lane, commands, outputs and failure statuses.

## AI and machine-learning engineering practices

### Data and dataset lifecycle
- Record dataset owner, provenance, license, permitted use, collection date, schema, version, and cryptographic digest.
- Separate training, validation, and held-out test data; detect duplicates and contamination across splits.
- Minimize personal data, redact secrets, enforce retention limits, and keep tenant datasets isolated.
- Track quality, coverage, representativeness, label agreement, missingness, and known limitations.
- Never convert private user content into shared training data without explicit, scoped authorization.

### Model and experiment lifecycle
- Register provider, model, immutable version, adapter, configuration, prompt/template version, dataset version, benchmark suite, commit, run ID, and environment.
- Establish a reproducible baseline before changing model weights, prompts, retrieval, tools, or routing.
- Compare candidates on identical fixtures and rubrics; report accuracy, task completion, safety, robustness, latency, tokens, memory, compute, cost, and failure rate.
- Use held-out evaluation, repeated trials, confidence intervals where appropriate, ablations, and regression suites.
- Track model drift, data drift, calibration, hallucination/error classes, refusal behavior, and subgroup performance where lawful and meaningful.
- Preserve failed runs and negative results. Never infer a benchmark pass from catalog presence or a successful build.

### Training, fine-tuning and distillation
- Prefer the Free-First Learning Policy: verified existing capability, cached/local work, open-source/local models, free quotas, smallest viable paid experiment, then larger compute only with explicit approval.
- Use supervised fine-tuning, preference optimization, RL/RLVR, retrieval augmentation, tool-use training, quantization, and distillation only when the task, data rights, compute budget, and evaluation design justify them.
- Keep a frozen baseline and compare the candidate against it on held-out tests before and after training.
- Record hyperparameters, seeds, training code commit, data manifests, hardware, GPU-hours, energy/cost estimates, checkpoints, and evaluation outputs.
- Apply early stopping, resource ceilings, rollback, safety testing, and catastrophic-forgetting checks.
- Do not train on hidden chain-of-thought or attempt to extract it. Evaluate observable outputs, task success, and verifiable intermediate artifacts.
- A scheduled inventory or training-queue preview is not model training. Actual training is a separate resource-consuming job and must have explicit budget, data, adapter, and approval gates.

### Model promotion and operations
- Keep model versions immutable and route via a registry with capability, context limits, latency/cost profiles, safety results, and fallback behavior.
- Promote only after independent evaluation, privacy/security review, regression tests, canary observation, and a documented rollback path.
- Separate sandbox, staging and production credentials/environments. Never expose secrets in Actions logs or artifacts.
- Use least-privilege GitHub permissions, pinned action versions where feasible, dependency scanning, SBOM/provenance, secret scanning, and protected environments.
- Require human approval for paid services, external side effects, production deploys, destructive operations, and model promotion.

## User model-training and AI education

DreamCo's user-facing learning path should progressively teach:
1. AI foundations, tokens, context windows, embeddings, inference and model families.
2. Prompt design, structured outputs, tool use, retrieval and evaluation.
3. Dataset sourcing, licensing, cleaning, labeling, train/validation/test splits and privacy.
4. Model comparison, experiment tracking, baselines, metrics and error analysis.
5. Fine-tuning concepts, supervised training, preference optimization and RL/RLVR.
6. Distillation, quantization, inference optimization and resource budgeting.
7. Deployment, monitoring, drift detection, incident response and rollback.

Provide guided labs, sample datasets with clear licenses, reproducible notebooks, quizzes, rubrics, sandbox exercises and project milestones. Use isolated per-user workspaces and never mix a user's private model, dataset, credentials or results into another tenant's workspace. Label lessons as educational, simulated, sandbox-verified or production-verified—never conflate them.

## Truthful completion states

Use distinct evidence states: documented, catalogued, implemented, unit-tested, integration-tested, sandbox-executed, runtime-route-verified, benchmark-verified, security-reviewed, canary-observed and production-verified. A higher state requires its own evidence. Missing routes, stale tests, unknown owners, unlicensed data, unavailable adapters and unverified model runs remain visible blockers.

## Operational limits

- GitHub cron is best-effort; five minutes is a target cadence, not a hard real-time guarantee.
- Twelve lanes mean each lane is scheduled once per hour while the complete Markdown inventory is refreshed every tick.
- The rotating workflow is read-only with respect to repository contents and does not deploy, spend money, invoke paid inference, train weights, or auto-promote models.
- Heavy or long-running experiments belong in separately approved workflows with budgets and isolated runners.
