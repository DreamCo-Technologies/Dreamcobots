# DreamCo First-Party Model Factory and Buddy Bootcamp Teaching System

Status: implementation blueprint; no proprietary checkpoint is claimed trained or ready.
Strategic priority: DreamCo's own models are the product. Third-party models are temporary development, research, evaluation, and optional fallback wrappers—not the long-term model identity or the only product customers can buy.

## 1. Non-negotiable product strategy

DreamCo will build and own a portfolio of first-party models:
- a Buddy Teacher model family;
- one specialist model family per canonical DreamCo division;
- shared foundation models for general language, code, math, vision, audio, and multimodal tasks where justified;
- category-specific customer and commercial models;
- compact deployment variants for low-cost inference.

Third-party APIs and third-party open-weight models may be used as teachers, research references, temporary wrappers, benchmark baselines, or optional user-selected integrations. They must be visibly labeled by provider and must never be represented as DreamCo-owned weights. DreamCo products must not silently depend on an external wrapper when a first-party model is advertised.

The business objective is to train, evaluate, version, license, host, and sell DreamCo-owned models. Customers may also choose third-party wrappers if they prefer them.

## 2. First-party model ownership levels

Use explicit product labels:
1. **DreamCo-trained** — model weights trained by DreamCo from an initialization or base whose rights permit the intended release; all data and code rights are documented.
2. **DreamCo fine-tuned** — DreamCo-trained adapter/checkpoint on a named, pinned base. Show the upstream base and its license prominently. Do not imply DreamCo owns upstream weights.
3. **DreamCo distilled** — student trained from permitted teacher outputs/data; document teacher terms, synthetic-data provenance, and any output restrictions.
4. **DreamCo hosted wrapper** — external provider inference behind DreamCo UX. Never label as a DreamCo-owned model.
5. **DreamCo retrieval package** — private retrieval/index/configuration over approved sources; not a new trained model checkpoint.

Every listing and endpoint must expose the exact ownership level, base model, revision, weights availability, license chain, and allowed customer operations.

## 3. Model factory: training path

### Phase A — establish lawful training corpus
- Build a source registry from public-domain, appropriately licensed, purchased, commissioned, and user-authorized datasets.
- Record dataset owner, exact source/version, license and terms, allowed training/commercial/redistribution operations, attribution, geographic restrictions, and proof.
- Separate text/code/image/audio/video/tabular data pipelines and modality-specific quality checks.
- Exclude unknown-rights sources from training until resolved. Public visibility is not permission.
- Create deduplicated, quality-filtered, contamination-checked train/validation/test splits with immutable manifests.
- Maintain PII/sensitive-data controls, opt-out/deletion workflows, and data minimization.

### Phase B — choose the right training strategy
- Start with compact models and proven recipes; use small-model pretraining or continued pretraining only when rights-cleared corpus and compute support it.
- Use LoRA/QLoRA for efficient specialization when base terms permit.
- Use knowledge distillation only when teacher terms allow it; log teacher/model version, prompt/task recipe, generated data provenance, filtering, and student evaluation.
- Train from random initialization only when there is a sound data, compute, and evaluation case.
- Use a mix of curriculum training, supervised fine-tuning, preference optimization, and tool-use training where evidence supports it.
- Keep a stable baseline; never overwrite the best validated checkpoint with an unproven daily update.

### Phase C — repeatable experiments
Every run pins:
- model architecture/config/tokenizer;
- initialization/base checkpoint and revision;
- dataset manifest hashes and rights decisions;
- code commit, container, dependencies, seed, hyperparameters;
- hardware, region, start/end, cost, logs, checkpoints;
- benchmark suite versions and results.

Use isolated jobs, budget caps, queue priorities, checkpoint/resume, cancellation, retry safety, and artifact integrity checks.

### Phase D — evaluate and promote
Required suites include:
- category-specific task accuracy and held-out generalization;
- reasoning, instruction following, tool-use and structured output;
- hallucination/factuality and calibrated uncertainty;
- privacy leakage, memorization, extraction and data contamination;
- safety, jailbreak resistance, prompt injection and misuse;
- fairness/accessibility and language coverage where relevant;
- latency, throughput, memory footprint, energy/compute and cost per successful task;
- regression against previous stable release and relevant external baselines.

Promotion requires minimum gates, reproducible evidence, rights approval, security approval, and human release approval. Failed candidates remain in quarantine; production can roll back.

## 4. One specialist model family per division

- Use the canonical division registry as the source of truth, not an independent manually maintained list.
- Every active division receives a model development record, subject taxonomy, approved corpus plan, task/benchmark suite, teacher curriculum, candidate model recipe, owner, and lifecycle state.
- A division may share a base architecture or tokenizer with other divisions, but its specialist data, training recipe, evaluation suite, and release lineage remain independently tracked.
- Do not force 65 separate giant foundation-model pretraining jobs. Start with compact shared first-party foundations and division-specific adapters/specialist checkpoints; expand to independent weights when data and benchmark evidence justify it.
- Each division reports: not_started, rights_review, corpus_ready, recipe_ready, training, evaluating, approved, deployed, or blocked_with_reason.
- A division is not "trained" just because a profile, prompt, wrapper, or config exists.

