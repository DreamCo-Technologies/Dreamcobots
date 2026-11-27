# Buddy Tiny GPT Baseline — Model Card

**Status:** Untrained reference implementation; Day 1 baseline harness  
**Model ID:** `dreamco/buddy-tiny-gpt-baseline`  
**Architecture:** One decoder block with causal self-attention, residual MLP, and byte-level next-token head  
**Tokenizer:** UTF-8 bytes (256 token IDs)  
**Default configuration:** context 8 bytes, width 8, seed 20261121  
**Training data:** none  
**Weight updates:** none  
**Checkpoint:** none

## Intended use

This small, dependency-free model exists to validate the first GPT-style engineering contracts: deterministic initialization, byte tokenization, tensor-shape expectations, causal masking, finite forward-pass logits, and a reproducible untrained loss measurement.

The fixed train/validation/test strings in `config/buddy-tiny-gpt-baseline.json` are generated synthetic fixtures. They are not external datasets and are not used to update model parameters.

## Limitations

- This model is a tiny educational reference, not a trained assistant.
- Its untrained cross-entropy is a reproducibility baseline, not a useful-language-capability score.
- It is not a 25M-parameter model and is not a recreation of GPT-5 or any proprietary architecture.
- It is not intended for production inference, customer data, or real user tasks.
- No optimizer, training loop, dataset ingestion, checkpoint creation, or model promotion is performed in Day 1.

## Reproducibility

Run:

```bash
python tools/run_buddy_gpt_baseline.py --config config/buddy-tiny-gpt-baseline.json --output-dir artifacts/buddy-gpt-baseline
python -m unittest tests.test_buddy_gpt_baseline
```

The evidence report records the config hash, deterministic initialization hash, fixture hashes, validation/test cross-entropy, Python version, platform, and commit SHA. A repeated run with the same code, configuration, and seed must reproduce the model and fixture hashes.

## Rights and safety

The baseline uses only original DreamCo code and synthetic fixtures. It does not download, ingest, or train on course material, public datasets, private repositories, customer records, user conversations, or teacher outputs. Model training and paid compute remain disabled and unauthorized.
