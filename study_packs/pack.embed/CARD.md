# pack.embed

Capability pack for Buddy study / future student training.

- capabilities: embeddings, rag
- sources: hf-capability-download-map.json
- train_allowed: false
- min_native_pass_rate: 0.7
- teacher: xai/grok-best-available
- automatic weight download: no
- git-lfs: not used
- hf_model_pipeline: sentence-similarity
- hf_dataset_task: sentence-similarity
- seed models: 3 / seed datasets: 1
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
