# nlp-tasks.summarization

HF task-zoo literacy drill for Buddy.

- HF pipeline: `summarization`
- metric: `rougeL_lite` (implemented in `../drill_runner.py`, stdlib only)
- pass floor: 0.35
- drills: 3 hand-authored items in `drills.jsonl`
- seed models: `facebook/bart-large-cnn`, `google/pegasus-xsum`
- seed datasets: `abisee/cnn_dailymail`, `EdinburghNLP/xsum`
- train_allowed: false; revisions null, licenses TBD until pinned

## Drill loop
1. Pin one model (repo_id + revision sha + verified license) in `sources.json`.
2. Produce predictions as JSONL `{"id":..., "pred":...}` (e.g. with `transformers.pipeline("summarization")`).
3. `python3 study_packs/nlp-tasks/drill_runner.py summarization --preds preds.jsonl --out summarization/evidence/<model>-<date>.json`
4. Only a score file in `evidence/` with a pinned revision counts. No evidence, no claim.
