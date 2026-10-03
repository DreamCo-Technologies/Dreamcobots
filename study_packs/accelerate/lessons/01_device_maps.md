# 01 · Device maps

A device map assigns each module to a device (`0`, `1`, `"cpu"`, `"disk"`).

- `device_map="auto"` fills GPUs in order, then CPU, then disk.
- `"balanced"` spreads layers evenly across GPUs; `"balanced_low_0"` keeps GPU 0 lighter for generation.
- `"sequential"` fills GPU 0 fully before moving on.
- `max_memory={0: "10GiB", "cpu": "30GiB"}` caps what each device may hold.
- `accelerate.infer_auto_device_map(model, max_memory=..., no_split_module_classes=[...])` computes the map without loading weights; pass the model's block class (for example `GPT2Block`) so a block is never split across devices.
- Inspect the result with `model.hf_device_map` after `from_pretrained(..., device_map=...)`.
