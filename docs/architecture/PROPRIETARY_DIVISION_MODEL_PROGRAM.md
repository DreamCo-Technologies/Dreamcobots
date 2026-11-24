# DreamCo Proprietary Division Model Program

Status: architecture and implementation plan; NOT a claim that models have already been trained.
Owner: DreamCo Technologies
Baseline: 65 MasterBot/division profiles currently discovered by the fleet builder. The live registry remains the source of truth; never hard-code this count as permanent.

## Product requirement

Every active division must have a DreamCo-owned, independently versioned specialist model artifact. A division model is not merely a prompt, API alias, routing rule, or third-party hosted endpoint. Its release bundle must include trainable/owned weights (or an explicitly documented adapter plus its exact base), tokenizer/configuration, training recipe, dataset manifest, evaluation results, model card, license/rights manifest, and a reproducible inference package.

"Owned" means DreamCo controls the original training outputs, checkpoints, release process, and license for the original DreamCo-authored contributions. When a model is derived from a third-party base, upstream copyright, license, attribution, use restrictions, and redistribution conditions continue to apply. DreamCo must not claim exclusive ownership of upstream weights or data.

## Model-factory pattern for every division

1. Discover the division's canonical ID, name, remit, source taxonomy, existing bots, skills, datasets, tests, and runtime route from the canonical registry. Do not create duplicate divisions for aliases.
2. Create a division model record: `dreamco.<division_slug>.<family>`, semantic version, owner, lifecycle state, intended use, prohibited use, languages/modalities, and dependencies.
3. Build a lawful corpus from licensed, public-domain, permissively licensed, internally authored, or explicitly permissioned data. Record source URL/ID, creator, license/version, retrieval date, allowed use, attribution, redistribution status, PII/sensitive-data screening, and deduplication fingerprint. Exclude data whose terms do not authorize the intended training and commercial deployment.
4. Start with a small permissively licensed base model where its exact version and license permit the intended use. Evaluate a compact model (for example, 0.5B–3B class where hardware and quality allow); use LoRA/QLoRA adapters initially to control cost. Distill from approved teacher outputs only when teacher terms and output/data rights permit it. Train from random initialization only when a measured requirement justifies the compute.
5. Fine-tune on division-specific data and tasks. Keep general capabilities through a balanced replay set and regression suite. Keep adapters, checkpoints, optimizer/config, seeds, and dataset manifests versioned.
6. Evaluate against held-out division tasks, general capability, factuality, calibration, safety, privacy leakage, prompt injection, bias, latency, memory, and cost. Compare with the previous release and a small-model baseline. No release on aggregate score alone: require all critical safety and rights gates.
7. Package an independent inference artifact and endpoint with resource limits, authentication, rate limits, telemetry, rollback, and model/version routing.
8. Promote only after reproducibility, benchmark, safety, license, and human approval gates pass. Failed or uncertain candidates remain sandbox-only.
9. Feed verified failures and reviewed corrections into a curated training queue; never automatically train on secrets, private user content, unreviewed generated data, or raw production logs.

## Hugging Face and learning sources

Use Hugging Face Hub, Datasets, Transformers, PEFT, TRL, Evaluate, Safetensors, and model/dataset cards as discovery and tooling sources—not blanket permission to train. Inspect the exact model and dataset license and its full terms on every version. A Hub category/tag is a discovery taxonomy, not a complete list of all knowledge or a legal grant. Use FreeCodeCamp as curriculum/tutorial material and implementation guidance; do not assume tutorial code, scraped content, or third-party datasets are automatically training-licensed. Supplement with official documentation, university/open-course materials, standards bodies, public-domain collections, and internally authored exercises, each with provenance and rights review.

## Taxonomy coverage

Maintain a versioned taxonomy import from the live Hugging Face Hub API/tags and dataset/model metadata. Map every discovered subject/category/tag to one or more canonical DreamCo divisions. Maintain explicit coverage states: mapped, mapped-with-shared-owner, awaiting-owner, excluded-with-reason. Shared categories can route to a canonical division plus collaborating divisions; do not create one division per tag. CI must fail if any in-scope taxonomy node is unmapped, stale, or points to a nonexistent division. Reconcile the taxonomy on a scheduled cadence and store source snapshot timestamps and diffs.

