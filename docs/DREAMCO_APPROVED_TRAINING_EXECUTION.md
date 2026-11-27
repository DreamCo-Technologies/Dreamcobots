# DreamCo approved division training execution

The Transformers runner can now emit training-result evidence that matches the division release gate. This is separate from the five-minute plan-only scheduler.

## Manual execution path

The workflow `DreamCo Division Training Execution` is manual-dispatch only and requires a self-hosted runner labelled:

`self-hosted, linux, x64, gpu, dreamco-training`

Configure the GitHub environment `dreamco-training` with required reviewers and the following secrets:
- `DREAMCO_ALLOW_TRAINING_EXECUTION=1` — explicit execution enable.
- `DREAMCO_ALLOW_MODEL_DOWNLOAD=1` — only when model downloads are separately approved; leave unset/false for cached local weights.

Dispatch requires:
- A job manifest under `artifacts/buddy-training-jobs/*.json`.
- A compute approval reference that exactly matches the manifest.
- A runner with the approved local DatasetHub path and the pinned base model cached, unless model download is separately enabled.
- PyTorch, Transformers, and PEFT installed on the runner.

The runner also needs the immutable tested source commit in `GITHUB_SHA` or the manifest. Base-model and tokenizer revisions must be pinned to 40-character commit SHAs.

## Evidence produced

The execution worker:
1. Re-validates compute approval, dataset card, rights status, dataset SHA-256, split hashes, MasterBot ownership, model license, tokenizer revision, base revision, and tested commit.
2. Executes the bounded SFT/LoRA job using the existing Transformers runner.
3. Hashes the division's trained weights, training checkpoints, and tokenizer files.
4. Copies those artifacts into a run-specific evidence directory and verifies copied hashes.
5. Writes `training-result.json` and `training-evidence-fragment.json`.

The training result contains the fields needed by the release gate: `execution_status=COMPLETED`, `weights_trained=true`, `production_promoted=false`, MasterBot/model identity, dataset ID/version/hash/split manifest, base-model revision, tokenizer revision, tested commit SHA, compute approval reference, checkpoint file manifest, and checkpoint digest.

The result is only `TRAINED_PENDING_BENCHMARK_AND_REVIEW`. It is not a production release. Domain/general/private-holdout/safety/regression benchmarks, runtime health, object storage backup evidence, and independent review remain required.

## Current infrastructure boundary

This first execution workflow expects the local DatasetHub path and model cache to be available on the self-hosted runner. The object-storage upload adapter and per-division PostgreSQL catalog are separate components; their live connection and durable queue integration are not yet configured by this workflow. No self-hosted runner, secrets, or real training job are assumed to exist.
