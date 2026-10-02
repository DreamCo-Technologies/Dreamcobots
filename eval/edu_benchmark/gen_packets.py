#!/usr/bin/env python3
"""Regenerate the course packets (bootcamp/, school_college/, frontier/) deterministically.

Source resolution (first match wins):
  1. $EDU_BENCH_SRC                         explicit source root
  2. the Dreamcobots repo root (../../ from this file) when run inside the repo
  3. ../repo_src                            box snapshot layout (outside the repo)
Every source's sha256 is checked against PINNED. If content matches, the pinned commit is
recorded. If not, the packet records the new sha with commit "WORKTREE (differs from pin ...)"
and a warning is printed, so drift is never silent.
Inputs that are NOT in this repo (the Benchmark Gap Planner CI artifact, the teammate
edu-mastery-scorecards repo) use pinned literal values. They are re-verified only when available
($EDU_GAP_QUEUE / ../repo_src/ci_artifacts, $EDU_SCORECARDS_REPO).
This script never sets evidence_state from planner or scorecard data.
"""
import json, hashlib, os, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
REPO = "DreamCo-Technologies/Dreamcobots"; COMMIT = "2ccd678e5a242e085285cae1f7cf6818b5557f70"; RETR = "2026-09-28T17:35:00-05:00"
def _pick_src():
    if os.environ.get("EDU_BENCH_SRC"): return pathlib.Path(os.environ["EDU_BENCH_SRC"]), "env"
    root = HERE.parent.parent
    if (root / "benchmarks/tasks/universal_1000_smoke.json").exists(): return root, "repo"
    return HERE.parent / "repo_src", "snapshot"
SRC, SRC_MODE = _pick_src()
# path -> (commit the content was read at, sha256). Content on main @5ba09f2 is byte-identical to these.
PINNED = {
 "benchmarks/README.md": (COMMIT, "4a3bacb1bf6f2c9a94d070ded205e919d676151cbd43a267a75b91f1eccd5862"),
 "benchmarks/tasks/universal_1000_smoke.json": (COMMIT, "ab55bf8772214a9faf03a9ac87bd9cad8cb2cf5f4ed7a17f3d7a3152a696f46e"),
 "buddy/frontier/frontier_competition_policy.json": (COMMIT, "0ef6aac8f9a85f7940ba7ac74fb0df4afd6129b4dfa3a757b15a58909e49d51c"),
 "config/buddy-frontier-readiness-gates.json": (COMMIT, "a6a2cc4f830fd16681e16c533ed116f74faf70d2cdd5dc33a8a371f3bd18033e"),
 "config/frontier-evidence-suite.json": (COMMIT, "6a0b9500a4cdb7bdb45c3ed1cf66845a45f90073f5933f41ba31cace8f0f1447"),
 "docs/BENCHMARK_EVIDENCE_LIFECYCLE.md": (COMMIT, "f7c9c8ed6aabfe1e8ec8ea45ad4d6245b49d720d7dd8ac6fd3852a2abcaf5eb9"),
 "docs/BUDDY_1000_SOURCE_BOOTCAMP.md": (COMMIT, "bd8a0ae84bdf22cb45cb89be8d616443053e6e38fde3933310d828661439e178"),
 "docs/BUDDY_FRONTIER_EVALUATION_HARNESS.md": (COMMIT, "1c76f7c08faaab48ed09c98c4f3e2b7e31b76b3f81b2779a9bb44ea16e947545"),
 "docs/FRONTIER_EVIDENCE_PLAN_2026.md": (COMMIT, "5c786cc89dfbbe007c93524ea83926b5872df744ec976baa8abd1c4b0e3ae5f7"),
 "docs/REASONING_EFFICIENCY_AND_AI_COURSE_SYSTEM.md": (COMMIT, "af51dfc6cbd795b353bf6430551e839f9fdca65c76a5e45cd933cb161f556f83"),
 "docs/universal-education-engine.md": (COMMIT, "88cf5af54fbdda6e0a3318ff399de5585b5f21aa78ea0109714e21caccb3e17c"),
 "evidence/frontier/current-status.assessment.json": (COMMIT, "a9706373788fc31b86d41e256d826e23c8bbba9351028c20dc01f5b41838a3ad"),
 "tools/verify_frontier_evidence.py": (COMMIT, "fe823ffa154ab3499488e734def847f44e40a872044f93a0b55df05cf12bb3df"),
 ".github/workflows/benchmark-gap-planner.yml": ("5ba09f2ea0c1ef49e8e41bbca78c317ad70be8e9", "ca00732369d82e6c8ac610b3c18729e55457646f3f165ab81eb0a49fc83c0bcf"),
 "tools/benchmark_gap_planner.py": ("5ba09f2ea0c1ef49e8e41bbca78c317ad70be8e9", "32db21e54436626df7dd152a95fa6e2f5838a12f191c54af18337d8c9856d6a4"),
}
WARN = []
def _sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def src_at(p, commit=None, retr=RETR, path_label=None):
    pin_commit, pin_sha = PINNED[p]; got = _sha(SRC / p)
    if got != pin_sha:
        WARN.append(f"{p}: sha256 {got[:12]} differs from pin {pin_sha[:12]} @{pin_commit[:7]}; re-pin after review")
        pin_commit = f"WORKTREE (differs from pin {pin_commit[:7]})"
    return {"repo": REPO, "path": path_label or p, "commit": pin_commit, "sha256": got, "retrieved_at": retr}
