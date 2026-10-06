# 02 Buddy bench scoring

Shows how `bench_map.json` turns a Buddy bench family into metric calls: math items
score with `exact_match`, code items with unbiased pass@k (the estimator HF
`code_eval` uses). The data is synthetic. Never paste these numbers into a scorecard.

`code_eval` itself executes generated code, so it stays off in CI and runs only inside
the universal sandbox with `HF_ALLOW_CODE_EVAL=1`.
