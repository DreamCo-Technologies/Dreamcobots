"""Transformers core drills: pipeline, Auto*, generate, chat templates.

Every drill runs against one pinned, license-checked model (see ../sources.json)
and uses plain asserts. Run: python study_packs/transformers/drills/run_drills.py
Writes a JSON run log to ../evidence/ unless --no-evidence is passed.
"""
from __future__ import annotations

import datetime as _dt
import json
import platform
import sys
import threading
import traceback
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parents[1]
SOURCES = json.loads((PACK_DIR / "sources.json").read_text())
MODEL = SOURCES["hf_models"][0]
REPO, REV = MODEL["repo_id"], MODEL["revision"]

_cache: dict = {}


def _tok_model():
    if "tm" not in _cache:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(REPO, revision=REV)
        model = AutoModelForCausalLM.from_pretrained(
            REPO, revision=REV, use_safetensors=True, trust_remote_code=False
        )
        model.eval()
        _cache["tm"] = (tok, model)
    return _cache["tm"]


def drill_pipeline() -> dict:
    """Module 1: pipeline() with a revision pin, batching, and output control."""
    from transformers import pipeline

    gen = pipeline("text-generation", model=REPO, revision=REV, device=-1)
    assert gen.task == "text-generation"
    prompts = ["The capital of France is", "One plus one equals"]
    out = gen(prompts, max_new_tokens=8, do_sample=False, return_full_text=False)
    assert len(out) == 2, "batch of 2 prompts must return 2 results"
    texts = [o[0]["generated_text"] for o in out]
    assert all(isinstance(t, str) and t for t in texts)
    assert not texts[0].startswith(prompts[0]), "return_full_text=False must strip the prompt"
    return {"outputs": texts}


def drill_auto() -> dict:
    """Module 2: AutoConfig / AutoTokenizer / AutoModelForCausalLM."""
    import torch
    from transformers import AutoConfig

    cfg = AutoConfig.from_pretrained(REPO, revision=REV)
    assert cfg.model_type == "llama", cfg.model_type
    tok, model = _tok_model()
    text = "Hello transformers"
    ids = tok(text)["input_ids"]
    assert tok.decode(ids, skip_special_tokens=True).strip() == text
    batch = tok(["short", "a bit longer input"], return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**batch).logits
    b, s = batch["input_ids"].shape
    assert tuple(logits.shape) == (b, s, cfg.vocab_size), tuple(logits.shape)
    return {"model_type": cfg.model_type, "vocab_size": cfg.vocab_size,
            "params": sum(p.numel() for p in model.parameters()),
            "logits_shape": list(logits.shape)}


def drill_generate() -> dict:
    """Module 3: greedy vs sampling, GenerationConfig, max_new_tokens, streaming."""
    import torch
    from transformers import GenerationConfig, TextIteratorStreamer

    tok, model = _tok_model()
    inputs = tok("Once upon a time", return_tensors="pt")
    n_in = inputs["input_ids"].shape[1]
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def run(**kw):
        with torch.no_grad():
            return model.generate(**inputs, pad_token_id=pad, **kw)

    g1 = run(max_new_tokens=12, do_sample=False)
    g2 = run(max_new_tokens=12, do_sample=False)
    assert torch.equal(g1, g2), "greedy must be deterministic"
    assert g1.shape[1] - n_in <= 12, "max_new_tokens exceeded"

    torch.manual_seed(7); s1 = run(max_new_tokens=12, do_sample=True, temperature=0.9, top_p=0.9, top_k=50)
    torch.manual_seed(7); s2 = run(max_new_tokens=12, do_sample=True, temperature=0.9, top_p=0.9, top_k=50)
    assert torch.equal(s1, s2), "seeded sampling must be reproducible"

    gc = GenerationConfig(max_new_tokens=5, do_sample=False, repetition_penalty=1.2,
                          pad_token_id=pad, eos_token_id=tok.eos_token_id)
    with torch.no_grad():
        g3 = model.generate(**inputs, generation_config=gc)
    assert g3.shape[1] - n_in <= 5, "GenerationConfig.max_new_tokens ignored"

    streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
    th = threading.Thread(target=run, kwargs=dict(max_new_tokens=12, do_sample=False, streamer=streamer))
    th.start()
    streamed = "".join(streamer)
    th.join()
    greedy_text = tok.decode(g1[0, n_in:], skip_special_tokens=True)
    assert streamed.strip() == greedy_text.strip(), (streamed, greedy_text)
    return {"greedy": greedy_text, "sampled_seed7": tok.decode(s1[0, n_in:], skip_special_tokens=True),
            "genconfig_5tok": tok.decode(g3[0, n_in:], skip_special_tokens=True)}


