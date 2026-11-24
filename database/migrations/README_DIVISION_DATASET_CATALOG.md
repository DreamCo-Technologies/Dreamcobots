# Per-division dataset catalog migration

This migration is deliberately operator-applied. The application adapter
`buddy/datasets/postgres_catalog.py` never creates schemas or tables.

For each pre-provisioned `dreamco_division_NNN` schema, apply the following
DDL as that division's approved schema owner (or through the reviewed migration
identity). Replace NNN with the zero-padded canonical MasterBot ID.

```sql
CREATE TABLE IF NOT EXISTS dreamco_division_NNN.dataset_catalog (
    dataset_id text NOT NULL,
    version integer NOT NULL CHECK (version > 0),
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    manifest jsonb NOT NULL,
    manifest_sha256 char(64) NOT NULL,
    content_sha256 char(64),
    created_at timestamptz NOT NULL,
    PRIMARY KEY (dataset_id, version),
    CHECK (jsonb_typeof(manifest) = 'object')
);
CREATE INDEX IF NOT EXISTS dataset_catalog_content_sha_idx
    ON dreamco_division_NNN.dataset_catalog (content_sha256);
ALTER TABLE dreamco_division_NNN.dataset_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE dreamco_division_NNN.dataset_catalog FORCE ROW LEVEL SECURITY;
CREATE POLICY division_dataset_catalog_isolation
    ON dreamco_division_NNN.dataset_catalog
    USING (masterbot_id = current_setting('dreamco.masterbot_id', true)::integer)
    WITH CHECK (masterbot_id = current_setting('dreamco.masterbot_id', true)::integer);
```

Run the DDL separately for all 65 schemas only after Phase 2B provisioning has
been reviewed and the schema owners/least-privilege service roles are confirmed.
Do not grant broad cross-division access. The runtime catalog adapter is division-scoped. Configure one least-privilege DSN per lane using DREAMCO_POSTGRES_DSN_MASTERBOT_001 through DREAMCO_POSTGRES_DSN_MASTERBOT_065. Each credential must have access only to its matching schema/table. Construct PostgresDatasetCatalog(masterbot_id=NNN) for that lane; the adapter resolves only that division's environment variable. A direct DSN is accepted only when the adapter is permanently bound to one canonical masterbot_id, and the adapter rejects attempts to use it for another division.

Do not use the shared DREAMCO_POSTGRES_DSN or DATABASE_URL bootstrap credentials for runtime dataset catalog writes. Those remain reserved for operator-approved read-only probes or schema provisioning. Do not put credentials in the source registry, manifests, artifacts, or logs.

The application must derive the MasterBot identity from authenticated server-side routing, never from an untrusted client field. The database role must have only the required table privileges within its authorized division schema; the RLS policy is an additional defense, not a substitute for per-division credentials.

## Data and lifecycle contract

- This table stores manifests and hashes, not dataset bytes.
- The local SQLite DatasetHub remains the offline/dev catalog until an
  explicitly configured PostgreSQL adapter is selected by deployment policy.
- A manifest version is immutable: reusing a dataset ID/version with a
  different manifest hash is rejected.
- Training approval, rights evidence, split hashes, holdout isolation, and
  privacy review remain required before any training job can consume a record.
- Object storage, ingestion workers, model-serving endpoints, and benchmark
  evidence are separate integrations; this migration does not certify them.
- Back up and restore the catalog before production use, and test RLS with the
  actual non-owner application role before marking a division connected.
