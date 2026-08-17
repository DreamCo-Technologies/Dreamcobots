# Model Benchmark Scorecard

The Actions system records benchmark results per model and per task. Every result is scored across **quality, speed, efficiency, reliability, and safety** and compared with a versioned measured baseline for that exact benchmark.

## Percentage semantics

A score of 100% means the measured result matches the current reference baseline for that benchmark. Scores above the baseline are capped at 100 for the scorecard. This prevents a percentage from being mistaken for an absolute measure of intelligence.

## Mastery gate

A benchmark is marked **mastered** only when:

- quality >= 95% of the measured reference
- speed >= 95%
- efficiency >= 90%
- reliability >= 98%
- safety >= 98%
- weighted overall >= 95%
- at least one verifiable evidence artifact exists

These are engineering gates, not a declaration of AGI or proof that a model is the best AI in the world.

## Frontier-equivalent target

The reference should be a documented, versioned measurement from a strong frontier system or an accepted benchmark reference. For each benchmark we store the evaluator version, task set, hardware/runtime conditions, model version, date, sample count and raw evidence. Baselines must be refreshed when the reference changes.

## Metrics

| Metric | What it measures |
|---|---|
| Quality | Correctness, task success, rubric score, factual/functional quality |
| Speed | Time-to-first-result and/or completion latency under the same protocol |
| Efficiency | Tokens, tool calls, compute, memory and other relevant resource use |
| Reliability | Variance, failure rate and reproducibility across repeated trials |
| Safety | Policy/security/compliance outcomes and unsafe failure rate |
| Overall | Weighted composite of the five normalized dimensions |

## Model comparison

Each model gets a row for every applicable benchmark. The public Actions/Pages view should expose:

- overall percentage
- every metric percentage
- raw measurements
- baseline used
- model/provider/version
- benchmark version
- evidence links
- mastery status
- capability category
- strengths and weaknesses
- regression history
- cost/resource information where available

## Important limitation

No benchmark score should be described as proving that a model has mastered all intelligence, achieved AGI, or equals the best AI on every possible task. Mastery is **benchmark-specific** and evidence-backed.
