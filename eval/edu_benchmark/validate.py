#!/usr/bin/env python3
"""Validate DreamCo course packets: JSON Schema structure + SET7 policy (fail-closed).

Usage:  python3 validate.py [packet.json ...]     (default: all */*.packet.json next to this file)
        python3 validate.py --self-test           (negative cases must FAIL)
        python3 validate.py --self-test --scorecards-repo /path/to/edu-mastery-scorecards
            (or EDU_SCORECARDS_REPO=...) also runs the bridge/scorecards consistency checks against that
            separate repo's gate (read-only). Without it those checks are reported as SKIPPED (not passed).
            A path that is given but missing is a FAILURE.
Stdlib only; uses `jsonschema` for the structural pass if it is installed.
"""
from __future__ import annotations
import copy, json, re, sys
sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "course_packet.schema.json").read_text())

# SET7 sec 3.1 defaults. A floor below these needs an approved_lowering record.
MIN_FLOORS = {"unit_practice_min": 0.90, "course_exit_mean_min": 0.90, "holdout_min": 0.90,
              "no_unit_below": 0.80, "min_comparable_runs": 3, "retention_retest_days": 7,
              "transfer_tasks_min": 1}
MAX_FLOORS = {"critical_regressions_max": 0}   # higher = weaker
STATES = SCHEMA["$defs"]["evidence_state"]["enum"]
PRE_TEST = {"unknown", "registered", "baselined", "testing"}
CLAIM_STATES = {"passed", "mastered_candidate", "mastered"}
PLANNER_TOKENS = ("benchmark-gap-queue", "benchmark_gap_queue")   # tools/benchmark_gap_planner.py output

# ---------------- minimal JSON Schema (subset used by our schema) ----------------
_T = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
def _is(v, t):
    if t == "integer": return isinstance(v, int) and not isinstance(v, bool)
    if t == "number": return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _T[t])

def schema_errors(inst, sch, path="$", root=SCHEMA):
    if "$ref" in sch:
        node = root
        for part in sch["$ref"].lstrip("#/").split("/"): node = node[part]
        return schema_errors(inst, node, path, root)
    errs = []
    if "type" in sch:
        ts = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(_is(inst, t) for t in ts):
            return [f"{path}: expected {ts}, got {type(inst).__name__}"]
    if "const" in sch and inst != sch["const"]: errs.append(f"{path}: must equal {sch['const']!r}")
    if "enum" in sch and inst not in sch["enum"]: errs.append(f"{path}: {inst!r} not in {sch['enum']}")
    if isinstance(inst, str):
        if len(inst) < sch.get("minLength", 0): errs.append(f"{path}: too short")
        if "pattern" in sch and not re.search(sch["pattern"], inst): errs.append(f"{path}: !~ {sch['pattern']}")
    if _is(inst, "number"):
        if "minimum" in sch and inst < sch["minimum"]: errs.append(f"{path}: < {sch['minimum']}")
        if "maximum" in sch and inst > sch["maximum"]: errs.append(f"{path}: > {sch['maximum']}")
    if isinstance(inst, list):
        if len(inst) < sch.get("minItems", 0): errs.append(f"{path}: needs >= {sch['minItems']} items")
        if "items" in sch:
            for i, v in enumerate(inst): errs += schema_errors(v, sch["items"], f"{path}[{i}]", root)
    if isinstance(inst, dict):
        for k in sch.get("required", []):
            if k not in inst: errs.append(f"{path}: missing '{k}'")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props: errs += schema_errors(v, props[k], f"{path}.{k}", root)
            elif sch.get("additionalProperties") is False: errs.append(f"{path}: unexpected '{k}'")
    return errs

def structural(p):
    try:
        import jsonschema  # optional
        v = jsonschema.Draft202012Validator(SCHEMA)
        return [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in v.iter_errors(p)], "jsonschema"
    except ImportError:
        return schema_errors(p, SCHEMA), "stdlib-subset"

