# Buddy Frontier Promotion Checklist (F0 → F4)

Status: **pre-F0** (see `evidence/frontier/current-status.assessment.json`: `claimable: false`, `run_count: 0`).
Owner seat: Buddy frontier release captain. Source of floors: `reports/BUDDY_FRONTIER_MODEL_AND_PACKAGES.md` §2.2.
Gates referenced: `config/buddy-frontier-readiness-gates.json` (G1–G7, `never_claim_frontier_without_evidence: true`).

A floor is promoted only when **every** box below is checked with a committed artifact path. No box is checked from a plan, catalog size, routing path, or a single unverified run.

## Common to every floor
- [ ] Suite id, version, and `suite_hash` pinned in `evidence/frontier/<suite>.bundle.json`
- [ ] Buddy subject and named reference subject(s) recorded (model/version/tools)
- [ ] External-assist usage logged (teacher/tool calls counted)
- [ ] Cost and latency recorded where measurable
- [ ] Failures preserved, not filtered
- [ ] Assessment file regenerated; `claimable` reflects evidence
- [ ] Signed scorecard (Grok-Buddy-F0-Scorecard / eval-harness owner) linked

## F0 Baseline
- [ ] At least one pinned lane run with artifacts under `evidence/frontier/`
- [ ] Methodology stub committed (task set, grader, holdout policy)
- Allowed after F0: internal "baseline measured" wording only

## F1 Peer parity (targeted)
- [ ] Match/beat designated catalog peers on **held-out** tasks in ≥1 lane
- [ ] Leakage/contamination check recorded
- [ ] Signed scorecard + methodology
- Allowed after F1: "parity on <lane>, <suite>" with link; no "frontier"

## F2 Multi-lane competitive
- [ ] Competitive on ≥4 lanes including coding, reasoning, tools, safety
- [ ] Independent or reproducible harness (others can rerun)
- [ ] Regression suite green against previously mastered capabilities
- Earliest floor where scoped "frontier-competitive" language or any `production_ready` flip may be **proposed** (still needs owner approval + Prod-Cert-Gate)

## F3 Broad frontier competition
- [ ] Competitive across the evaluation matrix (`buddy/frontier/evaluation_matrix.md`) vs strong baselines
- [ ] Published methodology; variance / confidence intervals where applicable
- [ ] G7 evidence: fair reference tasks, independent evaluation

## F4 Native distillation
- [ ] Recurring teacher solutions reproduced with lower external dependency
- [ ] Before/after + holdout + regression artifacts
- [ ] Student adapter artifacts exist (`trained_weights_exist` only if real)

## Path D allowlist sync (`config/buddy/approved-models-allowlist.json`)
- Keep `production_ready: false` until F2+ for the claimed scope **and** owner approval.
- `live_benchmark_ok: true` only per entry with a signed live benchmark artifact.
- Add a Buddy-native/student entry only after F4-style evidence for that adapter.
- Current (2026-09-21): 3 stub seeds, all `live_benchmark_ok: false`. Correct; no change.

## GitHub Pages disclosure
- Pages may show only aggregated status sourced from committed evidence (`config/buddy-pages-data-pipeline.json`: `validate_no_false_pass_claims`, `publish_only_after_gate`).
- Missing or stale evidence renders as unknown/stale, never success.
- Frontier floor shown on Pages must equal the floor in the latest assessment file.
- Never publish secrets, private data, or raw sensitive logs.

## Vanity-release blockers (auto-fail)
- Claim based on catalog size, provider list, or model branding
- Claim without held-out tasks or without a reference subject
- Pages or marketing ahead of assessment file
- `production_ready` flip without Prod-Evidence-Ledger link
