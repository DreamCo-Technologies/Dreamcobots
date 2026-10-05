# 02 · CPU and disk offload

When weights exceed GPU memory, Accelerate keeps them on CPU (or memory-mapped on disk) and moves each layer to the execution device only for its forward pass using hooks.

- `from_pretrained(..., device_map="auto", offload_folder="offload/")` enables disk offload.
- `offload_state_dict=True` lowers peak CPU RAM while loading.
- `init_empty_weights()` builds the model on the `meta` device (no memory), then `load_checkpoint_and_dispatch(model, ckpt, device_map=...)` streams real weights in.
- Offload trades speed for fit: outputs should be identical to an in-memory run, only slower. The pack's `acc.offload.parity` eval checks exactly that.
- bitsandbytes 8-bit with CPU offload needs `llm_int8_enable_fp32_cpu_offload=True` in `BitsAndBytesConfig`.
