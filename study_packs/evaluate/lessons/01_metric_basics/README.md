# 01 metric basics

`evaluate.load("exact_match")` downloads a metric script from the Hub, so it needs the
network. This lesson runs the same metrics offline through `metrics_adapter.py`:

- `exact_match`, with `ignore_case` / `ignore_punctuation` (same knobs as HF)
- `accuracy`
- `f1` (binary, `pos_label=1`)

Run: `python3 study_packs/evaluate/lessons/01_metric_basics/example_metric_basics.py`

With `HF_PACK_ALLOW_NETWORK=1` and `pip install evaluate==0.4.6`, the adapter calls the
real HF metric and labels the result `backend: hf_evaluate`.
