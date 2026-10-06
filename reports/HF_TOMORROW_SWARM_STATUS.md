# HF Swarm Status: Tomorrow Checklist
Created 2026-09-28 17:45 CT by Grok-HF-Swarm-Conductor. **Refreshed 2026-10-02 16:51 CT.** Pushed on branch `hf/swarm-status-checklist`, PR #12443.

## Rule
No lane may claim "mastery" or certification without linked eval/CERT evidence. **Verified mastery claims: 0.** Passing tests, open PRs, and license rows are not mastery.

## Main branch (DreamCo-Technologies/Dreamcobots @ origin/main 5ba09f2ea, checked 2026-10-02 16:45 CT)
- `docs/HUGGINGFACE_MASTERY_PLAN.md` is the plan only.
- On main now: `study_packs/hub/DAY1_NOTES.md`, `study_packs/hub/day1_audit.py`, `study_packs/hub/evidence/day1-inventory.json`, `study_packs/hub/evidence/drills.json`, `study_packs/hub/plugin-catalog.json` (Day1 inventory, hub lane). No other `study_packs/*` directory is on main.
- Open HF PRs are not merged and are not evidence of mastery: #12433, #12434, #12435, #12440, #12443, #12444, #12445, #12919.

## Lanes (current open PR numbers)
| Lane | Owner | Where | Status | Next |
|---|---|---|---|---|
| Hub Day-1 drills | HF-Hub-Master | PR #12444 (`study-pack/hf-hub-day1`) | in review | fix 2 bad repo ids (see License flags), re-run drills |
| Evaluate | HF-Evaluate | PR #12434 (`feat/hf-evaluate-study-pack`) | in review (13 tests) | first logged eval run into `evidence/` |
| Multimodal pack | HF-Mastery-Coach | PR #12433 (`hf/multimodal-study-pack-main`) | in review | keep MMS-TTS and CLIP out of sellable scope |
| Multimodal sellability gate | Buddy-Multimodal | PR #12445 (`buddy-multimodal-sellability-gate`) | in review | feed it the license table below |
| HF pin matrix | HF-Hub-Master | PR #12435 (`feat/hf-learning-pins`) | in review | re-run the verification block |
| Accelerate | HF-Accelerate | PR #12440 (`hf/accelerate-study-pack`) | in review | re-run the smoke test, keep the log |
| Datasets + NLP task zoo | HF-Mastery-Coach | **PR #12919** (`hf/unlanded-study-packs`), from `/workspace/hf-datasets-pack` + `/workspace/Dreamcobots` (`nlp-tasks-build/gen.py`) | in review. Tests: 13 passed with datasets 5.0.1, or 10 passed + 3 skipped without it | resolve nlp-tasks pins/licenses |
| Swarm status (this file) | Grok-HF-Swarm-Conductor | PR #12443 (`hf/swarm-status-checklist`) | in review | keep refreshed |
| Transformers core | HF-Transformers | `/workspace/hf-transformers-core` branch `study/transformers-core` @ 806ac5065 (1 commit, **not pushed**, no PR) | unlanded | push the branch and open a PR |
| TRL recipes | HF-TRL | `/workspace/study_packs/trl` (not a git repo; `status: plan_only`, all 6 gates pending) | unlanded, plan only | dry-run only; the license gates block training |
| Tokenizers / chat template | HF-Tokenizers | `/workspace/buddy-tokenizers` (not a git repo) | unlanded | put it in a repo path and add a test |
| Path B router | HF-Router-Wiring | `/workspace/pathb-router`: 0 commits beyond main | missing | adapter stub + contract test |
| O*NET / provenance configs | ONET-Ingest-Lead | `/workspace/onet-recon` configs | stub only | one ingest run with a provenance record |

Not landed and **not** bundled: the generated output in `/workspace/hf-datasets-pack`. That covers `study_packs/hf_packages/`, `study_packs/bot_learning_packages/`, `study_packs/pack.*`, `study_packs/index.json`, `tools/download_hf_package.sh`, and `reports/{HF_DOWNLOADABLE_PACKAGES,BUDDY_HUB_LEARNING_PACKAGES,HUGGINGFACE_CAPABILITY_PACKS}.md`. These are regenerable by `tools/build_hf_capability_packs.py`, `tools/build_hf_download_packages.py`, and `tools/buddy_scan_hubs.py`, which are already on main.

## License flags
These come from the Hub API (`https://huggingface.co/api/{models|datasets}/<id>`, fields `cardData.license`, `cardData.license_name`, `gated`), queried anonymously on 2026-10-02 16:49 CT. The raw results are in `/workspace/hf-license-audit/hub_license_audit.json` on the swarm box. "Commercial use" here means shipping in a **sellable data package**. Anything marked unclear needs owner or legal sign-off before it ships.

