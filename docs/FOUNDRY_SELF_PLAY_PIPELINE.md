# DreamCo self-play and fast foundry cache

## What this workflow does

`.github/workflows/foundry_fast_train.yml` runs a bounded, train-only self-play batch. It:

1. Verifies the Ed25519-signed authorization manifest and every referenced dataset digest.
2. Caches the tokenizer and packed train/validation shards using the recipe, signed-manifest and preprocessing-code fingerprints.
3. Loads an already-existing local checkpoint and generates a bounded number of rollouts from authorized `verified_trajectories` records whose deterministic split is `train`.
4. Executes candidate Python only inside a rootless Docker container with networking disabled, a read-only root filesystem, dropped capabilities, a non-root UID, CPU/memory/PID limits and a hard timeout.
5. Uploads raw rollout evidence plus quarantined DPO, GRPO and SFT candidate files as a workflow artifact.

The workflow does **not** train weights, merge adapters, update the repository, or promote a checkpoint. It has read-only repository permissions. Candidate records are explicitly marked `eligible_for_training: false`; teach-back is always `NOT_VERIFIED` until a human reviewer supplies the required evidence.

## Runner and repository prerequisites

The job uses a dedicated runner with the label:

`self-hosted, linux, x64, dreamco-rootless-sandbox`

That runner must have a working rootless Docker daemon. The sandbox image is built from `stages/05_model_foundry/Dockerfile.selfplay` during the job. A regular GitHub-hosted runner with a rootful Docker daemon is deliberately not accepted for executing model-generated code.

The workflow expects:

- `data/clean_room/authorization_manifest.json` containing a policy-owner-approved manifest with a `verified_trajectories` dataset.
- Repository secrets `DREAMCO_SOURCE_MANIFEST_SIGNATURE_B64` and `DREAMCO_POLICY_PUBLIC_KEY_PEM`.
- An existing local checkpoint directory with safetensors weights outside the GitHub checkout workspace (default: `/opt/dreamco/checkpoints/buddy-division-45m-v1/dpo`), plus the cached/local tokenizer. The checkout action cleans untracked workspace files, so do not store the only checkpoint copy under the repository checkout.
- Every eligible task to have a stable `task_id`, a prompt, an owner-authored `test_suite` that imports `solution` and contains real pytest tests, and optional rubric keywords.

The nightly schedule is 03:00 UTC. If the dedicated runner is offline, GitHub queues the job until a matching runner is available. No paid model API or provider key is used.

## Outputs

The workflow artifact contains:

- `rollouts.jsonl`: individual generated candidates and deterministic sandbox results.
- `dpo_candidates.jsonl`: passing/failed candidate comparisons, still requiring teach-back verification and owner review.
- `grpo_candidates.jsonl`: grouped rollout rewards for later GRPO research; not directly trainable.
- `sft_candidates.jsonl`: sandbox-passing traces, still pending teach-back verification.
- `rollouts.manifest.json`: source/checkpoint/output digests and explicit holdout/training boundaries.

To build final DPO preferences after a reviewer has updated the raw rollout rows with verified teach-back evidence, use the existing `generate_self_play_pairs.py` utility. Its output must then be included in a new, separately signed authorization manifest before a DPO training run. Do not edit the original signed source files in place.

## Important limits

- The script reads only the signed `train` split; it never opens validation or holdout records.
- Test pass is not teach-back verification, legal rights clearance, or model promotion. The grader evidence fingerprint is an unsigned hash, not a digital signature; owner authorization and the signed dataset manifest remain separate gates.
- The GRPO output is a research/evidence format only; a GRPO optimizer stage is not implemented by this workflow.
- The cache is an optimization, not an authorization boundary. Training still requires the signed shard manifest and explicit weight-update approval enforced by the Stage 05 training CLI.
- This is a self-play data-generation workflow, not a claim that Buddy has been trained or improved. Actual training and holdout promotion remain separate, explicitly authorized steps.


## Explicitly authorized training workflow

`.github/workflows/foundry-training-preflight.yml` is separate from nightly self-play. It runs CPU-only compile and guardrail checks on pull requests. Its optional GPU job runs only on manual dispatch when `DREAMCO_GPU_RUNNER_ENABLED=true`, and requires a locally stored policy-owner signing key plus a non-empty training approval reference. It verifies the signed source manifest, builds and signs token shards, and invokes the existing training CLI with explicit optimizer authorization.

The training runner label is `self-hosted, linux, x64, gpu`. It requires the signed source manifest, a separately signed token-shard manifest, local tokenizer/shard cache, a baseline checkpoint, and the local data and protected key material supplied through runner configuration:

- `DREAMCO_FOUNDRY_DATA_DIR` runner variable pointing to the signed manifest and public key
- `DREAMCO_FOUNDRY_POLICY_PRIVATE_KEY_PATH` runner variable pointing to a protected 0400/0600 private key
- `DREAMCO_TRAINING_APPROVAL_REFERENCE` secret containing the owner approval reference
- `DREAMCO_FOUNDRY_BASELINE_CHECKPOINT_PATH` optional baseline checkpoint path

After a successful training run, it evaluates the candidate against the signed holdout suite. If a baseline checkpoint is configured, it compares both reports and blocks promotion on regression. Without a baseline, it records candidate evaluation but explicitly leaves promotion blocked. It uploads artifacts for review; it does not automatically merge an adapter or replace a promoted checkpoint. For a DPO run, the signed authorization manifest must contain reviewed `verified_preferences` records; for `all`, the recipe must have non-empty authorized records for every enabled stage.

This is not a free hosted-GPU service. It uses the configured self-hosted GPU runner so compute, hardware, and private artifacts remain under owner control.
