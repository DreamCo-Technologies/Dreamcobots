# Evidence: plan-business-productivity-programs / manufacturing-productivity

> **Sandbox acceptance evidence, NOT production evidence.** Nothing here shows
> any real productivity, savings, uptime, quality or ROI improvement. No real
> factory data, no live integrations, no before/after measurements were used.
> Plan status stays `stub`; nothing was marked `production_ready`.

- **Program under test:** `config/universal-business-manufacturing-productivity-program.json`
  (schema `dreamco.universal_business_manufacturing_productivity.v1`, version `1.0.0`). It is #1 of a
  top-3 that is **proposed and waiting for owner confirmation** (see `top3_priority.json`).
- **Test file:** `tests/test_business_manufacturing_productivity_program.py` (unittest style, run with pytest, same as `tests/test_autonomous_business_and_deployment.py`)
- **Run date/time:** 2026-09-28 17:49:18 CDT (America/Chicago)
- **Commit under test:** `235ad52f2d216a255e504ebd0bd0e26b685faab4` on local branch `biz-productivity/manufacturing-acceptance` (base `origin/main` @ `24ca34bd8`). Not pushed.
- **Result:** 10 passed, 0 failed, 0 skipped (plus 46 subtests passed). Exit code 0. Full log: `pytest_output.log`.
- **Command:** `python3 -m pytest tests/test_business_manufacturing_productivity_program.py -v` (Python 3.13.5, pytest 9.1.1)

## What was tested
1. `schema` matches the expected id and `version` is semver.
2. All 7 list fields (business_types, manufacturing_domains, productivity_metrics, task_model,
   improvement_methods, factory_worker_types, integration_targets) are non-empty, contain only non-blank strings, and have no duplicates.
3. `task_model` has all 17 required fields (trigger … evidence).
4. `safety_rule` says Buddy "must not" bypass machine safety systems, lockout/tagout, regulated signoff, or human-required safety decisions.
5. `truth_rule` requires measured before/after evidence and forbids savings/ROI claims.
6. `tools/build_manufacturing_productivity_benchmarks.py` was run **in a temp-dir sandbox** (the tool and config were copied into a
   mirrored layout so the real `config/generated/` is never written). Every output case has `baseline_required` and
   `post_change_measurement_required` set to true, lists baseline/post-change/sample-period/data-source evidence, has
   `claim_status == no_improvement_claim_until_measured`, and contains no savings/ROI value or claim.
7. Sandbox workflow: a simulated **downtime root-cause analysis** task written in the `task_model` shape passes an in-test validator
   (worker role, metrics and integration targets all come from the config; baselines exist but are flagged `measured: false`) and is
   labelled `sandbox_simulated_not_production_evidence` with `production_evidence: false`.
8. Negative checks: the validator rejects an unmeasured savings claim (truth_rule), a step that bypasses a safety device (safety_rule), and a task with a missing task_model field.

## Limitations
- The sample task, its data and the validator all live inside the test. There is no runtime validator module and no real integration.
- The benchmark builder only produces a requirements matrix of what would have to be measured. It does not measure anything.