## 5. Buddy Teacher: make Bootcamp the model-training school

Buddy Teacher is itself a first-party model program, not just a system prompt that routes to a third-party chatbot.

### Teacher model capabilities
- Explain ML concepts from beginner to advanced, adapting to learner skill and goals.
- Teach Python, PyTorch, Transformers, tokenization, datasets, model architecture, optimization, evaluation, inference, quantization, PEFT/LoRA, distillation, deployment, MLOps, data governance, licensing, privacy, and safety.
- Generate exercises, code walkthroughs, diagrams (as source artifacts), quizzes, flashcards, labs, and capstone projects.
- Review training configs and code, diagnose stack traces, explain failed runs, and propose reproducible fixes.
- Teach model selection and cost estimation; distinguish pretraining, continued pretraining, fine-tuning, retrieval, and distillation.
- Provide citations/source references and distinguish established facts, estimates, and uncertain claims.
- Evaluate student work with rubrics and evidence; never fabricate completion or certification.
- Teach responsible use, dataset rights, security, and evaluation as required subjects—not optional extras.

### Teacher training pipeline
1. Curate a rights-cleared teaching corpus from original DreamCo lessons, licensed educational material, official documentation where terms permit, and user-authorized content.
2. Build a concept graph and prerequisite map spanning ML fundamentals through production systems.
3. Produce high-quality lesson/task examples with source provenance and human-reviewed answer keys.
4. Train a compact first-party Buddy Teacher candidate; use third-party models only as temporary teacher/critic aids when terms permit and label their contributions.
5. Evaluate pedagogy: correctness, clarity, adaptive explanation, misconception detection, code validity, exercise quality, feedback usefulness, and safe handling of high-impact domains.
6. Run blind human review and student learning-outcome studies; compare pre/post skill mastery, not just answer preference.
7. Promote versioned teacher releases only after factuality, citation, pedagogy, safety, and regression gates pass.
8. Feed verified learner misconceptions and anonymized/consented outcomes into curriculum improvement; do not train on private learner data by default.

### Buddy Bootcamp curriculum map
- **Level 0: Digital and Python foundations** — command line, Git, environments, Python, math, statistics, linear algebra, probability.
- **Level 1: ML foundations** — datasets, features, loss, gradients, optimization, train/validation/test, overfitting, evaluation.
- **Level 2: Deep learning** — tensors, neural nets, backpropagation, CNNs, transformers, attention, tokenizers, embeddings.
- **Level 3: LLM engineering** — instruction tuning, context, prompting, structured outputs, tool calling, RAG, evaluation.
- **Level 4: Efficient specialization** — LoRA/QLoRA, quantization, adapters, distillation, continued pretraining, small-model design.
- **Level 5: Data engineering and governance** — collection, licensing, provenance, deduplication, PII, synthetic data, splits, contamination.
- **Level 6: Training operations** — GPUs, distributed training, experiment tracking, checkpointing, cost controls, reproducibility, debugging.
- **Level 7: Evaluation and safety** — benchmarks, robustness, privacy, red-teaming, bias, calibration, safety cases.
- **Level 8: Deployment and MLOps** — inference servers, APIs, batching, caching, monitoring, scaling, rollback, versioning.
- **Level 9: Specialist division academies** — category-specific projects, data and benchmarks for each DreamCo division.
- **Level 10: Model business and commercialization** — model cards, licenses, hosting, pricing, marketplace listings, customer support, release management.
- **Level 11: Master builder capstone** — build, train/fine-tune, evaluate, deploy and document a model with a verifiable portfolio.

Every lesson includes objectives, prerequisites, source/provenance, explanation, worked example, hands-on lab, assessment, rubric, and mastery evidence. Bootcamp tracks progress by competency, not time spent.

### Teacher quality and governance
- Keep a versioned teacher benchmark with known-answer tests and held-out questions.
- Evaluate explanations against official references and run code snippets in safe sandboxes.
- Require source attribution for technical claims and flag stale documentation.
- Keep a stable teacher release while candidate teachers are tested.
- Human experts review curriculum and certification standards.
- Certification means demonstrated performance on specified tasks; it is not an unqualified professional credential.

## 6. Third-party wrappers remain optional

- Preserve wrappers for customers who explicitly choose them, for compatibility, fallback, research, or workloads where they outperform DreamCo.
- Make provider, model ID, cost, retention, region, and data-routing policy visible.
- Give customers a model selector and an option to disable external providers.
- Never route private customer training data to a third-party teacher without explicit consent and a rights/policy check.
- Add a first-party route preference: DreamCo model first when it meets the user's quality, safety, latency, and cost constraints; external fallback only when enabled.
- Track wrapper usage separately from DreamCo model usage and revenue.

## 7. Commercial model catalog

