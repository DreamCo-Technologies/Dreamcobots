# User-designated learning assets, division paths and progress

Every completed, rights-cleared Buddy study guide is converted into a structured learning package. The package retains upstream identity, pinned revision, license, attribution and rights evidence, while The user is recorded as the designated owner of independently authored summaries, explanations, exercises, assessments and curriculum organization, subject to applicable law, contributor agreements and upstream source terms.

## User data ownership and permissions

User-provided materials are registered separately in `config/buddy-user-learning-data-manifest.json`. The user remains the owner of their own materials. Each asset has independent consent scopes for study, summary creation, evaluation and model training. Empty manifest means no user files are authorized yet; never infer blanket consent. Respect retention, deletion, privacy and access controls. Do not copy private data into public curriculum artifacts.

## Per-summary learning package

Each approved guide yields:
- Executive and detailed summaries.
- Extracted key knowledge and concepts.
- Prerequisites and learning objectives.
- Ordered study path: read, understand sections, master concepts, inspect examples, practice, test, complete capstone.
- Spaced review schedule (1, 3, 7, 14 and 30 days).
- Division links and assessment requirements.
- Separate retrieval/study eligibility and weight-training eligibility.

A source with study rights but no training rights may be used for permitted study/retrieval only; it must not enter fine-tuning, distillation or other weight-training datasets.

## Division assignment and progress

The organizer creates a per-division curriculum index and initial progress ledger. Buddy's runtime must emit append-only events for assignment, study, lesson completion, quiz, exercise, capstone, mastery and remediation. The initial state is not progress. Five lessons/day is a target, not permission to bypass source review or learner capacity.

Mastery requires a configured score threshold and an independently verified capstone. Reading a summary or embedding a document is not mastery. Every division should report assigned, started, completed, mastered, overdue and remediation counts.

## Model training controls

Training candidates must carry a complete rights manifest, source hashes/revisions, deduplication and privacy checks, a baseline, holdout evaluation, approved compute/budget, versioned checkpoint and rollback plan. Do not run weight updates until a training backend and authorization are configured.

## Current implementation boundary

The organizer consumes existing approved guide JSON files in `data/buddy-study-guides/`. It does not create summaries for missing guides or claim the live Buddy service has assigned/studied them. The weekly workflow emits an auditable empty/partial report when guides are not yet available.
