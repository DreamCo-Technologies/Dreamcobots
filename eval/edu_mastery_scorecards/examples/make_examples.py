"""Generates EXAMPLE cards (fake data, placeholder hashes) for gate tests."""
import copy, json, os
H = lambda c: c * 64  # obviously placeholder hash
def bench(bid, suite, score, holdout=False, leak=True, ts="2026-09-01T12:00:00Z", ev="example-evaluator"):
    return {"bench_id": bid, "suite": suite, "holdout": holdout,
            "leakage_check": {"passed": leak, "method": "EXAMPLE n-gram overlap vs train"},
            "score": score, "max_score": 100, "run_id": f"EXAMPLE-run-{bid}", "run_timestamp": ts,
            "artifact_uri": f"file:///EXAMPLE/artifacts/{bid}.json", "artifact_sha256": H("a"), "evaluator": ev}
base = {
  "_example": True, "card_id": "EXAMPLE-CARD-ALG1-F2", "course_id": "EXAMPLE-k12-algebra-1",
  "course_title": "EXAMPLE Algebra I", "track": "k12", "version": "1.0.0",
  "learner": {"id": "EXAMPLE-buddy-adapter-v0", "type": "buddy_adapter"},
  "floors": {
    "F0": {"name": "baseline diagnostic", "required_benches": ["diag"], "min_score": 0.0, "holdout_required": False},
    "F1": {"name": "practice", "required_benches": ["practice"], "min_score": 0.70, "holdout_required": False},
    "F2": {"name": "held-out", "required_benches": ["holdout"], "min_score": 0.80, "holdout_required": True},
    "F3": {"name": "novel transfer + remediation retest", "required_benches": ["transfer", "retest"], "min_score": 0.80, "holdout_required": True},
    "F4": {"name": "regression retest + independent evaluator", "required_benches": ["regression"], "min_score": 0.80, "holdout_required": True, "min_days_since_prior_floor": 30, "independent_evaluator_required": True}},
  "bench_results": [bench("diag", "EXAMPLE-diag", 40), bench("practice", "EXAMPLE-practice", 78),
                    bench("holdout", "EXAMPLE-holdout", 85, holdout=True)],
  "provenance": {"sources": [{"uri": "EXAMPLE://openstax-algebra", "license": "CC-BY-4.0", "consent": True}]},
  "floor_attained": "F2", "status": "certified",
  "certificate": {"cert_id": "EXAMPLE-CERT-1", "floor": "F2", "issued_at": "2026-09-02T00:00:00Z",
                  "issued_by": "grok-edu-mastery-scorecards", "evidence_bench_ids": ["diag", "practice", "holdout"],
                  "evidence_hash": H("b")},
  "regression_watch": {"last_retest_at": None, "drift_flag": False}}
out = {"valid_certified_f2.json": base}
c = copy.deepcopy(base); c["card_id"] = "EXAMPLE-INVALID-NO-BENCHES"; c["bench_results"] = []
out["invalid_cert_no_benches.json"] = c
c = copy.deepcopy(base); c["card_id"] = "EXAMPLE-INVALID-OVERCLAIM-F3"; c["floor_attained"] = "F3"; c["certificate"]["floor"] = "F3"
out["invalid_overclaim_f3.json"] = c
c = copy.deepcopy(base); c["card_id"] = "EXAMPLE-INVALID-LEAKAGE"; c["bench_results"][2]["leakage_check"]["passed"] = False
out["invalid_leakage_failed.json"] = c
c = copy.deepcopy(base); c["card_id"] = "EXAMPLE-INVALID-MISSING-EVIDENCE"; c["certificate"]["evidence_bench_ids"].append("ghost")
out["invalid_missing_evidence_ref.json"] = c
c = copy.deepcopy(base); c["card_id"] = "EXAMPLE-VALID-F4"
c["bench_results"] += [bench("transfer", "EXAMPLE-transfer", 82, holdout=True, ts="2026-09-05T00:00:00Z"),
                       bench("retest", "EXAMPLE-retest", 84, holdout=True, ts="2026-09-06T00:00:00Z"),
                       bench("regression", "EXAMPLE-regression", 83, holdout=True, ts="2026-10-10T00:00:00Z", ev="EXAMPLE-independent-grader")]
c["floor_attained"] = "F4"; c["certificate"]["floor"] = "F4"; c["certificate"]["evidence_bench_ids"] += ["transfer", "retest", "regression"]
out["valid_certified_f4.json"] = c
d = copy.deepcopy(c); d["card_id"] = "EXAMPLE-INVALID-F4-TOO-SOON"; d["bench_results"][-1]["run_timestamp"] = "2026-09-20T00:00:00Z"
out["invalid_f4_retest_too_soon.json"] = d
d = copy.deepcopy(c); d["card_id"] = "EXAMPLE-INVALID-F4-SELF-GRADED"; d["bench_results"][-1]["evaluator"] = "grok-edu-mastery-scorecards"
out["invalid_f4_self_graded.json"] = d
here = os.path.dirname(os.path.abspath(__file__))
for name, card in out.items():
    with open(os.path.join(here, name), "w") as fh: json.dump(card, fh, indent=2)
print("\n".join(sorted(out)))
