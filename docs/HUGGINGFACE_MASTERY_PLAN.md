# Realistic Hugging Face Mastery Plan

Goal: build **DreamCo Study Packs** — licensed, capability-scoped datasets and evals Buddy can train or distill from — not "download all of Hugging Face and beat Grok in two weeks."

## What "master Hugging Face" actually means

Hugging Face is a **hub**, not a curriculum:

- 1M+ models, 300k+ datasets, 300k+ spaces (order-of-magnitude; the number changes daily)
- Most artifacts are **wrong license, duplicate, abandoned, contaminated, or unsafe to execute**
- Frontier labs do **not** train by ingesting the whole hub

Mastery for DreamCo is:

1. Know how to **search, license-check, pin a revision, and refuse junk**
2. Keep a **shortlist** of models/datasets per capability
3. Turn those into **study packs** with evals
4. Train **small adapters / students** only when the pack and license allow it
5. Promote a route only when Buddy learning proof + holdout pass

## Hard no

- No "train on everything"
- No automatic `git lfs` pull or weight execution in Actions
- No raw user/client data in global training
- No scraping proprietary Grok/GPT outputs into a public pack
- No claiming frontier parity because a student loss went down

Teacher stays `xai/grok-best-available` for routing and critique. Students are open-weight, license-clean checkpoints.

## Timeboxed plan (realistic)

### Phase 0 — week 0 (already started)
Inventory + gates. 14-day calendar in `config/huggingface-two-week-study.json`.

Exit: license table, pinned revisions, no auto-exec.

### Phase 1 — weeks 1–2: hub literacy
Learn the **product**, not 1M cards.

- Models / datasets / spaces / papers / collections / inference endpoints
- `revision=` pins, model cards, `license` metadata, gated repos, `safetensors` vs pickle
- Hub API search with filters: `license`, `pipeline_tag`, `library`, `likes`, last-modified

Deliverable: `config/generated/hf-hub-literacy-checklist.json` (manual, checked in CI as schema only).

### Phase 2 — weeks 3–6: capability shortlists
For each pack below, pick **3 datasets + 2 models + 1 eval suite**. Not 300.

| Pack id | Capability | Example HF search | Train target |
| --- | --- | --- | --- |
| `pack.instruct` | Follow instructions | instruction, ultrachat, tulu | 7B–8B instruct adapter |
| `pack.code` | Repo coding / tests | starcoder, stack-edu, swe-bench-lite style evals | code 7B student |
| `pack.reason` | Math / logic | gsm8k, math, otis-style public sets | reason 7B |
| `pack.tools` | Function calling | tool-use, gorilla, xlam public | tools 7B |
| `pack.research` | Cited research | hotpot, fever, ragbench public | rag adapter |
| `pack.safety` | Refusals / gates | public safety evals only | policy adapter |
| `pack.domain.*` | One DreamCo division at a time | only public + licensed domain text | LoRA on pack.instruct |

Each pack is a folder:

```
study_packs/<id>/
  CARD.md              # license, revision pins, purpose
  sources.json         # hf ids + revisions + licenses
  evals.json           # tasks and pass floors
  recipes/sft.yaml     # optional, not run in default CI
  recipes/dpo.yaml     # only after SFT eval
  evidence/            # before/after scores
```

### Phase 3 — weeks 7–10: eval before train
Run **eval-only** on shortlist models against pack evals (local GPU or rented box, never default Actions).

Promote to train only if:

- license allows derivatives
- exact revision recorded
- contamination check documented
- Grok teacher critique on a **held-out** 20-item slice agrees the student is weak on that pack

### Phase 4 — weeks 11–16: train students, not a new Grok
Budget that matches a serious indie / small-lab, not a frontier pretrain:

- Hardware: 1–8x 80GB GPUs or equivalent cloud, not a laptop
- Method: LoRA/QLoRA SFT → DPO/ORPO on pack preference pairs → optional teacher notes from Grok on **synthetic public tasks you own**
- Size: 3B–8B students first; 70B only if Phase 3 eval says the 8B saturates
- Do **not** start a 405B / 1T pretrain. That is a different company.

Success is: pack eval floor met **and** Buddy fleet regression still green.

### Phase 5 — ongoing: one pack per month
Add `pack.domain.realestate`, `pack.domain.finance-sandbox`, etc. Only public + licensed text. Finance packs stay synthetic.

## Capability pack contract

Every pack must declare:

- `capability_ids` matching Buddy bots / benchmarks
- `hf_datasets[]` with `repo_id`, `revision`, `license`, `split`
- `hf_models[]` student candidates with the same pins
- `eval_suite` and `min_native_pass_rate`
- `teacher`: Grok for critique, never as stolen weights
- `train_allowed`: false until Phase 3 signed off
- `privacy`: no client data

This matches `buddy/learning/study_data_schema.json` buckets:
concept knowledge, worked examples, practice tasks, benchmark cases, failure cases, tool-use patterns, safety cases.

## What Grok is for

- Rank which HF cards are worth a pack
- Write eval items and scoring rubrics
- Critique student traces
- Route live DreamCo bots (`grok-<slug>`) while students stay offline

Grok is the teacher/router. Hugging Face is the **library**. DreamCo study packs are the **courseware**. Buddy learning proof is the **report card**.

## 90-day scoreboard (use this, not vibes)

| Week | Must exist |
| --- | --- |
| 2 | Hub literacy + 14-day calendar evidence |
| 6 | 6 pack folders with pinned sources |
| 10 | Eval scores for 2 packs |
| 16 | One trained adapter with holdout + fleet regression |
| 24 | Three promoted student routes behind quality floors |

If a row is missing, you did not master HF. You only bookmarked it.
