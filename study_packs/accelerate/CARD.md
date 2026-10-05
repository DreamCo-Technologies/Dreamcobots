# Study pack: accelerate (big-model inference, device maps, offload)

Owner: Grok-HF-Accelerate. Plan: plan-huggingface-mastery.

## Purpose
Teach and verify how DreamCo runs local open models that don't fit on one device:
`device_map` (`auto` / `balanced` / `balanced_low_0` / `sequential` / explicit dict), `max_memory`,
CPU and disk offload (`offload_folder`), `init_empty_weights` + `load_checkpoint_and_dispatch`,
multi-GPU layer splitting, `accelerate config` / `accelerate launch`, and quantized (bitsandbytes 8/4-bit) loading with CPU offload.

## Pins
- accelerate `1.15.0` (tag `v1.15.0`, commit `6afc1e5ee217051fde702b23de2813344dc0fd33`), license Apache-2.0.
- Test model `hf-internal-testing/tiny-random-gpt2` @ `71034c5d8bde858ff824298bdedc65515b97d2b9` (random weights, license unspecified on the Hub; used only for local smoke tests, never packaged).

## Evals
See `evals.json`. CPU tasks run via `scripts/smoke_offload.py`. The multi-GPU task is `requires_gpu` and has **not** been run (no GPU on the evidence box).

## Truth flags
- automatic weight download in CI: no
- train in default CI: no
- trained_weights_exist: false
- mastery_claimed: false
- multi_gpu_verified: false
