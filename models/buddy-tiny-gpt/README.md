# Buddy Tiny GPT Baseline Model Card

- Model ID: `dreamco/buddy-tiny-gpt-baseline`
- Status: `UNTRAINED_RANDOM_INITIALIZATION`
- Architecture: small decoder-only causal transformer
- Parameters: 34,432 for the pinned default configuration
- Tokenizer: UTF-8 byte-level vocabulary (256 IDs)
- Default runtime: CPU, seed 42, PyTorch 2.10.0
- Data: seeded synthetic byte IDs for evaluation only
- Training: not performed
- Weight updates: not performed
- Checkpoint: not written
- Network/model downloads: disabled
- Production routing: disabled

This is an engineering baseline, not a useful language model. Its initial loss is a random-initialization reference on a synthetic fixture; it is not a quality score, a trained checkpoint, or evidence of general language ability.

Reproduce the report with:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r requirements-buddy-gpt.txt
python -m unittest tests.test_tiny_gpt_baseline
python tools/run_tiny_gpt_baseline.py --output artifacts/buddy-gpt-baseline/baseline.json
```

The runner writes a JSON report only. It has no optimizer, training loop, model downloader, or weight/checkpoint writer. Training remains separately blocked pending dataset/model rights review and explicit authorization.
