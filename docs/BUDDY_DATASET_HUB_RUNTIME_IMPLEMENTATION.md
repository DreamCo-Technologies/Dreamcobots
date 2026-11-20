# Buddy Dataset Hub Runtime Implementation

## Implemented in this increment

- Persistent SQLite dataset catalog with versioned JSON dataset cards.
- Content-addressed local object storage for explicitly approved CSV and JSONL files.
- SHA-256 file identity and row-level duplicate, empty-row, and basic PII-pattern checks.
- Dataset training gates for rights evidence, data plane, canonical primary MasterBot ownership, collaborator routing, and pinned train/validation/test split hashes.
- Opt-in metadata discovery for Hugging Face datasets and models, OpenML, UCI, and GitHub repository search.
- An authorized GitHub file reader requiring both DREAMCO_ALLOW_SOURCE_NETWORK=1 and GITHUB_TOKEN. It reads one UTF-8 file into memory; it does not automatically persist it.
- Read-only SQLite and optional PostgreSQL snapshot adapters. They require an authorization reference, exact approved SQL SHA-256, explicit bounded LIMIT, and a read-only transaction. Credentials are environment-only.
- Unknown-problem routing across the local catalog, optional external dataset/model metadata, and specialist MasterBot candidates. Every investigation is persisted in the Dataset Hub research-task queue.
- Reproducible SFT/LoRA training manifests bound to the canonical 65-MasterBot registry, verified dataset and base-model license evidence, immutable base-model commit SHA, split hashes, and an explicit compute approval reference.
- An opt-in local Transformers runner that verifies the live dataset card and object hashes, measures the base model on validation data, runs SFT or LoRA, evaluates validation and the isolated test split after training, and saves a local artifact.

## Storage and dataset cards

Default local path: .dreamco/dataset-hub/ (override with DREAMCO_DATASET_HOME). SQLite metadata is stored in catalog.sqlite3, content-addressed objects under objects/, and versioned cards under cards/. Unknown-problem investigations are stored in the same catalog database.

This is persistent local storage, not yet shared production infrastructure. Multi-node deployment still needs a secured object-store/database adapter, backup/restore, encryption/key management, retention, deletion and withdrawal workflows.

## Source discovery and connectors

Network is off by default. Set DREAMCO_ALLOW_SOURCE_NETWORK=1 only in an authorized execution environment to enable bounded read-only metadata requests. Hugging Face dataset and model results, OpenML, UCI and GitHub candidates remain rights-unverified until the exact card, license text, terms, intended use, attribution and redistribution rules are reviewed.

The authorized GitHub file reader additionally requires GITHUB_TOKEN with access to the selected repository. Do not place tokens in code, dataset cards, logs or committed files. A repository license does not automatically license every dataset or file within it.

Database snapshots require an explicit authorization reference and a query hash that the caller has approved. SQLite opens in read-only mode; PostgreSQL uses a read-only transaction. The first adapters do not yet implement database-specific row-level security, column-level minimization or enterprise secrets management.

## Quality controls and limitations

CSV and JSONL are the first supported local ingestion formats. Duplicate and empty-row checks are structural. Basic email, US phone and SSN patterns flag data for review; this is not a complete PII detector or a redaction system. Schema meaning, label correctness, class balance, representativeness, benchmark contamination and domain-specific safety require additional validators and human review.

Training-eligible datasets require a verified rights status, evidence reference, primary MasterBot owner, valid collaborators, and SHA-256 hashes for train, validation and isolated test splits. The test split is never used for training or in-training model selection.

## Training job creation and execution

Create a reviewed request JSON containing dataset_id, dataset_hub_path, masterbot_id, model_id, base_model_revision (40-character immutable commit SHA), model_license, model_license_url, model_license_status (VERIFIED), model_license_evidence, and compute_approval_id. Optional fields are training_method (sft or lora) and max_steps.

Create the manifest:

    python tools/create_buddy_training_job.py --request training-request.json

Run only after the compute owner explicitly authorizes the exact job:

    python tools/run_buddy_training_job.py --job artifacts/buddy-training-jobs/JOB.json --compute-approval-id APPROVAL_ID --execute-approved

The runner requires torch and transformers; LoRA additionally requires peft. Cached model files are used by default. To permit a base-model download, the operator must additionally pass --allow-model-download and set DREAMCO_ALLOW_MODEL_DOWNLOAD=1.

The runner evaluates the base model on validation data, trains the requested SFT/LoRA job, then evaluates validation and the isolated test split and saves a local model artifact plus metrics. It does not publish, merge, deploy or promote production weights. This PR has not executed a training run. CI compiles the runner and tests policy/hash validation only; it does not download model weights or consume GPU/paid compute.

Language-model loss before/after fine-tuning is an initial training metric, not a complete model-competitiveness benchmark. A separate independent benchmark suite must measure general and division-specific tasks, private holdouts, regression and safety before mastery or promotion.

## Remaining production work

- Shared encrypted object storage and managed metadata database with backup/restore and deletion/withdrawal support.
- Persistent authenticated GitHub ingestion through least-privilege connector scopes and human review.
- Enterprise database connectors with row/column policies, sensitive-field minimization and secrets management.
- Full dataset-card and license/terms capture for Hugging Face, OpenML, UCI and GitHub.
- Parquet/Arrow streaming, schema-aware validation, semantic deduplication, labeling and domain-specific quality scoring.
- Training fleet orchestration, checkpoint resume, cost/quota enforcement, model registry, signed artifacts and rollback.
- Independent baseline suites for every MasterBot and candidate open-weight model, with reproducible hardware/prompt/tool controls.
- Verified 65-MasterBot to 45-division crosswalk; do not invent this mapping.

Paid compute, model downloads, dataset ingestion, external applications, production weight updates, merges and deployments remain explicit approval-gated. No discovery listing or route is itself training approval or proof of learning.