Coverage domains include: language and linguistics; text/NLP; code/software; mathematics; science; physics; chemistry; biology; medicine/health information (with strict safety gates); social sciences; history; geography; law (informational only); economics/business/finance; education; arts/design; music/audio; speech; vision/images; video; robotics; geospatial; time-series; tabular/structured data; multimodal; reasoning/planning; cybersecurity (defensive); and domain-specific industrial/engineering fields. The live source taxonomy, not this illustrative list, determines actual coverage.

## Buddy and Buddy Bootcamp

Buddy is the central teacher/orchestrator and evaluation coordinator, not an unbounded authority. Bootcamp provides a common foundation curriculum plus a specialist curriculum for every division:
- foundations: reading comprehension, writing, math, scientific method, reasoning, source evaluation, citation/provenance, coding, data literacy, and tool use;
- professional practice: privacy, security, safety, bias, uncertainty, intellectual property, licensing, and escalation;
- division mastery: domain knowledge, task workflows, tool/API skills, case studies, and held-out practical exams;
- teaching mastery: explain concepts at multiple levels, diagnose misconceptions, build exercises, grade against rubrics, and provide evidence-based feedback.

Buddy's own model must have its own independently versioned DreamCo training artifacts and evaluation. Teacher-generated synthetic examples are labeled as synthetic, filtered, deduplicated, and checked against trusted references before use. Student models cannot be promoted solely because Buddy approves them; use independent benchmarks and human review.

## Licensing and intellectual-property policy

Maintain separate rights records for (a) base-model weights/code/tokenizer, (b) training datasets, (c) code and training recipes, (d) DreamCo-produced adapters/checkpoints, and (e) final packaged model. Never infer a license from a repository name, model card badge, or "open" label alone.

For each candidate record the exact upstream license identifier/version, source URL, required notices/attribution, restrictions, redistribution/hosting rights, commercial-use permission, derivative-work conditions, acceptable-use requirements, and legal-review status. Reject or quarantine candidates with missing, custom, research-only, non-commercial, or otherwise incompatible terms until reviewed. Check dataset terms independently of model terms.

DreamCo should issue its own license for original DreamCo model releases:
- Proprietary commercial release: DreamCo retains copyright in original DreamCo-created weights/materials and grants customers only the rights stated in a reviewed commercial license; no implied rights to upstream components.
- Community release: only for model artifacts whose complete upstream chain permits redistribution; choose an OSI-compatible license only when all included components qualify and obligations are met.
- API/service terms: separate from weight license; state usage, privacy, retention, rate limits, and prohibited uses.
The exact license text and ownership claims require qualified IP counsel before external release. Do not label a derivative model "fully proprietary" if upstream terms grant downstream rights or impose obligations.

## CI and operational gates

Per division, CI verifies: canonical registry mapping; model manifest schema; pinned upstream revisions; dataset rights/provenance; no secrets/PII in artifacts; deterministic training/evaluation configuration; artifact checksums; held-out benchmark thresholds; safety/privacy tests; model-card completeness; license compatibility; endpoint smoke test; rollback metadata; and release approval. Training jobs run on an explicit budget/compute schedule and publish status, metrics, costs, and artifacts. "Daily" means daily eligible data review, evaluation, and training when a rights-cleared dataset and compute budget are available—not forced daily weight updates that degrade quality.

## Rollout phases

A. Inventory and rights audit all 65 current division profiles and Buddy.
B. Pilot 3 divisions with distinct modalities/domains; prove reproducible small-model fine-tuning and independent deployment.
C. Expand to every canonical division using shared training infrastructure and per-division configs/adapters.
D. Complete taxonomy reconciliation, Bootcamp exams, and cross-division evaluations.
E. Release proprietary checkpoints only after rights and quality gates.