# ---------------- SET7 policy checks ----------------
def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def policy_errors(p):
    e, f, st = [], p["floors"], p["evidence_state"]
    lowered = {a["floor"]: a for a in f.get("approved_lowering", [])}
    # 1. floors: numeric, fail-closed, never silently below defaults
    nulls = [k for k in list(MIN_FLOORS) + list(MAX_FLOORS) if f.get(k) is None]
    for k, lo in MIN_FLOORS.items():
        v = f.get(k)
        if v is not None and v < lo:
            a = lowered.get(k)
            if not a or a["to"] != v or a["from"] < v:
                e.append(f"floors.{k}={v} below policy {lo} without matching approved_lowering record")
    for k, hi in MAX_FLOORS.items():
        v = f.get(k)
        if v is not None and v > hi and k not in lowered:
            e.append(f"floors.{k}={v} weaker than policy {hi} without approved_lowering")
    if None not in (f.get("no_unit_below"), f.get("unit_practice_min")) and f["no_unit_below"] > f["unit_practice_min"]:
        e.append("floors.no_unit_below exceeds unit_practice_min (inconsistent)")
    if nulls:
        if p["track"] != "frontier_f_tier":
            e.append(f"null floors {nulls} only allowed on frontier_f_tier pending definition")
        elif not f.get("todo", {}).get("owners"):
            e.append("null floors require floors.todo.owners")
        if st not in PRE_TEST:
            e.append(f"evidence_state '{st}' not allowed while floors {nulls} are undefined (fail-closed)")
    # 2. holdout isolation
    hb, pb = p["holdout_bank"], p["practice_bank"]
    hold_ids = set(hb.get("public_task_ids", [])) | set(hb["rotation"].get("burned_item_ids", []))
    bad_uses = set(pb["allowed_uses"]) & {"holdout", "gate"}
    if bad_uses: e.append(f"practice_bank.allowed_uses contains {bad_uses}")
    for need in ("train", "fine_tune", "rag", "lessons", "practice"):
        if need not in hb["forbidden_uses"]: e.append(f"holdout_bank.forbidden_uses must include '{need}'")
    pb_blob = json.dumps(pb)
    for tok in {hb["bank_id"], hb["private_store_path"].split()[0]}:
        if tok and tok in pb_blob: e.append(f"practice_bank references holdout token '{tok}'")
    if pb["ref"].rstrip("/") and hb["private_store_path"].split()[0].startswith(pb["ref"].split()[0].rstrip("/") + "/"):
        e.append("holdout store path is nested under practice ref")
    pids = {i["item_id"] for i in pb["items"]}
    leak = (pids | {x for m in p["modules"] for x in m.get("practice_item_ids", [])}) & hold_ids
    if leak: e.append(f"holdout/burned ids used as practice: {sorted(leak)}")
    # 3. EXAMPLE marking
    for i in pb["items"]:
        if i["is_example"] and not (i["item_id"].startswith("EXAMPLE-") and "EXAMPLE" in i["prompt"]):
            e.append(f"example item {i['item_id']} not clearly marked EXAMPLE")
    if p.get("is_example"):
        if "EXAMPLE" not in p["title"]: e.append("is_example packet title must contain EXAMPLE")
        if any(not i["is_example"] for i in pb["items"]): e.append("is_example packet has non-example items")
        if st in CLAIM_STATES: e.append("EXAMPLE packet can never reach a claim state")
    # 4. referential integrity
    obj = {o["id"] for o in p["objectives"]}; mods = {m["module_id"] for m in p["modules"]}
    for m in p["modules"]:
        for r in m["prereqs"]:
            if r not in mods: e.append(f"module {m['module_id']} prereq '{r}' unknown")
        for o in m["objective_ids"]:
            if o not in obj: e.append(f"module {m['module_id']} objective '{o}' unknown")
        for x in m.get("practice_item_ids", []):
            if x not in pids: e.append(f"module {m['module_id']} practice item '{x}' not in practice_bank")
    # 5. evidence / repetitions / state
    runs = p["evidence"]["runs"]
    missing_fields = set(SCHEMA["$defs"]["run"]["required"]) - set(p["evidence"]["required_run_fields"])
    if missing_fields: e.append(f"evidence.required_run_fields missing {sorted(missing_fields)}")
    if any(r["simulated"] for r in runs) and st not in PRE_TEST:
        e.append("simulated runs cannot support a post-testing state")
    # 5b. a work queue / green CI job is not a scored run (Benchmark Gap Planner, see ALIGNMENT_NOTES.md)
    for r in runs:
        refs = " ".join(str(r.get(k, "")) for k in ("trace_ref", "artifact_uri"))
        if any(tok in refs for tok in PLANNER_TOKENS):
            e.append(f"run {r['run_id']} cites a gap-planner queue as evidence; a planner work list/green job is not a scored run")
    if st in {"mastered_candidate", "mastered"}:
        n = f.get("min_comparable_runs") or 0
        hold = [r for r in runs if r["bank"] == "holdout" and not r["simulated"]]
        groups = {}
        for r in hold:
            groups.setdefault((r["fixture_hash"], r["grader_version"], r["subject_version"]), []).append(r)
        best = max(groups.values(), key=len, default=[])
        if max(n, 3) > len(best):
            e.append(f"state {st} needs >= {max(n,3)} comparable holdout reps (same fixture/grader/subject); have {len(best)}")
        for r in best:
            if f.get("holdout_min") is None or r["score"] < f["holdout_min"]:
                e.append(f"run {r['run_id']} holdout score {r['score']} below floor {f.get('holdout_min')}")
            if not (r["safety_passed"] and r["regression_passed"]) or r["external_assistance"]:
                e.append(f"run {r['run_id']} fails safety/regression/independence")
            if (r.get("leakage_check") or {}).get("passed") is False:
                e.append(f"run {r['run_id']} has a FAILED leakage_check (SET7 4.3: burn + replace before any claim)")
            for u, s in r["unit_scores"].items():
                if f.get("no_unit_below") is None or s < f["no_unit_below"]:
                    e.append(f"run {r['run_id']} unit {u}={s} below no_unit_below")
        if not [r for r in runs if r["bank"] == "transfer" and r["score"] >= (f.get("holdout_min") or 2)]:
            e.append(f"state {st} needs >= 1 passing transfer run")
        if hb["store_status"] != "active": e.append(f"state {st} requires an active sealed holdout store")
    if st == "mastered":
        ret = [r for r in runs if r["bank"] == "retention"]
        if best and ret:
            gap = (max(_ts(r["started_at"]) for r in ret) - max(_ts(r["ended_at"]) for r in best)).days
            if gap < (f.get("retention_retest_days") or 7): e.append(f"retention retest only +{gap}d")
        else:
            e.append("state mastered needs a retention retest run")
    return e

