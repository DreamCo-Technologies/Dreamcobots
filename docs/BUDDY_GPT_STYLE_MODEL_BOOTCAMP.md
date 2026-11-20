# Buddy Bootcamp: GPT-Style Model Engineering Track

**Status:** DEFINED — curriculum and lab specifications only; NOT TRAINED  
**Owner:** DreamCo owner (final approval)  
**Teacher:** approved documentation and eligible open-weight/inference teachers  
**Student:** Buddy and DreamCo model candidates  
**Lab:** isolated Buddy Bootcamp sandbox  
**Track ID:** `ai_ml.gpt_style_model_engineering`

## Purpose

Teach Buddy to understand, implement, train, evaluate, and safely serve a small GPT-style language model. This is an educational reproduction of public model-engineering techniques, not a recreation of proprietary GPT-5 architecture or weights. The target is a reproducible small baseline (initially CPU-friendly, with a 25M-parameter class experiment as an optional milestone), not frontier capability.

## Source material and use boundaries

1. [freeCodeCamp — Build and Train a 25M Parameter LLM From Scratch on Your CPU](https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu/) (2026-10-08). Topics reported by the article: byte-level vocabulary, pretraining, cross-entropy, hybrid linear/sparse attention, MoE, tied embeddings, image patches, RL with unit-test rewards, multi-seed experimentation.
2. [freeCodeCamp — Build and Train a GLM-5.3-Flash Model From Scratch with Python](https://www.freecodecamp.org/news/build-and-train-a-glm-53-flash-model-from-scratch-with-python/) (2026-11-14). Topics reported: 260-token byte vocabulary, 192-token context, linear/sparse attention, MoE, 2D RoPE image patches, curriculum/interleaving, GRPO-style reward experiments. The article reports 16/24 Python tasks after its RL stage; this is a course-reported result, not a DreamCo benchmark.
3. [Vuk Rosić — Code & Train GPT-5 From Scratch in Python](https://www.youtube.com/watch?v=xzCJpWliUE0) (2025-08-07) and [public educational implementation](https://github.com/vukrosic/gpt5-from-scratch). The repository identifies itself as a small learning model, states GPT-5 is not open sourced, and lists an MIT license. Treat its architecture guesses as hypotheses, not facts about GPT-5.
4. [freeCodeCamp — Train Your Own LLM](https://www.freecodecamp.org/news/train-your-own-llm) (2025-04-10): tokenization, dataset preparation, SFT, instruction tuning, LoRA, and chatbot fine-tuning.

**Rights and provenance:** use these sources as citations and study references. Do not copy course text, slides, notebooks, or code into DreamCo without checking the exact license and permission. The Vuk repository's MIT license applies to that repository's code, not to the FreeCodeCamp videos/articles or other linked materials. No course content, Gmail, private repository content, or teacher outputs are automatically authorized training data. Dataset rights must be independently cleared before any training run.

## Cumulative learning sequence

| Unit | Lesson and lab | Required evidence |
| --- | --- | --- |
| 01 — Reproducible baseline | Tensor shapes, embeddings, causal next-token prediction, logits, cross-entropy, tiny-batch overfit test | Shape assertions, loss decreases on a fixed tiny batch, seed/config recorded |
| 02 — Tokenization and data | Byte-level tokenizer, special tokens, sequence packing, truncation, byte/token accounting, deduplication and split isolation | Tokenizer round-trip tests, dataset manifest, leakage and duplicate checks |
| 03 — Transformer core | Causal multi-head attention, positional embeddings/RoPE, residuals, normalization, MLP/SwiGLU, backprop | Attention mask tests, finite gradients, causal leakage test, tiny-batch overfit |
| 04 — Efficient architectures | Linear and sparse attention concepts, KV cache, grouped-query attention comparison, MoE routing, tied embeddings | Numerical equivalence where applicable, routing invariants, memory/latency profile |
| 05 — Optimization and systems | AdamW baseline, optional Muon comparison, warmup/cosine schedule, clipping, weight decay, AMP, accumulation, batch sizing, CPU/GPU profiling | Reproducible run config, tokens/sec, peak memory, loss curves, cost estimate |
| 06 — Pretraining and evaluation | Train/validation/test splits, curriculum/interleaving, checkpoints, perplexity, sample inspection, multi-seed uncertainty | Baseline report, held-out evaluation, sample generations, checkpoint hash |
| 07 — Post-training | SFT, LoRA/QLoRA concepts, preference data, reward design, GRPO/PPO concepts, unit-test reward loops | Rights-cleared examples, reward-hacking tests, held-out task score, regression report |
| 08 — Multimodal and serving | Image patches, vision encoder, multimodal token boundaries, inference, sampling, quantization, caching, structured outputs and safety | Synthetic image fixtures, inference contract tests, latency/throughput and safety report |
| 09 — DreamCo integration | Model registry, adapter/checkpoint metadata, Buddy routing, database/dataset lineage, fallback and permission boundaries | Registry schema tests, route allowlist tests, no-write-by-default integration test |
| 10 — Graduation | Re-run pinned baseline, held-out transfer, adversarial tests, ablation, multi-seed comparison and model card | Independent evidence packet; no graduation on catalog entries or lesson completion alone |

## Teacher → student daily cycle

1. Teacher presents one concept, cites the source, and labels claims as documented fact, implementation observation, or hypothesis.
2. Buddy explains the concept from memory and predicts expected tensor shapes, failure modes, and metrics.
3. Buddy completes one isolated lab using synthetic or rights-cleared fixtures.
4. The harness checks correctness, safety, reproducibility, and performance.
5. Buddy receives targeted remediation and repeats the task on a held-out variant.
6. The ledger records what was demonstrated, not what was merely read.

Each packet must satisfy the existing `config/buddy-bootcamp-curriculum-v1.json` training_unit contract: `capability_id, objective, lesson, practice, sandbox_task, transfer_task, rubric, benchmark, provenance`.

## Required engineering principles

- Implement the smallest correct baseline before advanced architecture.
- Overfit one tiny batch to validate the training loop before scaling.
- Inspect dataset examples and generated samples before trusting aggregate metrics.
- Keep train, validation, and final test sets separate; never tune on the final holdout.
- Pin seeds, dependencies, tokenizer, data hashes, configs, and code revision.
- Compare one change at a time; use ablations and multiple seeds where feasible.
- Profile before optimizing; report tokens/sec, loss/perplexity, memory, latency, throughput, and cost.
- Save checkpoints and verify their hashes; keep rollback and recovery paths.
- Reward functions are attack surfaces: test reward hacking, leakage, shortcut solutions, and grader exploitation.
- A smaller model's success does not establish frontier-model parity.

## Distillation and training gates

**Current state: NOT TRAINED.** This addition defines lessons and target behaviors only. No dataset has been approved or ingested; no training job, GPU/CPU run, checkpoint, adapter, model-weight update, or benchmark has been produced by this curriculum change.

Before any real weight update, require:
- eligible open-weight student model and documented license;
- teacher identity/version and permission for the intended use (hosted proprietary models are inference teachers only where terms permit; never seek proprietary weights);
- dataset card, canonical URL, license/terms, consent/rights, PII review, provenance, deduplication, contamination checks and quality approval;
- versioned dataset hash, transformations, tokenizer, split IDs and isolated holdout;
- baseline suite, run ID, config, seeds, compute authorization and budget approval;
- training logs, checkpoint hash, independent evaluation, regressions and model card.

Unknown or restricted dataset rights mean **BLOCKED**. No paid compute, paid API credits, production writes, or deployment is authorized by this curriculum.

## Acceptance criteria

- All 10 units have the required training-unit fields and source provenance.
- The lesson planner marks each unit ready only when its required fields are present.
- No source is represented as proof of GPT-5's private architecture.
- No benchmark or training claim is made without a run artifact and independent evaluation.
- Dataset counts are separated into discovered, cataloged, rights-cleared, quality-approved, training-ready, and actually used.
- Bootcamp mastery requires repeat pass, held-out transfer, no active regression, and fresh evidence.
- Buddy's explanations and lab outputs are stored as curriculum evidence, not described as weight learning.

## DreamCo mapping

- Existing Bootcamp: `config/buddy-bootcamp-program.json`, `config/buddy-bootcamp-curriculum-v1.json`, `buddy/bootcamp/buddy_bootcamp.yaml`.
- Teacher syllabus: `docs/GROK_TEACHES_BUDDY_SYLLABUS_v0.md`.
- Lesson planner: `tools/bootcamp_lesson_planner.py`.
- Learning procedures: `buddy/learning/study_methods.py` (currently explicitly reports `weights_trained: false`).
- Follow-up implementation: connect these units to the Bootcamp lesson planner/engine and add deterministic tests before claiming executable or tested status.
