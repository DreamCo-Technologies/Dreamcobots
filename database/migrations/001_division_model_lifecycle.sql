-- DreamCo per-division lifecycle schema migration template.
-- {schema} is substituted only from canonical MasterBot IDs 001..065.
CREATE TABLE IF NOT EXISTS {schema}.schema_migrations (
    version text PRIMARY KEY,
    migration_sha256 char(64) NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {schema}.dataset_catalog (
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
    ON {schema}.dataset_catalog (content_sha256);

CREATE TABLE IF NOT EXISTS {schema}.model_registry (
    model_name text NOT NULL,
    model_version text NOT NULL,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    manifest jsonb NOT NULL,
    manifest_sha256 char(64) NOT NULL,
    weights_sha256 char(64),
    tokenizer_sha256 char(64),
    lifecycle_state text NOT NULL DEFAULT 'SPECIFIED_NOT_TRAINED',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (model_name, model_version),
    CHECK (jsonb_typeof(manifest) = 'object')
);

CREATE TABLE IF NOT EXISTS {schema}.training_jobs (
    job_id text PRIMARY KEY,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    idempotency_key text NOT NULL UNIQUE,
    status text NOT NULL CHECK (status IN ('QUEUED','LEASED','RUNNING','COMPLETED','FAILED','DEAD_LETTER','CANCELLED')),
    manifest jsonb NOT NULL,
    manifest_sha256 char(64) NOT NULL,
    approval_ref text NOT NULL,
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 20),
    available_at timestamptz NOT NULL DEFAULT now(),
    locked_by text,
    lease_expires_at timestamptz,
    last_error_type text,
    result jsonb,
    result_sha256 char(64),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(manifest) = 'object'),
    CHECK (result IS NULL OR jsonb_typeof(result) = 'object')
);
CREATE INDEX IF NOT EXISTS training_jobs_claim_idx
    ON {schema}.training_jobs (status, available_at, created_at);
CREATE INDEX IF NOT EXISTS training_jobs_lease_idx
    ON {schema}.training_jobs (lease_expires_at)
    WHERE status IN ('LEASED','RUNNING');

CREATE TABLE IF NOT EXISTS {schema}.benchmark_runs (
    run_id text PRIMARY KEY,
    plan_id text NOT NULL,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    model_name text NOT NULL,
    model_version text NOT NULL,
    holdout_sha256 char(64) NOT NULL,
    evidence jsonb NOT NULL,
    evidence_sha256 char(64) NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(evidence) = 'object')
);
CREATE INDEX IF NOT EXISTS benchmark_runs_model_idx
    ON {schema}.benchmark_runs (model_name, model_version, created_at);

CREATE TABLE IF NOT EXISTS {schema}.teacher_student_lineage (
    lineage_id text PRIMARY KEY,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    teacher_model_id text NOT NULL,
    teacher_revision text NOT NULL,
    student_model_name text NOT NULL,
    student_model_version text NOT NULL,
    dataset_id text NOT NULL,
    rights_evidence text NOT NULL,
    output_use_permission boolean NOT NULL DEFAULT false,
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(manifest) = 'object')
);

CREATE TABLE IF NOT EXISTS {schema}.resource_usage (
    usage_id text PRIMARY KEY,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    job_id text,
    cpu_seconds numeric(18,6) NOT NULL DEFAULT 0,
    gpu_seconds numeric(18,6) NOT NULL DEFAULT 0,
    peak_memory_bytes bigint,
    storage_bytes bigint,
    generated_tokens bigint NOT NULL DEFAULT 0,
    cost_usd numeric(18,8) NOT NULL DEFAULT 0,
    evidence jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(evidence) = 'object')
);

CREATE TABLE IF NOT EXISTS {schema}.queue_events (
    event_id text PRIMARY KEY,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    job_id text NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(payload) = 'object')
);
CREATE INDEX IF NOT EXISTS queue_events_job_idx
    ON {schema}.queue_events (job_id, created_at);

CREATE TABLE IF NOT EXISTS {schema}.audit_events (
    event_id text PRIMARY KEY,
    masterbot_id integer NOT NULL CHECK (masterbot_id BETWEEN 1 AND 65),
    actor_ref text NOT NULL,
    approval_ref text,
    event_type text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(payload) = 'object')
);
CREATE INDEX IF NOT EXISTS audit_events_type_idx
    ON {schema}.audit_events (event_type, created_at);

-- Enforce division isolation for all tenant-scoped tables. Runtime roles must
-- set this transaction-locally from authenticated server-side identity.
ALTER TABLE {schema}.dataset_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.dataset_catalog FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.dataset_catalog;
CREATE POLICY division_scope ON {schema}.dataset_catalog
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.model_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.model_registry FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.model_registry;
CREATE POLICY division_scope ON {schema}.model_registry
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.training_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.training_jobs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.training_jobs;
CREATE POLICY division_scope ON {schema}.training_jobs
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.benchmark_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.benchmark_runs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.benchmark_runs;
CREATE POLICY division_scope ON {schema}.benchmark_runs
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.teacher_student_lineage ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.teacher_student_lineage FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.teacher_student_lineage;
CREATE POLICY division_scope ON {schema}.teacher_student_lineage
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.resource_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.resource_usage FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.resource_usage;
CREATE POLICY division_scope ON {schema}.resource_usage
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.queue_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.queue_events FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.queue_events;
CREATE POLICY division_scope ON {schema}.queue_events
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

ALTER TABLE {schema}.audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.audit_events FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS division_scope ON {schema}.audit_events;
CREATE POLICY division_scope ON {schema}.audit_events
 USING (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer)
 WITH CHECK (masterbot_id = nullif(current_setting('dreamco.masterbot_id', true), '')::integer);

REVOKE ALL ON ALL TABLES IN SCHEMA {schema} FROM PUBLIC;