def validate(p):
    s, engine = structural(p)
    return s + ([] if s else policy_errors(p)), engine

# ---------------- self-test: each mutation MUST fail ----------------
def self_test(files):
    bc = json.loads(files[0].read_text())
    def m(fn):
        q = copy.deepcopy(bc); fn(q); return q
    def run(r=1, bank="holdout", score=0.95, fh="a"):
        return {"run_id": f"r{r}{bank}", "bank": bank, "rep_index": r, "fixture_hash": "sha256:" + fh * 64, "grader_version": "g1",
                "subject_version": "s1", "started_at": "2026-10-01T00:00:00Z", "ended_at": "2026-10-01T00:10:00Z", "cost_usd": 0,
                "latency_ms": 1, "score": score, "unit_scores": {"U-x": 0.9}, "external_assistance": False,
                "safety_passed": True, "regression_passed": True, "simulated": False}
    cases = {
        "holdout_min lowered to 0.85 silently": m(lambda q: q["floors"].update(holdout_min=0.85)),
        "no_unit_below lowered to 0.7 silently": m(lambda q: q["floors"].update(no_unit_below=0.7)),
        "min_comparable_runs=2": m(lambda q: q["floors"].update(min_comparable_runs=2)),
        "fail_closed false": m(lambda q: q["floors"].update(fail_closed=False)),
        "holdout unsealed": m(lambda q: q["holdout_bank"].update(sealed=False)),
        "holdout items inlined": m(lambda q: q["holdout_bank"].update(items=["x"])),
        "practice references holdout bank": m(lambda q: q["practice_bank"].update(ref=q["holdout_bank"]["bank_id"])),
        "holdout id reused as practice": m(lambda q: (q["holdout_bank"].update(public_task_ids=["universal-1000-smoke-001"]))),
        "null floor on bootcamp": m(lambda q: q["floors"].update(holdout_min=None)),
        "mastered_candidate with 2 reps": m(lambda q: (q.update(evidence_state="mastered_candidate"), q["holdout_bank"].update(store_status="active"),
                                                        q["evidence"].update(runs=[run(1), run(2), run(1, "transfer")]))),
        "mastered_candidate with 3 incomparable reps": m(lambda q: (q.update(evidence_state="mastered_candidate"), q["holdout_bank"].update(store_status="active"),
                                                        q["evidence"].update(runs=[run(1, fh="a"), run(2, fh="b"), run(3, fh="c"), run(1, "transfer")]))),
    }
    leak = run(1); leak["leakage_check"] = {"passed": False, "method": "test"}
    cases["mastered_candidate with a FAILED leakage_check rep"] = m(lambda q: (q.update(evidence_state="mastered_candidate"), q["holdout_bank"].update(store_status="active"),
                                                        q["evidence"].update(runs=[leak, run(2), run(3), run(1, "transfer")])))
    planner = run(9, "practice"); planner["trace_ref"] = "github:DreamCo-Technologies/Dreamcobots/actions/runs/37065929919 artifact benchmark-gap-queue"
    cases["gap-planner queue cited as a run (green job != evidence)"] = m(lambda q: q["evidence"].update(runs=[planner]))
    ok_lower = m(lambda q: q["floors"].update(holdout_min=0.85, approved_lowering=[{"floor": "holdout_min", "from": 0.9, "to": 0.85,
                  "approved_by_human": "TEST-ONLY", "rationale": "self-test positive control", "approved_at": "2026-09-28"}]))
    ok_mc = m(lambda q: (q.update(evidence_state="mastered_candidate"), q["holdout_bank"].update(store_status="active"),
                         q["evidence"].update(runs=[run(1), run(2), run(3), run(1, "transfer")])))
    fails = 0
    for name, q in cases.items():
        errs, _ = validate(q)
        print(f"  [{'OK ' if errs else 'BAD'}] must FAIL: {name}  -> {errs[0] if errs else 'accepted!'}")
        fails += not errs
    for name, q in {"approved lowering record": ok_lower, "mastered_candidate w/ 3 comparable reps + transfer": ok_mc}.items():
        errs, _ = validate(q)
        print(f"  [{'OK ' if not errs else 'BAD'}] must PASS: {name}  {errs if errs else ''}")
        fails += bool(errs)
    return fails

