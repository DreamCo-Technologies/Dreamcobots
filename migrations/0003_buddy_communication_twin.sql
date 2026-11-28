-- Buddy Personal Communication Twin: owner-scoped mobile bridge state.
-- Raw inbound message bodies are never stored. Provider contact IDs are encrypted.
CREATE TABLE IF NOT EXISTS communication_twin_settings (
  owner_id TEXT PRIMARY KEY,
  settings JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mobile_bridge_devices (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('ios','android')),
  provider TEXT NOT NULL CHECK (provider IN ('bluebubbles_mac_relay','android_companion')),
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  source_consent_granted BOOLEAN NOT NULL DEFAULT FALSE,
  secret_reference TEXT NOT NULL CHECK (secret_reference ~ '^[A-Z][A-Z0-9_]{2,127}$'),
  allowed_contact_ids JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(allowed_contact_ids) = 'array'),
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT mobile_bridge_devices_owner_device_uq UNIQUE (owner_id, device_id),
  CONSTRAINT mobile_bridge_devices_provider_platform_ck CHECK (
    (platform = 'ios' AND provider = 'bluebubbles_mac_relay') OR
    (platform = 'android' AND provider = 'android_companion')
  )
);
CREATE INDEX IF NOT EXISTS mobile_bridge_devices_owner_enabled_idx
  ON mobile_bridge_devices (owner_id, enabled);

CREATE TABLE IF NOT EXISTS mobile_bridge_contact_mappings (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  provider_contact_hash TEXT NOT NULL,
  provider_contact_ciphertext TEXT NOT NULL,
  provider_contact_iv TEXT NOT NULL,
  provider_contact_tag TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT mobile_bridge_contact_mapping_owner_device_hash_uq
    UNIQUE (owner_id, device_id, provider_contact_hash),
  CONSTRAINT mobile_bridge_contact_mapping_owner_device_fk
    FOREIGN KEY (owner_id, device_id)
    REFERENCES mobile_bridge_devices (owner_id, device_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS mobile_bridge_contact_mapping_owner_device_contact_idx
  ON mobile_bridge_contact_mappings (owner_id, device_id, contact_id);

CREATE TABLE IF NOT EXISTS mobile_bridge_replay_events (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT mobile_bridge_replay_owner_device_event_uq
    UNIQUE (owner_id, device_id, event_id),
  CONSTRAINT mobile_bridge_replay_owner_device_fk
    FOREIGN KEY (owner_id, device_id)
    REFERENCES mobile_bridge_devices (owner_id, device_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS mobile_bridge_replay_expires_at_idx
  ON mobile_bridge_replay_events (expires_at);

-- This table stores generated reply drafts only, never inbound message bodies.
CREATE TABLE IF NOT EXISTS communication_twin_drafts (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  draft_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  message_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('sms','messaging')),
  draft_body TEXT NOT NULL CHECK (length(draft_body) BETWEEN 1 AND 12000),
  status TEXT NOT NULL DEFAULT 'pending_approval'
    CHECK (status IN ('pending_approval','sending','sent','rejected','delivery_unknown','expired')),
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT communication_twin_drafts_owner_draft_uq UNIQUE (owner_id, draft_id),
  CONSTRAINT communication_twin_drafts_owner_device_message_uq UNIQUE (owner_id, device_id, message_id),
  CONSTRAINT communication_twin_drafts_owner_device_fk
    FOREIGN KEY (owner_id, device_id)
    REFERENCES mobile_bridge_devices (owner_id, device_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS communication_twin_drafts_owner_status_idx
  ON communication_twin_drafts (owner_id, status);

CREATE TABLE IF NOT EXISTS communication_twin_audit_events (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  device_id TEXT,
  action TEXT NOT NULL,
  channel TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  decision TEXT NOT NULL CHECK (decision IN ('allowed','blocked','draft_only')),
  reason TEXT NOT NULL CHECK (length(reason) BETWEEN 1 AND 500),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS communication_twin_audit_owner_time_idx
  ON communication_twin_audit_events (owner_id, created_at DESC);

CREATE TABLE IF NOT EXISTS mobile_bridge_delivery_receipts (
  id BIGSERIAL PRIMARY KEY,
  owner_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  provider_message_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('sms','messaging')),
  status TEXT NOT NULL CHECK (status IN ('accepted','delivered','failed','unknown')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT mobile_bridge_delivery_owner_device_idempotency_uq
    UNIQUE (owner_id, device_id, idempotency_key),
  CONSTRAINT mobile_bridge_delivery_owner_device_fk
    FOREIGN KEY (owner_id, device_id)
    REFERENCES mobile_bridge_devices (owner_id, device_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS mobile_bridge_delivery_owner_time_idx
  ON mobile_bridge_delivery_receipts (owner_id, created_at DESC);

-- Enforce owner isolation even if a future route forgets an explicit owner filter.
DO $$
DECLARE table_name TEXT;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'communication_twin_settings',
    'mobile_bridge_devices',
    'mobile_bridge_contact_mappings',
    'mobile_bridge_replay_events',
    'communication_twin_drafts',
    'communication_twin_audit_events',
    'mobile_bridge_delivery_receipts'
  ] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I', table_name || '_owner_isolation', table_name);
    EXECUTE format(
      'CREATE POLICY %I ON %I USING (owner_id = NULLIF(current_setting(''app.owner_id'', true), '''')) WITH CHECK (owner_id = NULLIF(current_setting(''app.owner_id'', true), ''''))',
      table_name || '_owner_isolation', table_name
    );
  END LOOP;
END $$;

-- Communication audit history is append-only. Deletion remains available through
-- the explicit owner data-rights workflow; updates are never permitted.
CREATE OR REPLACE FUNCTION reject_communication_twin_audit_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'communication twin audit history is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS communication_twin_audit_append_only ON communication_twin_audit_events;
CREATE TRIGGER communication_twin_audit_append_only
  BEFORE UPDATE ON communication_twin_audit_events
  FOR EACH ROW EXECUTE FUNCTION reject_communication_twin_audit_mutation();
