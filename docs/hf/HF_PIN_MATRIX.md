# HF learning pin matrix

Source of truth for `requirements-hf-learning.txt`. This stack is **opt-in**: default CI does not install it, and no default test imports these packages.

| Package | Pin | Why | License (from package metadata) |
|---|---|---|---|
| torch | 2.14.0+cpu | Tensor runtime; CPU wheel keeps opt-in installs light. Matches the existing Accelerate venv. | BSD-3-Clause family (Apache-2.0/BSD/MIT components) |
| transformers | 5.17.0 | Model loading, tokenization, training loops | Apache-2.0 |
| tokenizers | 0.23.2 | Fast tokenizers required by transformers 5.17 | Apache-2.0 |
| safetensors | 0.8.0 | Safe weight format (no pickle) | Apache-2.0 |
| huggingface_hub | 1.33.0 | Hub download/upload, model cards. Pinned to 1.x because transformers 5.17 resolves against it (a 2.0.0 exists in `/workspace/hf-venv` but is not used here). | Apache-2.0 |
| accelerate | 1.15.0 | Device maps, CPU offload, multi-GPU | Apache-2.0 |
| datasets | 5.0.1 | Dataset loading/streaming for study packs | Apache-2.0 |
| evaluate | 0.4.6 | Metrics for Buddy F0 / edu benches | Apache-2.0 |
| peft | 0.21.0 | LoRA / adapter training for Buddy student adapters | Apache-2.0 |

## Tested

- Python: 3.13.5 (Linux x86_64)
- Date: 2026-09-28

## Verification

```bash
python3 -m venv /tmp/hf-pins-venv
/tmp/hf-pins-venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-hf-learning.txt
/tmp/hf-pins-venv/bin/python -c "import torch,transformers,datasets,huggingface_hub,tokenizers,safetensors,accelerate,evaluate,peft; print('SMOKE_OK')"
/tmp/hf-pins-venv/bin/pip check
```

Result on 2026-09-28: every package imported at the pinned version, `SMOKE_OK` printed, and `pip check` reported "No broken requirements found."

## Default CI safety

- No workflow in `.github/workflows/` installs `requirements-hf-learning.txt`. Default jobs install only `requirements-buddy-learning.txt`, `requirements-tools.txt`, `requirements-media.txt`, or `openpyxl`.
- No file under `tests/` imports transformers, datasets, peft, evaluate, accelerate, or huggingface_hub at module level.
- `requirements-buddy-learning.txt` keeps its loose `torch>=2,<3` / `safetensors>=0.4,<1` ranges. These pins sit inside those ranges, so the two files don't conflict.

## Updating pins

Bump the version in both files, rerun the verification block above in a fresh venv, and update the date and result here in the same commit.
