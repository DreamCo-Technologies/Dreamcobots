"""Regression comparison of this build against a previous release of the career-pathways pack.

For every study plan (asset) present in both builds, compares, item by item:
  * linked_occupation  - each crosswalk-linked O*NET-SOC code (title and Job Zone must be unchanged)
  * knowledge_value / skill_value - each top knowledge / Essential Skill element (importance value and rank)
  * entry_target       - each Year-4 entry target (presence and order)
  * practice_citation  - each practice task's (practice_id, O*NET-SOC code, O*NET task ID) citation
  * citation_valid     - each current citation resolves to a task of that occupation in task_statements.csv
                         and the occupation is linked to the major
  * gate_check         - each license/provenance gate check (pass in the baseline must still pass)
  * onet_text_leakage  - the current plan text has zero 5-word runs of O*NET task, Job Zone or
                         occupation-description text (occupation titles removed first)
Every difference must be explained by authored/target_overrides.json or authored/release_changes.json;
anything else is 'unexplained_change' or 'regressed' and fails the record.

Writes per asset:
  data/dreamco_knowledge/evidence/regression/<asset_id>/<YYYYMMDD>-<NN>.results.json   (item-level results)
  data/dreamco_knowledge/evidence/regression/<asset_id>/<YYYYMMDD>-<NN>.json           (evidence record,
      config/evidence_provenance_schema.json fields + split/n_items/metric/score/threshold/passed)
No model, API or human grader is involved: this is a deterministic DreamCo comparison script.

Usage: python regression.py --baseline-ref 8cc1ce1 --repo /workspace/dc-ecp [--run-id 20261002-01]
"""
import argparse, datetime, hashlib, json, pathlib, re, subprocess
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent
RAW, DATA, PLANS, AUTH = ROOT / "raw", ROOT / "data", ROOT / "study_plans", ROOT / "authored"
EVIDENCE = DATA / "dreamco_knowledge" / "evidence" / "regression"
REPO_PREFIX = "study_packs/career_pathways/"
OK = {"preserved", "changed_with_reason", "improved"}
METRIC = ("fraction of regression items (linked occupation codes, knowledge/skill values, entry targets, practice-task "
          "citations, citation validity, license-gate checks, O*NET text leakage) that are preserved, improved, or "
          "changed with a documented reason, versus the baseline release")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


GATE_VOLATILE = ("evaluated_at",)
SELF_REFERENTIAL_CHECKS = ("synthesis_asset_record",)


def gate_digest(gate_bytes):
    """sha256 of the gate file as canonical JSON (sorted keys) without its volatile evaluated_at timestamp, so the
    hash is stable across gate reruns that change nothing else."""
    g = json.loads(gate_bytes)
    for k in GATE_VOLATILE:
        g.pop(k, None)
    return sha_bytes(json.dumps(g, sort_keys=True, separators=(",", ":")).encode())