def src(p): return src_at(p)
_POLICY = HERE / "SET7_COURSE_MASTERY_FLOORS_AND_HOLDOUT_POLICY.md"
if _POLICY.exists():   # in-repo layout: policy ships in the same tree as the packets
    POLICY_SRC = {"repo": REPO, "path": "eval/edu_benchmark/SET7_COURSE_MASTERY_FLOORS_AND_HOLDOUT_POLICY.md", "commit": "same tree as this packet", "sha256": _sha(_POLICY)}
else:                  # box layout
    _POLICY = HERE.parent / "SET7_COURSE_MASTERY_FLOORS_AND_HOLDOUT_POLICY.md"
    POLICY_SRC = {"repo": "local", "path": str(_POLICY), "commit": "n/a (local draft v0.1)", "sha256": _sha(_POLICY)}
RUN_FIELDS = ["run_id","bank","rep_index","fixture_hash","grader_version","subject_version","started_at","ended_at","cost_usd","latency_ms","score","unit_scores","external_assistance","safety_passed","regression_passed","simulated"]
FORBID = ["train","fine_tune","rag","lessons","prompts","practice"]
ROT = {"cadence":"weekly","burned_item_policy":"retire_and_replace_before_any_claim","isomorphism_screen":"fail_closed","burned_item_ids":[]}
STD_FLOORS = {"fail_closed": True, "unit_practice_min": 0.9, "course_exit_mean_min": 0.9, "no_unit_below": 0.8, "holdout_min": 0.9, "transfer_tasks_min": 1, "min_comparable_runs": 3, "retention_retest_days": 7, "critical_regressions_max": 0, "efficiency_envelope": None, "trust_suite_required": None,
  "basis": "SET7 sec 3.1: 0.90 seed from benchmarks/tasks/universal_1000_smoke.json mastery_threshold=0.9; no unit <0.80, >=3 comparable runs, +7d retention are SET7 policy (runs>=3 also matches config/frontier-evidence-suite.json minimum_repetitions=3).", "approved_lowering": []}
PLACEHOLDER_STORE = "PLACEHOLDER://private-eval-store/eval/holdouts/{cid}/  (proposed in SET7 sec 7; NOT provisioned, not in any repo)"


