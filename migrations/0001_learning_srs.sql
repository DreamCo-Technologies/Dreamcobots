-- Buddy shared spaced-repetition persistence.
-- Review history and mastery evidence are append-only; card state is mutable.
CREATE TABLE IF NOT EXISTS learning_review_history (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL,
  learner_id TEXT NOT NULL,
  deck_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  division_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  scheduler_name TEXT NOT NULL,
  scheduler_version TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4),
  reviewed_at TIMESTAMPTZ NOT NULL,
  due_at TIMESTAMPTZ NOT NULL,
  prior_state JSONB NOT NULL,
  resulting_state JSONB NOT NULL,
  predicted_retrievability DOUBLE PRECISION CHECK (
    predicted_retrievability IS NULL OR
    (predicted_retrievability >= 0 AND predicted_retrievability <= 1)
  ),
  actual_recall BOOLEAN NOT NULL,
  desired_retention DOUBLE PRECISION,
  scheduler_config JSONB NOT NULL DEFAULT '{}'::jsonb,
  parameter_set_id TEXT,
  provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT learning_review_history_event_id_uq UNIQUE (event_id)
);
CREATE INDEX IF NOT EXISTS learning_review_history_learner_item_time_idx
  ON learning_review_history (learner_id, deck_id, item_id, reviewed_at, event_id);

CREATE TABLE IF NOT EXISTS learning_card_states (
  id BIGSERIAL PRIMARY KEY,
  learner_id TEXT NOT NULL,
  deck_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  division_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  scheduler_name TEXT NOT NULL,
  scheduler_version TEXT NOT NULL,
  state JSONB NOT NULL,
  due_at TIMESTAMPTZ NOT NULL,
  last_reviewed_at TIMESTAMPTZ NOT NULL,
  desired_retention DOUBLE PRECISION CHECK (
    desired_retention IS NULL OR (desired_retention > 0.70 AND desired_retention < 0.97)
  ),
  parameter_set_id TEXT,
  latest_event_id TEXT NOT NULL REFERENCES learning_review_history(event_id),
  replay_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT learning_card_states_learner_deck_item_uq UNIQUE (learner_id, deck_id, item_id)
);
CREATE INDEX IF NOT EXISTS learning_card_states_learner_due_idx
  ON learning_card_states (learner_id, due_at);

CREATE TABLE IF NOT EXISTS learning_mastery_evidence (
  id BIGSERIAL PRIMARY KEY,
  evidence_id TEXT NOT NULL,
  learner_id TEXT NOT NULL,
  deck_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  division_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  benchmark_id TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  score DOUBLE PRECISION,
  verified_at TIMESTAMPTZ NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT learning_mastery_evidence_evidence_id_uq UNIQUE (evidence_id)
);
CREATE INDEX IF NOT EXISTS learning_mastery_evidence_learner_item_idx
  ON learning_mastery_evidence (learner_id, deck_id, item_id);

CREATE OR REPLACE FUNCTION reject_learning_evidence_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'learning evidence ledgers are append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS learning_review_history_append_only ON learning_review_history;
CREATE TRIGGER learning_review_history_append_only
  BEFORE UPDATE OR DELETE ON learning_review_history
  FOR EACH ROW EXECUTE FUNCTION reject_learning_evidence_mutation();

DROP TRIGGER IF EXISTS learning_mastery_evidence_append_only ON learning_mastery_evidence;
CREATE TRIGGER learning_mastery_evidence_append_only
  BEFORE UPDATE OR DELETE ON learning_mastery_evidence
  FOR EACH ROW EXECUTE FUNCTION reject_learning_evidence_mutation();
