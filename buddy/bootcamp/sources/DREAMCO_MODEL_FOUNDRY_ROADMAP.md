# DreamCo Model Foundry: owner-controlled training roadmap

## What we are building

DreamCo trains model weights from random initialization. No pretrained base model is silently imported. The owner controls the training code, model configuration, tokenizer strategy, local data, checkpoints, evaluation records and release decision. The first implementation is a small byte-level decoder-only research model; the existing 45,038,208-parameter division configurations remain architecture blueprints until a real run produces checkpoint hashes and evaluation evidence.

## FreeCodeCamp course concepts to implement

Reference: [Build and Train a 25M Parameter LLM From Scratch on Your CPU](https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu/) (October 8, 2026).

The published course outline covers random-initialized pretraining, next-token cross-entropy, a compact byte-level vocabulary, hybrid linear/sparse attention, Mixture of Experts (MoE), tied embeddings, multimodal image-patch inputs, code generation evaluated by automated unit tests, a lightweight reinforcement-learning reward loop, and experiments across temperatures, reward functions and multiple random seeds.

The current DreamCo trainer implements the foundation: byte-level, randomly initialized, causal next-token training with train/validation/untouched-holdout partitions and checkpoint provenance. It does **not** yet implement MoE, hybrid linear/sparse attention, image-patch multimodality, or reinforcement learning. Those are explicit subsequent engineering phases, not completed features.

## Parallel division design

The 65-division registry is the source of truth. Each eligible division receives its own dataset scope, deterministic seed, strategy assignment, checkpoint and evidence record. The planner creates one job per eligible division and recommends bounded concurrency of four jobs on an owner-controlled runner. This is parallel job scheduling, not a claim that all 65 jobs have already trained or that one computer has unlimited capacity.

Nine initial training profiles vary sequence length, batch size and learning rate: domain-adaptive pretraining, code/tool sequences, instruction-response sequences, classification/extraction-formatted text, retrieval/grounded-generation text, time-series text, simulation/planning text, safety/policy text and scientific-reasoning text. They currently share a causal next-token objective and small common decoder architecture. Distinct classification heads, retrieval losses, true time-series objectives and multimodal objectives require additional task-specific implementations before certification.

## Data ownership and license gate

The empty manifest at `config/authorized-training-datasets/manifest.json` is intentional. Add only datasets whose provenance and rights are documented. Keep actual text files outside the Git checkout in `$HOME/DreamCo-private-data` (or set `DREAMCO_AUTHORIZED_DATA_ROOT`). Manifest paths are relative to that directory.

Every approved entry must include a unique dataset ID and relative local path; exact SHA-256; owner and owner-attestation reference; license ID and license evidence reference; `rights_status: APPROVED`; explicit `training`, `commercial_model_use`, and `derivative_models` permissions; and division IDs approved to use the data.

Missing, unknown, mismatched or unapproved rights are blocked. Public availability does not count as training permission. Keep client data, personal data and secrets out unless separately authorized and protected. Redistribution is a separate permission; model ownership does not grant redistribution rights over source data.

## Two-week sprint acceptance gates

1. Days 1–2: private runner, data directory, owner-authored corpus, provenance and license manifest; verify exact hashes.
2. Days 3–4: repeatable random-init CPU run; record seed, code revision, config and checkpoint hash.
3. Days 5–7: train/validation/untouched-holdout evaluation, checkpoint reload, deterministic rerun and baseline benchmarks.
4. Days 8–10: expand strategy lanes and run eligible divisions concurrently with bounded compute; keep ineligible divisions explicitly blocked.
5. Days 11–12: add code-task execution/reward evaluation and multi-seed significance checks.
6. Days 13–14: architecture research for MoE, sparse/linear attention and image-patch inputs; publish only models with reproducible evidence and a reviewed model card.

The two-week deliverable is a working, measurable owner-controlled training system and experimental checkpoints for divisions with approved data and compute. It is not a promise that 65 specialized models will reach frontier capability in two weeks.

## Private execution

The Model Foundry workflow uses a self-hosted GitHub Actions runner labelled `dreamco-private-training`. It does not upload training corpora or model checkpoints as repository artifacts. Checkpoints are written to `$HOME/DreamCo-models` on that runner. A runner must be installed, secured and labelled by the repository owner before manual training dispatch can execute.