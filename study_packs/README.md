# DreamCo Study Packs

Metadata-only Hugging Face capability packs (spec: `docs/HUGGINGFACE_MASTERY_PLAN.md`).

- Packs: **12**
- Teacher: `xai/grok-best-available`
- Automatic weight download: **no** (no git-lfs)
- train_allowed: **false** for every pack
- All revisions `null` and licenses `TBD` until pinned (see `DAY1_INVENTORY.md`)

| Pack | Capabilities | Seeds (models + datasets) | train_allowed | Day-1 pin status | Card |
| --- | --- | --- | --- | --- | --- |
| `pack.instruct` | instruction-fidelity, buddy-chat | 5 (3 + 2) | false | unpinned | [CARD.md](pack.instruct/CARD.md) |
| `pack.code` | coding, debugging, repo-tools | 5 (3 + 2) | false | unpinned | [CARD.md](pack.code/CARD.md) |
| `pack.reason` | math, reasoning | 4 (2 + 2) | false | unpinned | [CARD.md](pack.reason/CARD.md) |
| `pack.tools` | tool-use, function-calling | 0 (0 + 0) | false | unpinned | [CARD.md](pack.tools/CARD.md) |
| `pack.research` | research, citations, rag | 0 (0 + 0) | false | unpinned | [CARD.md](pack.research/CARD.md) |
| `pack.safety` | safety, refusals, permission-gates | 2 (1 + 1) | false | unpinned | [CARD.md](pack.safety/CARD.md) |
| `pack.embed` | embeddings, rag | 4 (3 + 1) | false | unpinned | [CARD.md](pack.embed/CARD.md) |
| `pack.rerank` | reranking | 1 (1 + 0) | false | unpinned | [CARD.md](pack.rerank/CARD.md) |
| `pack.vision` | vision | 1 (1 + 0) | false | unpinned | [CARD.md](pack.vision/CARD.md) |
| `pack.speech` | speech | 2 (2 + 0) | false | unpinned | [CARD.md](pack.speech/CARD.md) |
| `pack.translate` | multilingual | 1 (1 + 0) | false | unpinned | [CARD.md](pack.translate/CARD.md) |
| `pack.summarize` | summarization | 1 (1 + 0) | false | unpinned | [CARD.md](pack.summarize/CARD.md) |

Regenerate with `python3 tools/build_hf_capability_packs.py`.
