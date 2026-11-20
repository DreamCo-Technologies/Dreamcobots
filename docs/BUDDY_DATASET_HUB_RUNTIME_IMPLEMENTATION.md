# Buddy Dataset Hub Runtime Implementation

## What is implemented in this increment

- A persistent SQLite dataset catalog with versioned JSON dataset cards.
- Content-addressed local object storage for explicitly approved CSV and JSONL files.
- SHA-256 source-file identity and row-level duplicate, empty-row, and basic PII-pattern checks.
- Explicit training rights evidence and data-plane gates; unknown rights and evaluation holdouts cannot be ingested for training.
- Metadata-only discovery adapters for Hugging Face, OpenML, UCI and public GitHub repository search. Network calls are off by default and require \`DREAMCO_ALLOW_SOURCE_NETWORK=1\`; no source files are downloaded.
- An unknown-problem router that searches the local catalog, optionally searches external metadata, and suggests specialist MasterBots.
- Reproducible model training job manifests that require an explicit compute approval ID and immutable base-model revision. The manifest is queued for a registered runner; this increment does not launch training.

## Storage and cards

Default local path: \`.dreamco/dataset-hub/\` (override with \`DREAMCO_DATASET_HOME\`). SQLite metadata is stored in \`catalog.sqlite3\`, immutable content objects under \`objects/\`, and versioned cards under \`cards/\`. Production multi-node deployments still need a secured object-store/database adapter, backup/restore, encryption/key management, retention and deletion workflows.

## Source adapters

The adapters issue bounded read-only metadata requests only. Hugging Face results expose dataset IDs and tags; OpenML, UCI and GitHub results expose catalog metadata. Every result remains rights-unverified until its exact dataset card, license text, terms, intended use and attribution requirements have been reviewed. A GitHub repository license does not automatically license all data in that repository.

## Quality controls and limitations

CSV and JSONL are the initial supported local ingestion formats. Duplicate and empty-row checks are structural. Basic email, US phone and SSN patterns flag data for review; this is not a complete PII detector or a redaction system. Schema meaning, label quality, class balance, representativeness, benchmark contamination and domain-specific safety require additional validators and human review. Quarantined content is not registered as trainable.

## Training and benchmarking boundary

A training job request requires a rights-approved dataset, a non-holdout split, model ID, pinned base-model revision and explicit compute approval ID. It records a reproducibility contract but remains \`NOT_EXECUTED\` until a real registered runner is connected. No model weights are changed. A separate benchmark runner must record before/after scores, private holdout results, regression and safety checks. Production weight promotion remains a separate human-approved action.

## Next adapters

- Encrypted object storage and managed metadata database for shared production use.
- Authenticated private GitHub repository ingestion through least-privilege connector scopes.
- Database adapters for approved read-only SQL snapshots, query allowlists and row/column minimization.
- Hugging Face dataset card/revision fetch and license/terms review workflow.
- OpenML/UCI full metadata and citation/license capture.
- Parquet/Arrow streaming, schema-aware validation, semantic deduplication and domain-specific labeling.
- Registered training runners for Transformers/TRL/PEFT and approved cloud GPU backends.
- Baseline/holdout benchmark harness and signed model artifact registry.