# ---- Benchmark Gap Planner (CI artifact, not in repo) ingest: literal values only; NEVER moves evidence_state ----
GP_COMMIT = "5ba09f2ea0c1ef49e8e41bbca78c317ad70be8e9"; GP_RETR = "2026-10-02T16:44:00-05:00"
GP_RUN, GP_ART = 37065929919, 11252566778
GP_QUEUE_SHA = "6d75a7ab8e7b6566ad511dcfb5be31ef84b204392d173ad5a50c9b68477b4676"   # inner benchmark-gap-queue.json (runs 37065929919 + 37032509096 identical)
# Literal summary of that artifact (verified below when the artifact file is available).
PINNED_GAP_SUMMARY = {"schema": "dreamco.benchmark_gap_queue.v1", "divisions": 65, "queue_items": 65, "divisions_listed": 65,
    "by_action": {"RUN_BENCHMARKS": 65}, "by_reason": {"no measured evidence": 65}, "by_priority": {"0": 65},
    "items_with_benchmark_or_score": 0, "measurement_policy": "unknown is not failure", "mastery_policy": "repeatable evidence required"}
def _gap_queue_file():
    cands = [os.environ.get("EDU_GAP_QUEUE"), HERE.parent / f"repo_src/ci_artifacts/benchmark-gap-planner/run-{GP_RUN}/benchmark-gap-queue.json"]
    return next((pathlib.Path(c) for c in cands if c and pathlib.Path(c).exists()), None)
def _summarize(q):
    items = q["queue"]
    count = lambda k: {str(v): sum(1 for i in items if i.get(k) == v) for v in sorted({i.get(k) for i in items}, key=str)}
    return {"schema": q["schema"], "divisions": q["divisions"], "queue_items": len(items), "divisions_listed": len({i["division"] for i in items}),
            "by_action": count("action"), "by_reason": count("reason"), "by_priority": count("priority"),
            "items_with_benchmark_or_score": sum(1 for i in items if "benchmark" in i or "score" in i),
            "measurement_policy": q["measurement_policy"], "mastery_policy": q["mastery_policy"]}
def ingest_gap_queue():
    f = _gap_queue_file()
    if f is not None:
        if _sha(f) != GP_QUEUE_SHA or _summarize(json.loads(f.read_text())) != PINNED_GAP_SUMMARY:
            sys.exit(f"gap queue {f} differs from the pinned artifact; update PINNED_GAP_SUMMARY/GP_QUEUE_SHA deliberately")
    summary = PINNED_GAP_SUMMARY
    art = f"github:{REPO}/actions/runs/{GP_RUN}/artifacts/{GP_ART} (benchmark-gap-queue.json)"
    refs = [
      {"path": art, "key": "summary", "value": summary, "binding": False,
       "note": "Gap Planner run 37065929919 (2026-10-02 16:17 CT, head 5ba09f2, green). 'Green' only means the job ran. Its input benchmark-scores.json does not exist on main, so every division is queued RUN_BENCHMARKS / 'no measured evidence'. It contains no scores, thresholds, or per-course data. Context only; does not move evidence_state."},
      {"path": "tools/benchmark_gap_planner.py", "key": "inputs/outputs", "value": "reads benchmark-scores.json {results:[division,benchmark,score,target,status,evidence_count]}; writes benchmark-gap-queue.json (artifact only, never committed); 'divisions' = 65 MasterBots, not courses", "binding": False,
       "note": f"@{GP_COMMIT[:7]} lines 14-34; target comes from the (absent) input file; script defines no threshold of its own."}]
    sources = [src_at(".github/workflows/benchmark-gap-planner.yml", GP_COMMIT, GP_RETR), src_at("tools/benchmark_gap_planner.py", GP_COMMIT, GP_RETR),
               {"repo": REPO, "path": f"actions/runs/{GP_RUN}/artifacts/{GP_ART}:benchmark-gap-queue.json", "commit": GP_COMMIT, "sha256": GP_QUEUE_SHA, "retrieved_at": GP_RETR}]
    gap = {"gap": f"Benchmark Gap Planner: benchmark-scores.json is absent on main (404 @ {GP_COMMIT[:7]}), so the scheduled green runs report {summary['by_reason']} across {summary['divisions']} divisions. There are no per-bot or per-benchmark scores to ingest. Its queue is keyed by MasterBot division (1-65), not course_id, and no course->division map exists.",
           "owner": "Dreamcobots benchmark owners (unassigned) + Grok-Edu-Benchmark-Planner"}
    return refs, sources, gap
