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


## Complete freeCodeCamp routing into Buddy's live study scheduler

The full source-route manifest is generated with `python tools/build_freecodecamp_routes.py`. It keeps one route record for every discovered video and grants all 65 divisions catalog access; subject tags add specialty recommendations without hiding the shared catalog. Unclassified items remain discoverable through a review lane.

Buddy's runtime adapter is `buddy.learning.freecodecamp_source`:

- `resources_for_division(division_id)` returns every catalog candidate for that division.
- `select_next_for_division(division_id, capability_gaps, recent=...)` delegates next-lesson selection to the existing evidence-driven study scheduler.
- Each resource points to the original official source and prescribes original notes, sandbox practice, target benchmark, holdout, and regression steps.

This is a real route into the scheduler, not an automatic video-watching claim. The scheduler selects a lesson; a worker or learner must open the official source and complete the study and practice steps. Video/audio downloads, transcript ingestion, and model training remain disabled unless separately authorized. The CI workflow regenerates and validates the complete route manifest and runs the adapter tests.


## Temporary study-download cleanup

If an authorized study worker needs temporary files, it must create an attempt-scoped workspace with `buddy.learning.study_artifact_cleanup.study_download_workspace(base_dir)`. The context manager removes that workspace in a `finally` block after success, failure, or cancellation. It refuses paths outside the configured managed root and does not follow symlink workspaces.

Example:

```python
from pathlib import Path
from buddy.learning.study_artifact_cleanup import study_download_workspace

with study_download_workspace(Path("/tmp/dreamco-study")) as workspace:
    # Any permitted, temporary study files live only here.
    run_authorized_study_step(workspace)
# The workspace and its temporary files are erased here.
```

Keep learning evidence, provenance, benchmark results, and original learner-authored notes in the approved evidence store outside this temporary directory. Do not upload media or temporary study files as GitHub Actions artifacts or commit them to the repository. The current freeCodeCamp catalog workflow reads metadata only; it does not download lesson media. GitHub-hosted runner files are also discarded when each job's ephemeral runner is torn down.

The cleanup helper is covered by tests for normal completion, exceptions, idempotence, and refusal to delete paths outside its managed workspace. A study worker must use this context manager for its temporary files; adding the helper does not imply that a video-watching worker is already running.
