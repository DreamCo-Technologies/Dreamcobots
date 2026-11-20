# Buddy Dataset Hub Runtime Implementation

## Implemented in this increment

- Persistent SQLite dataset catalog with versioned JSON dataset cards.
- Content-addressed local object storage for explicitly approved CSV and JSONL files.
- SHA-256 file identity and row-level duplicate, empty-row, and basic PII-pattern checks.
- Dataset training gates for rights evidence, data plane, canonical primary MasterBot ownership, collaborator routing, and pinned train/validation/test split hashes.
- Opt-in metadata discovery for Hugging Face datasets and models, OpenML, UCI, GitHub repositories, Zenodo research records, Data.gov catalogs, and Kaggle (when operator API credentials are configured).
- An authorized GitHub file reader requiring both DREAMCO_ALLOW_SOURCE_NETWORK=1 and GITHUB_TOKEN. It reads one UTF-8 file into memory; it does not automatically persist it.
- Read-only SQLite and optional PostgreSQL snapshot adapters. They require an authorization reference, exact approved SQL-and-parameter SHA-256, explicit bounded LIMIT, and a read-only transaction. Credentials are environment-only.
- A verified-work example builder that synthesizes original instruction/response examples from human-reviewed, rights-cleared DreamCo commits, tests, PRs, workflow results, and lessons. It requires at least three verified records per MasterBot lane, keeps train/validation/test splits, rejects personal or third-party copied content, and emits a candidate card that is not training-approved.
- A rotating autonomous discovery fleet that scans five of the 65 MasterBot lanes per daily run, persists external candidates and their MasterBot routes in SQLite, and completes a full 65-lane rotation every 13 daily runs.
- Conservative license triage for CC0, CC-BY, MIT, Apache-2.0, BSD, Unlicense and 0BSD identifiers. This is only a candidate filter; AI-training permission, rights in every included file, privacy and quality still require verification.
- Unknown-problem routing that can automatically search external metadata when both DREAMCO_AUTO_DISCOVERY=1 and DREAMCO_ALLOW_SOURCE_NETWORK=1 are configured. Every investigation and discovered candidate is persisted.
- Reproducible SFT/LoRA training manifests bound to the canonical 65-MasterBot registry, verified dataset and base-model license evidence, immutable base-model commit SHA, split hashes, and an explicit compute approval reference.
- An opt-in local Transformers runner that verifies the live dataset card and object hashes, measures the base model on validation data, runs SFT or LoRA, evaluates validation and the isolated test split after training, and saves a local artifact.
- A cross-model benchmark manifest and runner that compares a pinned baseline, trained candidate and license-verified open-weight alternatives on the same MasterBot's isolated test split using bits per UTF-8 byte, throughput and latency. It requires explicit compute approval and execution flags; it does not train or promote models.

## Storage and dataset cards

Default local path: .dreamco/dataset-hub/ (override with DREAMCO_DATASET_HOME). SQLite metadata is stored in catalog.sqlite3, content-addressed objects under objects/, and versioned cards under cards/. Unknown-problem investigations are stored in the same catalog database.

This is persistent local storage, not yet shared production infrastructure. Multi-node deployment still needs a secured object-store/database adapter, backup/restore, encryption/key management, retention, deletion and withdrawal workflows.

## Source discovery and connectors

Network is off by default for ordinary commands. The scheduled Buddy Sandbox Bootcamp workflow enables DREAMCO_ALLOW_SOURCE_NETWORK=1 for a bounded daily metadata scan of five MasterBot lanes. It caches the local Dataset Hub between workflow runs and uploads discovery/catalog artifacts. Five lanes per day means a complete 65-lane rotation every 13 daily runs. The scan searches Hugging Face datasets and models, OpenML, UCI, GitHub repository metadata, Zenodo, Data.gov and Kaggle when operator API credentials are configured.

These are discovery sources, not an exhaustive index of the internet. Search results remain metadata candidates. Hugging Face dataset-card front matter is inspected where possible, but the full card, each file's license, contributors' rights, terms, privacy and intended AI-training use still require review. A public listing or license tag never authorizes training.

The authorized GitHub file reader additionally requires GITHUB_TOKEN with access to the selected repository. Do not place tokens in code, dataset cards, logs or committed files. A repository license does not automatically license every dataset or file within it.

Database snapshots require an explicit authorization reference and a query hash that the caller has approved. SQLite opens in read-only mode; PostgreSQL uses a read-only transaction. The first adapters do not yet implement database-specific row-level security, column-level minimization or enterprise secrets management.

## Autonomous discovery and legal-use triage

The daily runner is:

    python tools/run_buddy_dataset_discovery.py --lanes-per-run 5 --limit 3

It rotates through all 65 canonical MasterBots, persists each discovered source candidate with a stable key, first/last-seen timestamps and one primary MasterBot route, and records the query and source metadata. It does not download dataset files or train weights. Unknown-problem routing can perform the same bounded source search when both DREAMCO_AUTO_DISCOVERY=1 and DREAMCO_ALLOW_SOURCE_NETWORK=1 are set.

The license triage module recognizes a small, conservative set of license identifiers (CC0, CC-BY, MIT, Apache-2.0, BSD, Unlicense and 0BSD). A candidate is not even marked potentially suitable for training unless it also carries explicit AI-training permission, verified content rights, a passed privacy review and valid source provenance. Even then the result is only a candidate requiring quality checks and final review. Unknown, non-commercial, research-only, share-alike, custom and ambiguous licenses are blocked from automatic training triage. This is not legal advice and does not establish that all files under a dataset have the same rights.

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
- Full dataset-card and file-level license/terms capture for every connector, including Zenodo, Data.gov and Kaggle.
- Additional source adapters and authenticated access for private or subscription sources, with exact scopes and terms.
- A managed persistent catalog/object store; current workflow caching and artifacts are best-effort persistence, not a production database.
- Parquet/Arrow streaming, schema-aware validation, semantic deduplication, labeling and domain-specific quality scoring.
- Training fleet orchestration, checkpoint resume, cost/quota enforcement, model registry, signed artifacts and rollback.
- Independent baseline suites for every MasterBot and candidate open-weight model, with reproducible hardware/prompt/tool controls.
- Verified 65-MasterBot to 45-division crosswalk; do not invent this mapping.

Daily public metadata discovery is scheduled, but it is not exhaustive. Dataset-file downloads and ingestion, paid compute, external applications, production weight updates, merges and deployments remain explicit approval-gated. No discovery listing or route is itself training approval or proof of learning.
