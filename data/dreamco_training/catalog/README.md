# DreamCo Training Catalog

This directory is the versioned home for original DreamCo learning assets and rights-cleared dataset manifests.

## Directory contract

- `sources/` — normalized source metadata and provenance records; no bulk copies of third-party course content.
- `lessons/` — original DreamCo lessons and worked examples.
- `labs/` — original hands-on labs, code tasks, simulations, and project briefs.
- `assessments/` — original rubrics, task variants, transfer tests, and locked holdout manifests.
- `datasets/` — versioned manifests for approved training/evaluation datasets, with train/validation/holdout separation.
- `evidence/` — benchmark runs, artifact references, and review decisions.
- `releases/` — immutable catalog snapshots and changelogs.

## Required record fields

Every catalog record must carry a stable ID, title, version, skills, source references, source commit/hash where relevant, ownership class, license/attribution, transformation history, privacy classification, quality review, and publication/training eligibility.

## Ownership defaults

Unknown rights means `unknown_do_not_publish`. Public accessibility is not ownership. A source citation is not a license grant. Third-party course content remains reference-only unless the exact asset's terms permit the intended reuse.

## DreamCo originality standard

A DreamCo lesson must contain original explanations, examples, practice, and assessment. It must not be a copied transcript, course module, slide deck, proprietary exercise, or answer key. Training examples must be derived only from rights-cleared source material or created by DreamCo with documented rights.

## Training state

Catalog creation is not model training. Dataset manifests are not trained weights. Record actual training only when a registered trainer has produced a run ID, checkpoint/adapter artifact, configuration, resource usage, and independent evaluation.
