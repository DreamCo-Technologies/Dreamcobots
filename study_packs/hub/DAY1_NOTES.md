# Hugging Face Day 1

Checked on 2026-09-28 against the public Hub. No token was sent. No weights were downloaded.

The inventory drill checked 31 ids from `config/huggingface-two-week-study.json` and `config/hf-capability-download-map.json`.

| Result | Count |
|---|---|
| Public | 23 |
| Gated | 7 |
| Missing | 0 |
| Not a model id | 1 |

Gated: `meta-llama/Llama-3.1-70B-Instruct`, `meta-llama/Llama-3.1-8B-Instruct`, `meta-llama/Llama-Guard-3-1B`, `google/gemma-2-27b-it`, `google/gemma-2-9b-it`, `mistralai/Mistral-Large-Instruct`, and the dataset `bigcode/the-stack-smol`. Those need a Hugging Face account and an accepted license. This run did not test a token.

`openai-community/gpt-oss-study-only-if-license-allows` is a note in the 14-day plan, not a model id. It was not requested.

`mistralai/Mistral-Large-Instruct` is gated. It is not missing.

Licenses to read before any sale: `tatsu-lab/alpaca` is `cc-by-nc-4.0`. `deepseek-ai/DeepSeek-V3` and `openai/clip-vit-base-patch32` returned no license field.

The download helper now accepts the `hf` command as well as `huggingface-cli`.

Logs: `study_packs/hub/evidence/day1-inventory.json`.
