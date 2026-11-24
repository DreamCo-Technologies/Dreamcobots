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
2. Verify all schemas and owner roles have been provisioned and the migration principal is a member of each matching NOLOGIN owner role.
3. Record a change approval ID and the exact migration SHA-256 from the plan.
4. Set `DREAMCO_POSTGRES_DSN` in a protected environment and `DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS=1`.
5. Run with `--apply --approval-id ... --expected-migration-sha256 ...`.

The apply path validates all 65 schemas and roles before committing DDL, records the migration hash in each schema, and writes an approval-linked audit event. It uses one transaction so any failure rolls back the full 65-schema migration. Re-running an already applied identical hash is a no-op; a changed hash for the same version is blocked.

## Current truth

The migration is code and tests only until an operator runs it against a real PostgreSQL instance with approved credentials. CI uses mocks and does not create production tables. Object storage, live worker credentials, application-role grants, backup/restore verification and real RLS tests remain separate deployment gates.