## Truthful status reporting

Track separately: planned, data-cleared, base-selected, trained, benchmarked, safety-approved, license-approved, deployed, and released. A profile in a fleet catalog is not a trained model. A workflow passing is not proof of trained weights. Report model counts by verified state and link each state to immutable evidence.

## Mandatory per-division model identity and operating contract

Every active canonical division has a separately registered first-party model product, even when several divisions share a compatible base architecture or tokenizer. The division record must expose:
- Stable model name and immutable model ID, canonical division ID, semantic version, release channel, owner, and lifecycle state.
- Independently versioned trainable parameters: full weights or a named adapter/checkpoint with the exact immutable base model, config, and dependency hashes. Checkpoints include optimizer/scheduler state where resumption is supported.
- Tokenizer artifact and revision owned by the release, or a precise shared-tokenizer ID, version, vocabulary/config hashes, and compatibility tests. A shared tokenizer does not merge model ownership or versioning.
- Dataset manifest and exact versioned training/evaluation data lineage, rights snapshot, provenance, transformations, deduplication, split strategy, and hashes.
- Reproducible training recipe, code/container/dependency lock, seed, compute/hardware, budget, run logs, checkpoints, and evaluation outputs.
- Division-specific benchmark suite, held-out datasets, acceptance thresholds, safety/privacy tests, model card, license/notice bundle, and signed release manifest.
- Independently addressable inference deployment and API contract, with auth, scoped keys, quotas, rate limits, telemetry, model/version pinning, health checks, and rollback.
- Division-specific continuous improvement policy, candidate queue, evaluation history, approved data sources, and release/promotion history.

No division is considered trained, independently deployable, or production-ready merely because its registry entry, prompt, adapter configuration, API alias, or third-party wrapper exists. A shared serving cluster is allowed, but each division must have its own logical endpoint identity, authorization scope, version pin, metrics, and rollback target.

## Division endpoint and API contract

Expose a stable division route such as `/v1/divisions/{division_id}/models/{model_version}/responses` and a registry discovery route such as `/v1/divisions/{division_id}/models`. The exact route can follow the repository's existing API conventions. Each response records division ID, model ID/version, tokenizer version, deployment revision, request trace ID, and usage metadata without logging sensitive prompt content by default. Support version pinning, streaming where supported, structured output/tool contracts where evaluated, timeouts, cancellation, quotas, safe fallback policy, and health/readiness endpoints. External provider wrappers must be clearly identified as wrappers and must never masquerade as the division's first-party checkpoint.

## Continuous learning and AI/ML knowledge currency

Each division owns a continuous improvement lane with these stages:
1. Discover new AI/ML research, model releases, datasets, benchmark suites, libraries, security advisories, standards, and domain-specific knowledge from approved sources (including Hugging Face Hub/Spaces/Datasets, official framework documentation, papers, model cards, dataset cards, standards bodies, and curated educational material).
2. Capture source, publication/revision date, author, license/terms, retrieval timestamp, content hash, modality, subject tags, and intended use in an immutable source ledger.
3. Classify into the canonical division taxonomy; route cross-domain material to multiple divisions with explicit ownership and deduplication.
4. Apply rights, privacy, security, quality, relevance, freshness, and contamination checks. Public availability is not a training license.
5. Produce a versioned knowledge update, retrieval index, benchmark candidate, or training candidate. Keep retrieval/knowledge updates separate from weight updates.
6. Run offline evaluations and compare with the current champion, prior versions, and external baselines.
7. Train only when data rights, compute budget, validation coverage, and expected value pass. Use replay/regularization and regression checks to reduce catastrophic forgetting.
8. Promote through staged sandbox, canary, and production gates with human approval for release. Keep rollback to the previous champion.
9. Record what changed, why, source evidence, cost, benchmark deltas, known limitations, and next review date.

