# Local Buddy Model Blueprint

This blueprint defines a practical local-first path for a small DreamCo language model. It does not claim a trained model exists until checkpoints and benchmark evidence are committed or referenced.

## Architecture
- Decoder-only Transformer.
- Token embeddings with tied output projection.
- RoPE positional encoding.
- Pre-normalization with RMSNorm.
- Multi-head self-attention with grouped-query attention (GQA).
- SwiGLU MLP blocks.
- Causal attention mask.
- Optional Flash/SDPA attention when supported by the local runtime.

## Tokenizer
Train SentencePiece Unigram or BPE on DreamCo-permitted text. Keep tokenizer training data separate from evaluation data. Preserve vocabulary version, normalization settings, special tokens, source provenance, and hashes.

## Training stages
1. Data audit, deduplication, provenance, and license checks.
2. Train/validation split by source to reduce leakage.
3. Tokenizer training.
4. Lightweight pretraining or continued pretraining.
5. Validation and held-out transfer evaluation.
6. Lightweight supervised fine-tuning (SFT) using a versioned DreamCo chat format.
7. Regression suite and safety checks.
8. Optional quantization for local deployment.

## Minimal dependency goal
Keep the reference implementation based on Python, PyTorch, SentencePiece, and standard-library utilities. Optional acceleration packages must have graceful fallbacks.

## Local-first rule
Training and inference must work on one user's device without distributed training. CPU is the compatibility baseline; Apple Metal/MPS, CUDA, and ROCm are optional accelerators. Quantized inference is preferred for constrained hardware.

## Chat format
Use explicit role tokens:
`<system>`, `<user>`, `<assistant>`, `<eos>`.
Keep an optional JSON-output mode controlled by configuration rather than forcing JSON on ordinary chat.

## Overfitting controls
Use source-level splits, deduplication, held-out transfer tasks, validation-loss monitoring, early stopping, and regression testing. Do not train against benchmark test sets.

## Parameter target
The reference configuration targets approximately 500M parameters. That is an engineering target, not a statement that Buddy currently has 500M trained parameters. A smaller local profile should remain available for phones/laptops and low-memory devices.

## Benchmark interpretation
A local model can be optimized for speed, cost, and educational value without claiming parity with frontier hosted models. Report parameter count, hardware, quantization, context length, training data scope, and benchmark revision with every result.
