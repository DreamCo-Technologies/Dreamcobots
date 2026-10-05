# Day 1 Inventory — License, Provenance, Exact Checkpoints

Focus: License, provenance, and exact checkpoint inventory

No weights are downloaded. Inspect model/dataset cards and commit history on the Hub only.

## Checklist

- [ ] For every seed in `study_packs/*/sources.json`, record the license from the Hub card
- [ ] Confirm license allows eval (and note whether derivatives/training are allowed)
- [ ] Record exact `revision` (commit sha) and set `pin_status` to `pinned`
- [ ] Record provenance: publisher org, gated/ungated, paper or data card link
- [ ] Flag gated / restricted / non-commercial repos; keep `train_allowed: false`
- [ ] Record exact checkpoint inventory for each `student_shortlist` entry below
- [ ] Confirm no weight download and no git-lfs used

## Seed inventory by pack

| Pack | Models | Datasets | Status |
| --- | --- | --- | --- |
| `pack.instruct` | 3 | 2 | unpinned |
| `pack.code` | 3 | 2 | unpinned |
| `pack.reason` | 2 | 2 | unpinned |
| `pack.tools` | 0 | 0 | no seeds (search_hints only) |
| `pack.research` | 0 | 0 | no seeds (search_hints only) |
| `pack.safety` | 1 | 1 | unpinned |
| `pack.embed` | 3 | 1 | unpinned |
| `pack.rerank` | 1 | 0 | unpinned |
| `pack.vision` | 1 | 0 | unpinned |
| `pack.speech` | 2 | 0 | unpinned |
| `pack.translate` | 1 | 0 | unpinned |
| `pack.summarize` | 1 | 0 | unpinned |

## student_shortlist (inventory targets only — not approved for training)

| repo_id | license | revision | pin_status |
| --- | --- | --- | --- |
| `meta-llama/Llama-3.1-70B-Instruct` | TBD | TBD | unpinned |
| `Qwen/Qwen2.5-72B-Instruct` | TBD | TBD | unpinned |
| `deepseek-ai/DeepSeek-V3` | TBD | TBD | unpinned |
| `mistralai/Mistral-Large-Instruct` | TBD | TBD | unpinned |
| `google/gemma-2-27b-it` | TBD | TBD | unpinned |
| `openai-community/gpt-oss-study-only-if-license-allows` | TBD | TBD | unpinned |

Teacher route: `xai/grok-best-available`.
