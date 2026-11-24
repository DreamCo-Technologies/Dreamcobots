# DreamCo per-division model lifecycle

The generated division model manifest now gives every canonical MasterBot a distinct model ID and a concrete lifecycle plan. The manifest remains plan-only until the evidence fields are populated by real runs.

## Per-division contract

Each of the 65 division records has:
- A stable model ID, a planned first release version, and a current version that remains 0.0.0 until a real checkpoint exists.
- A division-owned adapter or full-weight checkpoint path, with a distinct object-storage key namespace.
- A shared-per-base-model tokenizer rule: the exact tokenizer ID/revision is pinned to the selected base model and its tokenizer files are hashed beside the division checkpoint. A division-specific tokenizer is allowed only after benchmark and migration evidence.
- An SFT plus LoRA/QLoRA default recipe; full fine-tuning only after compute benchmarking; DPO only with separately approved preference data.
- A teacher plan coordinated by Buddy Bootcamp, using only license-verified and pinned teacher models whose output-use terms and data-classification rules allow the intended distillation.
- A schedule policy, domain evaluation plan, private evaluation-only holdout, safety/regression suites, and runtime candidate modes.
- Explicit release evidence slots for data, training, benchmark, runtime, license, and independent review.

## Scheduling semantics

The planner runs every five minutes and rotates a fair-share division lane. A six-hour full-fleet sweep preflights all 65 divisions. These are orchestration and evidence cycles, not a command to retrain every model every five minutes.

Actual weight training is eligible only when a new approved job has:
1. A rights-cleared, versioned dataset with immutable split hashes.
2. A license-verified base model at an immutable revision.
3. A compatible tokenizer revision and recorded hashes.
4. A compute approval and available runner capacity.
5. A per-division training manifest and isolated output/checkpoint namespace.

The current planner workflow still records plan-only lane evidence; it does not itself execute model training. The separate governed Transformers runner can execute an approved manifest when the dataset, model files, compute, and approvals are available. No division is marked trained merely because a schedule fired.

## Model size and growth

The policy uses 25 million parameters as an initial student target and a 25M–500M planning band. Final size is selected only after licensing, memory, throughput, and domain benchmark measurements. This is a planning target, not evidence that a 25M model has already been built.

## Hugging Face coverage and unresolved ownership

The existing taxonomy map covers 37 task families and 10 capability packs across 65 MasterBots, with 55 proposed domain routes. Twenty MasterBot-to-domain mappings and ten standalone domain profiles remain pending owner review. They are deliberately not guessed or auto-assigned. The generated model plan preserves that unresolved status.

## Promotion

A division remains BLOCKED until its exact checkpoint, dataset lineage, test commit, general/domain/private-holdout/safety/regression benchmarks, object storage and backup/restore evidence, runtime health, and independent approval are joined by the release gate. A successful unit test or schedule run is not a trained model.
