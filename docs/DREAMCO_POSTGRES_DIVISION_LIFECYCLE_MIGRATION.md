# DreamCo PostgreSQL division lifecycle migration

This migration installs the metadata and queue tables needed by the 65 per-division model lifecycles. It does not create schemas or roles; Phase 2B provisioning must already have created each `dreamco_division_NNN` schema and its matching NOLOGIN, non-superuser owner role.

## Tables created in every division schema

- `dataset_catalog`: immutable dataset manifest versions and content hashes.
- `model_registry`: model names/versions, manifest hashes, weight and tokenizer hashes, lifecycle state.
- `training_jobs`: idempotent queue jobs, leases, retry counters, dead-letter states, manifests and results.
- `benchmark_runs`: immutable holdout benchmark evidence.
- `teacher_student_lineage`: teacher/student revision, dataset and rights provenance.
- `resource_usage`: CPU/GPU time, memory, tokens, storage and cost evidence.
- `queue_events` and `audit_events`: append-only operational and approval references.
- `schema_migrations`: applied migration version and exact SHA-256.

All tenant-scoped tables enable and FORCE row-level security. Policies require the application to set `dreamco.masterbot_id` transaction-locally from authenticated server-side identity. The migration grants no application roles and revokes PUBLIC table access; least-privilege grants and RLS tests with real runtime roles are a separate owner-reviewed step.

## Safe application

1. Review the SQL and run `python -m buddy.datasets.migrate_division_lifecycle` for a read-only 65-schema plan.
2. Verify all schemas and owner roles have been provisioned and the migration principal is a member of each matching NOLOGIN, non-superuser, non-BYPASSRLS owner role.
3. Record a change approval ID and the exact migration SHA-256 from the plan.
4. Set `DREAMCO_POSTGRES_DSN` in a protected environment and `DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS=1`.
5. Run with `--apply --approval-id ... --expected-migration-sha256 ...`.

The apply path validates each of the 65 schemas and owner roles, switches to that division's NOLOGIN owner role for its DDL, records the migration hash in that schema, and writes an approval-linked audit event with the original migration principal recorded as the actor. It uses one transaction so any failure rolls back the full 65-schema migration. Re-running an already applied identical hash is a no-op; a changed hash for the same version is blocked.

## Current truth

The migration is code and tests only until an operator runs it against a real PostgreSQL instance with approved credentials. CI uses mocks and does not create production tables. Object storage, live worker credentials, application-role grants, backup/restore verification and real RLS tests remain separate deployment gates.

## Durable training queue contract

After the lifecycle migration has been applied and least-privilege runtime grants/RLS have been verified, `buddy.datasets.postgres_training_queue.PostgresTrainingQueue` provides a division-scoped queue:
- `enqueue` requires a valid training job manifest, matching compute approval, and idempotency key.
- `lease_next` uses `FOR UPDATE SKIP LOCKED`, lease expiry, and bounded attempts so multiple workers do not claim the same job.
- `heartbeat` renews only the active worker's unexpired lease.
- `complete` accepts only a versioned training result with the matching MasterBot ID and trained-weight evidence.
- `fail` records a sanitized error type, applies exponential retry delay, and moves exhausted jobs to `DEAD_LETTER`.
- Queue transitions are recorded in `queue_events`.

The queue adapter does not launch a GPU or train by itself. A trusted worker must lease a job, verify and fetch the approved dataset/model artifacts, execute the explicit Transformers runner, upload immutable artifacts, and then complete the job with the evidence result. The five-minute polling workflow remains disabled until a real self-hosted worker, protected database credentials, object storage, and per-division runtime grants are configured.

## Object storage adapter

`buddy.datasets.object_store.S3ObjectStore` adds immutable, division-scoped S3-compatible storage for dataset objects, trained weights, checkpoints, tokenizers and benchmark evidence. It uses the SDK's standard credential chain (no keys in manifests), requires HTTPS endpoints, bucket versioning and AES-256/KMS default encryption, and verifies SHA-256 metadata on upload and download.

Object keys are derived from canonical MasterBot IDs and content hashes. Upload requires `DREAMCO_ALLOW_OBJECT_STORE_WRITES=1` plus an approval reference; an existing content-addressed key is accepted only when its metadata hash and byte count match. Reads require an authorization reference and matching division prefix. The adapter is covered by mocked tests only; no bucket or credentials have been configured or accessed by CI.

The governed ingestion worker can now accept injected `object_store` and `postgres_catalog` adapters. When both are supplied, it first writes the content-addressed dataset object to the division's encrypted/versioned bucket prefix, then persists the versioned manifest and object key in that division's PostgreSQL schema. A retry after a partial failure reuses the same local content hash and safely retries the object/catalog writes; metadata changes create a new dataset version. PostgreSQL catalog persistence without durable object storage is rejected.
