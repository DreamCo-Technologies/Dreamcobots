# TRL pack eval plan (plan-only)

Eval runs before training (baseline) and after each stage (SFT, DPO, GRPO), on the same held-out split.

1. Baseline: score the untouched base model on the task holdout. Record the result as evidence for `eval_baseline_before_train` in `gates.json`.
2. After SFT: same suite. Promote to DPO only if the task metric improves and no regression shows up on a general sanity set.
3. After DPO and GRPO: same suite plus a preference or reward win-rate against the previous stage.
4. Scorecards go to `study_packs/trl/scorecards/<pack_id>/<date>.json` (F0-style: model, data hash, metrics, commit). No scorecard means no claim.

No metrics exist yet. This file defines what gets measured, not results.
