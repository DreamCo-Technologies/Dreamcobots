# DreamCo First-Party Training Data Factory

Status: first-party authored seed corpus and source governance contract; training is not approved or executed by this artifact.

## Purpose

Create DreamCo-originated teaching and task examples that can later be reviewed and used to train Buddy Teacher and specialist divisions. DreamCo must preserve evidence of authorship and assignment; an original draft is not automatically company-owned or training-authorized.

## Initial seed

- `data/dreamco_training/bootcamp/core_lessons.v1.jsonl` contains 13 original Bootcamp teaching examples across the 13 core curriculum modules.
- Every record has a stable ID, split, prompt, answer, evaluation rubric, topic tags, source lineage, and authoring/rights state.
- The current examples are draft candidates. `training_permission=NOT_GRANTED`, `owner_claim=PENDING_ASSIGNMENT_REVIEW`, and `human review` remain mandatory.
- Train, validation, and test assignments are pinned in the source file. The builder never moves test examples into training.

## Source ecosystem

`config/dreamco-training-source-registry.json` defines nine source families beyond any one catalog: DreamCo original work, official technical documentation, public dataset catalogs, research metadata, code/software, government/standards data, user contributions, teacher outputs, and evaluation-only assets.

Metadata discovery is enabled only through explicitly configured adapters. Download and training remain disabled by default. Exact license, file-level rights, privacy, consent, provenance, and intended use must be reviewed before ingestion.

## Sharing model

- Share approved common-foundation resources through immutable dataset references and content hashes.
- Materialize separate division records/namespaces and access grants.
- Keep division-private raw data, customer data, holdouts, weights, checkpoints, and tokenizer state isolated.
- Cross-division collaboration requires an explicit owner grant and is recorded in the manifest.
- Buddy can search the shared catalog and route only to resources its task and data classification are authorized to use.

## Training handoff

1. Review authorship/assignment and approve each original lesson for the intended training purpose.
2. Validate the JSONL schema, provenance, PII/secrets, duplicate rate, label quality, and split isolation.
3. Create a versioned dataset card with rights evidence and a primary division owner (or an explicitly approved shared-foundation owner).
4. Register through the local DatasetHub; ingestion produces `INGESTED_PENDING_BENCHMARK`, not trained weights.
5. Establish a baseline and private holdout before a separately approved SFT/LoRA job.
6. Hash the base model, tokenizer, data splits, code commit, configuration, checkpoints, and final weights.
7. Run independent domain/general/safety/privacy/robustness/regression and resource benchmarks before any promotion.

## Current limitations

- The seed pack is a small authored starting point, not a comprehensive domain corpus or a trained teacher model.
- The source registry describes governed discovery targets; it does not imply all connectors, subscriptions, credentials, or downloads are active.
- The existing local DatasetHub is not proof of production PostgreSQL/S3/queue availability.
- No external data has been downloaded, no provider output has been assumed trainable, and no paid compute has been started.
