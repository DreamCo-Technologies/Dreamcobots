# Buddy Mastery Bootcamp

The bootcamp is a closed-loop learning program for Buddy. It does not claim mastery because a lesson was read; it requires measurable benchmark evidence.

## Daily cycle

1. Inspect benchmark history.
2. Select the largest high-impact capability gap.
3. Choose the study resource with the best expected improvement per minute.
4. Study authorized material.
5. Build a small sandbox exercise.
6. Run the targeted benchmark.
7. If it fails, classify the failure and choose the next prerequisite/resource.
8. If it passes, run an unseen holdout.
9. Run regression tests.
10. Record score delta, time, cost, retries and external calls.
11. Promote only after repeated validated success.

## Graduation

A capability graduates when it repeatedly passes its target benchmark, passes an independent holdout, and introduces no unacceptable regression. Graduation is versioned so a later failure can reopen the capability for study.

## Efficient learning

The bootcamp favors targeted remediation over broad rereading. It uses benchmark failures as the curriculum driver, tracks which resources improve which capabilities, and can reuse authorized evidence for future learners/models without exposing client data or copying restricted external material.


## freeCodeCamp source and division queues

The public freeCodeCamp channel is registered as a metadata-only discovery source at `buddy/bootcamp/sources/freecodecamp/`. The scheduled catalog job discovers public video metadata and assigns multi-label subject tags. It does not download video/audio or scrape transcripts.

Generate deterministic study candidates for the canonical 65 divisions with:

```bash
python tools/sync_freecodecamp_catalog.py
python tools/build_freecodecamp_division_queues.py
python tools/build_freecodecamp_division_queues.py --check
python -m unittest discover -s tests -p 'test_freecodecamp_division_queues.py' -v
```

The generated `config/generated/freecodecamp-division-learning-queues.json` contains up to 30 ranked candidates per division by default. Each division receives shared technical foundations plus explicitly mapped specialty tracks. A division without a defensible specialty mapping receives a foundation-only queue and remains flagged for owner review; the planner does not invent a specialty.

Every queued item starts as `queued_not_studied`. Rights review remains required, and media/transcript ingestion and training eligibility remain false. A queue item can advance only after authorized study material is turned into an original lesson or notes, a sandbox exercise is completed, and targeted, holdout, and regression evidence is recorded. Queue generation itself never changes a model or grants mastery.


Learning evidence is evaluated by `tools/validate_freecodecamp_learning_evidence.py`. Its result distinguishes rights-pending, study-pending, studied-but-unverified, and mastered. Mastery requires verified rights evidence, a study attestation and original-notes hash, a passed sandbox artifact, and separate target, holdout, and regression run IDs. Even a mastered capability record does not authorize training on the source material; training rights remain a separate review.
