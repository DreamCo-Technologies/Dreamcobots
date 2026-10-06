# HF Hub Day-1 Literacy Notes (Dreamcobots)

Day-1 focus (from `config/huggingface-two-week-study.json`, day 1): *"License, provenance, and exact checkpoint inventory"*.
Phase 1 scope (from `docs/HUGGINGFACE_MASTERY_PLAN.md`, "Phase 1 — weeks 1–2: hub literacy"): `revision=` pins, model cards,
`license` metadata, gated repos, safetensors vs pickle, Hub search filters.

Every Hub fact below that is marked **[observed]** was produced by a drill run on 2026-09-28 ~17:33 CDT, anonymously
(`HF_TOKEN` unset, no stored token), with `huggingface_hub 2.0.0`. Logs: `evidence/`. Anything not marked observed is
background knowledge and should be re-checked against the Hub docs.

`claimable: false` — these notes are study material, not proof of mastery or of any trained artifact.

---

## 0. The Dreamcobots HF inventory (what the repo actually references)

| Source file | Field | Ids |
| --- | --- | --- |
| `config/huggingface-two-week-study.json` | `student_shortlist` | `meta-llama/Llama-3.1-70B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`, `deepseek-ai/DeepSeek-V3`, `mistralai/Mistral-Large-Instruct`, `google/gemma-2-27b-it`, `openai-community/gpt-oss-study-only-if-license-allows` |
| `config/hf-capability-download-map.json` | `seed_models` (10 packs) | `meta-llama/Llama-3.1-8B-Instruct`, `Qwen/Qwen2.5-7B-Instruct` (instruct + reason), `google/gemma-2-9b-it`, `Qwen/Qwen2.5-Coder-7B-Instruct`, `bigcode/starcoder2-7b`, `deepseek-ai/deepseek-coder-6.7b-instruct`, `BAAI/bge-small-en-v1.5`, `sentence-transformers/all-MiniLM-L6-v2`, `intfloat/e5-base-v2`, `microsoft/phi-4`, `openai/whisper-small`, `openai/whisper-tiny`, `Helsinki-NLP/opus-mt-en-es`, `facebook/bart-large-cnn`, `openai/clip-vit-base-patch32`, `BAAI/bge-reranker-base`, `meta-llama/Llama-Guard-3-1B` |
| `config/hf-capability-download-map.json` | `seed_datasets` | `tatsu-lab/alpaca`, `HuggingFaceH4/ultrachat_200k`, `bigcode/the-stack-smol`, `openai/openai_humaneval`, `gsm8k`, `openai/gsm8k`, `sentence-transformers/all-nli`, `Anthropic/hh-rlhf` |
| `config/huggingface-capability-packs.json` | `search_hints` only | no repo ids (hints like `ultrachat`, `gsm8k`, `hotpotqa`) |
| `bots/lib-huggingface.md` | capability list | no repo ids (Transformers / PEFT / Datasets / Inference Endpoints bot profile) |

Unique totals: **23 model ids, 8 dataset ids.** `tools/build_hf_capability_packs.py` merges both configs into
`study_packs/<pack>/sources.json` with `revision: null`, `license: "TBD"`, `pin_status: "unpinned"`;
`tools/build_hf_download_packages.py` writes `study_packs/hf_packages/<pack>/package.json` with `revision: "main"`,
`license: "verify-on-model-card"`, `download: False`. Day-1 work = replace those placeholders with real values
(drill 5 gathers them).

---

## 1. Repo types and ids

- Three repo types: **model**, **dataset**, **space**. Same git+LFS/Xet storage underneath; different URL prefix and API.
  - model: `https://huggingface.co/openai/whisper-tiny`
  - dataset: `https://huggingface.co/datasets/openai/gsm8k` (this is exactly what `item()` in
    `tools/build_hf_download_packages.py` builds with its `datasets/` prefix)
  - space: `https://huggingface.co/spaces/<owner>/<name>`
- Id format: `<namespace>/<name>` where namespace is a user or org (`BAAI`, `meta-llama`, `sentence-transformers`).
- In the Python API the type is a parameter, not part of the id: `hf_hub_download(repo_id, filename, repo_type="dataset")`,
  `HfApi().dataset_info("openai/gsm8k")`.
- **Legacy un-namespaced ids redirect.** [observed] `gsm8k` (listed in `seed_datasets.pack.reason`) resolves to
  `openai/gsm8k` with the same sha `740312add88f…`. So `pack.reason` lists the **same dataset twice**. Fix: keep only
  `openai/gsm8k`.
- **Ids that do not exist.** [observed] `mistralai/Mistral-Large-Instruct` and
  `openai-community/gpt-oss-study-only-if-license-allows` (both in `student_shortlist`) return RepositoryNotFound.
  The second one is a placeholder note, not a repo id. Mistral publishes versioned names (e.g. `Mistral-Large-Instruct-2411`
  / `-2407`). Choose one explicitly, then re-audit.

## 2. Model cards and YAML metadata

- The model card is `README.md` in the repo. Its YAML front-matter is machine-readable metadata. `HfApi.model_info()`
  returns it as `info.card_data`, and `ModelCard.load(repo_id)` parses the file.
