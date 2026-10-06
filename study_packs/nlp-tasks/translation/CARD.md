# nlp-tasks.translation

HF task-zoo literacy drill for Buddy.

- HF pipeline: `translation`
- metric: `chrf_lite` (implemented in `../drill_runner.py`, stdlib only)
- pass floor: 0.5
- drills: 5 hand-authored items in `drills.jsonl`
- seed models: `Helsinki-NLP/opus-mt-en-es`, `Helsinki-NLP/opus-mt-en-fr`, `facebook/nllb-200-distilled-600M`
- seed datasets: `wmt/wmt14`, `facebook/flores`
- train_allowed: false; revisions null, licenses TBD until pinned

## Drill loop
1. Pin one model (repo_id + revision sha + verified license) in `sources.json`.
2. Produce predictions as JSONL `{"id":..., "pred":...}` (e.g. with `transformers.pipeline("translation")`).
3. `python3 study_packs/nlp-tasks/drill_runner.py translation --preds preds.jsonl --out translation/evidence/<model>-<date>.json`
4. Only a score file in `evidence/` with a pinned revision counts. No evidence, no claim.
