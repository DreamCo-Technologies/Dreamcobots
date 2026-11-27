# DreamCo independent division model lifecycle

The canonical MasterBot registry defines 65 divisions. This lifecycle gives every division a distinct versioned model identity, weights directory, checkpoint directory, tokenizer snapshot, dataset lane, benchmark record and serving identity. The registry is a specification: it deliberately reports every division as not trained until real evidence exists.

## Model identity and artifacts

Each division receives `dreamco/{division-slug}-mini`, version `0.1.0`, with isolated paths under `artifacts/division-models/masterbot-NNN-{division-slug}/v0.1.0/`. A common, license-reviewed base model is allowed to reduce cost, but each division's trained SFT weights or LoRA adapter, checkpoints and tokenizer snapshot must be independently stored and hashed. The base model ID and immutable revision remain unset until owner-approved model selection is complete.

## Teacher and student flow

Buddy coordinates the curriculum, routes to approved teachers, reviews generated examples and tracks evidence. A teacher is not presumed to be trained or connected. Provider calls require explicit per-request paid approval; local teachers require pinned model revisions and license review. Teacher outputs are untrusted candidates, not ground truth. Dataset provenance, output-use rights, quality filtering, deduplication, privacy screening and holdout contamination checks precede student training.

## Training sequence

1. Verify the division's PostgreSQL namespace and least-privilege service identity.
2. Ingest rights-cleared, privacy-reviewed data into that division's dataset lane.
3. Pin train, validation and test manifests and hashes; keep private benchmark holdouts separate.
4. Select an immutable base-model revision and verify its license and hardware requirements.
5. Create a training job with compute approval, division model identity, seed and hyperparameters.
6. Run SFT or LoRA in an isolated worker, save periodic checkpoints, final weights and a division-owned tokenizer snapshot.
7. Record hardware, duration, token counts, memory, cost, training logs, dataset/model hashes and checkpoint hashes.
8. Run independent baseline, domain, general capability, safety, privacy, latency and cost benchmarks.
9. Promote only after review and separate explicit approval; keep previous weights available for rollback.

## Evidence truth

`SPECIFIED_NOT_TRAINED` is the generated starting state. A CI test of the registry proves only that identities and paths are structurally valid. It does not prove a GPU, database, dataset, model download, training run, checkpoint, benchmark or endpoint is available. Never advance lifecycle state without corresponding immutable artifacts and evidence.

## Current scope

This phase adds the 65-division identity registry and checkpoint/evidence-aware training execution contract. It does not provision GPUs, configure paid providers, create production tables, download base models, or launch training. Those require credentials, hardware capacity, rights-reviewed data and explicit compute approval.