- Key fields:
  - `license`: SPDX-like id (`apache-2.0`, `mit`) or `other` + `license_name` + `license_link`.
  - `pipeline_tag`: the task (drives the Hub widget and search filters). `hf-capability-download-map.json`'s
    `hf_model_pipeline` values are pipeline tags.
  - `base_model`: provenance, i.e. what this checkpoint was fine-tuned/quantized from.
  - also `library_name`, `language`, `tags`, `datasets`, `model-index` (eval results).
- [observed, drill 1] `BAAI/bge-small-en-v1.5`: license `mit`, pipeline_tag `feature-extraction`, library
  `sentence-transformers`, base_model none, YAML keys `language, license, model-index, tags`, sha `5c38ec7c…`.
- [observed, drill 5] Provenance through `base_model`: `meta-llama/Llama-3.1-8B-Instruct` → `meta-llama/Meta-Llama-3.1-8B`,
  `Qwen/Qwen2.5-7B-Instruct` → `Qwen/Qwen2.5-7B`, `google/gemma-2-9b-it` → `google/gemma-2-9b`,
  `sentence-transformers/all-MiniLM-L6-v2` → `nreimers/MiniLM-L6-H384-uncased`.
- [observed] What the license field alone does not tell you. These need a human to read the text:
  - `Qwen/Qwen2.5-72B-Instruct` = `other` / `qwen`, but `Qwen/Qwen2.5-7B-Instruct` = `apache-2.0`. Sizes in the same family carry different licenses.
  - `deepseek-ai/deepseek-coder-6.7b-instruct` = `other` / `deepseek`.
  - `bigcode/starcoder2-7b` = `bigcode-openrail-m` (use restrictions).
  - `meta-llama/*` = `llama3.1` / `llama3.2`. `google/gemma-*` = `gemma`.
  - `deepseek-ai/DeepSeek-V3`, `openai/clip-vit-base-patch32`: **no license in card metadata**, so read the repo LICENSE file.
  - dataset `tatsu-lab/alpaca` = `cc-by-nc-4.0` (non-commercial, which matters for a paid DreamCo product).
  - `bigcode/the-stack-smol`, `sentence-transformers/all-nli`: no license in metadata.
- Rule from `docs/HUGGINGFACE_MASTERY_PLAN.md` ("Phase 3"): promote to train only if license allows derivatives.
  `train_allowed` stays `false` everywhere.

## 3. Revisions: branches, tags, commit SHAs, pinning

- Every Hub repo is a git repo. A `revision` can be a branch (`main`), a tag (`v1.0`), a PR ref (`refs/pr/12`), a
  conversion ref (`refs/convert/parquet` on datasets), or a full 40-char **commit SHA**.
- Only a commit SHA is immutable. `main` moves.
  - [observed] `sentence-transformers/all-MiniLM-L6-v2` last_modified 2026-06-01.
  - [observed] `microsoft/phi-4` last_modified 2026-07-14.
  - A `revision: "main"` pin (what `build_hf_download_packages.py` writes) does not reproduce.
- List refs: `HfApi().list_repo_refs(repo_id)` returns `.branches`, `.tags`, `.converts`, `.pull_requests` (with `include_pull_requests=True`).
  History: `list_repo_commits(repo_id)`.
- Pin with `revision=`: `hf_hub_download(..., revision=sha)`, `snapshot_download(..., revision=sha)`,
  `model_info(repo_id, revision=sha)`, and in transformers `from_pretrained(repo_id, revision=sha)`.
- [observed, drill 2] `openai/whisper-tiny`:
  - one branch `main` → `169d4a4341b33bc18d8881c4b69c2e104e1cc0af`, **no tags**, 62 commits.
  - `config.json` downloaded at that SHA landed in `snapshots/169d4a43…/config.json`.
  - its blob file name `417aa9de…` equals the git blob SHA-1 of the bytes, which is an integrity check for non-LFS files.
  - `refs/main` in the cache contains the pinned SHA.
- Dreamcobots action: copy `latest_sha` from `evidence/drill_05_inventory_audit.json` into `sources.json` `revision`
  **after** license review, and set `pin_status: "pinned"`.

## 4. Gated models

- A gated repo has public **metadata** (card, file list, sha) but gated **files**. `model_info().gated` is `False`,
  `"auto"` (instant approval once you accept), or `"manual"` (the owner reviews each request).
- Access flow: log in on the website, open the model page, accept the terms / fill the form, wait for approval (manual),
  then call with a token from that account.
- Token scopes: `read` is enough for downloads. A `write` token also works. A **fine-grained** token needs the permission
  for read access to public gated repos you can access. Without it, gated downloads fail even after acceptance.
- HTTP behavior (huggingface_hub raises `GatedRepoError`, a subclass of `RepositoryNotFoundError`, so catch it first):
  - no token → **401** → Dreamcobots label `needs-token`
  - token, terms not accepted / not yet approved → **403** → `needs-accept`
  - token, accepted → 200 → `accessible`
  - nonexistent **or private** repo, anonymous → **401** `RepositoryNotFoundError`. The Hub does not reveal whether a
    private repo exists. [observed: `mistralai/Mistral-Large-Instruct` returned http=401 in drill 3]
