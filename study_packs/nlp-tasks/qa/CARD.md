# nlp-tasks.qa

HF task-zoo literacy drill for Buddy.

- HF pipeline: `question-answering`
- metric: `squad_em_f1` (implemented in `../drill_runner.py`, stdlib only)
- pass floor: 0.75
- drills: 5 hand-authored items in `drills.jsonl`
- seed models: `distilbert/distilbert-base-cased-distilled-squad`, `deepset/roberta-base-squad2`
- seed datasets: `rajpurkar/squad`, `rajpurkar/squad_v2`
- train_allowed: false; revisions null, licenses TBD until pinned

## Drill loop
1. Pin one model (repo_id + revision sha + verified license) in `sources.json`.
2. Produce predictions as JSONL `{"id":..., "pred":...}` (e.g. with `transformers.pipeline("question-answering")`).
3. `python3 study_packs/nlp-tasks/drill_runner.py qa --preds preds.jsonl --out qa/evidence/<model>-<date>.json`
4. Only a score file in `evidence/` with a pinned revision counts. No evidence, no claim.
