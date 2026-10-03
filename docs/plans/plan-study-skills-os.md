# plan-study-skills-os (draft, local only)

Owner: Grok-Edu-Study-Skills-OS. Status: draft. Nothing below is production ready unless it says so with evidence.
Upstream snapshot: DreamCo-Technologies/Dreamcobots @ 24ca34bd (see evidence/upstream_snapshots/SHAS.txt).

## What already exists upstream
- `buddy/learning/learning_strategies_catalog.json`: spaced_repetition, active_recall, interleaving and others, all status `catalogued`.
- `buddy/learning/study_methods.py`: `spaced_repetition()` returns a fixed day 1/3/7 schedule and a two-pass retained flag. No card state, no intervals, no ease.
- `docs/universal-education-engine.md`: learning loop and mastery rule (repeated success, novel variants, transfer, retention, regression).
- `bots/education-app-bot.md` and `bots/tutoring-matcher.md`: declare SRS, quizzes, tutoring. Both `Production ready: False`.
- `client/src/pages/`: no learner desks. `LearningMatrixPage.tsx` is an ML-methods matrix.

## Components
| # | Component | Builds on | Gap | Priority | Gate / evidence |
|---|---|---|---|---|---|
| 1 | SRS review engine (SM-2, later FSRS) | study_methods.spaced_repetition | No real scheduler | P0 | Unit tests pass; catalog rule still holds. Prototype done locally (8/8 tests). |
| 2 | Review API + storage | server/, shared/ | No card/review tables or routes | P0 | Route tests; review log persisted; no student PII in logs |
| 3 | Pages learn desks: Review, Notes, Exam, Tutor | client/src/pages, website/ | None exist | P1 | Playwright smoke per desk; stub banners until API live |
| 4 | Notes desk (notes to cards) | active_recall | No note model or card generation | P1 | Generated cards reviewed by learner before entering deck |
| 5 | Exam / quiz desk | education-app-bot quiz claim | No quiz runtime | P1 | Holdout items; scoring tests; ties to Edu-Mastery-Scorecards floors |
| 6 | Tutoring loop (Buddy) | universal education engine loop | No loop wired to learner data | P2 | Sandbox transcripts; before/after retention on synthetic learners |
| 7 | Certify Education App Bot SRS claim | bots/education-app-bot.md | Claim with no runtime | P2 | Only after 1 and 2 pass; evidence ledger entry |

## Truth rules
- No `production_ready` flips without linked CI/runtime evidence.
- Synthetic learners only until consent and privacy gates exist.
- Pages desks show a stub banner until wired to a live API.

## Proposed upstream paths
- `buddy/learning/srs/` (from `srs/`)
- `tests/test_buddy_srs_sm2.py` (from `tests/test_sm2.py`)
- `docs/plans/plan-study-skills-os.md` (this file)
