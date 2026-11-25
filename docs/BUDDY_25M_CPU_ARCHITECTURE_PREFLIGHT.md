# Buddy 25M CPU architecture preflight

The repository's CPU model-training code and the 25M-class course must not be conflated. A small baseline is useful for pipeline tests, but it is not evidence of a 25-million-parameter model.

This profile defines a byte-level decoder architecture with:
- vocabulary: 256
- context length: 256
- hidden width: 640
- transformer layers: 5
- attention heads: 10
- feed-forward width: 2,560
- tied token/output embeddings

The parameter estimator counts the PyTorch-style combined QKV/output projections, feed-forward weights, biases, affine layer norms, token/position embeddings, and final norm. The expected count for this architecture is **24,946,560 parameters**, within 2% of the 25,000,000 target.

## Run the preflight

```bash
python -m pytest -q tests/test_buddy_model_architecture_preflight.py
```

## Important boundary

This is an architecture-size estimate and a testable specification. It does not instantiate a model, create weights, download a dataset, execute training, authorize paid compute, or establish CPU performance. Before any training run, the actual model implementation must be instantiated and its parameter count compared to this report. Training still requires explicit approval and rights-cleared local data.