def git_show(repo, ref, path):
    r = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{REPO_PREFIX}{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def _tok(s):
    return re.findall(r"[a-z0-9]+", str(s).lower())


def _grams(s, n=5):
    w = _tok(s)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def onet_text_grams():
    g = set()
    for t in pd.read_csv(RAW / "task_statements.csv")["Task"]:
        g |= _grams(t)
    jz = pd.read_csv(RAW / "job_zone_reference.csv")
    for c in ["Name", "Experience", "Education", "Job Training", "Examples"]:
        for t in jz[c]:
            g |= _grams(t)
    for t in pd.read_csv(RAW / "occupation_data.csv")["Description"]:
        g |= _grams(t)
    return g


def leak_hits(text, grams, titles):
    for ti in titles:
        text = text.replace(ti, " | ")
    return sorted(" ".join(h) for h in _grams(text) & grams)


def compare_asset(old, new, old_tasks, new_tasks, old_gate, new_gate, new_md, old_md, ctx):
    cip = new["cip"]
    ov = ctx["overrides"].get(cip)
    cites_changes = {c["practice_id"]: c for c in ctx["release_changes"].get(cip, [])}
    items = []

    def add(kind, key, status, detail=None, reason=None):
        it = {"kind": kind, "key": key, "status": status}
        if detail is not None:
            it["detail"] = detail
        if reason:
            it["reason"] = reason
        items.append(it)

    # linked occupations
    oo = {o["soc"]: o for o in old["occupations"]}
    no = {o["soc"]: o for o in new["occupations"]}
    for soc in sorted(set(oo) | set(no)):
        a, b = oo.get(soc), no.get(soc)
        if a and b and a["title"] == b["title"] and a["job_zone"] == b["job_zone"]:
            add("linked_occupation", soc, "preserved")
        else:
            add("linked_occupation", soc, "unexplained_change", {"baseline": a, "current": b})

    # knowledge / skill values
    for kind, field in (("knowledge_value", "top_knowledge"), ("skill_value", "top_skills")):
        ov_ = {e: (i, v) for i, (e, v) in enumerate(old[field])}
        nv_ = {e: (i, v) for i, (e, v) in enumerate(new[field])}
        for e in sorted(set(ov_) | set(nv_)):
            if ov_.get(e) == nv_.get(e):
                add(kind, e, "preserved")
            else:
                add(kind, e, "unexplained_change", {"baseline_rank_value": ov_.get(e), "current_rank_value": nv_.get(e)})

    # entry targets
    ot = [t["soc"] for t in old["entry_targets"]]
    nt = [t["soc"] for t in new["entry_targets"]]
    for soc in list(dict.fromkeys(ot + nt)):
        if soc in ot and soc in nt and ot.index(soc) == nt.index(soc):
            add("entry_target", soc, "preserved")
            continue
        detail = {"baseline_position": ot.index(soc) + 1 if soc in ot else None,
                  "current_position": nt.index(soc) + 1 if soc in nt else None}
        if ov and ov["targets"] == nt:
            add("entry_target", soc, "changed_with_reason", detail, "authored/target_overrides.json: " + ov["reason"])
        else:
            add("entry_target", soc, "unexplained_change", detail)

    # practice citations
    oc = {t["practice_id"]: (t["onet_soc_code"], int(t["onet_task_id"])) for t in old_tasks}
    nc = {t["practice_id"]: (t["onet_soc_code"], int(t["onet_task_id"])) for t in new_tasks}
    for pid in sorted(set(oc) | set(nc)):
        a, b = oc.get(pid), nc.get(pid)
        detail = {"baseline": a and {"onet_soc_code": a[0], "onet_task_id": a[1]},
                  "current": b and {"onet_soc_code": b[0], "onet_task_id": b[1]}}
        if a == b:
            add("practice_citation", pid, "preserved", detail)
            continue
        ch = cites_changes.get(pid)
        if (ch and a and b and (ch["removed"]["onet_soc_code"], ch["removed"]["onet_task_id"]) == a
                and (ch["added"]["onet_soc_code"], ch["added"]["onet_task_id"]) == b):
            add("practice_citation", pid, "changed_with_reason", detail, "authored/release_changes.json: " + ch["reason"])
        else:
            add("practice_citation", pid, "unexplained_change", detail)

    # citation validity of the current build
    linked = set(no)
    for pid, (soc, tid) in sorted(nc.items()):
        ok = soc in linked and (soc, tid) in ctx["task_index"]
        add("citation_valid", pid, "preserved" if ok else "failed",
            {"onet_soc_code": soc, "onet_task_id": tid, "occupation_linked": soc in linked,
             "task_belongs_to_occupation": (soc, tid) in ctx["task_index"]})

    # gate checks
    # synthesis_asset_record is not compared: its status depends on whether validation evidence (this record) is linked.
    og = {c["id"]: c["status"] for c in old_gate["checks"] if c["id"] not in SELF_REFERENTIAL_CHECKS}
    ng = {c["id"]: c["status"] for c in new_gate["checks"] if c["id"] not in SELF_REFERENTIAL_CHECKS}
    rank = {"fail": 0, "warn": 1, "pass": 2}
    for cid in sorted(set(og) | set(ng)):
        a, b = og.get(cid), ng.get(cid)
        d = {"baseline": a, "current": b}
        if a == b:
            add("gate_check", cid, "preserved", d)
        elif a is not None and b is not None and rank[b] > rank[a]:
            add("gate_check", cid, "improved", d)
        else:
            add("gate_check", cid, "regressed", d)
    add("gate_outcome", "outcome", "preserved" if new_gate["outcome"] == old_gate["outcome"] else
        ("improved" if new_gate["outcome"] == "approved_for_sale" else "regressed"),
        {"baseline": old_gate["outcome"], "current": new_gate["outcome"],
         "baseline_rights_ceiling": old_gate.get("rights_ceiling"), "current_rights_ceiling": new_gate.get("rights_ceiling")})

    # O*NET text leakage
    hits_new = leak_hits(new_md, ctx["grams"], ctx["titles"])
    hits_old = leak_hits(old_md, ctx["grams"], ctx["titles"])
    add("onet_text_leakage", "plan_markdown", "preserved" if not hits_new and not hits_old else
        ("improved" if not hits_new else "failed"),
        {"current_5gram_hits": len(hits_new), "baseline_5gram_hits": len(hits_old),
         "current_examples": hits_new[:5], "baseline_examples": hits_old[:5]})
    return items, len(hits_new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-ref", required=True)
    ap.add_argument("--repo", required=True, help="git clone containing study_packs/career_pathways at the baseline ref")
    ap.add_argument("--run-id", default=None, help="<YYYYMMDD>-<NN>; default today's date with -01")
    ap.add_argument("--threshold", type=float, default=1.0)
    a = ap.parse_args()
    now = datetime.datetime.now().astimezone()
    run_id = a.run_id or now.strftime("%Y%m%d") + "-01"
    assert re.fullmatch(r"\d{8}-\d{2}", run_id), run_id
    full_ref = subprocess.run(["git", "-C", a.repo, "rev-parse", a.baseline_ref], capture_output=True, text=True,
                              check=True).stdout.strip()

    old_sel = {m["cip"]: m for m in json.loads(git_show(a.repo, full_ref, "data/majors_selected.json"))}
    old_pt = json.loads(git_show(a.repo, full_ref, "data/practice_tasks.json"))["tasks"]
    new_sel = json.loads((DATA / "majors_selected.json").read_text())
    new_pt = json.loads((DATA / "practice_tasks.json").read_text())["tasks"]
    tov = json.loads((AUTH / "target_overrides.json").read_text())
    rch = json.loads((AUTH / "release_changes.json").read_text())
    tasks = pd.read_csv(RAW / "task_statements.csv", dtype={"O*NET-SOC Code": str})
    ctx = {"overrides": tov["overrides"], "release_changes": rch["practice_citation_changes"],
           "task_index": set(zip(tasks["O*NET-SOC Code"], tasks["Task ID"].astype(int))),
           "grams": onet_text_grams(),
           "titles": sorted(pd.read_csv(RAW / "occupation_data.csv")["Title"], key=len, reverse=True)}
    evaluator = f"edu-career-pathways regression.py sha256:{sha_bytes((ROOT / 'regression.py').read_bytes())}"
    summary = []
    for new in new_sel:
        cip, aid = new["cip"], new["asset_id"]
        old = old_sel.get(cip)
        if old is None:
            summary.append((aid, None, "no baseline (new in this build); no regression record written"))
            continue
        stem = next(p.stem for p in PLANS.glob(f"{cip}_*.md"))
        old_md_b = git_show(a.repo, full_ref, f"study_plans/{stem}.md")
        old_gate_b = git_show(a.repo, full_ref, f"study_plans/{stem}/license_gate.json")
        if old_md_b is None or old_gate_b is None:
            summary.append((aid, None, "baseline plan file missing at this stem; no record written"))
            continue
        new_md_p, new_gate_p = PLANS / f"{stem}.md", PLANS / stem / "license_gate.json"
        new_asset = json.loads((PLANS / stem / "asset.json").read_text())
        items, leaks = compare_asset(
            old, new, [t for t in old_pt if t["cip_code"] == cip], [t for t in new_pt if t["cip_code"] == cip],
            json.loads(old_gate_b), json.loads(new_gate_p.read_text()), new_md_p.read_text(), old_md_b.decode(), ctx)
        n_ok = sum(i["status"] in OK for i in items)
        score = round(n_ok / len(items), 4)
        counts = {}
        for i in items:
            counts.setdefault(i["kind"], {}).setdefault(i["status"], 0)
            counts[i["kind"]][i["status"]] += 1
        passed = score >= a.threshold and leaks == 0
        results = {
            "schema": "dreamco.edu_career_pathways.regression_results.v1",
            "asset_id": aid, "cip": cip, "run_id": run_id,
            "baseline": {"git_ref": full_ref, "repo_path": REPO_PREFIX,
                         "files": {"majors_selected.json": sha_bytes(git_show(a.repo, full_ref, "data/majors_selected.json")),
                                   "practice_tasks.json": sha_bytes(git_show(a.repo, full_ref, "data/practice_tasks.json")),
                                   f"{stem}.md": sha_bytes(old_md_b),
                                   f"{stem}/license_gate.json#canonical_without_evaluated_at": gate_digest(old_gate_b)}},
            "current": {"asset_integrity_hash": new_asset["integrity_hash"],
                        "files": {"majors_selected.json": sha_bytes((DATA / "majors_selected.json").read_bytes()),
                                  "practice_tasks.json": sha_bytes((DATA / "practice_tasks.json").read_bytes()),
                                  f"{stem}.md": sha_bytes(new_md_p.read_bytes()),
                                  f"{stem}/license_gate.json#canonical_without_evaluated_at": gate_digest(new_gate_p.read_bytes())}},
            "evaluator_version": evaluator, "metric": METRIC, "threshold": a.threshold,
            "n_items": len(items), "n_ok": n_ok, "score": score, "current_onet_5gram_hits": leaks, "passed": passed,
            "counts_by_kind_and_status": counts, "items": items,
            "not_compared": ["Practice prompt, rubric and outline wording are intentionally rewritten "
                             "(authored/release_changes.json#global_changes) and are not diffed word by word; their "
                             "originality is covered by the onet_text_leakage item.",
                             "Fields added after the baseline (entry-weighted knowledge, outline_elements, quality_flags, "
                             "license blocks) have no baseline counterpart and are not compared.",
                             "The gate check synthesis_asset_record is not compared: it depends on whether this evidence is linked."],
            "determinism": ("This file has no run timestamp, and the gate file is hashed as canonical JSON without "
                            "evaluated_at, so rerunning regression.py on an unchanged build reproduces it byte for byte. "
                            "The run time is in the evidence record's retrieved_at.")}
        out = EVIDENCE / aid
        out.mkdir(parents=True, exist_ok=True)
        rp = out / f"{run_id}.results.json"
        rp.write_text(json.dumps(results, indent=2) + "\n")
        record = {
            "evidence_id": f"regression:{aid}:{run_id}",
            "capability_id": "career-pathway-study-plan",
            "source_type": "dreamco_experiment",
            "source_reference": new_asset["integrity_hash"],
            "retrieved_at": now.isoformat(timespec="seconds"),
            "content_version": (f"candidate: this build of {aid} (plan markdown {new_asset['integrity_hash']}); "
                                f"baseline: previous release git {full_ref[:7]} ({REPO_PREFIX}); O*NET 31.0"),
            "license_or_usage_basis": ("DreamCo-original evaluation output. Compared inputs are O*NET 31.0-derived fields "
                                       "(CC BY 4.0, USDOL/ETA; O*NET is a trademark of USDOL/ETA) and DreamCo-original text."),
            "transformation": "original_evaluation",
            "evaluator_version": evaluator,
            "integrity_hash": "sha256:" + sha_bytes(rp.read_bytes()),
            "results_path": str(rp.relative_to(ROOT)),
            "evidence_root": "study_packs/career_pathways/data/dreamco_knowledge/evidence",
            "split": "full_release_all_items",
            "n_items": len(items),
            "metric": METRIC,
            "score": score,
            "threshold": a.threshold,
            "passed": passed,
            "grader": "deterministic script (no model, no human grader)",
        }
        (out / f"{run_id}.json").write_text(json.dumps(record, indent=2) + "\n")
        summary.append((aid, score, f"n_items={len(items)} passed={passed} leaks={leaks} counts={json.dumps(counts)}"))
    for aid, score, msg in summary:
        print(aid, score, msg)
    print(f"records={sum(1 for s in summary if s[1] is not None)} all_passed="
          f"{all(('passed=True' in m) for _, s, m in summary if s is not None)}")


if __name__ == "__main__":
    main()
