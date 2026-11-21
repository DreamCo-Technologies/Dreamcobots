# Buddy Tiny GPT Baseline

## Scope

This is a small decoder-only transformer reference implementation for Bootcamp engineering exercises. It is intentionally a baseline harness, not a trained model or production inference service.

The implementation includes:
- UTF-8 byte-level tokenization with a fixed 256-ID vocabulary
- Learned positional embeddings
- Causal multi-head self-attention
- Residual transformer blocks, layer normalization, and a GELU feed-forward network
- Next-byte logits and cross-entropy evaluation
- Seeded synthetic input fixtures and a deterministic report hash

## Reproduction

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r requirements-buddy-gpt.txt
python -m unittest tests.test_tiny_gpt_baseline
python tools/run_tiny_gpt_baseline.py --output artifacts/buddy-gpt-baseline/baseline.json
```

The default architecture is 2 layers, 2 attention heads, 32 embedding dimensions, a 32-byte context window, and 34,432 parameters. The runner is CPU-only and records the seed, runtime versions, configuration, initial loss, tensor shape, and report hash.

## Safety and interpretation

The runner performs a forward-only evaluation using seeded synthetic byte IDs. It does not execute an optimizer, update weights, save model checkpoints, download models, access external sources, or use paid compute. The data card explicitly marks the synthetic fixture as not approved for weight training.

The initial loss is only a random-initialization reference on a synthetic fixture. It is not a language-quality benchmark, trained-model result, or promotion signal. Weight training requires a separately reviewed dataset card, verified rights and provenance, a pinned model license/revision, explicit compute authorization, and a separate explicit training authorization.

## Current milestone status

- Day 1 baseline configuration, model card, data card, and report runner: implemented; local deterministic tests and a CPU evaluation-only run passed. CI artifact rerun is pending on the follow-up PR.
- Day 2 tokenizer: UTF-8 round-trip tests pass; deduplication, split-isolation, and full provenance pipeline are still open.
- Days 3–4 model skeleton and causal transformer block: implemented; shape, finite-gradient, unchanged-weight, and causal-leakage tests pass locally.
- Days 5–7 optimizer, profiling, pretraining, checkpoint, second-seed training repeat: blocked until separately authorized; no training was run.
- Days 8–10 SFT, reward loop, multimodal exercise: not started.
- Days 11–12 Buddy registry/lineage/routing and benchmark-gap closure: next integration phase; current report contains preliminary model/dataset lineage identifiers only.
- Days 13–14 independent rerun, security/reliability review, graduation: pending CI artifacts and independent review.


## Registry and routing status

The baseline has a read-only registry entry in `config/buddy-model-registry.json`. Its training run, weight artifact, verified dataset rights, and benchmark evidence are intentionally absent, so Buddy's route resolver must return `BLOCKED_NO_ELIGIBLE_MODEL`. The engineering benchmark contract is in `config/buddy-tiny-gpt-benchmark-contract.json`; capability-quality scoring remains `NOT_RUN`. Passing the baseline tests does not enable production routing.
