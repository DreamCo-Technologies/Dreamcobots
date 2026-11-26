# Buddy Adaptive Spaced Repetition

**Status:** FSRS-6 adapter, configurable Anki Classic-style profile, Leitner,
SM-2, and append-only SQLite local/offline storage are implemented. PostgreSQL
schema and a SQL migration are included. API/UI integration, Anki release-level
parity fixtures, production migration execution, and learner-data benchmarking
remain acceptance gates; this is not yet certified production-ready.

## Scheduler policy

| Scheduler | Role | Implementation status |
|---|---|---|
| FSRS-6 | Default adaptive scheduler for new decks | Integrated through pinned official `fsrs==6.3.3`; fuzzing is disabled by default for deterministic replay |
| Leitner | Beginner/classroom mode | Implemented; correct advances a box and incorrect returns to box 1 |
| SM-2 | Legacy scheduler compatibility and transparent baseline | Implemented and retained |
| Anki Classic-style | Legacy ease/interval and learning/relearning-step profile | Implemented as a configurable compatibility profile; not claimed to be byte-for-byte parity with a specific Anki release |

The FSRS adapter uses the official Open Spaced Repetition Python implementation,
with the scheduler's JSON serialization for card state and review logs. Its
default desired retention is 0.90 and is configurable per deck. FSRS fuzzing is
off by default so identical event histories and parameter sets replay
deterministically.

## Shared data contract

Every review event preserves:
- stable learner, deck, item and division identifiers;
- UTC review timestamp and client event/idempotency identifier;
- scheduler name and semantic version;
- rating, prior state, resulting state, due date and interval;
- desired retention and parameter-set identifier where applicable;
- predicted retrievability, actual recall outcome and provenance.

The stable learner/deck/item key is shared across divisions. A review in one
division can therefore update the same learner memory used by another division,
while division IDs remain attached for routing and reporting.

## Persistence and offline sync

The local SQLite store applies a versioned schema migration and provides:
- append-only review history with database-enforced update/delete prevention;
- idempotent event ingestion by event ID and payload hash;
- conflict rejection when an event ID is reused with different content;
- deterministic ordering and a replay-required marker for out-of-order offline events;
- current card state and due-item lookup across division memberships;
- a separate append-only mastery-evidence ledger.

PostgreSQL table definitions are in `shared/schema.ts`; the corresponding
idempotent SQL migration is `migrations/0001_learning_srs.sql`. Applying that
migration to a production database is a deployment operation and is not
performed by CI.

## Recall is not mastery

A correct recall event updates the scheduler and records actual recall. It does
**not** award curriculum mastery or certification. Mastery must be written as a
separate benchmark-backed evidence record with its own provenance and review
criteria.

## FSRS optimization gate

Use FSRS-6 scheduling now with the library's published default parameters.
Personalized optimization is intentionally not run on synthetic or insufficient
history. Before enabling optimized parameters:
1. collect eligible, consented learner review histories;
2. retain parameter provenance and optimizer/library version;
3. split training and held-out histories to avoid leakage;
4. benchmark FSRS and SM-2 on identical held-out histories at matched retention;
5. report review load, retention, calibration and confidence intervals.

## Cross-division and operational acceptance

- All divisions use this shared package; no division forks scheduler math.
- Offline clients queue events with stable idempotency IDs; server-side replay is
  required when older events arrive after newer events.
- Short-term learning/relearning steps remain separate from long-term review.
- Time is stored in UTC and rendered in the learner's locale.
- Database API routes, authentication/authorization, UI settings, telemetry,
  concurrency/load tests, Anki version-specific parity fixtures and production
  migration execution remain required before production certification.