| Repo id | Type | License (Hub `cardData.license`) | Gated | Commercial use in a sellable package | Referenced by |
|---|---|---|---|---|---|
| `facebook/mms-tts-eng` | model | cc-by-nc-4.0 | no | **no** (non-commercial) | #12433 study_packs/multimodal/sources.json |
| `openai/clip-vit-base-patch32` | model | *(none declared)* | no | unclear (no license on Hub) | #12433 study_packs/multimodal/sources.json; #12444 hub/evidence/drill_05_inventory_audit.json |
| `meta-llama/Llama-3.1-8B-Instruct` | model | llama3.1 | yes (manual) | unclear (Llama 3.1 community license: conditional, gated) | #12444 hub/drills/drill_03_gated_probe; #12444 hub/evidence/drill_05_inventory_audit.json |
| `meta-llama/Llama-3.1-70B-Instruct` | model | llama3.1 | yes (manual) | unclear (Llama 3.1 community license: conditional, gated) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `meta-llama/Llama-Guard-3-1B` | model | llama3.2 | yes (manual) | unclear (Llama 3.2 community license: conditional, gated) | #12444 hub/drills/drill_03_gated_probe; #12444 hub/evidence/drill_05_inventory_audit.json |
| `google/gemma-2-9b-it` | model | gemma | yes (manual) | unclear (Gemma terms: conditional, gated) | #12444 hub/drills/drill_03_gated_probe; #12444 hub/evidence/drill_05_inventory_audit.json |
| `google/gemma-2-27b-it` | model | gemma | yes (manual) | unclear (Gemma terms: conditional, gated) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `mistralai/Mistral-Large-Instruct` | model | **unverified**: HTTP 401 (Invalid username or password.) | unverified | unclear | #12444 hub/drills/drill_03_gated_probe; #12444 hub/evidence/drill_05_inventory_audit.json |
| `openai/whisper-tiny` | model | apache-2.0 | no | yes | #12433 study_packs/multimodal/sources.json; #12444 hub/drills/drill_02 |
| `openai/whisper-small` | model | apache-2.0 | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `google/vit-base-patch16-224` | model | apache-2.0 | no | yes | #12433 study_packs/multimodal/sources.json |
| `MIT/ast-finetuned-speech-commands-v2` | model | bsd-3-clause | no | yes | #12433 study_packs/multimodal/sources.json |
| `hf-internal-testing/tiny-random-gpt2` | model | *(none declared)* | no | unclear (no license on Hub) | #12440 study_packs/accelerate/sources.json |
| `BAAI/bge-small-en-v1.5` | model | mit | no | yes | #12444 hub/drills/drill_01; #12444 hub/evidence/drill_05_inventory_audit.json |
| `BAAI/bge-reranker-base` | model | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `sentence-transformers/all-MiniLM-L6-v2` | model | apache-2.0 | no | yes | #12444 hub/drills/drill_03_gated_probe; #12444 hub/drills/drill_04; #12444 hub/evidence/drill_05_inventory_audit.json |
| `intfloat/e5-base-v2` | model | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `Qwen/Qwen2.5-7B-Instruct` | model | apache-2.0 | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `Qwen/Qwen2.5-72B-Instruct` | model | other (qwen) | no | unclear (custom license) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | model | apache-2.0 | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `bigcode/starcoder2-7b` | model | bigcode-openrail-m | no | unclear (OpenRAIL-M use restrictions) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `deepseek-ai/DeepSeek-V3` | model | *(none declared)* | no | unclear (no license on Hub) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | model | other (deepseek) | no | unclear (custom license) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `microsoft/phi-4` | model | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `openai-community/gpt-oss-study-only-if-license-allows` | model | **unverified**: HTTP 401 (Invalid username or password.) | unverified | unclear | #12444 hub/evidence/drill_05_inventory_audit.json |
| `facebook/bart-large-cnn` | model | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json; #12919 study_packs/nlp-tasks/summarization/sources.json |
| `google/pegasus-xsum` | model | *(none declared)* | no | unclear (no license on Hub) | #12919 study_packs/nlp-tasks/summarization/sources.json |
| `Helsinki-NLP/opus-mt-en-es` | model | apache-2.0 | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json; #12919 study_packs/nlp-tasks/translation/sources.json |
| `Helsinki-NLP/opus-mt-en-fr` | model | apache-2.0 | no | yes | #12919 study_packs/nlp-tasks/translation/sources.json |
| `facebook/nllb-200-distilled-600M` | model | cc-by-nc-4.0 | no | **no** (non-commercial) | #12919 study_packs/nlp-tasks/translation/sources.json |
| `distilbert/distilbert-base-uncased-finetuned-sst-2-english` | model | apache-2.0 | no | yes | #12919 study_packs/nlp-tasks/classification/sources.json |
| `cardiffnlp/twitter-roberta-base-sentiment-latest` | model | cc-by-4.0 | no | yes (attribution) | #12919 study_packs/nlp-tasks/classification/sources.json |
| `dslim/bert-base-NER` | model | mit | no | yes | #12919 study_packs/nlp-tasks/ner/sources.json |
| `distilbert/distilbert-base-cased-distilled-squad` | model | apache-2.0 | no | yes | #12919 study_packs/nlp-tasks/qa/sources.json |
| `deepset/roberta-base-squad2` | model | cc-by-4.0 | no | yes (attribution) | #12919 study_packs/nlp-tasks/qa/sources.json |
| `openai/gsm8k` | dataset | mit | no | yes | #12919 study_packs/datasets/sources.json; #12444 hub/evidence/drill_05_inventory_audit.json |
| `openai/openai_humaneval` | dataset | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `Anthropic/hh-rlhf` | dataset | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `HuggingFaceH4/ultrachat_200k` | dataset | mit | no | yes | #12444 hub/evidence/drill_05_inventory_audit.json |
| `bigcode/the-stack-smol` | dataset | *(none declared)* | yes (auto) | unclear (no license on Hub) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `sentence-transformers/all-nli` | dataset | *(none declared)* | no | unclear (no license on Hub) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `tatsu-lab/alpaca` | dataset | cc-by-nc-4.0 | no | **no** (non-commercial) | #12444 hub/evidence/drill_05_inventory_audit.json |
| `stanfordnlp/sst2` | dataset | unknown | no | unclear (Hub says unknown) | #12919 study_packs/nlp-tasks/classification/sources.json |
| `fancyzhx/ag_news` | dataset | unknown | no | unclear (Hub says unknown) | #12919 study_packs/nlp-tasks/classification/sources.json |
| `eriktks/conll2003` | dataset | other | no | unclear (custom license) | #12919 study_packs/nlp-tasks/ner/sources.json |
| `rajpurkar/squad` | dataset | cc-by-sa-4.0 | no | yes (attribution + share-alike) | #12919 study_packs/nlp-tasks/qa/sources.json |
| `rajpurkar/squad_v2` | dataset | cc-by-sa-4.0 | no | yes (attribution + share-alike) | #12919 study_packs/nlp-tasks/qa/sources.json |
| `abisee/cnn_dailymail` | dataset | apache-2.0 | no | yes | #12919 study_packs/nlp-tasks/summarization/sources.json |
| `EdinburghNLP/xsum` | dataset | unknown | no | unclear (Hub says unknown) | #12919 study_packs/nlp-tasks/summarization/sources.json |
| `wmt/wmt14` | dataset | unknown | no | unclear (Hub says unknown) | #12919 study_packs/nlp-tasks/translation/sources.json |
| `facebook/flores` | dataset | cc-by-sa-4.0 | yes (auto) | yes (attribution + share-alike) | #12919 study_packs/nlp-tasks/translation/sources.json |

