# Buddy Dataset Hub Runtime Implementation

## Implemented in this increment

- Persistent SQLite dataset catalog with versioned JSON dataset cards.
- Content-addressed local object storage for explicitly approved CSV and JSONL files.
- SHA-256 file identity and row-level duplicate, empty-row, and basic PII-pattern checks.
- Dataset training gates for rights evidence, data plane, canonical primary MasterBot ownership, collaborator routing, and pinned train/validation/test split hashes.
- Opt-in metadata discovery for Hugging Face datasets and models, OpenML, UCI, and GitHub repository search.
- An authorized GitHub file reader requiring both DREAMCO_ALLOW_SOURCE_NETWORK=1 and GITHUB_TOKEN. It reads one UTF-8 file into memory; it does not automatically persist it.
- Read-only SQLite and optional PostgreSQL snapshot adapters. They require an authorization reference, exact approved SQL SHA-256, explicit bounded LIMIT, and a read-only transaction. Credentials are environment-only.
- A verified-work example builder that synthesizes original instruction/response examples from human-reviewed, rights-cleared DreamCo commits, tests, PRs, workflow results, and lessons. It requires at least three verified records per MasterBot lane, keeps train/validation/test splits, rejects personal or third-party copied content, and emits a candidate card that is not training-approved.
- Unknown-problem routing across the local catalog, optional external dataset/model metadata, and specialist MasterBot candidates. Every investigation is persisted in the Dataset Hub research-task queue.
- Reproducible SFT/LoRA training manifests bound to the canonical 65-MasterBot registry, verified dataset and base-model license evidence, immutable base-model commit SHA, split hashes, and an explicit compute approval reference.
- An opt-in local Transformers runner that verifies the live dataset card and object hashes, measures the base model on validation data, runs SFT or LoRA, evaluates validation and the isolated test split after training, and saves a local artifact.
- A cross-model benchmark manifest and runner that compares a pinned baseline, trained candidate and license-verified open-weight alternatives on the same MasterBot's isolated test split using bits per UTF-8 byte, throughput and latency. It requires explicit compute approval and execution flags; it does not train or promote models.

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

## Creating original DreamCo training data

Prepare a JSONL file of reviewed evidence records. Each record must include event_id, source_url, evidence_type, verified=true, human_reviewed=true, training_allowed=true, rights_status=VERIFIED, contains_personal_data=false, third_party_content_included=false, primary_masterbot_id, task, verified_lesson, acceptance_criteria, and test_evidence.

Build a separate candidate dataset for one MasterBot lane (at least three independently verified records):

    python tools/build_dreamco_training_examples.py --events verified-work.jsonl --masterbot-id 41 --out candidates/dreamcodelab.jsonl --card-out candidates/dreamcodelab-card.json --license-url https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/LICENSE

Review the generated data and card. The builder deliberately sets training_approved=false and rights_status=PENDING_HUMAN_REVIEW. Only after the rights/ownership and content review should an authorized operator update the card with verified evidence and explicit training approval, then register it:

    python tools/register_buddy_dataset.py --card candidates/dreamcodelab-card-reviewed.json --file candidates/dreamcodelab.jsonl

The generator creates original summaries and practice examples; it does not ingest raw conversation logs, copy third-party source text, or train weights.

## Training job creation and execution

Create a reviewed request JSON containing dataset_id, dataset_hub_path, masterbot_id, model_id, base_model_revision (40-character immutable commit SHA), model_license, model_license_url, model_license_status (VERIFIED), model_license_evidence, and compute_approval_id. Optional fields are training_method (sft or lora) and max_steps.

Create the manifest:

    python tools/create_buddy_training_job.py --request training-request.json

Run only after the compute owner explicitly authorizes the exact job:

    python tools/run_buddy_training_job.py --job artifacts/buddy-training-jobs/JOB.json --compute-approval-id APPROVAL_ID --execute-approved

The runner requires torch and transformers; LoRA additionally requires peft. Cached model files are used by default. To permit a base-model download, the operator must additionally pass --allow-model-download and set DREAMCO_ALLOW_MODEL_DOWNLOAD=1.

The runner evaluates the base model on validation data, trains the requested SFT/LoRA job, then evaluates validation and the isolated test split and saves a local model artifact plus metrics. It does not publish, merge, deploy or promote production weights. This PR has not executed a training run. CI compiles the runner and tests policy/hash validation only; it does not download model weights or consume GPU/paid compute.

Bits per UTF-8 byte is a comparable language-modeling metric across tokenizers, but it is not a complete domain task benchmark. The cross-model runner does not yet measure all task suites, safety, reliability, memory/cost or end-to-end agent workflows. A separate independent benchmark suite must measure those dimensions and private holdouts before mastery or promotion.

## Cross-model benchmark creation

Create a reviewed request JSON with dataset_id, dataset_hub_path, masterbot_id, compute_approval_id, and a candidates array. Each candidate requires model_id, immutable 40-character revision, license, license_url, license_status=VERIFIED, license_evidence, and role (exactly one baseline plus one or more trained_candidate/open_weight_alternative entries).

Create the benchmark manifest:

    python tools/create_buddy_model_benchmark.py --request benchmark-request.json

Execute only after explicit approval:

    python tools/run_buddy_model_benchmark.py --job artifacts/buddy-model-benchmarks/JOB.json --compute-approval-id APPROVAL_ID --execute-approved

Model downloads additionally require --allow-model-download and DREAMCO_ALLOW_MODEL_DOWNLOAD=1. The runner uses the same per-MasterBot held-out examples for each candidate and does not train, deploy or promote models. CI tests manifest and holdout validation only; no models are downloaded or benchmarked by CI.

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
