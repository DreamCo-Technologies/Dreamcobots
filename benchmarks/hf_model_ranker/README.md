# Hugging Face model-type ranker

`catalog.json` is the picker the Hub categories do not provide. `rank.py` scores those types for a task from license, hardware, and task fit. It does not download weights, so a rank is not a live benchmark.

```bash
python3 benchmarks/hf_model_ranker/rank.py --task "code generation"
python3 -m unittest benchmarks.hf_model_ranker.test_rank
```