# ---------------- bridge / scorecards consistency (read-only use of their gate) ----------------
def bridge_self_test(bc, repo=None):
    import scorecard_bridge as sb
    gate_path = sb.scorecards_gate_path(repo)
    if gate_path is None:
        print("  [SKIP] 12 bridge checks NOT run: edu-mastery-scorecards is a separate repo; set EDU_SCORECARDS_REPO or --scorecards-repo to run them"); return 0
    spec_md = gate_path.parent.parent / "docs" / "EVIDENCE_CARD_SPEC.md"
    if not gate_path.exists() or not spec_md.exists():
        print(f"  [BAD] scorecards repo requested but gate/spec not found under {gate_path.parent.parent}"); return 1
    gate = sb.load_gate(gate_path)
    fails = 0
    def check(name, cond, detail=""):
        nonlocal fails
        print(f"  [{'OK ' if cond else 'BAD'}] {name}  {'' if cond else detail}"); fails += not cond
    # mapping vs their spec table (EVIDENCE_CARD_SPEC.md:15-19)
    rows = {m.group(1): float(m.group(2)) for m in re.finditer(r"^\| (F[0-4]) \|[^|]*\| ([0-9.]+) \|", spec_md.read_text(), re.M)}
    mine = {k: v["min_score"] for k, v in sb.MAPPING["their_defaults"].items() if k.startswith("F")}
    check("mapping their_defaults == EVIDENCE_CARD_SPEC.md F0-F4 min_score table", rows == mine, f"{rows} vs {mine}")
    check("mapping F4 30-day rule present in spec text", "at least 30 days later" in spec_md.read_text() and sb.MAPPING["their_defaults"]["F4"]["min_days_since_prior_floor"] == 30)
    def pk(**kw):
        q = copy.deepcopy(bc); q.update(evidence_state="mastered_candidate"); q["holdout_bank"]["store_status"] = "active"
        q["provenance"]["license"] = "TEST-ONLY"; q.update(kw); return q
    def rn(i, bank, score=0.95, fh="a", unit=0.9, leak=True, ts="2026-10-01T00:10:00Z"):
        r = {"run_id": f"t{i}{bank}", "bank": bank, "rep_index": i, "fixture_hash": "sha256:" + fh * 64, "grader_version": "g1", "subject_version": "s1",
             "started_at": ts, "ended_at": ts, "cost_usd": 0, "latency_ms": 1, "score": score, "unit_scores": {"U-x": unit},
             "external_assistance": False, "safety_passed": True, "regression_passed": True, "simulated": False,
             "artifact_uri": f"file:///TEST/{i}{bank}.json", "artifact_sha256": "c" * 64, "evaluator": "TEST-evaluator"}
        if leak: r["leakage_check"] = {"passed": True, "method": "TEST"}
        return r
    base_runs = [rn(1, "baseline", 0.2), rn(1, "practice"), rn(1, "holdout"), rn(2, "holdout"), rn(3, "holdout"), rn(1, "transfer")]
    B = {"learner": {"id": "TEST-learner", "type": "buddy_adapter"}, "consent": True}
    def go(q, runs):
        q["evidence"]["runs"] = runs; return sb.bridge(q, dict(B, runs=runs), gate)
    r = go(pk(), base_runs)
    check("bridge: 3 comparable leakage-checked reps + transfer -> card F2, gate PASS, no certificate, state untouched",
          r["ok"] and r["their_floor"] == "F2" and r["card"]["certificate"] is None and r["card"]["status"] != "certified" and r["packet_evidence_state_unchanged"] == "mastered_candidate", r)
    lo = {k: v["min_score"] for k, v in r["card"]["floors"].items()}
    check("bridge: card floors F1-F4 >= SET7 0.90 and >= their defaults (strictest wins)",
          all(lo[k] >= max(MIN_FLOORS["holdout_min"], sb.MAPPING["their_defaults"][k]["min_score"]) for k in ("F1", "F2", "F3", "F4"))
          and r["card"]["floors"]["F4"]["min_days_since_prior_floor"] >= max(30, MIN_FLOORS["retention_retest_days"]), lo)
    r = go(pk(), base_runs[:4] + base_runs[5:])
    check("bridge: only 2 holdout reps -> F2 NOT reached", r["their_floor"] in (None, "F0", "F1"), r["their_floor"])
    nl = [dict(x) for x in base_runs]; [x.pop("leakage_check") for x in nl if x["bank"] == "holdout"]
    r = sb.bridge(dict(pk(), evidence=dict(bc["evidence"], runs=[])), dict(B, runs=nl), gate)
    check("bridge: missing leakage_check -> treated as failed, F2 NOT reached", r["their_floor"] in (None, "F0", "F1"), r["their_floor"])
    lowu = [dict(x) for x in base_runs]; lowu[3] = rn(2, "holdout", unit=0.75)
    r = sb.bridge(dict(pk(), evidence=dict(bc["evidence"], runs=[])), dict(B, runs=lowu), gate)
    check("bridge: unit 0.75 < no_unit_below -> their F2 above our cap is FLAGGED (ok=false)", r["conflict_their_floor_above_our_cap"] and not r["ok"], r)
    r = sb.bridge(dict(pk(), evidence=dict(bc["evidence"], runs=[])), dict(B, runs=base_runs, consent=False), gate)
    check("bridge: provenance without consent -> their gate FAIL", not r["their_gate_pass"])
    for name, q, b in [("frontier packet", dict(pk(), track="frontier_f_tier"), B),
                       ("duplicate run_id", pk(), dict(B, runs=base_runs + [base_runs[2]])),
                       ("no learner", pk(), {"runs": base_runs})]:
        try: sb.bridge(q, b, gate); refused = False
        except sb.BridgeRefusal: refused = True
        check(f"bridge: refuses {name}", refused)
    real = sb.bridge(bc, dict(B, runs=bc["evidence"]["runs"]), gate)
    check("bridge: real BC packet (0 runs) -> their_floor None, gate not ok", real["their_floor"] is None and not real["ok"], real["their_floor"])
    return fails

def main(argv):
    st = "--self-test" in argv
    sc_repo, rest, it = None, [], iter(argv)
    for a in it:
        if a == "--scorecards-repo": sc_repo = next(it, None)
        elif a.startswith("--scorecards-repo="): sc_repo = a.split("=", 1)[1]
        else: rest.append(a)
    files = [Path(a) for a in rest if not a.startswith("--")] or sorted(HERE.glob("*/*.packet.json"))
    bad = 0
    for fp in files:
        errs, engine = validate(json.loads(fp.read_text()))
        print(f"{'PASS' if not errs else 'FAIL'}  {fp.relative_to(HERE) if fp.is_absolute() else fp}  [{engine}]")
        for x in errs: print("   -", x)
        bad += bool(errs)
    if st:
        print("self-test (policy negatives/positives on a copy of the bootcamp packet):")
        bad += self_test(sorted(HERE.glob("bootcamp/*.packet.json")))
        print("bridge/scorecards consistency (read-only import of edu-mastery-scorecards gate):")
        bad += bridge_self_test(json.loads(sorted(HERE.glob("bootcamp/*.packet.json"))[0].read_text()), sc_repo)
    print("RESULT:", "ALL PASS" if not bad else f"{bad} FAILURE(S)")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
