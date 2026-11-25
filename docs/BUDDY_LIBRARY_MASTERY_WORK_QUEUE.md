# Buddy library mastery work queue

This queue turns the current 38 ecosystem registry and 531 unique library/technology seed candidates into explicit work items for source verification, original guide authoring, sandbox practice, benchmark design, and review.

## Per-candidate workflow

1. Resolve the canonical package identity and exact ecosystem.
2. Verify the official registry, current version, docs, and source repository.
3. Review license, security advisories, maintenance, and reuse permissions.
4. Inventory the public API for a pinned version with provenance.
5. Write original use cases and at least three exercises.
6. Build a safe local sandbox; do not execute untrusted packages before review.
7. Define a task benchmark, private holdout, and regression evidence.
8. Obtain human review before the guide becomes searchable for Buddy's internal learning.

## Honest inventory boundary

The 531 entries are seed names from DreamCo's existing curated list, not verified package records. The 38 ecosystems are discovery targets, not a complete worldwide registry. Adapter coverage varies; manual-review ecosystems remain manual until an adapter is implemented and tested.

## Rights and security

No package download, code execution, evaluation, or model training is authorized by a seed entry. Unknown licenses and rights remain pending. Buddy must use the universal library registry's approval flow before a guide is searchable or used in training.

## Validate

```bash
python -m pytest -q tests/test_buddy_library_mastery_work_queue.py
python tools/validate_buddy_library_mastery_work_queue.py
```