Sell first-party model products as:
- hosted API subscriptions;
- private dedicated endpoints;
- team/enterprise deployments;
- downloadable weights where the license and supply chain allow;
- division-specific pretrained models;
- customer-specific fine-tuning and managed retraining;
- support, evaluation, and update subscriptions.

For each listing show model ownership level, model/version hash, category, base/teacher provenance, training-data rights summary, license, benchmark evidence, supported hardware, context/modality, price, usage caps, support policy, and known limitations.

A customer purchase grants only the rights stated in the listing's license. Customer-specific fine-tunes must preserve upstream restrictions. DreamCo may sell models only when it can lawfully grant the advertised rights.

## 8. Initial engineering sequence

1. Inventory existing model builder, LoRA plans, division registry, model router, model benchmark framework, Bootcamp, data provenance, licensing, storage, queues, and CI.
2. Add canonical model-family registry and lifecycle validation for all divisions.
3. Add rights-cleared corpus manifest and training recipe schemas.
4. Add one compact first-party pilot model in a low-risk domain, with reproducible training/evaluation.
5. Build the Buddy Teacher curriculum graph and first-party teacher baseline.
6. Add a division pilot and customer fine-tuning flow using tenant isolation and spend caps.
7. Add first-party-only inference mode and explicit wrapper opt-in.
8. Publish only after license, safety, benchmark, and security gates pass.
9. Scale to all divisions using measured resource budgets and dependency-aware queues.

## 9. Acceptance criteria

- No wrapper is mislabeled as DreamCo-owned.
- Every division has a tracked model-family record and measurable training status.
- At least one first-party pilot checkpoint is actually trained, hashed, reproducible, evaluated, and license-cleared before calling it a trained DreamCo model.
- Buddy Teacher has its own training lineage and benchmarked teaching ability.
- Bootcamp covers the complete curriculum and tracks verified mastery.
- Users can select first-party-only mode; external wrappers are optional and clearly disclosed.
- Customers can purchase or subscribe to first-party models with explicit license terms.
- Customers can train eligible purchased models with their own rights-cleared data and isolated jobs.
- No cross-tenant data access; no silent third-party training-data sharing.
- No release without rights, safety, security, benchmark, and human approval.

## 10. Current truth

This is a target architecture and rollout specification. It does not claim that DreamCo has already trained its own foundation models, that Buddy Teacher is already a top-performing teacher model, or that the marketplace is already selling production checkpoints. Those claims require actual artifacts, benchmark reports, rights manifests, deployed services, and verified customer flows.


## 12. First-party verified-work data factory (candidate generation)

The Python repository includes `tools/build_dreamco_training_examples.py`, which converts approved, independently verified DreamCo work records into original instruction/response candidates for one canonical MasterBot lane at a time. Its JSONL output is compatible with common dataset loaders (including Hugging Face Datasets' JSON loader) and can be adapted for other training frameworks. Compatibility does not grant rights to train or redistribute.

Each source record must carry:
- a unique event ID and HTTPS evidence URL;
- an allowed evidence type (verified commit/test, approved PR/workflow, verified bug fix, original lesson, or approved synthetic example);
- explicit `verified=true`, `human_reviewed=true`, `training_allowed=true`, and `rights_status=VERIFIED`;
- explicit negative attestations for secrets, personal data, and third-party content;
- one canonical integer MasterBot ID, an original task and lesson, acceptance criteria, and test evidence.

The builder rejects duplicate IDs and duplicate task/lesson content, mixed MasterBot ownership, malformed evidence arrays, non-HTTPS sources, common PII patterns, and common credential/private-key patterns. It creates deterministic example IDs and SHA-256 hashes for source records, each split, the complete candidate rows, and the emitted JSONL file. The manifest is an integrity aid, not a proof of correctness, privacy, or legal rights.

**Important limits:** the PII/secret checks are defense-in-depth heuristics, not a complete scanner. Human source review remains mandatory. Three or more records are required to create train/validation/test partitions, but small partitions are only bootstrap fixtures—not statistically sufficient model-evaluation datasets. Private benchmark holdouts must be maintained in a separate store and must never be exported by this builder.

Every generated card is marked `PENDING_HUMAN_REVIEW`, `training_approved=false`; the builder does not register data, download third-party content, execute training, update weights, or promote a model. A separate approved training job must pin the dataset-card revision and content hashes, base model/tokenizer revisions, training recipe, compute approval, code commit, and held-out benchmark suite. Training other models is permitted only after each target model's license, data rights, output-use restrictions, and deployment terms have been reviewed independently.

### Dataset lanes and sharing boundary

- Build one primary-owner dataset at a time for each of the 65 MasterBots.
- Shared foundation examples may be separately curated and explicitly scoped for reuse after rights/privacy review; division-private data, credentials, checkpoints, and private holdouts stay isolated.
- Do not merge division datasets merely to increase row counts. Use a documented collaboration manifest when multiple divisions are authorized to share a source.
- Keep source-event provenance and dataset-card versions with every exported training run.
- Candidate generation does not imply that any division currently has sufficient data, trained weights, or a certified model.