GP_REFS, GP_SOURCES, GP_GAP = ingest_gap_queue()

# ---- edu-mastery-scorecards (teammate repo, NOT part of Dreamcobots; read-only) refs for F0 alignment ----
SC_COMMIT = "466e831dab89124c46453268902abe9e8088dac6"
SC_PINNED = {"docs/EVIDENCE_CARD_SPEC.md": "60336ba94b4fb1ac3b92fa90a2180ac323c924da5628a8f8d86f0b0fbcd4e2e3",
             "gate/cert_gate.py": "ae974754d21238894dfa642cf98569d9d665b2d4b30cbae31c2e96a859bda97f"}
def sc_src(p):
    root = os.environ.get("EDU_SCORECARDS_REPO")
    if root and (pathlib.Path(root) / p).exists() and _sha(pathlib.Path(root) / p) != SC_PINNED[p]:
        WARN.append(f"edu-mastery-scorecards {p} differs from pin @{SC_COMMIT[:7]}; alignment notes may be stale")
    return {"repo": "edu-mastery-scorecards (Grok-Edu-Mastery-Scorecards; separate repo, not in Dreamcobots)", "path": p, "commit": SC_COMMIT, "sha256": SC_PINNED[p], "retrieved_at": GP_RETR}

smoke = json.loads((SRC/"benchmarks/tasks/universal_1000_smoke.json").read_text())
t = smoke["tasks"][0]
caps = t["required_capabilities"]
bc = {
 "schema":"dreamco.edu.course_packet.v0.1", "course_id":"BC-universal-1000-smoke", "version":"0.1.0",
 "title": smoke["name"] + " (Bootcamp course packet)", "track":"bootcamp", "is_example": False,
 "objectives": [{"id":"OBJ-1","statement": "Given an unseen legitimate productivity goal: " + t["goal"], "observable": True}] +
   [{"id": f"OBJ-{c}", "statement": f"Demonstrate observable {c.replace('_',' ')} as part of the decomposition, scored by the grader.", "observable": True} for c in caps],
 "modules": [{"module_id": f"U-{c}", "title": c.replace('_',' ').title(), "required": True, "prereqs": [],
   "concepts":[{"concept_id": c, "name": c.replace('_',' '), "prereqs": []}], "objective_ids": ["OBJ-1", f"OBJ-{c}"], "practice_item_ids": [t["task_id"]]} for i,c in enumerate(caps)],
 "practice_bank": {"bank_id":"PB-universal-1000-smoke", "visibility":"practice", "ref": f"github:{REPO}@{COMMIT}:benchmarks/tasks/universal_1000_smoke.json",
   "allowed_uses":["train","rag","lessons","drills","adaptive_samples"],
   "items":[{"item_id": t["task_id"], "module_id":"U-task_decomposition", "kind":"exercise", "prompt": t["goal"], "expected_check":"Covers all required_capabilities: " + ", ".join(caps) + " (grader rubric not yet pinned)", "is_example": False, "source_ref":"benchmarks/tasks/universal_1000_smoke.json#tasks[0]"}]},
 "holdout_bank": {"bank_id":"HB-universal-1000-smoke", "sealed": True, "private_store_path": PLACEHOLDER_STORE.format(cid="BC-universal-1000-smoke"), "store_status":"placeholder_not_provisioned", "item_count": 0,
   "public_task_ids": [], "forbidden_uses": FORBID, "dual_control_required": True, "rotation": ROT, "public_disclosure":"aggregate_scores_and_evidence_refs_only"},
 "grader_contract": {"grader_id":"benchmarks/buddy_benchmark_runner.py", "grader_version": None, "type":"deterministic", "score_range":[0,1], "timeout_s": None, "assistance_policy":"none", "judge_policy_disclosed": False,
   "comparability_keys":["fixture_hash","grader_version","subject_version","timeout_s","assistance_policy"], "entrypoint":"python3 benchmarks/buddy_benchmark_runner.py benchmarks/tasks/universal_1000_smoke.json",
   "notes":"Runner is stdlib shell per benchmarks/README.md; grader_version and timeout not pinned in repo -> TODO."},
 "floors": dict(STD_FLOORS), "evidence_state":"registered",
 "evidence":{"required_run_fields": RUN_FIELDS, "bundle_ref": None, "runs": []},
 "provenance":{"sources":[src("benchmarks/tasks/universal_1000_smoke.json"), src("benchmarks/README.md"), src("docs/BUDDY_1000_SOURCE_BOOTCAMP.md"), src("docs/BENCHMARK_EVIDENCE_LIFECYCLE.md"), POLICY_SRC] + GP_SOURCES,
   "rights_note":"Task text quoted from DreamCo-owned public repo; practice-only because it is public. No third-party content.", "license": None},
 "repo_references":[
   {"path":"benchmarks/tasks/universal_1000_smoke.json","key":"mastery_threshold","value":0.9,"binding":False,"note":"Seed for 0.90 floors (floors object is the binding copy)."},
   {"path":"benchmarks/tasks/universal_1000_smoke.json","key":"tasks[0].human_approval_required_for","value":t["human_approval_required_for"],"binding":False},
   {"path":"benchmarks/tasks/universal_1000_smoke.json","key":"tasks[0].baseline_score","value":t["baseline_score"],"binding":False,"note":"Placeholder 0.0 in repo, not a measured baseline."}] + GP_REFS,
 "open_gaps":[
   {"gap":"Only 1 public practice task; the smoke task is public so it can NEVER be a holdout. Need a sealed holdout set (>=1 transfer task) authored under dual control.","owner":"Bootcamp Commandant + Grok-Edu-Benchmark-Planner","blocking_states":["passed","mastered_candidate","mastered"]},
   {"gap":"Per-unit scoring: runner emits one task score; no_unit_below 0.80 needs per-capability unit_scores from the grader.","owner":"Bootcamp Commandant"},
   {"gap":"grader_version / timeout_s not pinned; efficiency envelope for deployment tier undefined.","owner":"Bootcamp Commandant"},
   GP_GAP,
   {"gap":"Scorecards bridge: provenance.license is null and there is no consent record, so every card bridged to edu-mastery-scorecards FAILs its gate (cert_gate.py:114-116). Runs also need artifact_uri, artifact_sha256, evaluator, and leakage_check.","owner":"Grok-Edu-Benchmark-Planner + Grok-Edu-Mastery-Scorecards"}]
}

