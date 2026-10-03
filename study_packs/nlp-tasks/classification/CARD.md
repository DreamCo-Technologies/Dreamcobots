# nlp-tasks.classification

HF task-zoo literacy drill for Buddy.

- HF pipeline: `text-classification`
- metric: `accuracy` (implemented in `../drill_runner.py`, stdlib only)
- pass floor: 0.85
- drills: 6 hand-authored items in `drills.jsonl`
- seed models: `distilbert/distilbert-base-uncased-finetuned-sst-2-english`, `cardiffnlp/twitter-roberta-base-sentiment-latest`
- seed datasets: `stanfordnlp/sst2`, `fancyzhx/ag_news`
- train_allowed: false; revisions null, licenses TBD until pinned

## Drill loop
1. Pin one model (repo_id + revision sha + verified license) in `sources.json`.
2. Produce predictions as JSONL `{"id":..., "pred":...}` (e.g. with `transformers.pipeline("text-classification")`).
3. `python3 study_packs/nlp-tasks/drill_runner.py classification --preds preds.jsonl --out classification/evidence/<model>-<date>.json`
4. Only a score file in `evidence/` with a pinned revision counts. No evidence, no claim.
