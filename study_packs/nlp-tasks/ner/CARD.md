# nlp-tasks.ner

HF task-zoo literacy drill for Buddy.

- HF pipeline: `token-classification`
- metric: `entity_f1` (implemented in `../drill_runner.py`, stdlib only)
- pass floor: 0.8
- drills: 5 hand-authored items in `drills.jsonl`
- seed models: `dslim/bert-base-NER`
- seed datasets: `eriktks/conll2003`
- train_allowed: false; revisions null, licenses TBD until pinned

## Drill loop
1. Pin one model (repo_id + revision sha + verified license) in `sources.json`.
2. Produce predictions as JSONL `{"id":..., "pred":...}` (e.g. with `transformers.pipeline("token-classification")`).
3. `python3 study_packs/nlp-tasks/drill_runner.py ner --preds preds.jsonl --out ner/evidence/<model>-<date>.json`
4. Only a score file in `evidence/` with a pinned revision counts. No evidence, no claim.
