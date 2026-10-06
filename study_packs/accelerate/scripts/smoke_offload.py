"""CPU smoke evals for the accelerate study pack. Exits nonzero on any failure."""
import sys
import tempfile

import torch
from accelerate import dispatch_model, infer_auto_device_map, init_empty_weights
from transformers import AutoConfig, AutoModelForCausalLM

MODEL = "hf-internal-testing/tiny-random-gpt2"
REV = "71034c5d8bde858ff824298bdedc65515b97d2b9"
results = {}


def record(task, ok, detail=""):
    results[task] = ok
    print(f"{'PASS' if ok else 'FAIL'} {task} {detail}".rstrip())


torch.manual_seed(0)
base = AutoModelForCausalLM.from_pretrained(MODEL, revision=REV).eval()
inputs = torch.tensor([[1, 2, 3, 4, 5]])
with torch.no_grad():
    ref = base.generate(inputs, max_new_tokens=8, do_sample=False, pad_token_id=0)

# acc.device_map.max_memory: a cpu budget of 60% of weights must split layers across cpu and disk.
param_bytes = sum(p.numel() * p.element_size() for p in base.parameters())
budget = param_bytes * 6 // 10
dmap = infer_auto_device_map(
    base, max_memory={"cpu": budget, "disk": 10 * param_bytes}, no_split_module_classes=["GPT2Block"]
)
placed = set(dmap.values())
seen = {}
for name, dev in dmap.items():
    if dev == "cpu":
        mod = base.get_submodule(name) if name else base
        for p in mod.parameters():  # dedupe tied weights (lm_head shares wte)
            seen[id(p)] = p.numel() * p.element_size()
cpu_bytes = sum(seen.values())
record(
    "acc.device_map.max_memory",
    {"cpu", "disk"} <= placed and 0 < cpu_bytes <= budget,
    f"devices={sorted(map(str, placed))} cpu_bytes={cpu_bytes} budget={budget}",
)

# acc.offload.parity: dispatch half the blocks to disk, compare greedy tokens.
model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REV).eval()
n = model.config.n_layer
split = {"transformer.wte": "cpu", "transformer.wpe": "cpu", "transformer.drop": "cpu",
         "transformer.ln_f": "cpu", "lm_head": "cpu"}
for i in range(n):
    split[f"transformer.h.{i}"] = "disk" if i >= n // 2 else "cpu"
with tempfile.TemporaryDirectory() as off:
    model = dispatch_model(model, device_map=split, main_device="cpu", offload_dir=off)
    with torch.no_grad():
        out = model.generate(inputs, max_new_tokens=8, do_sample=False, pad_token_id=0)
record("acc.offload.parity", torch.equal(out, ref), f"disk_blocks={n - n // 2}/{n}")

# acc.empty_weights.meta
cfg = AutoConfig.from_pretrained(MODEL, revision=REV)
with init_empty_weights():
    empty = AutoModelForCausalLM.from_config(cfg)
devs = {p.device.type for p in empty.parameters()}
record("acc.empty_weights.meta", devs == {"meta"}, f"param_devices={sorted(devs)}")

# acc.multi_gpu.balanced
if torch.cuda.device_count() >= 2:
    print("SKIP acc.multi_gpu.balanced (GPUs present but runner not implemented here)")
else:
    print(f"SKIP acc.multi_gpu.balanced requires_gpu (cuda_devices={torch.cuda.device_count()})")

passed = sum(results.values())
print(f"SUMMARY {passed}/{len(results)} CPU tasks passed")
sys.exit(0 if passed == len(results) else 1)
