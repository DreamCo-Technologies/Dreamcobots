# Fallback vs HF evaluate parity (2026-09-28)

This checks the pack's own offline fallbacks against real `evaluate==0.4.6` metrics.
It is tooling evidence. It is NOT a Buddy score.

Environment: fresh venv, `pip install evaluate==0.4.6 scikit-learn`, `HF_PACK_ALLOW_NETWORK=1`.
Inputs: the synthetic rows from `lessons/01_metric_basics`.

| metric | kwargs | hf_evaluate | local_fallback |
|---|---|---|---|
| exact_match | none | 0.25 | 0.25 |
| exact_match | ignore_case=True | 0.75 | 0.75 |
| accuracy | none | 0.75 | 0.75 |
| f1 | none | 0.8 | 0.8 |

All four match. Offline suite: `python3 -m pytest tests/test_study_pack_evaluate.py -q` gave 13 passed.
