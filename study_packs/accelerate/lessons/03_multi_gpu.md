# 03 · Multi-GPU

Two different things share the name:

1. **Model splitting for inference** (this pack): one model's layers spread across GPUs with `device_map="balanced"` or `"auto"`. Runs are sequential (naive pipeline), so it adds capacity, not speed.
2. **Data-parallel training** via `accelerate launch --num_processes N script.py` with an `Accelerator()` in the script (`accelerator.prepare(model, optim, dataloader)`); configure once with `accelerate config`.

For higher-throughput serving across GPUs, use tensor-parallel servers (vLLM/TGI). That's the inference-serve lane, not this pack.

Status: the `acc.multi_gpu.balanced` eval is defined but unverified. It needs a box with at least two GPUs.
