# Wikipedia learning bridge

The bridge makes every goal in `reports/goals_to_gates.json` and every task in
`config/buddy-benchmark-task-registry.json` discoverable against English
Wikipedia. It emits a reviewable index at
`website/data/wikipedia-learning-target-map.json` and exposes a read-only
MediaWiki REST search adapter.

```sh
python3 tools/build_wikipedia_learning_map.py
python3 tools/build_wikipedia_learning_map.py --check
python3 -m unittest tests.test_wikipedia_learning_bridge buddy.learning.benchmark_learning_adapter_test
```

Benchmark outcomes can be converted into learning events that retain the goal,
benchmark ID, and Wikipedia source references. A failed benchmark recommends
source review followed by an original sandbox practice task and a separate
retest. Wikipedia is a discovery/cross-reference source, not ground truth or
professional advice.

The bridge stores article citations and provenance fields, not article bodies.
Model-weight training stays blocked unless the user explicitly consents, the
specific page's rights and terms have been reviewed, training is isolated, and
an independent holdout is verified. Even then the result is only a candidate
for review; this bridge does not launch training or certify legal eligibility.
Wikipedia text is generally CC BY-SA 4.0 and may also be available under GFDL;
verify the actual page and applicable obligations before redistribution or use
in a training corpus. Images and other media require their own license checks.