sc_units = [("U1","Descriptive statistics",[]),("U2","Probability basics",["U1"]),("U3","Sampling distributions & CLT",["U2"]),("U4","Confidence intervals & hypothesis tests",["U3"])]
sc = {
 "schema":"dreamco.edu.course_packet.v0.1", "course_id":"SC-EXAMPLE-intro-statistics", "version":"0.1.0-example",
 "title":"EXAMPLE — Intro Statistics (school/college course packet skeleton)", "track":"school_college", "is_example": True,
 "objectives":[{"id":f"OBJ-{u}","statement":f"EXAMPLE objective: learner correctly solves {n.lower()} problems and explains the method.","observable":True,"is_example":True} for u,n,_ in sc_units],
 "modules":[{"module_id":u,"title":n,"required":True,"prereqs":p,"concepts":[{"concept_id":f"{u}-C1","name":f"EXAMPLE concept for {n}","prereqs":[f"{q}-C1" for q in p]}],"objective_ids":[f"OBJ-{u}"],"practice_item_ids":[f"EXAMPLE-{u}-P1",f"EXAMPLE-{u}-P2"]} for u,n,p in sc_units],
 "practice_bank":{"bank_id":"PB-EXAMPLE-intro-statistics","visibility":"practice","ref":"PLACEHOLDER://practice/SC-EXAMPLE-intro-statistics/items.jsonl (EXAMPLE; inline items below)",
   "allowed_uses":["train","rag","lessons","drills","adaptive_samples"],
   "items":[it for u,n,_ in sc_units for it in (
     {"item_id":f"EXAMPLE-{u}-P1","module_id":u,"kind":"exercise","prompt":f"EXAMPLE PLACEHOLDER practice item ({n}) — replace with an educator-authored item.","expected_check":"EXAMPLE PLACEHOLDER check","is_example":True},
     {"item_id":f"EXAMPLE-{u}-P2","module_id":u,"kind":"novel_variant","prompt":f"EXAMPLE PLACEHOLDER isomorphic variant ({n}).","expected_check":"EXAMPLE PLACEHOLDER check","is_example":True})]},
 "holdout_bank":{"bank_id":"HB-EXAMPLE-intro-statistics","sealed":True,"private_store_path":PLACEHOLDER_STORE.format(cid="SC-EXAMPLE-intro-statistics"),"store_status":"placeholder_not_provisioned","item_count":None,
   "public_task_ids":[],"forbidden_uses":FORBID,"dual_control_required":True,"rotation":ROT,"public_disclosure":"aggregate_scores_and_evidence_refs_only"},
 "grader_contract":{"grader_id":"EXAMPLE-deterministic-numeric-plus-rubric","grader_version":None,"type":"hybrid","score_range":[0,1],"timeout_s":None,"assistance_policy":"none","judge_policy_disclosed":True,
   "comparability_keys":["fixture_hash","grader_version","subject_version","timeout_s","assistance_policy"],"entrypoint":None,
   "notes":"EXAMPLE: numeric answers auto-graded with tolerance; explanations via educator rubric (educator override per universal-education-engine.md). Human learners: PII excluded from evidence."},
 "floors": dict(STD_FLOORS), "evidence_state":"unknown",
 "evidence":{"required_run_fields":RUN_FIELDS,"bundle_ref":None,"runs":[]},
 "provenance":{"sources":[src("docs/universal-education-engine.md"), src("docs/REASONING_EFFICIENCY_AND_AI_COURSE_SYSTEM.md"), POLICY_SRC],
   "rights_note":"EXAMPLE packet; all items are placeholders. Real items must be original DreamCo content (BUDDY_BOT_BOOTCAMP.md source integrity) with rights recorded per item.","license":None},
 "open_gaps":[
   {"gap":"No real course content; pick a pilot course + educator owner; author practice + sealed holdout banks.","owner":"Grok-Edu-Benchmark-Planner (+ human educator reviewer)","blocking_states":["registered","baselined","testing","passed","mastered_candidate","mastered"]},
   {"gap":"Human-learner evidence schema variant (PII handling, consent) not defined; run schema is bot-oriented.","owner":"Grok-Edu-Benchmark-Planner"}]
}