def drill_chat_template() -> dict:
    """Module 4: apply_chat_template and its flags."""
    import torch

    tok, model = _tok_model()
    assert tok.chat_template, "tokenizer must ship a chat_template"
    msgs = [{"role": "system", "content": "You are concise."},
            {"role": "user", "content": "Name one primary color."}]
    no_gen = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
    with_gen = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    assert with_gen.startswith(no_gen) and len(with_gen) > len(no_gen)
    header = with_gen[len(no_gen):]
    assert "assistant" in header, header

    ids = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True)
    if isinstance(ids, dict) or hasattr(ids, "keys"):  # newer versions may return BatchEncoding
        ids = ids["input_ids"]
    assert list(ids) == tok(with_gen, add_special_tokens=False)["input_ids"]

    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_dict=True, return_tensors="pt")
    assert "input_ids" in enc and "attention_mask" in enc

    prefill = msgs + [{"role": "assistant", "content": "The color is"}]
    cont = tok.apply_chat_template(prefill, tokenize=False, continue_final_message=True)
    assert cont.rstrip().endswith("The color is"), cont[-60:]

    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=16, do_sample=False,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
    reply = tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    assert reply.strip(), "empty reply"
    return {"generation_header": header, "reply": reply}


DRILLS = {
    "tc.pipeline.pinned_textgen": drill_pipeline,
    "tc.auto.load_pinned": drill_auto,
    "tc.generate.controls": drill_generate,
    "tc.chat_template.render": drill_chat_template,
}


def main(argv: list[str]) -> int:
    import torch
    import transformers

    # Lesson from run_20260928T175119: multi-threaded CPU matmuls made two greedy
    # generate() calls diverge after 11 tokens (float reduction order + near-tie
    # logits). One intra-op thread makes CPU greedy decoding bit-reproducible.
    torch.set_num_threads(1)
    results = []
    for did, fn in DRILLS.items():
        try:
            detail = fn()
            results.append({"id": did, "passed": True, "detail": detail})
        except Exception as exc:  # record honestly
            results.append({"id": did, "passed": False, "error": repr(exc),
                            "traceback": traceback.format_exc()[-2000:]})
        print(("PASS " if results[-1]["passed"] else "FAIL ") + did, flush=True)
    now = _dt.datetime.now().astimezone()
    log = {
        "schema": "dreamco.study_pack.run_log.v1",
        "pack_id": "pack.transformers-core",
        "ran_at": now.isoformat(timespec="seconds"),
        "host": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "device": "cpu",
        "torch_num_threads": torch.get_num_threads(),
        "model": {"repo_id": REPO, "revision": REV, "license": MODEL["license"]},
        "passed": sum(r["passed"] for r in results),
        "total": len(results),
        "results": results,
    }
    if "--no-evidence" not in argv:
        path = PACK_DIR / "evidence" / f"run_{now.strftime('%Y%m%dT%H%M%S')}.json"
        path.write_text(json.dumps(log, indent=2) + "\n")
        print(f"evidence: {path}")
    return 0 if log["passed"] == log["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
