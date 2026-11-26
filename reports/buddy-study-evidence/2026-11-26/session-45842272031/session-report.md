# Buddy Study Evidence Session — 2026-11-26

Status: **Completed with explicit boundaries**

- Session: buddy-study-45842272031-20261126T144609Z
- Executed commit: f325db2ca614d2a17a86d9d960a4f43076043ad6
- PR: https://github.com/DreamCo-Technologies/Dreamcobots/pull/18637
- Workflow run: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45842272031
- Full evidence artifact: https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45842272031/artifacts/15129366177
- Artifact retention ends: 2026-12-26

## Results

| Activity | Result |
|---|---:|
| Canonical domain divisions attempted | 55 / 55 |
| Shared-foundation activity completed | 55 |
| Failed division activities | 0 |
| Specialist mappings awaiting owner review | 55 |
| Proposed exact-name mappings | 45 |
| Unresolved supplemental mappings | 10 |
| Canonical MasterBot lanes reconciled | 65, including 20 shared platform lanes |
| Selected lessons per division | 5 |
| Active recall | 6 / 6 (100%) |
| Held-out assessment | 14 / 14 (100%) |
| First-party glossary terms extracted | 12 |
| Study harness tests | 12 passed |
| Existing byte-BPE trainer tests | 8 passed |

## Lessons selected

1. **tok-06** — Corpus quality and rights
2. **tok-01** — Text-to-token pipeline
3. **tok-04** — Byte-level coverage
4. **tok-11** — Evaluation and fairness
5. **tok-12** — Release and operations

The shared scheduler selected these risk-first lessons for each domain. Each division received a profile-aware provenance packet and a recorded focus area. The session does not claim that each division's specialist business logic was exercised.

## Tokenizer result

- Training source: data/buddy-authorized-corpora/synthetic-ci-corpus.txt
- Source ID: dreamco-synthetic-tokenizer-ci-v1
- Rights evidence: original-synthetic-ci-fixture-no-third-party-content
- SHA-256 of training corpus: 8a81744f145294343b3091292d6f4a11d2a05e317cf8ee15a6825129ebaf278e
- Requested / actual vocabulary: 512 / 512
- Merges: 256
- Tokenizer artifact SHA-256: 7bbce2f0fe513893d94dd285b7f89898e1db9f6046c8c0068edf79be9700d809
- Held-out probes were excluded from fitting and passed exact round-trip checks.
- Neural model weights were not trained or changed; no checkpoint was created.

## Provenance and safety

Only first-party DreamCo instructional material and the synthetic CI fixture were used. The link-only reference section of the study guide was excluded. No external videos, transcripts, gated materials, unknown-rights content, secrets, or paid compute were used.

The active-recall assessment used fixed first-party reference-answer fixtures. It validates the recall questions and scoring mechanics; it is not independent inference by a trained Buddy model.

## Division status

All 55 domain divisions completed the shared-foundation activity. The full per-division status, lesson IDs, focus areas, and individual output hashes are in [division-hashes.json](./division-hashes.json). The input/output hashes, source provenance, assessment scores, test results, failures, and blocker details are in [session-index.json](./session-index.json).

No division mastery was awarded. All 55 specialist mappings remain pending owner review: 45 are proposed exact-name matches and 10 are unresolved. No specialist owner was assigned.

## Remaining blockers

- Specialist ownership and mapping approvals are still required before division-specific curriculum can be promoted.
- This session does not complete the full specialist curriculum or division mastery gates.
- External video/transcript study was not attempted because item-level study and derivative permissions were not verified.
- No neural model-weight training or distillation was performed or authorized.
- Independent Buddy model inference remains unverified; the learner harness is deterministic.

The full artifact contains the tokenizer JSON, glossary, active-recall answers, worked exercises, held-out cases, all 55 detailed division packets, test output, checksums, and machine-readable session evidence. The two repository files above preserve the durable index and all per-division hashes beyond the artifact's retention window.