Cadence: continuously monitor approved feeds where infrastructure supports it; reconcile source indexes and taxonomy daily; run scheduled evaluation at least daily when compute is available; start training only when an eligible data/model improvement candidate exists. Do not promise every new dataset or model is consumed instantly. Never auto-train from raw production prompts, customer-private data, secrets, copyrighted material without rights, benchmark answer keys, or unreviewed synthetic outputs. Keep customer-specific fine-tuning isolated and opt-in; it must not flow into shared division models without explicit, documented permission.

## Machine-learning practice library for Buddy and Bootcamp

Buddy should teach and apply the full ML lifecycle across applicable divisions, not only LLM fine-tuning. Maintain versioned lessons, runnable labs, checklists, rubrics, reference implementations, and practical assessments for:

- Problem framing: task definition, target/label design, assumptions, baselines, success metrics, constraints, error costs, causal vs predictive questions.
- Data engineering: collection, ingestion, schema contracts, labeling, annotation guidelines, inter-annotator agreement, provenance, consent, licensing, privacy, PII minimization, deduplication, sampling, class imbalance, missingness, outliers, leakage, drift, train/validation/test splits, temporal/group splits, synthetic data review.
- Classical ML: linear/logistic regression, regularization, trees, random forests, gradient boosting, SVM, nearest neighbors, naive Bayes, clustering, dimensionality reduction, anomaly detection, ranking, recommendation, calibration, feature engineering, feature stores.
- Deep learning: tensors, autograd, optimization, initialization, normalization, CNNs, RNNs, LSTMs, attention, transformers, embeddings, autoencoders, graph neural networks, diffusion and generative models, multimodal architectures.
- LLM engineering: tokenization, pretraining, continued pretraining, SFT, preference optimization, RLHF/RLAIF concepts, LoRA/QLoRA, quantization, distillation, retrieval-augmented generation, tool use, structured decoding, context management, memory, agents, guardrails.
- Specialized modalities: computer vision, OCR, image generation, video, speech recognition/synthesis, audio understanding, time series, geospatial, tabular, graph, robotics, sensor/IoT, multimodal learning.
- Evaluation: proper baselines, cross-validation, stratification, statistical power, confidence intervals, significance, bootstrap, ablation, error analysis, subgroup/fairness evaluation, robustness, adversarial testing, calibration, uncertainty, OOD detection, human evaluation, benchmark contamination prevention.
- Training systems: experiment tracking, reproducibility, seeds, checkpointing, distributed data/model parallelism, mixed precision, GPU memory, gradient accumulation, schedulers, early stopping, hyperparameter optimization, resource scheduling, cost/performance tradeoffs.
- MLOps: data/model registries, feature and dataset versioning, CI/CD/CT, model packaging, serving, autoscaling, observability, latency/throughput, drift monitoring, retraining triggers, canaries, shadow tests, rollback, incident response, model retirement.
- Trustworthy AI: privacy, differential privacy concepts, federated learning concepts, secure aggregation, membership-inference and model-inversion testing, data poisoning, prompt injection, model extraction, supply-chain security, bias, accessibility, explainability, documentation, human oversight, regulatory and domain-specific controls.
- Research literacy: paper reading, reproduction, benchmark critique, source verification, citation, uncertainty, conflicting evidence, and translating research into tested engineering hypotheses.
- Product and economics: inference unit economics, GPU utilization, latency budgets, model routing, licensing, model cards, dataset datasheets, deployment tiers, SLAs, monitoring cost, lifecycle and deprecation policy.

Buddy must adapt depth to learner level, explain tradeoffs, generate exercises, inspect learner work, detect misconceptions, grade with transparent rubrics, and cite current authoritative sources for time-sensitive claims. It should distinguish established practice, active research, and speculation. Bootcamp completion requires practical projects and independent exams, not passive lesson consumption.

## Per-division release manifest additions

The signed manifest must additionally include model display name, immutable model ID, semantic version, canonical division ID, weight/checkpoint URI and hashes, base-model lineage, tokenizer ownership/shared reference and hashes, endpoint/API schema version, deployment revision, benchmark suite/version and thresholds, continuous-learning lane ID, last successful evaluation, current champion pointer, rollback target, and license approval evidence.
