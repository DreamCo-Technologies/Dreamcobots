# Next steps (top 3)

1. Land `buddy/media/sellability_gate.py` + `tests/test_sellability_gate.py` in DreamCo-Technologies/Dreamcobots (same paths). First code that enforces config/buddy-training-data-provenance-policy.json. Built and passing locally (12 tests).
2. Add `movie` and `user_upload` media types to config/buddy_multimodal_learning_fabric.json and docs/multimodal-learning-fabric.md, pointing at the provenance schema (config/buddy_multimodal_provenance_record.schema.json).
3. Wire `combine()` into tools/video_package_compiler.py and the LP/RP/DP package builders so a package cannot be marked sellable unless every input asset passes.

Owner-only: the current GitHub token gets 403 on writes to DreamCo-Technologies/Dreamcobots. Needs a token (or GitHub App) with contents + pull-request write on that repo, or the owner applies the patch.
