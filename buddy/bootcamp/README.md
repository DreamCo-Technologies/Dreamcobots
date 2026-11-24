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


## DreamCo-authored lesson factory

External sources are reference inputs, not the curriculum output. Buddy must create an independently authored DreamCo lesson for each selected division/capability gap. A lesson package includes:

- fresh, plain-language explanation and learning objectives
- original worked examples and code or domain examples
- guided, independent, and stretch practice
- a hands-on project with acceptance criteria
- quiz questions with original answer explanations
- sandbox tasks, targeted benchmark, unseen holdout, and regression checks
- accessibility notes, prerequisites, source provenance, and rights status

The lesson contract is `buddy/bootcamp/sources/original-lesson.schema.json`; use `buddy/bootcamp/templates/original-lesson.md` as the authoring template. Validate JSON lesson packages with:

```bash
python tools/validate_original_lesson.py path/to/lesson.json
python -m unittest discover -s tests -p 'test_original_lesson.py' -v
```

The authoring policy forbids copying transcripts, course text, exercises, or answer keys. Public metadata and source links may identify topics; actual source material may be used only within the applicable permission. Mark every lesson with provenance and rights review. Training DreamCo model weights on source-derived material remains disabled unless a separate rights approval explicitly permits it. Original DreamCo-authored lesson assets can be stored and reused under DreamCo's own content policy, subject to review.


## Daily original-lesson production target

The daily target is five original DreamCo lesson packages per division (65 divisions; 325 planned slots per UTC day). The scheduled workflow builds a metadata-only work plan. A slot remains `queued_not_created` until an actual lesson has original explanations, worked examples, practice, an assessment and answer key, source provenance, a rights review, schema validation, sandbox results, target and holdout benchmarks, and regression evidence. The planner does not count placeholders as lessons and does not claim that a target has been met merely because the workflow ran.

Run locally:

```bash
python tools/build_daily_lesson_plan.py --lessons-per-division 5
python -m unittest discover -s tests -p 'test_daily_lesson_plan.py' -v
```

## Permissioned study worker and temporary-file lifecycle

All study adapters that create temporary working files must execute through `buddy.learning.permissioned_study_worker.run_study_attempt` (or the source adapter's `execute_study_plan`). The callback receives an attempt-scoped workspace and an explicit allowlist of operations. The workspace is erased in a `finally` block on normal completion, exceptions, and cancellation. The callback must place every temporary download, extracted file, and scratch artifact inside that workspace. Do not write media to the repository, shared caches, workflow artifacts, or persistent runner directories. Keep only original DreamCo-authored lesson content, learner notes intended for retention, rights/provenance records, hashes, and benchmark evidence outside the workspace.

The freeCodeCamp catalog remains metadata-only. Its plans explicitly prohibit media downloads and transcript ingestion. A download or transcript operation is rejected unless the source is rights-approved and a rights evidence reference is supplied. Model training is always a separate permission and remains disabled by this worker. The daily plan artifact contains task metadata only, never course media.

## Ownership and third-party rights

DreamCo should retain records showing who authored each original lesson and when. DreamCo may claim rights in original expression it creates, subject to applicable law, agreements, and the actual authorship of the work. That does not transfer ownership of third-party course materials. Source links, attribution, license terms, permission evidence, and restrictions remain attached to each lesson. Public availability, a YouTube upload, or another creator's reuse does not by itself grant permission to copy, download, redistribute, or train on that material. When source permissions are uncertain, use only permitted metadata and independently written explanations/examples, and leave media, transcript, redistribution, and model-training gates closed until reviewed.
