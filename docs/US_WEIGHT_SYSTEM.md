# DreamCo US Weight System

Goal: a **United States–owned weight stack** that is **efficient enough to reach frontier-class specialists**, then scale. "At all cost" here means **maximum legal compute, best public methods, no wasted FLOPs**. It does **not** mean stolen weights, harvested Grok/GPT traces, fake leaderboards, or claiming a checkpoint that does not exist.

`trained_weights_exist` remains **false** until a signed card + shard hashes land in `weights/`.

## Efficiency stack (what actually moves quality per watt)

1. **Do not pretrain first.** RAG + LoRA on a strong US-legal base (Llama, Gemma, OLMo, gpt-oss) until evals saturate.
2. **Sparse compute.** Mixture-of-Experts so only a slice of parameters fire per token (DeepSeek-V3 *idea*, not their files).
3. **Compress KV.** Multi-head latent attention / GQA / MLA-style memory cut so long context is cheap.
4. **Predict more than one token** only if a holdout shows it helps; MTP is optional.
5. **Train small, distill down.** Teacher = Grok API for *critiques on owned tasks*. Student = your dense or MoE checkpoint.
6. **Quantize for serve.** bf16 train → fp8/int8/int4 serve with the same eval floor.
7. **Adapters over full finetune.** Per-customer LoRA stays off the base until merge gates pass.

## Model line (ship in this order)

| Id | Params active / total | Role | Hardware reality |
| --- | --- | --- | --- |
| `dream-edge` | ~3B dense | Phone / offline | Laptop |
| `dream-work` | ~8–14B dense | Default student | 1×24–80GB |
| `dream-pro` | ~20–70B dense or small MoE | Serious specialist | multi-GPU |
| `dream-moe` | ~20B active / 200B+ total | Efficiency bet | cluster |
| `dream-frontier` | research cluster | Only after dream-moe holdout wins | national-scale $ |

You do not jump to `dream-frontier`. That is how labs burn cash and still lose to Grok.

## Data that is allowed

- Public licensed datasets pinned on HF / OLMo / Dolma-class corpora
- Customer private data → **private adapter only**
- Synthetic tasks **you** generate and own
- Grok used as grader/teacher text on those owned tasks, not as a weight dump

Forbidden: leaked checkpoints, ToS-breaking scrape of frontier APIs into a public weight file, client data in the global mix.

## Promotion gates (non-negotiable)

Same Buddy learning proof already on main:

- failing baseline recorded
- hidden holdout
- ≥3 native passes
- safety pack
- rollback hashes
- owner approval

No gate, no "frontier" word on the card.

## Cost honesty

- LoRA on 8B: hundreds to low thousands of dollars
- 70B SFT: tens of thousands
- From-scratch MoE near V3 scale: **tens of millions** and a real cluster team

Efficiency is how you climb that ladder without lighting money on fire. It is not a shortcut around physics.
