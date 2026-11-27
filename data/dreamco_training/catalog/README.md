# DreamCo Training Catalog

This directory is the versioned home for original DreamCo learning assets and rights-cleared dataset manifests.

## Initial repository inventory

`repository_asset_inventory_seed.json` records **1,223 candidate paths** discovered from a complete Git tree scan at commit `7a74b23732e2bfff03813f00edc8eeb1404fc6fd`. It contains path, blob hash, and file-size metadata only; no file bodies were copied. Every candidate is marked `unknown_do_not_publish`, `rights_review: pending`, and `training_eligible: false` until individual review.

## Directory contract

- `sources/` — normalized source metadata and provenance records; no bulk copies of third-party course content.
- `lessons/` — original DreamCo lessons and worked examples.
- `labs/` — original hands-on labs, code tasks, simulations, and project briefs.
- `assessments/` — original rubrics, task variants, transfer tests, and locked holdout manifests.
- `datasets/` — versioned manifests for approved training/evaluation datasets, with train/validation/holdout separation.
- `evidence/` — benchmark runs, artifact references, and review decisions.
- `releases/` — immutable catalog snapshots and changelogs.

## Current original lesson bundle

`../lessons/universal_task_mastery_lessons_v1.json` contains six original DreamCo lesson drafts linked to the six modules in `../courses/universal_task_mastery_v1.json`. Topics cover task decomposition, rights-aware research, evidence-based debugging, reproducible analytics, safe incident recovery, and professional safety boundaries. The lessons include objectives, authored explanations, worked examples, practice tasks, common failure modes, and assessment rubrics. They are `draft_needs_independent_review` and `not_eligible_until_reviewed_and_split`; do not treat them as certified training or production training data yet.

The catalog builder indexes these lesson IDs and their review status. Run `python3 tools/build_dreamco_training_catalog.py` after changing the lesson library, then inspect the generated `data/dreamco_training/catalog.json` diff before committing it.

## Required record fields

Every catalog record must carry a stable ID, title, version, skills, source references, source commit/hash where relevant, ownership class, license/attribution, transformation history, privacy classification, quality review, and publication/training eligibility.

## Ownership defaults

Unknown rights means `unknown_do_not_publish`. Public accessibility is not ownership. A source citation is not a license grant. Third-party course content remains reference-only unless the exact asset's terms permit the intended reuse.

## DreamCo originality standard

A DreamCo lesson must contain original explanations, examples, practice, and assessment. It must not be a copied transcript, course module, slide deck, proprietary exercise, or answer key. Training examples must be derived only from rights-cleared source material or created by DreamCo with documented rights.

## Training state

Catalog creation is not model training. Dataset manifests are not trained weights. Record actual training only when a registered trainer has produced a run ID, checkpoint/adapter artifact, configuration, resource usage, and independent evaluation.
