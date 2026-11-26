# Buddy Adaptive Spaced Repetition

**Status:** implementation in progress. Leitner and SM-2 are implemented locally;
FSRS is the target default but is not yet integrated or certified by this change.

## Product decision

Buddy exposes one shared review-history and scheduling contract across Buddy
Bootcamp, all divisions, and future learning surfaces. Scheduler choice is
versioned per learner/deck so existing schedules can be migrated without
silently changing due dates.

| Scheduler | Intended role | Behavior |
|---|---|---|
| FSRS | Default for new adaptive decks after validated integration | Model-based difficulty, stability and retrievability; configurable desired retention |
| Leitner | Beginner/classroom mode | Correct answers advance boxes; incorrect answers return to box 1 |
| SM-2 | Legacy compatibility and transparent baseline | Per-card ease, interval and repetition state |
| Anki classic | Compatibility profile | SM-2-family scheduling with configurable learning/relearning steps and graduating intervals |

Do not label Anki classic as identical to pure SM-2. Do not claim a fixed review
reduction percentage or universal superiority without a reproducible benchmark
on the same review history and retention target.

## Shared data contract

Every review event must preserve:
- stable learner, deck, item and division identifiers;
- UTC review timestamp and client event/idempotency identifier;
- scheduler name and semantic version;
- rating, prior state, resulting state, due date and interval;
- desired retention and parameter-set identifier where applicable;
- predicted retrievability (when supported), actual recall outcome and provenance.

Review history is append-only. Corrections are compensating events, not edits to
past evidence. Offline clients queue events and synchronize idempotently; the
server is authoritative for conflict resolution and final due dates.

## Persistence model

The production schema should provide the following logical entities:
- `learning_items`: canonical reviewable concepts and content version;
- `learner_memory`: learner/item scheduler state;
- `review_history`: immutable event ledger;
- `learning_schedules`: scheduler version, due date and retention target;
- `mastery_records`: benchmark-backed mastery, kept separate from recall;
- `fsrs_parameters`: optimized, versioned parameters with provenance;
- `learning_recommendations`: explainable next actions.

Use transactional updates for event insertion and state advancement. Enforce
unique idempotency keys and learner/item/scheduler constraints. Store timestamps
in UTC and render them in the learner's locale.

## FSRS integration gate

Use a maintained, version-pinned open-source FSRS implementation; do not
reimplement the FSRS equations from memory. Before enabling it by default:
1. Confirm the selected library API and supported scheduler/model version.
2. Add a thin Buddy adapter with explicit serialization and migration tests.
3. Test Again/Hard/Good/Easy ratings, learning/relearning steps, timezone and
   daylight-saving boundaries, long intervals, invalid history and replay.
4. Verify deterministic replay for a fixed event stream and parameter set.
5. Optimize only from a learner's eligible review history; retain parameter
   provenance and fall back safely when history is insufficient.
6. Make desired retention visible and configurable, with a documented default.
7. Benchmark FSRS and SM-2 on identical held-out review histories at matched
   retention targets; publish review load, retention, calibration and confidence
   intervals rather than unsupported universal percentages.

## Cross-division and operational acceptance

- All divisions call the shared scheduler contract; no division forks the math.
- Recall success is not equivalent to curriculum mastery or certification.
- Keep short-term learning/relearning steps separate from long-term scheduling.
- Record run ID, code revision, scheduler version, parameter version and
  predicted-versus-observed outcomes for every evaluation.
- Include migration, rollback, duplicate-event, offline-sync and concurrency tests.
- Do not claim production readiness until database migrations, API integration,
  UI settings, telemetry, security review and exact-head CI all pass.
