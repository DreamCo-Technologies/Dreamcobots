# Model Foundry byte-level BPE integration

Model Foundry now supports two tokenizer modes:

- `byte_level`: fixed 256-token byte vocabulary; no tokenizer fitting occurs.
- `byte_bpe`: fits deterministic byte-level BPE merges using only the authorized 80% training split.

The dataset is split before tokenizer fitting. The tokenizer never sees validation or holdout bytes. Validation and holdout are encoded only after the training-split tokenizer is fixed. Checkpoint metadata records the tokenizer artifact hash, vocabulary size, training-split hash, and the fact that holdout was not used.

## 25M BPE profile

`config/buddy-25m-bpe-cpu-architecture-profile.json` defines a 512-token BPE target with an estimated 25,110,400 parameters. The actual tokenizer vocabulary must equal the profile vocabulary; Model Foundry rejects a mismatch. If the authorized training split produces fewer merges, create/review a matching profile and recheck the parameter target rather than silently padding or relabeling the tokenizer.

## Run mode

Call `train_from_scratch(..., tokenizer_type="byte_bpe", tokenizer_vocab_size=512, architecture_profile=...)` only after the existing dataset rights manifest and explicit runtime authorization gates pass. The profile is disabled by default. This change does not run training, download data, or authorize paid compute.

## Validate

```bash
python -m pytest -q tests/test_buddy_byte_bpe_trainer.py tests/test_model_foundry.py
```

The BPE helper tests verify that merges are learned from the training split only and that holdout-only patterns are not used to build the tokenizer. No model-weight run or benchmark result is claimed.