- [observed, drill 3 + 5] Gated inventory models (all `manual`):
  - `meta-llama/Llama-3.1-70B-Instruct`
  - `meta-llama/Llama-3.1-8B-Instruct`
  - `meta-llama/Llama-Guard-3-1B`
  - `google/gemma-2-27b-it`
  - `google/gemma-2-9b-it`

  Gated dataset: `bigcode/the-stack-smol` (`auto`). Anonymous `config.json` metadata requests to the gated models returned 401.
- The `needs-accept` branch could **not** be observed, because the drills ran with no token.

## 5. huggingface_hub essentials

```python
from huggingface_hub import HfApi, hf_hub_download, snapshot_download, whoami
api = HfApi()
api.model_info("BAAI/bge-small-en-v1.5")                 # sha, gated, card_data, pipeline_tag, siblings
api.dataset_info("openai/gsm8k")
api.list_repo_files("openai/whisper-tiny", revision=sha) # file names only, no download
api.list_repo_refs("openai/whisper-tiny")                # branches / tags / converts
hf_hub_download("openai/whisper-tiny", "config.json", revision=sha)   # one file -> cached path
snapshot_download("sentence-transformers/all-MiniLM-L6-v2", revision=sha,
                  allow_patterns=["config.json", "tokenizer*", "vocab.txt"])  # subset of a repo
whoami()   # raises when anonymous: observed LocalTokenNotFoundError in 2.0.0
```

- `allow_patterns` / `ignore_patterns` are fnmatch globs over repo paths. This is how you honor the plan's
  "no automatic weight download" rule (`docs/HUGGINGFACE_MASTERY_PLAN.md` "Hard no"; `automatic_weight_download: false`
  in `config/huggingface-capability-packs.json`).
- Safetensors vs pickle: `.bin`/`.pt`/`.ckpt` are pickle and can execute code on load. Prefer `.safetensors`.
  The drills download neither.
- [observed, drill 4] allow_patterns for 9 config/tokenizer files of `all-MiniLM-L6-v2` fetched **716,270 bytes**
  total. Zero weight files.
- CLI: huggingface_hub 2.0.0 ships only the `hf` binary (`hf auth login`, `hf download`, `hf cache`). [observed] No
  `huggingface-cli` entrypoint was installed in `/workspace/hf-venv/bin`. The generated `tools/download_hf_package.sh`
  checks for `huggingface-cli`, so it would exit 1 with a current install.
- Anonymous calls work for public repos but print a rate-limit warning [observed]. Tokens raise rate limits.

## 6. Cache layout

- Root: `HF_HOME` (default `~/.cache/huggingface`). Hub cache: `HF_HUB_CACHE` (default `$HF_HOME/hub`). Token file:
  `$HF_HOME/token`. The `cache_dir=` argument overrides per call.
- Per repo: `models--<org>--<name>/` (or `datasets--…`, `spaces--…`):
  - `blobs/<hash>`: the actual bytes. Hash = git SHA-1 for regular files, SHA-256 for LFS files.
  - `refs/<branch>`: text file holding the commit SHA that the branch resolved to.
  - `snapshots/<commit_sha>/<path>`: symlinks into `blobs/`. Identical files across revisions share one blob.
- [observed, drill 4, hub 2.0.0] The cache also contains `.locks/`, a `CACHEDIR.TAG`, and `trees/<sha>.json` (per-revision file listing).
- Inspect or clean with `scan_cache_dir()` / `hf cache` CLI. [observed] `scan_cache_dir` reported `size_on_disk=709849`, 9 files, 1 revision.

## 7. HF_TOKEN and auth precedence

- Token lookup order: explicit `token=` arg, then the `HF_TOKEN` env var, then the stored `$HF_HOME/token` (written by `hf auth login`).
  `token=False` forces anonymous.
- Never commit tokens. Never put them in Actions logs. Dreamcobots CI should stay anonymous or use a read-only
  fine-grained token scoped to gated-repo read.
- The drills print `token_present` / `HF_TOKEN env set` in their first line so every log shows its auth context.
  [observed: `token_present=False | HF_TOKEN env set=False` in all 5 logs]

---

## Day-1 findings to act on (repo config changes; not made, local notes only)

1. Replace `mistralai/Mistral-Large-Instruct` with an existing, versioned Mistral id, or drop it. (`config/huggingface-two-week-study.json`)
2. Replace the placeholder `openai-community/gpt-oss-study-only-if-license-allows` with a real id, or remove it.
3. Remove the duplicate `gsm8k`; keep `openai/gsm8k`. (`config/hf-capability-download-map.json` `seed_datasets.pack.reason`)
4. Flag `tatsu-lab/alpaca` as non-commercial (cc-by-nc-4.0).
5. Five gated models need an account to accept terms before any config/tokenizer fetch.
6. Read the full license text for the entries whose metadata license is `other` or missing.
7. Pin `latest_sha` values from drill 5 into `sources.json` only after items 4–6.