f0 = {
 "schema":"dreamco.edu.course_packet.v0.1", "course_id":"F0", "version":"0.0.1-undefined",
 "title":"F0 frontier tier — UNDEFINED in repo (skeleton only)", "track":"frontier_f_tier", "is_example": False,
 "objectives":[{"id":"OBJ-F0-TODO","statement":"TODO(Grok-Buddy-F0-Scorecard / Frontier Loop Captain): F0 is not defined anywhere in DreamCo-Technologies/Dreamcobots@2ccd678. Candidate observable objective to confirm: pass the 5 Q4 lanes of config/frontier-evidence-suite.json under the suite's comparability rules.","observable":True}],
 "modules":[{"module_id":f"LANE-{l['id']}","title":l["id"].replace('_',' '),"required":True,"prereqs":[],"concepts":[{"concept_id":l["id"],"name":l["id"].replace('_',' '),"prereqs":[]}],"objective_ids":["OBJ-F0-TODO"],"practice_item_ids":l["training_tasks"]}
    for l in json.loads((SRC/"config/frontier-evidence-suite.json").read_text())["lanes"]],
 "practice_bank":{"bank_id":"PB-buddy-frontier-core-2026-q4-training","visibility":"practice","ref":f"github:{REPO}@{COMMIT}:config/frontier-evidence-suite.json#lanes[].training_tasks",
   "allowed_uses":["train","rag","lessons","drills","adaptive_samples"],
   "items":[{"item_id":tt,"module_id":f"LANE-{l['id']}","kind":"exercise","prompt":f"Task id '{tt}' from config/frontier-evidence-suite.json (prompt text not in repo).","is_example":False,"source_ref":"config/frontier-evidence-suite.json"}
     for l in json.loads((SRC/"config/frontier-evidence-suite.json").read_text())["lanes"] for tt in l["training_tasks"]]},
 "holdout_bank":{"bank_id":"HB-buddy-frontier-core-2026-q4-holdout","sealed":True,"private_store_path":"PLACEHOLDER://private-eval-store/frontier/buddy-frontier-core-2026-q4/holdout/ (FRONTIER_EVIDENCE_PLAN_2026.md step 1: 'private evaluation store'; path not defined in repo)","store_status":"placeholder_not_provisioned","item_count":None,
   "public_task_ids":[h for l in json.loads((SRC/"config/frontier-evidence-suite.json").read_text())["lanes"] for h in l["holdout_tasks"]],
   "forbidden_uses":FORBID,"dual_control_required":True,"rotation":ROT,"public_disclosure":"aggregate_scores_and_evidence_refs_only"},
 "grader_contract":{"grader_id":"tools/verify_frontier_evidence.py (evidence validator) + per-lane deterministic graders (TODO)","grader_version":None,"type":"deterministic","score_range":[0,1],"timeout_s":None,"assistance_policy":"declared_external_assistance","judge_policy_disclosed":False,
   "comparability_keys":["fixture_hash","grader_version","subject_version","timeout_s","assistance_policy"],"entrypoint":None,
   "notes":"Per-lane deterministic graders are step 3 of FRONTIER_EVIDENCE_PLAN_2026.md, not yet in repo. verify_frontier_evidence.py validates bundles, it does not grade."},
 "floors":{"fail_closed":True,"unit_practice_min":None,"course_exit_mean_min":None,"no_unit_below":None,"holdout_min":None,"transfer_tasks_min":None,"min_comparable_runs":None,"retention_retest_days":None,"critical_regressions_max":None,"efficiency_envelope":None,"trust_suite_required":None,
   "basis":"No F0-F4 tier definitions or F-tier numeric floors exist in Dreamcobots@2ccd678 (searched docs/, config/, buddy/frontier/, GitHub code search). All numeric fields null by rule: do not invent.",
   "todo":{"owners":["Grok-Buddy-F0-Scorecard","Frontier Loop Captain"],"reason":"Define F0 and its floors. Note repo suite uses score_threshold 0.8 (below SET7 0.90); adopting it needs an approved_lowering record or a raise to 0.90."},
   "approved_lowering":[]},
 "evidence_state":"unknown",
 "evidence":{"required_run_fields":RUN_FIELDS,"bundle_ref":f"github:{REPO}@{COMMIT}:evidence/frontier/current-status.assessment.json (claimable=false, run_count=0)","runs":[]},
 "provenance":{"sources":[src("config/frontier-evidence-suite.json"), src("docs/FRONTIER_EVIDENCE_PLAN_2026.md"), src("docs/BUDDY_FRONTIER_EVALUATION_HARNESS.md"), src("buddy/frontier/frontier_competition_policy.json"), src("config/buddy-frontier-readiness-gates.json"), src("tools/verify_frontier_evidence.py"), src("evidence/frontier/current-status.assessment.json"), POLICY_SRC] + GP_SOURCES + [sc_src("docs/EVIDENCE_CARD_SPEC.md"), sc_src("gate/cert_gate.py")],
   "rights_note":"Only DreamCo-owned repo config quoted (task ids, thresholds). No holdout stems exist or are included.","license":None},
 "repo_references":[
   {"path":"config/frontier-evidence-suite.json","key":"minimum_repetitions","value":3,"binding":False},
   {"path":"config/frontier-evidence-suite.json","key":"score_threshold","value":0.8,"binding":False,"note":"Conflicts with SET7 0.90; NOT adopted as F0 floor."},
   {"path":"config/frontier-evidence-suite.json","key":"suite_id","value":"buddy-frontier-core-2026-q4","binding":False},
   {"path":"buddy/frontier/frontier_competition_policy.json","key":"progression","value":"stage_1..stage_5 (tool_use/repo_repair -> broad frontier competition)","binding":False,"note":"5 named stages, no numeric floors; NOT confirmed to equal F0-F4."},
   {"path":"config/buddy-frontier-readiness-gates.json","key":"gates","value":"G1-foundation .. G7-frontier-comparison (qualitative requires-lists)","binding":False},
   {"path":"docs/BUDDY_FRONTIER_EVALUATION_HARNESS.md","key":"Score design","value":"vector of measurements; no single intelligence score","binding":False},
   {"path":"evidence/frontier/current-status.assessment.json","key":"claimable","value":False,"binding":False},
   {"path":f"edu-mastery-scorecards@{SC_COMMIT[:7]}:docs/EVIDENCE_CARD_SPEC.md#L15-L19","key":"F0..F4 min_score","value":{"F0":0.0,"F1":0.7,"F2":0.8,"F3":0.8,"F4":0.8},"binding":False,
    "note":"Per-(course, learner) evidence-card floors (spec:3,12), NOT Buddy frontier tiers. Values sit below SET7 0.90 (policy:52-54), so they are NOT adopted. F0-F4 numeric floors stay null."},
   {"path":f"edu-mastery-scorecards@{SC_COMMIT[:7]}:docs/EVIDENCE_CARD_SPEC.md#L19","key":"F4 retest","value":"regression retest >= 30 days after prior floor + evaluator independent of cert issuer","binding":False,
    "note":"Stricter than SET7 retention +7d. Recorded as a conflict; not adopted."}] + GP_REFS,
 "open_gaps":[
   {"gap":"F0-F4 not defined in repo; confirm whether they map to frontier_competition_policy stage_1..5 (5 items vs F0-F4 = 5) or to readiness gates, then set numeric floors.","owner":"Grok-Buddy-F0-Scorecard / Frontier Loop Captain","blocking_states":["baselined","testing","passed","mastered_candidate","mastered"]},
   {"gap":"Suite score_threshold 0.8 vs SET7 floor 0.90: needs human decision (raise, or record approved_lowering).","owner":"Frontier Loop Captain + human owner"},
   {"gap":"Private eval store and per-lane graders not provisioned (FRONTIER_EVIDENCE_PLAN steps 1 and 3).","owner":"Frontier Loop Captain"},
   {"gap":"Name collision: edu-mastery-scorecards defines F0-F4 as course evidence-card floors (EVIDENCE_CARD_SPEC.md:12-19; 0.00/0.70/0.80/0.80/0.80). These are not frontier tiers. Owners must either rename one side or confirm they are unrelated. The bridge refuses frontier_f_tier packets.","owner":"Grok-Buddy-F0-Scorecard + Grok-Edu-Mastery-Scorecards + human owner"},
   GP_GAP]
}
out = HERE
for p, d in [("bootcamp/BC-universal-1000-smoke.packet.json", bc), ("school_college/SC-example.packet.json", sc), ("frontier/F0.packet.json", f0)]:
    (out/p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n"); print("wrote", p)
print(f"sources: {SRC_MODE} ({SRC})")
for w in WARN: print("WARNING:", w)
