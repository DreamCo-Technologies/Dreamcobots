# Buddy Study Evidence Session

- Status: completed_with_boundaries
- Session: buddy-study-45846724922-20261126T151234Z
- Created: 2026-11-26 09:12:34 America/Chicago
- Executed commit: bd3a788c5fd246dd6d757e7f994ee5138a2c9027
- Workflow: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45846724922
- Durable index: `session-index.json`
- Full evidence artifact: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45846724922/artifacts/15131217738
- Artifact ZIP SHA-256: 250b310ad70137ce12ae189ddfdd957e8339aa452d8946ae0796d3ae69b1a43e
- Evidence SHA-256: a6da8dd9184d9f7aa6c9ef3d583d3a4728d62f2718ab6a266d6857f73e250186
- Input source/control files hashed: 17
- Output hashes recorded: 9; checksum files verified: 11

## Division results

- Attempted: 55 of 55 canonical domain divisions
- Completed shared foundation: 55
- Failed: 0
- Whole divisions blocked: 0
- Active-recall subactivity blocked: 55 divisions
- Specialist mappings awaiting owner review: 55 (45 proposed exact-name matches; 10 unresolved)
- Mastery awarded: 0

Every division completed the same five shared-foundation lessons; these are reused activities, not 275 separate specialist lessons. The full per-division IDs, statuses, blocked subactivities, and output hashes are in `division-results.json` inside the evidence artifact and summarized in `session-index.json`.

## Selected shared-foundation lessons

1. `tok-06` — Corpus quality and rights
2. `tok-01` — Text-to-token pipeline
3. `tok-04` — Byte-level coverage
4. `tok-11` — Evaluation and fairness
5. `tok-12` — Release and operations

## Completed evidence

- Glossary: 8 definitions extracted from the first-party study guide with source-line references
- Worked exercises: BPE merge frequency, Unicode NFC/NFKC, role markers, tokenizer compatibility, and vocabulary sweep
- Tokenizer CLI: passed; vocabulary 512; 256 merges
- Held-out checks: 14/14 passed; held-out data was not used for training
- Study harness tests: 15 passed
- Trainer and scheduler tests: 11 passed
- No external materials, secrets, paid compute, or network access were used by the study script

## Blockers and limits

- Active recall: BLOCKED. No learner responses or Buddy inference result were supplied; no score is assigned.
- The repository's local-model configuration is a target configuration, not a trained checkpoint; weight settings report that no weight files are present.
- No neural model weights were trained or changed; no checkpoint hash exists.
- This run proves shared-foundation exercises, not specialist mastery or division-specific business logic.
- Specialist mapping and owner assignment remain pending.

See `session-index.json` for exact input/output hashes, provenance, per-division output hashes, activity scores, tests, blockers, and artifact references.
