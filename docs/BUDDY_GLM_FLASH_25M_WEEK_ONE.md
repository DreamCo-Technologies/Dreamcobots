# Buddy 25M+ parameter experiment: one-week milestone

## Scope
A 25M+ parameter model cannot reproduce GLM-5.3-Flash's broad capabilities by copying a few responses. GLM-5.3-Flash has approximately 320B total / 18B active parameters. This experiment is a **small original Buddy model**, not a compressed copy of GLM's weights or architecture.

## Day-by-day acceptance criteria
1. Review GLM-5.3-Flash's official model card and MIT license, and separately confirm the inference provider's output-training terms. **Do not assume model-weight licensing automatically permits API output distillation.**
2. Gather a locally stored, provenance-recorded, rights-cleared dataset; remove private data and benchmark holdouts. No automatic external scraping.
3. Install PyTorch locally on the user's Mac, verify MPS availability and memory headroom.
4. Create a separate authorization manifest for the exact training split. It must include `dataset_id`, `dataset_sha256`, `license`, `model_id`, `model_revision`, `train_split_sha256`, `holdout_split_sha256`, `compute_profile`, `max_cost_usd: 0`, `owner_approved: true`, `dataset_authorized: true`, and `training_execution_approved: true`. The trainer verifies the SHA-256 hashes of both supplied train and holdout files and rejects identical splits. The manifest is an owner attestation, not independent legal verification.
5. Run the bounded local experiment only after reviewing the authorization manifest: `python -m buddy.certification.train_original_25m --licensed-data /path/to/approved-train.txt --holdout-data /path/to/approved-holdout.txt --authorization /path/to/training-authorization.json --output-dir /path/out --steps 100`. Start with fewer steps if memory constrained.
6. Evaluate on the separate untouched holdout file. Report loss, independent task metrics, hardware, runtime, and reproducible checkpoint hashes.
7. If provider terms permit teacher-output training, add separately reviewed GLM-generated examples with provenance and compare distilled-vs-undistilled students. Otherwise use independently licensed instruction data.
8. Publish evidence of completed experiments and blockers; never declare model GLM-equivalent or production-ready without independent proof.

## Safety and limitations
- The committed trainer does **not** invoke GLM or perform distillation. It is a byte-level transformer training baseline with >25M parameters, and may be slow on a 24GB Mac.
- Training is blocked unless the authorization manifest explicitly approves this run, records a separate holdout file and matching hash, pins a model revision, and sets a zero-dollar local CPU/MPS budget. The trainer never selects CUDA or hosted compute.
- No pretrained weights, model downloads, external inference, cloud compute, or API costs are initiated by this repository code.
- Keep training data and checkpoints outside Git unless explicitly approved and scrubbed; model weights can be large and sensitive.
- A one-week checkpoint is an engineering goal, not a guaranteed outcome or frontier-quality model.