Notes:
- **Confirmed non-commercial (cc-by-nc-4.0):** `facebook/mms-tts-eng` (#12433), `facebook/nllb-200-distilled-600M` (#12919 nlp-tasks translation), and `tatsu-lab/alpaca` (#12444 inventory). `facebook/mms-tts-spa` is also cc-by-nc-4.0, which matches the reported `mms-tts-*` flag.
- **CLIP declares no license:** `openai/clip-vit-base-patch32` (and `openai/clip-vit-large-patch14`, checked for comparison) has no `cardData.license`. The flag is confirmed, so treat it as unclear and keep it out of sellable packages.
- **Gated (manual):** every Llama (`llama3.1`, `llama3.2`) and Gemma (`gemma`) model referenced. `bigcode/the-stack-smol` and `facebook/flores` are gated `auto`.
- **Bad ids (HTTP 401 means the repo does not exist or is private):**
  - `mistralai/Mistral-Large-Instruct`. The real `mistralai/Mistral-Large-Instruct-2411` reports `other (mrl)`, gated no; `-2407` reports `other (mrl)`, gated auto.
  - `openai-community/gpt-oss-study-only-if-license-allows` is a placeholder. The real `openai/gpt-oss-20b` reports `apache-2.0`, gated no.
- `deepseek-ai/DeepSeek-V3` has no cardData license but ships `LICENSE-CODE` and `LICENSE-MODEL` files. It stays unclear until those are read.

## Next concrete study/run checklist (priority order)
Run from the repo root of the relevant branch. Use `/workspace/hf-pins-venv` for HF libraries. Every result is evidence, not mastery.

1. **Land-ready check for #12919.** Run `python3 -m pytest tests/test_study_pack_datasets.py tests/test_nlp_task_zoo_drills.py -q -rs`. Expect 13 passed with `datasets==5.0.1`, or 10 passed + 3 skipped without it. Also run `python3 study_packs/nlp-tasks/drill_runner.py --selftest --out study_packs/nlp-tasks/evidence/harness-selftest-<date>.json` (harness evidence only).
2. **Remove non-commercial assets from sellable scope.**
   - In `study_packs/nlp-tasks/translation/sources.json`, mark `facebook/nllb-200-distilled-600M` as study-only.
   - In #12433, keep `commercial_ok: false` for `facebook/mms-tts-eng` and `null` for CLIP.
   - Drop `tatsu-lab/alpaca` from any package manifest.
   - Feed these rows to the #12445 sellability gate: `python3 -m pytest tests/test_sellability_gate.py -q`.
3. **Resolve nlp-tasks pins (19 ids).**
   - For each id in `study_packs/nlp-tasks/*/sources.json`, run `curl -s https://huggingface.co/api/models/<id>` (or `/api/datasets/<id>`) and write `.sha` into `revision` and `.cardData.license` into `license`.
   - Then change `test_no_training_no_pins_claimed` to assert a 40-hex revision, like `test_study_pack_datasets.py` does, and re-run step 1.
4. **Fix the #12444 hub drills.**
   - Replace `mistralai/Mistral-Large-Instruct` with `mistralai/Mistral-Large-Instruct-2411` in `drills/drill_03_gated_probe.py`.
   - Replace the gpt-oss placeholder in the inventory with `openai/gpt-oss-20b`.
   - Re-run `bash study_packs/hub/drills/run_all.sh /workspace/hf-pins-venv/bin/python`. It writes `study_packs/hub/evidence/run_summary.tsv` plus `drill_0*.log`, and every exit_code should be 0.
5. **First real NLP eval (classification).**
   - Generate predictions with `transformers.pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", revision=<sha>)` over `study_packs/nlp-tasks/classification/drills.jsonl`, writing `preds/classification.jsonl` (`{"id","pred"}` per line).
   - Then run `python3 study_packs/nlp-tasks/drill_runner.py classification --preds preds/classification.jsonl --model distilbert/distilbert-base-uncased-finetuned-sst-2-english --revision <sha> --out study_packs/nlp-tasks/classification/evidence/run_<date>.json`.
   - Pass means accuracy >= 0.85 and `evidence_valid: true`.
6. **Evaluate (#12434).**
   - Run `python3 -m pytest tests/test_study_pack_evaluate.py -q`.
   - Run `python3 study_packs/evaluate/lessons/02_buddy_bench_scoring/example_buddy_bench_scoring.py > study_packs/evaluate/evidence/<date>_buddy_bench.json`. The last line must be JSON with `ok: true`.
7. **Transformers core (unpushed).** In `/workspace/hf-transformers-core`, run `python3 -m pytest tests/test_transformers_core_pack.py -q` and `python3 study_packs/transformers/drills/run_drills.py`, which writes `study_packs/transformers/evidence/run_<ts>.json`. Then push `study/transformers-core` and open a PR.
8. **Multimodal (#12433).** Run `python3 -m pytest tests/test_study_pack_multimodal.py -q` and `python3 study_packs/multimodal/drill_runner.py`, which writes `study_packs/multimodal/evidence/run_<ts>.json` and `latest.json`.
9. **Accelerate (#12440).** Run `python3 -m pytest tests/test_accelerate_study_pack.py -q` and `python3 study_packs/accelerate/scripts/smoke_offload.py > study_packs/accelerate/evidence/smoke_run.txt`.
10. **Pins (#12435).** Run the `docs/hf/HF_PIN_MATRIX.md` verification block in a fresh `/tmp/hf-pins-venv`. Expect `SMOKE_OK` and `pip check` reporting no broken requirements.
11. **TRL (plan only).** Run `python3 /workspace/study_packs/trl/scripts/train_sft.py --dry-run` only. `license_base_model` and `license_dataset` stay pending. Llama and Gemma are gated with conditional licenses, so pick an apache-2.0 or mit base (for example `Qwen/Qwen2.5-7B-Instruct` or `microsoft/phi-4`) before any approved run.

## Path to sellable data packages
Before anything can be sold, each package needs four things: a per-asset license row marked "yes" above, a provenance record (#12445 schema), an eval/quality report in `evidence/`, and landing on main. No package has all four yet.

## Blockers
- Review/merge of open PRs is owner-only. Agents do not merge.
- 2 repo ids in #12444 cannot be verified (HTTP 401).
- The nlp-tasks pins are still `null` / `TBD`.
- 3 lanes are unlanded outside PRs: transformers-core (unpushed), TRL, and tokenizers.
