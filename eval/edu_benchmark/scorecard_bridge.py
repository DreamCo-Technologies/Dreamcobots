#!/usr/bin/env python3
"""Bridge: SET7 course packet + evidence bundle -> edu-mastery-scorecards evidence card.

The bridge is READ-ONLY with respect to both sides. It never edits a packet, never changes
evidence_state, and never issues a certificate (certificate is always null).
Mapping and citations: scorecard_mapping.json. Notes: ALIGNMENT_NOTES.md.

Usage:
  EDU_SCORECARDS_REPO=/path/to/edu-mastery-scorecards \
  python3 scorecard_bridge.py PACKET.json --bundle BUNDLE.json [--out card.json] [--gate PATH/cert_gate.py]
BUNDLE (dreamco.edu.evidence_bundle.v0.1):
  {"schema": "dreamco.edu.evidence_bundle.v0.1", "course_id": ..., "version": ...,
   "learner": {"id": ..., "type": "buddy_adapter|human|model"},
   "card_track": "k12|stem|college|career"   (only for school_college packets),
   "consent": false,                           (provenance consent; default false)
   "runs": [ ...packet run objects; if omitted, packet.evidence.runs are used ]}
Exit 0 only if: our validator passes, their gate PASSes, and their floor <= our policy cap.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True        # never drop __pycache__ into the scorecards repo
HERE = Path(__file__).resolve().parent
MAPPING = json.loads((HERE / "scorecard_mapping.json").read_text())
def scorecards_gate_path(repo=None):
    """edu-mastery-scorecards is a separate teammate repo (not vendored here). Point at it explicitly."""
    repo = repo or os.environ.get("EDU_SCORECARDS_REPO")
    return (Path(repo) / "gate" / "cert_gate.py") if repo else None
DEFAULT_GATE = scorecards_gate_path()
FLOORS = ["F0", "F1", "F2", "F3", "F4"]
GATE_BANKS = {"holdout", "transfer", "remediation_retest", "retention"}
CARD_TRACKS = {"k12", "stem", "college", "career"}
LEARNER_TYPES = {"buddy_adapter", "human", "model"}

class BridgeRefusal(Exception):
    pass

def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_gate(path=DEFAULT_GATE):
    if path is None or not Path(path).exists():
        raise FileNotFoundError(f"scorecards cert gate not found ({path}); set EDU_SCORECARDS_REPO or pass --gate")
    spec = importlib.util.spec_from_file_location("their_cert_gate", str(path))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def card_floors(p, best_holdout, transfers, remeds, rets):
    """strictest_wins; slots are filled with real run ids or left as MISSING-* (fail closed)."""
    f, d = p["floors"], MAPPING["their_defaults"]
    nulls = [k for k in ("unit_practice_min", "holdout_min", "min_comparable_runs", "transfer_tasks_min", "retention_retest_days") if f.get(k) is None]
    if nulls:
        raise BridgeRefusal(f"packet floors {nulls} are null; no card can be built from undefined floors")
    def slots(runs, n, tag):
        ids = [r["run_id"] for r in runs[:n]]
        return ids + [f"MISSING-{tag}-{i}" for i in range(len(ids) + 1, n + 1)]
    hmin = f["holdout_min"]
    return {
      "F0": {"name": d["F0"]["name"], "required_benches": slots(p["_runs"]["baseline"], 1, "baseline"), "min_score": d["F0"]["min_score"], "holdout_required": False},
      "F1": {"name": d["F1"]["name"], "required_benches": slots(p["_runs"]["practice"], 1, "practice"), "min_score": max(d["F1"]["min_score"], f["unit_practice_min"]), "holdout_required": False},
      "F2": {"name": d["F2"]["name"], "required_benches": slots(best_holdout, max(f["min_comparable_runs"], 3), "holdout-rep"), "min_score": max(d["F2"]["min_score"], hmin), "holdout_required": True},
      "F3": {"name": d["F3"]["name"], "required_benches": slots(transfers, max(f["transfer_tasks_min"], 1), "transfer") + slots(remeds, 1, "remediation-retest"), "min_score": max(d["F3"]["min_score"], hmin), "holdout_required": True},
      "F4": {"name": d["F4"]["name"], "required_benches": slots(rets, 1, "retention"), "min_score": max(d["F4"]["min_score"], hmin), "holdout_required": True,
             "min_days_since_prior_floor": max(d["F4"]["min_days_since_prior_floor"], f["retention_retest_days"]), "independent_evaluator_required": True},
    }

def bench(r, p):
    lc = r.get("leakage_check") or {"passed": False, "method": "NOT RECORDED (bridge fail-closed)"}
    return {"bench_id": r["run_id"], "suite": f"{p['course_id']}@{p['version']}:{r['bank']}", "holdout": r["bank"] in GATE_BANKS,
            "leakage_check": {"passed": bool(lc["passed"]), "method": lc["method"]}, "score": r["score"], "max_score": 1,
            "run_id": r["run_id"], "run_timestamp": r["ended_at"], "artifact_uri": r.get("artifact_uri") or r.get("trace_ref") or "",
            "artifact_sha256": r.get("artifact_sha256", ""), "evaluator": r.get("evaluator", "")}

def our_cap(p, best_holdout, transfers, remeds, rets):
    """Highest scorecard floor that SET7 policy itself would allow, plus the reasons it stops."""
    f, why = p["floors"], []
    ok_run = lambda r: r["safety_passed"] and r["regression_passed"] and not r["external_assistance"] and (r.get("leakage_check") or {}).get("passed") is True
    cap = None
    if p["_runs"]["baseline"]: cap = "F0"
    else: return None, ["no baseline run"]
    if p["_runs"]["practice"]: cap = "F1"
    else: return cap, ["no practice run"]
    if p["holdout_bank"]["store_status"] != "active": return cap, ["holdout store not active (SET7 4.2)"]
    if len(best_holdout) < max(f["min_comparable_runs"], 3): return cap, [f"only {len(best_holdout)} comparable holdout reps (need {max(f['min_comparable_runs'], 3)})"]
    for r in best_holdout:
        if not ok_run(r): why.append(f"run {r['run_id']} fails safety/regression/independence/leakage")
        for u, s in r["unit_scores"].items():
            if s < f["no_unit_below"]: why.append(f"run {r['run_id']} unit {u}={s} < no_unit_below {f['no_unit_below']}")
    if why: return cap, why
    cap = "F2"
    if not (transfers and remeds) or not all(ok_run(r) for r in transfers + remeds): return cap, ["F3 needs passing, leakage-checked transfer + remediation_retest runs"]
    cap = "F3"
    if not rets: return cap, ["no retention run"]
    gap = (max(_ts(r["started_at"]) for r in rets) - max(_ts(r["ended_at"]) for r in best_holdout)).days
    if gap < f["retention_retest_days"]: return cap, [f"retention only +{gap}d"]
    return "F4", []

def build_card(p, bundle):
    if p["track"] == "frontier_f_tier":
        raise BridgeRefusal("frontier_f_tier has no scorecards track (their schema:12) and their F0-F4 are not frontier tiers")
    lr = bundle.get("learner") or {}
    if not lr.get("id") or lr.get("type") not in LEARNER_TYPES:
        raise BridgeRefusal("bundle.learner {id, type in buddy_adapter|human|model} is required (not derived)")
    if p["track"] == "school_college":
        if bundle.get("card_track") not in CARD_TRACKS: raise BridgeRefusal("school_college needs bundle.card_track in k12|stem|college|career")
        track = bundle["card_track"]
    else:
        track = "bootcamp"
    for k in ("course_id", "version"):
        if k in bundle and bundle[k] != p[k]: raise BridgeRefusal(f"bundle {k}={bundle[k]!r} does not match packet {p[k]!r}")
    runs = [r for r in bundle.get("runs", p["evidence"]["runs"]) if not r["simulated"]]
    ids = [r["run_id"] for r in runs]
    if len(ids) != len(set(ids)):
        raise BridgeRefusal("duplicate run_id in bundle; their gate keys benches by id (cert_gate.py:49) and would hide a rep")
    by = {b: [r for r in runs if r["bank"] == b] for b in ("baseline", "practice", "holdout", "transfer", "remediation_retest", "retention")}
    groups = {}
    for r in by["holdout"]: groups.setdefault((r["fixture_hash"], r["grader_version"], r["subject_version"]), []).append(r)
    best = max(groups.values(), key=len, default=[])
    p = dict(p, _runs=by)
    floors = card_floors(p, best, by["transfer"], by["remediation_retest"], by["retention"])
    mapped = by["baseline"] + by["practice"] + best + by["transfer"] + by["remediation_retest"] + by["retention"]
    rets = by["retention"]
    card = {"_example": bool(p.get("is_example")), "card_id": f"BRIDGE-{p['course_id']}-{p['version']}-{lr['id']}",
            "course_id": p["course_id"], "course_title": p["title"], "track": track, "version": p["version"],
            "learner": {"id": lr["id"], "type": lr["type"]}, "floors": floors, "bench_results": [bench(r, p) for r in mapped],
            "provenance": {"sources": [{"uri": f"{s['repo']}:{s['path']}@{s['commit']}", "license": p["provenance"].get("license") or "",
                                        "consent": bool(bundle.get("consent", False))} for s in p["provenance"]["sources"]]},
            "floor_attained": None, "status": "draft", "certificate": None,
            "regression_watch": {"last_retest_at": max((r["started_at"] for r in rets), default=None), "drift_flag": any(not r["regression_passed"] for r in runs)}}
    cap, cap_why = our_cap(p, best, by["transfer"], by["remediation_retest"], by["retention"])
    return card, cap, cap_why

def bridge(p, bundle, gate=None):
    import validate as ours
    gate = gate or load_gate()
    our_errs, _ = ours.validate(p)
    card, cap, cap_why = build_card(p, bundle)
    highest, _ = gate.floor_status(card)
    card["floor_attained"] = highest
    st_map = MAPPING["field_map"]["status"]; st = st_map[p["evidence_state"]]
    card["status"] = ("floor_met" if highest else "in_progress") if st.startswith("floor_met") else st
    ok, reasons = gate.check_card(card)
    idx = lambda x: -1 if x is None else FLOORS.index(x)
    conflict = idx(highest) > idx(cap)
    return {"card": card, "our_validator_errors": our_errs, "our_policy_cap": cap, "our_cap_reasons": cap_why,
            "their_gate_pass": ok, "their_gate_reasons": reasons, "their_floor": highest,
            "conflict_their_floor_above_our_cap": conflict, "packet_evidence_state_unchanged": p["evidence_state"],
            "ok": (not our_errs) and ok and not conflict}

def main(argv):
    ap = argparse.ArgumentParser(); ap.add_argument("packet"); ap.add_argument("--bundle", required=True)
    ap.add_argument("--out"); ap.add_argument("--gate", default=str(DEFAULT_GATE) if DEFAULT_GATE else None,
                    help="path to edu-mastery-scorecards gate/cert_gate.py (default: $EDU_SCORECARDS_REPO/gate/cert_gate.py)"); a = ap.parse_args(argv)
    if not a.gate or not Path(a.gate).exists():
        print("ERROR: scorecards cert gate not available; set EDU_SCORECARDS_REPO=/path/to/edu-mastery-scorecards or pass --gate"); return 2
    p = json.loads(Path(a.packet).read_text()); b = json.loads(Path(a.bundle).read_text())
    try:
        res = bridge(p, b, load_gate(a.gate))
    except BridgeRefusal as e:
        print("REFUSED:", e); return 2
    if a.out: Path(a.out).write_text(json.dumps(res["card"], indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "card"}, indent=2))
    return 0 if res["ok"] else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
