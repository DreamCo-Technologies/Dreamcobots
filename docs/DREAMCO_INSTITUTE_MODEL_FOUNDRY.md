# DreamCo Institute — Turnkey AI Model Foundry & Curriculum-in-a-Box

## Commercial positioning
DreamCo Institute sells untrained architecture blueprints and the tools/curriculum to build models, not a store of pretrained weights. A DIY kit includes an architecture specification, tokenizer workflow, division curriculum, clean-room data admission contract, training recipes, hardware preflight, evaluation gates and reproducibility/packaging guidance.

The initial catalog is generated from the canonical 65-MasterBot registry with three tiers: 45M Edge, 350M Workstation and 1B Sovereign (195 SKUs).

## Product tiers
| Tier | Intended environment | Included assets |
|---|---|---|
| 45M Edge | CPU experimentation, edge GPU, Raspberry Pi/Jetson exploration | 45,040,128-parameter target config, tokenizer workflow, domain curriculum, contract/routing holdouts |
| 350M Workstation | Workstation GPU or Apple Silicon; memory-efficient fine-tuning | 349,996,032-parameter target config, multi-division curriculum, SFT/DPO recipes, quantized packaging plan |
| 1B Sovereign | Larger consumer/pro GPU or multi-GPU | 1,020,086,272-parameter target config, sequence-packing plan, Buddy orchestration curriculum, 65-division holdout plan |

The architecture estimator counts the declared bias-free Llama-style embeddings, attention projections, SwiGLU projections and normalization weights. It is a config-derived estimate; the actual instantiated model tensor count must be independently checked before sale.\n\nHardware labels are guidance, not guarantees. Memory depends on context length, batch size, optimizer states, activation checkpointing, precision, quantization, framework overhead and whether the buyer is pretraining or parameter-efficiently fine-tuning. Full pretraining can require substantially more memory than inference.

## Rights, clean-room and ownership
- Blueprint kits contain no pretrained weights. Manifests state weights_included=false and weights_status=UNTRAINED_BLUEPRINT_READY_FOR_TRAINING.
- Dataset admission requires a specific rights status, explicit training approval, source evidence, local snapshot path and SHA-256. Public availability is not training permission.
- Unknown, missing or disputed rights block ingestion and training. Buyer-private data stays on buyer-controlled infrastructure by default.
- Clean-room claims are scoped to recorded provenance of architecture, source materials and training run; they are not blanket legal guarantees. Third-party dependencies retain their own licenses and terms.
- Buyer ownership and zero DreamCo royalties are product-contract terms that must appear in the executed agreement; they do not erase third-party obligations.
- No benchmark result may be marketed until an actual trained artifact is hashed and evaluated against an independent, isolated holdout suite.

## Lifecycle
1. Select division and tier.
2. Generate buyer kit and inspect manifest.
3. Detect hardware and review estimated fit.
4. Admit only buyer-owned or explicitly licensed datasets with documented training permission.
5. Train using an approved, pinned backend and immutable run configuration.
6. Record dataset, tokenizer, config, code and checkpoint hashes.
7. Evaluate development data and private holdouts separately; expected answers never enter model inputs.
8. Run safety/regression gates and independent review.
9. Only then issue a verified checkpoint/model card and list a premium pretrained upgrade.

The initial train_my_agent.py is a fail-closed preflight, not a functioning training engine. It does not download packages, upload buyer data, start paid compute or execute training. A backend adapter must be separately implemented and reviewed before training is enabled.

## Commands
Generate the 195-SKU catalog only:
    python scripts/dreamco_model_foundry.py --catalog-only

Generate all 195 buyer-kit folders:
    python scripts/dreamco_model_foundry.py

Generate one buyer kit:
    python scripts/dreamco_model_foundry.py --division-id 1 --tier 45m-edge

Hardware and buyer preflight:
    python scripts/dreamco_hardware_detector.py
    python scripts/train_my_agent.py --kit commercial_kits/dreamco_001_dreamfinance_45m-edge_kit

## Verification
    python -m unittest tests.test_dreamco_model_foundry -v
    python scripts/dreamco_model_foundry.py --catalog-only

A generated catalog or kit is a product specification, not evidence that a model was trained, benchmarked, certified, deployed or legally cleared.
