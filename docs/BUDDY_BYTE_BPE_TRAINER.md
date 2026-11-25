# Rights-gated byte-level BPE tokenizer trainer

This is a small, deterministic byte-level BPE implementation for controlled tokenizer experiments. It is separate from model-weight training and does not use a network or fetch third-party data.

## Run

Prepare a manifest that points only to local files under `data/buddy-authorized-corpora/`. Each entry must include a verified SHA-256, source type, rights evidence, explicit model-training permission, privacy review, and a declaration that the corpus is neither sensitive nor holdout data.

```bash
python -m pytest -q tests/test_buddy_byte_bpe_trainer.py
python tools/train_buddy_byte_bpe_tokenizer.py --manifest authorized-corpus-manifest.json --root . --output artifacts/tokenizer.json --vocab-size 512 --confirm-authorized-training
```

The explicit flag is an additional confirmation, not a substitute for rights evidence. Unknown rights, missing permission, sensitive data, holdout data, path traversal, and hash mismatch fail closed.

The trainer records corpus provenance and can encode/decode UTF-8 text without loss. It does not train model weights, download datasets, or prove downstream language-model quality. Benchmark fertility, compression, multilingual coverage, and downstream effects separately before adopting a tokenizer.
