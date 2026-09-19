# DreamCo US Open Model Foundry

Position: a **United States** place where customers build **their** open-source software and **optional open-weight** models. DeepSeek is a research lab that published methods and weights. DreamCo is the workshop: LoRA, RAG, evals, licenses, and Buddy proof — not a clone of DeepSeek-V3 weights.

`trained_weights_exist` is still **false** until a customer or DreamCo actually trains and signs a model card.

## Open source vs open weights

| Mode | Code | Weights | What customers get |
| --- | --- | --- | --- |
| Code version | yes | no | Runtime, RAG, LoRA recipes, evals |
| Open source | OSI license | no | Forkable foundry |
| Open weights | maybe | yes | Exact checkpoint + card + hashes |
| Private | no | no | Org-only adapters and indexes |

DeepSeek publishes some of both. Llama is often **open weight, not OSI open source**. Say which one you are selling.

## LoRA techniques we support as recipes (not silent training)

| Recipe | When to use | Notes |
| --- | --- | --- |
| LoRA | Full-rank adapter on attn/MLP | Classic PEFT; small file |
| QLoRA | 4-bit base + LoRA | Fits 7B–70B on fewer GPUs |
| DoRA | When LoRA plateaus | Magnitude + direction |
| LoRA+ / LoRA-FA | Faster convergence | Separate LR for A/B |
| rsLoRA | Rank-stable scaling | Better high rank |
| LoHA / LoKr | Tight VRAM | Kronecker / Hadamard |
| AdaLoRA | Adaptive rank | Drops dead ranks |
| VeRA / LoRA-XS | Many tenants | Shared matrices + tiny vectors |
| QLoRA + DPO/ORPO | After SFT | Preference align |
| Multi-LoRA serve | Per customer / per bot | Merge only after eval |

Never merge an adapter into the base until holdout + safety + fleet regression pass.

## RAG and vector databases

Retrieval is how most customers get "a custom model" **without** a 671B pretrain.

| Backend | Best for | Deploy |
| --- | --- | --- |
| DreamCo local store | Tests, laptops, no extra service | Default sandbox |
| FAISS | Local / on-prem dense search | Workstation |
| Chroma | Dev prototypes | Single node |
| Qdrant | Production filters + hybrid | US VPC |
| Weaviate | Hybrid + modules | Cluster |
| Milvus / Zilliz | Large scale | Cluster |
| pgvector | Already on Postgres | Simple prod |
| Pinecone | Managed SaaS | US region only if required |

Contract for every index:

- embedding model + revision pinned
- chunker version hashed
- source license and deletion/revocation
- no secrets in chunks
- query goes through Buddy permission gates

Pattern: **Grok teacher** for hard reasoning, **open student + RAG** for private corpora, **LoRA** when the same mistakes repeat in evals.

## Customer path to "build my own frontier-class specialist"

1. Pick a base (Llama, Gemma, OLMo, gpt-oss, Qwen — license checked).
2. Stand up RAG on their docs (US region).
3. Measure gaps with Buddy eval packs.
4. Train a **private LoRA** on pack data they own.
5. Serve base + RAG + adapter. Keep Grok as fallback route.
6. Optional: publish **open weights** of *their* adapter if license allows.

That is the US DeepSeek-shaped **product**. The DeepSeek-shaped **pretrain** is a multi-million-dollar cluster decision, not a checkbox.
