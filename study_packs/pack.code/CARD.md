# pack.code

Capability pack for Buddy study / future student training.

- capabilities: coding, debugging, repo-tools
- sources: huggingface-capability-packs.json, hf-capability-download-map.json
- train_allowed: false
- min_native_pass_rate: 0.75
- teacher: xai/grok-best-available
- automatic weight download: no
- git-lfs: not used
- hf_model_pipeline: text-generation
- hf_dataset_task: text2text-generation
- seed models: 3 / seed datasets: 2
- Day-1 pin status: unpinned

## License / revision pins

Every entry in `sources.json` starts with `revision: null`, `license: "TBD"`,
`pin_status: "unpinned"`. Pin exact Hugging Face `repo_id` + `revision` (commit sha)
and a verified license in sources.json before any eval or train job.

## Layout

- `sources.json` — HF ids + revisions + licenses
- `evals.json` — tasks and pass floors
- `recipes/sft.yaml` — stub, not run in default CI
- `recipes/dpo.yaml` — stub, only after SFT eval
- `evidence/` — before/after scores
