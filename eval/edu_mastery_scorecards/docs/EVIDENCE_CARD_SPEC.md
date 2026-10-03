# Course Mastery Evidence Card: spec v1.0

One card per (course, learner). Schema: `schema/course_evidence_card.schema.json`. Gate: `gate/cert_gate.py`.

## Rule
**No completion certificate without benches.** A card may carry `certificate` or `status: certified` only when every
required bench for the claimed floor, and every lower floor, has a `bench_results` entry with a `run_id`, an
`artifact_uri`, a 64-hex `artifact_sha256`, a valid `run_timestamp`, and `score/max_score >= min_score`.
`floor_attained` must equal the highest floor the evidence supports (no over-claiming), and every
`certificate.evidence_bench_ids` entry must resolve to a real bench result. Provenance sources need a license and consent.

## F-style floors (defaults; per-course cards may raise them)
| Floor | Meaning | Min score | Held-out + leakage check |
|---|---|---|---|
| F0 | Baseline diagnostic recorded | 0.00 | no |
| F1 | Practice benches passed | 0.70 | no |
| F2 | Held-out benches passed | 0.80 | yes |
| F3 | Novel-transfer bench plus a retest after remediation | 0.80 | yes |
| F4 | F3, plus a regression retest at least 30 days later by an evaluator independent of the cert issuer | 0.80 | yes |

## Fields
`card_id`, `course_id`, `course_title`, `track` (k12|stem|college|career|bootcamp), `version`, `learner {id, type}`,
`floors {F0..F4: name, required_benches[], min_score, holdout_required, min_days_since_prior_floor?, independent_evaluator_required?}`,
`bench_results[] {bench_id, suite, holdout, leakage_check{passed,method}, score, max_score, run_id, run_timestamp, artifact_uri, artifact_sha256, evaluator}`,
`provenance.sources[] {uri, license, consent}`, `floor_attained`, `status` (draft|in_progress|remediation|floor_met|certified|revoked),
`certificate {cert_id, floor, issued_at, issued_by, evidence_bench_ids[], evidence_hash} | null`, `regression_watch {last_retest_at, drift_flag}`.

## Usage
`python3 gate/cert_gate.py card.json` exits 0 on PASS, 1 on FAIL with reasons. Tests: `python3 -m unittest -v tests.test_cert_gate`.
All files in `examples/` are EXAMPLE data with placeholder hashes, not real learner results.
