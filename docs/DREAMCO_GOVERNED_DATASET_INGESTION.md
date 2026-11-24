# DreamCo governed dataset ingestion

## Lifecycle
1. Discover dataset metadata from approved source adapters. Discovery is not permission to download or train.
2. An owner reviews dataset card, file-level terms, source provenance, intended training use, privacy, and content rights.
3. Stage a JSONL file. Every row includes canonical `masterbot_id`, `split` (train/validation/test), and `text` or instruction/output.
4. Create a job manifest with `create_ingestion_job(card, source_file, approval_id)`.
5. Execute from a trusted worker only after setting `DREAMCO_ALLOW_DATASET_INGESTION=1` and supplying the matching approval ID.
6. The worker validates division ownership, computes split hashes, runs DatasetHub quality/PII-pattern checks, and stores a content-addressed object and versioned card.
7. Result status is `INGESTED_PENDING_BENCHMARK`; it does not train a model. Baseline/domain benchmark gates must run before training is separately approved.

## Required card evidence
The card needs stable dataset ID, source/source ID, HTTPS source and license URLs, explicit AI training permission, verified content rights, passed privacy review, `rights_status=VERIFIED`, rights evidence reference, `training_approved=true`, canonical primary MasterBot ID, and an approved training data plane.

Only permissive licenses recognized by `buddy/datasets/license_policy.py` are eligible for automated triage. This is not legal advice; owner review remains required. Unknown/custom/non-commercial/share-alike terms remain blocked unless reviewed under a separate policy.

## Safety and limitations
- This worker consumes a local staged JSONL file; it does not download arbitrary URLs.
- A public metadata record or license tag alone never authorizes training.
- Default file-size ceiling is 512 MiB; cross-division rows are rejected.
- Train/validation/test split hashes are computed from the actual file; all three splits must be non-empty.
- DatasetHub runs structure, duplicate-rate, and PII-pattern checks before storage. Pattern scanning is not a complete privacy classifier.
- Repeating the same dataset ID and file hash is idempotent; changed bytes create a new version.
- No model weights are updated and no compute is consumed.
- Remote download adapters, cloud object storage, durable worker queues, dead-letter handling, and end-to-end cloud execution remain separate deployment phases.
