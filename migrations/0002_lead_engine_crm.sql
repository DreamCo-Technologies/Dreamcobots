-- DreamCo Lead Engine owner-scoped CRM persistence.
-- Application transactions must SET LOCAL app.owner_id before accessing these tables.
CREATE TABLE IF NOT EXISTS lead_engine_records (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  lead_id TEXT NOT NULL,
  organization_name TEXT NOT NULL,
  stage TEXT NOT NULL CHECK (stage IN ('attract','capture','qualify','nurture','convert')),
  qualification_score INTEGER NOT NULL DEFAULT 0 CHECK (qualification_score BETWEEN 0 AND 100),
  qualification_tier TEXT NOT NULL DEFAULT 'cold' CHECK (qualification_tier IN ('hot','warm','cold')),
  suppression_status TEXT NOT NULL DEFAULT 'active'
    CHECK (suppression_status IN ('active','opted_out','replied','bounced','complaint','owner_blocked')),
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT lead_engine_records_owner_lead_uq UNIQUE (owner_id, lead_id)
);
CREATE INDEX IF NOT EXISTS lead_engine_records_owner_stage_idx
  ON lead_engine_records (owner_id, stage);
CREATE INDEX IF NOT EXISTS lead_engine_records_owner_updated_idx
  ON lead_engine_records (owner_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS lead_engine_activities (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  lead_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN (
    'lead_created','stage_changed','qualification_updated','consent_updated',
    'suppression_changed','owner_note','proposal_handoff','conversion_recorded'
  )),
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT lead_engine_activities_owner_event_uq UNIQUE (owner_id, event_id),
  CONSTRAINT lead_engine_activities_owner_lead_fk
    FOREIGN KEY (owner_id, lead_id)
    REFERENCES lead_engine_records (owner_id, lead_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS lead_engine_activities_owner_lead_time_idx
  ON lead_engine_activities (owner_id, lead_id, created_at DESC);

ALTER TABLE lead_engine_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_engine_records FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS lead_engine_records_owner_isolation ON lead_engine_records;
CREATE POLICY lead_engine_records_owner_isolation ON lead_engine_records
  USING (owner_id = NULLIF(current_setting('app.owner_id', true), ''))
  WITH CHECK (owner_id = NULLIF(current_setting('app.owner_id', true), ''));

ALTER TABLE lead_engine_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_engine_activities FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS lead_engine_activities_owner_isolation ON lead_engine_activities;
CREATE POLICY lead_engine_activities_owner_isolation ON lead_engine_activities
  USING (owner_id = NULLIF(current_setting('app.owner_id', true), ''))
  WITH CHECK (owner_id = NULLIF(current_setting('app.owner_id', true), ''));

-- Activity history is append-only. Retention/deletion is handled by a separately
-- authorized data-rights workflow, not by normal CRM activity updates.
CREATE OR REPLACE FUNCTION reject_lead_engine_activity_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'lead engine activity history is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS lead_engine_activities_append_only ON lead_engine_activities;
CREATE TRIGGER lead_engine_activities_append_only
  BEFORE UPDATE OR DELETE ON lead_engine_activities
  FOR EACH ROW EXECUTE FUNCTION reject_lead_engine_activity_mutation();
