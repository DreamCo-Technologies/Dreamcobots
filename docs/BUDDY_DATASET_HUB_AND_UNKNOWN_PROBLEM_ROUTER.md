# Buddy Dataset Hub, Bootcamp Training, and Unknown-Problem Router

**Status:** Routing policy and deterministic local index builder added; live source adapters, verified manifests, and model training workers remain separate implementation milestones.

## Objective

Build DreamCo's own governed dataset platform, inspired by the useful Hub workflows of Hugging Face: discover datasets and models, catalog metadata, inspect dataset cards, version revisions, build reproducible manifests, evaluate quality, route data to specialist divisions, and train eligible Buddy/student models.

DreamCo's own assets should become a first-class training collection: authored lessons, code, tests, task traces, verified fixes, synthetic fixtures, domain workflows, benchmark examples, and user-contributed data with explicit rights. Preserve source ownership and do not relabel third-party data as DreamCo-owned.

## Dataset lifecycle

1. Discover a candidate from DreamCo repositories, approved Hugging Face catalog search, public data portals, GitHub, OpenML, UCI, research supplements, or an authorized database/API.
2. Record canonical source, dataset/revision ID, owner, license and terms URL, access date, creator, transformations, content hash, intended use, attribution, redistribution, and commercial-use conditions.
3. Inspect dataset card and a permitted sample; validate schema, labels, language/domain coverage, duplicates, sensitive content, provenance, freshness, contamination, and quality.
4. Assign a data plane: public reference/retrieval, DreamCo-owned training, licensed training, user-contributed opt-in training, or evaluation-only holdout.
5. Create immutable versioned manifests and reproducible train/validation/test split hashes. Keep final holdouts isolated.
6. Route eligible candidates to the correct MasterBot lane and collaborators; record why the route was chosen.
7. Use retrieval and tool/workflow improvements before fine-tuning. Fine-tune only where benchmarks demonstrate a repeatable gap and data rights permit it.
8. Train in an isolated sandbox, record configuration/checkpoints/cost/metrics, evaluate domain and general capability, then request independent review.

A dataset listed as open or carrying a train flag is only a discovery lead. It is not approval to use the data commercially, redistribute it, train on it, or claim DreamCo ownership. Unknown terms block training.

## 65 MasterBot routing

Every canonical MasterBot receives its own dataset discovery lane and manifest namespace. The initial builder uses category and keyword heuristics to suggest candidate datasets; it deliberately labels these routes HEURISTIC_DISCOVERY_ONLY. The authoritative 65-MasterBot to 45-division crosswalk is still unresolved and must not be fabricated. A verified crosswalk and owner-approved tags replace heuristics before mastery claims.

Shared foundation data may support language, reasoning, instruction following, code, math, data handling, tool use, and safety. Domain datasets stay under one primary owner with explicit secondary collaborators. Shared base models do not mean shared private datasets or merged division weights.

## Unknown-problem routing

When Buddy encounters an unknown problem or missing capability, it should classify the missing skill, search the local DreamCo dataset index and prior verified lessons, search authorized Hugging Face datasets/models and approved public dataset registries, search DreamCo repositories/docs/tests/issue history and permitted connectors/databases/APIs, compare candidates by relevance/quality/freshness/license/cost/access/privacy, inspect a permitted sample in a sandbox, create a provenance manifest, route the candidate to a primary MasterBot and collaborators, create a benchmark or regression fixture, and re-test.

If no suitable data exists, Buddy creates a missing-data research task and reports the blocker. It must not pretend it solved an unknown problem merely because it found a dataset.

## Training Buddy and other models

The target fleet includes Buddy's foundation/student models and 65 independently tracked MasterBot specialist model profiles. Use a measured ladder: retrieval first; then adapters/SFT/LoRA/QLoRA or distillation where legally permitted and justified; then continued pretraining/full fine-tuning only with approved data and compute. Training from scratch is separate research.

For every run, pin base model/license/revision, tokenizer, dataset manifest and split hashes, code commit, seed, hyperparameters, environment, compute budget, logs, checkpoint hashes, domain/general/private-holdout scores, safety regressions, cost, latency, throughput, memory, and rollback. A profile or route is not a trained model. A model is not mastered without reproducible independent evidence.

## Safety and operating limits

- Default deny for unknown ownership, licenses, terms, consent, and training purpose.
- Personal memory, retrieval, procedural knowledge, aggregate product improvement, cross-user sharing, and foundation-model training are separate data planes and consents.
- Never train on benchmark holdouts or private user data without purpose-specific permission.
- Never bypass logins, paywalls, CAPTCHAs, access controls, provider restrictions, or rate limits.
- Paid compute, paid APIs, production weight changes, merges, and deployments require separate approval.
- Scheduled CI can validate routing and manifests; it is not a promise of continuous GPU training.

## Current implementation boundary

The route builder consumes the repository's existing dataset catalog and emits discovery-only candidate routes for all 65 registry entries. It does not download or study dataset files, verify current external terms, create checkpoints, or train weights. Live Hugging Face/OpenML/Kaggle/GitHub connectors, dataset storage/versioning, rights-review UI, ingestion workers, quality pipelines, training execution, and per-model evaluation remain follow-on runtime work.
