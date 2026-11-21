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


## Task-routed learning across platforms

When a user requests an outcome, Buddy should decompose it into skills and prerequisites, inspect benchmark gaps, and rank eligible learning resources before choosing a lesson. The route must account for relevance, practice mode, source quality, permissions, license review, and cost. See `task_learning_router.py` for deterministic route selection and `learning_source_catalog.yaml` for the initial cross-platform source inventory.

The router emits a plan; it does not claim that a provider was accessed, a course was completed, a task was executed, or model weights were trained. Provider adapters must independently implement authorization, retrieval, execution, evidence capture, and contract tests. See `docs/BUDDY_TASK_TO_LEARNING_PLATFORM_ROADMAP.md` for the platform capability map and phased implementation plan.

A learning route must never bypass account controls, scrape gated courses, copy proprietary course material, launch paid compute without explicit approval, or train on evaluation holdouts.
