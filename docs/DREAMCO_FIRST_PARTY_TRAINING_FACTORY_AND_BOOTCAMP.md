# DreamCo First-Party Training Factory and Buddy Bootcamp

## Purpose

DreamCo will build and own an auditable data-production system for Buddy and the 65 canonical MasterBot lanes. The factory creates original, rights-cleared examples, training curricula, evaluation packs, and reproducible manifests. It also prepares approved datasets for training compatible third-party/open-weight models when the model license and compute budget permit.

The factory is not a promise that 65 models have already been trained. Each lane remains `SPECIFIED_NOT_TRAINED` until real checkpoints, hashes, training logs, and evaluation evidence exist.

## First-party data streams

1. **Verified engineering lessons** — original explanations derived from merged/approved DreamCo commits, verified tests, resolved bugs and successful workflows. Require a source commit/run, a human reviewer, explicit training permission, no secrets or personal data, and a primary MasterBot owner.
2. **Original Bootcamp exercises** — DreamCo-authored tasks, rubrics, reference solutions, edge cases, recovery drills and grading fixtures. Each generated record is marked synthetic/original and includes its deterministic seed, generator version and reference-answer provenance.
3. **Expert-reviewed domain lessons** — original procedures, definitions, worked examples and annotations written or licensed for the intended use. Record reviewer, authority, revision, scope and expiry.
4. **Simulation and tool traces** — isolated test-environment trajectories with tool permissions, inputs/outputs, state transitions, and expected outcomes. Production user/customer data is excluded by default.
5. **Approved user contributions** — opt-in contributions with explicit scope, consent, retention, withdrawal and training rights. Keep tenant data isolated; do not repurpose one user's data for another division.
6. **Third-party licensed corpora** — Hugging Face, GitHub, OpenML, UCI, Kaggle, Data.gov, Zenodo, academic repositories, official APIs and other documented sources. These remain third-party assets with their own license and attribution; discovery never grants training permission.

## Build pipeline

`discover -> source pinning -> rights and consent review -> classification -> privacy/security scan -> schema and label QA -> deduplication -> contamination scan -> owner routing -> split generation -> immutable hashes -> dataset card -> human approval -> baseline -> sandbox training -> post-training benchmark -> independent review`

No dataset enters a training job unless its dataset card, exact source revision, license/rights evidence, privacy review, owner, content hash, split hashes, model/tokenizer revisions and compute approval are all present. Private holdouts are stored separately and are never included in training manifests.

## Data-sharing design

Use a **federated shared-foundation / isolated-specialist** model:

- Shared across divisions: approved generic lessons, reusable schemas, public-reference indexes, common tool-use patterns, safe synthetic fixtures, common tokenizer artifacts when explicitly selected, and shared evaluation methodology.
- Owned by one division by default: domain-specific training rows, annotations, customer-derived records, labels, adapters/checkpoints, retrieval indexes and private domain procedures.
- Never shared by default: private holdouts, benchmark answer keys, user/customer data, secrets, credentials, restricted licensed content, or another division's weights.
- Cross-division reuse requires provenance, compatible license/consent, privacy review, source-owner approval and a newly versioned destination dataset. Preserve source lineage; copying data does not change ownership.

Buddy receives access through a policy-aware router. It can search permitted shared resources and each division's authorized lane, but cannot use its coordinator role to bypass access controls.

## Buddy Bootcamp

The 65-lane plan maps every division to the 37 structured Hugging Face task-family references (2,405 division/task assignments), division capability packs, Bootcamp levels, dataset planes and model identities. Hugging Face is one source taxonomy, not the entire curriculum.

Bootcamp additionally covers ML foundations, data engineering, instruction following, reasoning, math, retrieval, tool use, vision, audio, speech, video, multilingual systems, safety/privacy, authorized reverse engineering, SFT, LoRA/QLoRA, distillation rights, MLOps, evaluation, observability and rollback. The existing Bootcamp sandbox layers and scorecard remain the acceptance framework.

External resource families include Hugging Face, GitHub, OpenML, UCI, Kaggle (where terms permit), government open data, Zenodo, academic papers/supplementary data, official documentation/APIs, DreamCo-owned code/tests, original simulations and opt-in user contributions. Each adapter must declare whether it supports metadata discovery, file inspection, ingestion, or training; do not describe metadata-only adapters as operational ingestion.

## Model training targets

- Buddy foundation/student models and orchestration skills.
- 65 division-specific model identities with isolated adapters/checkpoints and evaluation lanes.
- Smaller task-specific classifiers, rankers, embedders and tool routers.
- Compatible external models through SFT/LoRA/QLoRA or permitted distillation; base-model terms and teacher-output rights are checked independently.
- From-scratch foundation-model research remains a separate, explicitly budgeted and technically reviewed program.

Prefer retrieval and tool improvements before weight updates when knowledge changes frequently. Choose the smallest method that passes the same held-out task benchmark. Record tokens/examples per second, wall time, CPU/GPU and memory, storage, latency, throughput, cost, energy-relevant utilization, quality, robustness, safety and regression.

## Factory output and truth boundary

`tools/build_dreamco_training_factory.py` produces a 65-lane plan from pinned configuration files. It does not create training examples, download source data, approve rights, provision PostgreSQL/S3/queues, run a model, or change weights. The current dataset hub uses local SQLite/content-addressed objects; production shared storage remains a separate integration gate.

A plan, catalog entry, CI success, dry run or curriculum count is not training evidence. A model is considered trained only when the approved runner records the exact dataset/model/tokenizer revisions, compute allocation, seed, checkpoint hashes, logs, baseline/post-training results and independent review.
