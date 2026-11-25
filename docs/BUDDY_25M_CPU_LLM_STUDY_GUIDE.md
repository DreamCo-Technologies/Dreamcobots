# Buddy 25M-Class CPU-First LLM Engineering — Study Guide

**Canonical track:** `buddy-25m-cpu-llm-from-scratch`  
**Status:** 18-module curriculum defined; no Buddy model weights are claimed trained.  
**Coverage:** Shared foundations for all 55 canonical divisions and all 65 MasterBot lanes; specialist ownership still follows the reviewed crosswalk.

## Course references

- [freeCodeCamp: Build and Train a 25M Parameter LLM From Scratch on Your CPU](https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu/)
- [freeCodeCamp YouTube: Build & Train a GLM-5.3-Flash Model From Scratch with Python](https://www.youtube.com/watch?v=-gfgQfw2g_E)
- [Expanded freeCodeCamp GLM-5.3-Flash article](https://www.freecodecamp.org/news/build-and-train-a-glm-53-flash-model-from-scratch-with-python/)
- [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter1/1)
- [Hugging Face Transformers Course](https://huggingface.co/docs/course)

The linked YouTube course is about 44 minutes. Its chapter guide is encoded in `config/buddy-25m-cpu-llm-course.json`. The article/video are study references only: transcript, media, derivative-summary, evaluation, redistribution and model-training permissions are separate. Do not treat a public video or free course as a training license.

## What Buddy must learn

### 1. Research and experiment design
- Ask testable questions and preregister a hypothesis, baseline, primary metric, controls and stopping rule.
- Pin code, data, tokenizer, model configuration, dependency versions and seeds.
- Run multiple seeds, quantify variance and uncertainty, and distinguish statistical from practical significance.

### 2. Tokenization and representations
- Understand UTF-8 bytes, byte-level vocabularies, token IDs, embeddings, vocabulary/sequence-length trade-offs and tokenization fairness.
- The course's 260-token byte-level vocabulary and 192-token context are reference example settings, not universal defaults.
- Compare against BPE, WordPiece and Unigram using the dedicated tokenizer course; require exact round-trip, coverage and multilingual/code tests.

### 3. Transformer architecture
- Implement embeddings, forward pass, logits, causal masking and parameter accounting.
- Study residual pathways, manifold-constrained hyperconnections, tied input/output weights, RMSNorm, RoPE and NoPE.
- Compare full, linear and sparse attention; understand sparse indexers and long-context retrieval behavior.
- Study Mixture-of-Experts routing, top-k expert selection, shared experts, load balancing and routing collapse.

### 4. Multimodal vision
- Learn patch embeddings, modality boundaries and 2D positional encoding.
- Reproduce the course's 32×32 image / 16 patch-token example with generated geometric images; measure shapes and generalize to other sizes.

### 5. Pretraining from zero
- Build a small causal language model from random initialization.
- Learn cross-entropy, AdamW, optimizer settings, data mixtures, interleaving, curriculum order, checkpointing and loss analysis.
- Train only on original synthetic or first-party rights-cleared data; keep validation, test and private holdout isolated.

### 6. Post-training and reinforcement learning
- Build a sandboxed code-task environment: generate a candidate, run automated unit tests, collect structured rewards and report task success.
- Study reward shaping, group sampling and GRPO-style advantages.
- Compare parameter-efficient updates with full updates; freeze layers where specified and verify untouched weights remain unchanged.
- Test reward hacking, hidden tests, regressions, temperature, group size and multiple seeds.

### 7. Release and operations
- Report exact parameter count, tokenizer/model compatibility, checkpoint hashes, baseline/post-training metrics, latency, memory and cost.
- Run safety, privacy, regression and independent holdout checks.
- Demonstrate reproducible restore and rollback before promoting a release.

## Eighteen-module sequence

The canonical lesson IDs, objectives, labs, transfer tasks and benchmarks are stored in the JSON course manifest. They cover research design; byte tokenization; embeddings; parameter counting; residual/hyperconnection paths; normalization and positional encodings; linear/sparse attention; MoE; vision patches; pretraining; data interleaving; sandboxed code RL; reward design and GRPO; parameter-efficient updates; hyperparameter experiments; statistical evaluation; regression/release; and the final CPU-first capstone.

## Division delivery

Every canonical division receives the shared AI/model literacy foundation. Division-specific projects are routed through `config/generated/masterbot-55-domain-crosswalk.json`; the 10 unresolved domain-to-MasterBot mappings remain review-required. All 65 MasterBot lanes receive shared learning material, while specialist ownership is not silently reassigned.

## Capstone acceptance

Buddy must produce an original model specification, tokenizer comparison, rights-cleared data manifest, measured parameter count, training/evaluation plan, sandbox security tests, multi-seed result report, private-holdout result, model card, checkpoint hashes and rollback evidence. A planned run, CI pass, course view or synthetic-data smoke test does not count as trained weights or production model mastery.

## Truthful status

- Course and study guide: defined.
- 18 modules: specified, not yet assessed.
- Video transcript ingestion: not performed.
- Model weight training: not performed or authorized.
- Paid GPU/accelerator compute: not authorized.
