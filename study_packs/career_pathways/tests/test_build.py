import csv, hashlib, json, os, pathlib, re
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
import sys; sys.path.insert(0, str(ROOT)); import build

PLANS = sorted((ROOT / "study_plans").glob("*.md"))
SCHEMAS = {"provenance": "data_package_asset_provenance.schema.json",
           "license_gate": "data_package_license_gate.schema.json",
           "asset": "data_package_synthesis_asset.schema.json"}


def schema_dir():
    """Live DreamCo schemas if present (env, repo root, merchant checkout), else the vendored snapshot in tests/schemas."""
    for d in [os.environ.get("DREAMCO_SCHEMAS_DIR"), ROOT.parents[1] / "schemas", "/workspace/dp-merchant/schemas"]:
        if d and all((pathlib.Path(d) / f).is_file() for f in SCHEMAS.values()):
            return pathlib.Path(d)
    return ROOT / "tests" / "schemas"


def validator(kind):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((schema_dir() / SCHEMAS[kind]).read_text())
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


import functools


@functools.lru_cache(maxsize=1)
def _pins():
    return build.load_pins()


def sidecar(plan):
    return plan.with_suffix("")


def test_links_exist_in_official_sources():
    cw = build.load_crosswalk(); pairs = set(zip(cw.cip, cw.soc))
    occ = set(pd.read_csv(ROOT/"raw/occupation_data.csv", dtype=str)["O*NET-SOC Code"])
    rows = list(csv.DictReader(open(ROOT/"data/major_to_onet.csv")))
    assert len(rows) > 0
    for r in rows:
        assert (r["cip_code"], r["onet_soc_code"]) in pairs
        assert r["onet_soc_code"] in occ


def test_major_tiers_and_coverage():
    """27 authored majors (exactly build.MAJORS) plus generated majors for every included code in data/coverage.csv."""
    majors = json.loads((ROOT/"data/majors_selected.json").read_text())
    tiers = {m["cip"]: m["tier"] for m in majors}
    assert sorted(c for c, t in tiers.items() if t == "authored") == sorted(build.MAJORS) and len(build.MAJORS) == 27
    assert set(tiers.values()) == {"authored", "generated"}
    assert len(majors) == len(tiers) == len(PLANS)
    cov = list(csv.DictReader(open(ROOT/"data/coverage.csv")))
    assert {r["cip_code"] for r in cov} == set(build.load_crosswalk().cip)  # every crosswalk CIP code is accounted for
    inc = {r["cip_code"]: r["tier"] for r in cov if r["status"] == "included"}
    assert inc == tiers
    assert all(r["reason"] for r in cov)
    rules = json.loads((ROOT/"authored/coverage_rules.json").read_text())
    jz = pd.read_csv(ROOT/"raw/job_zones.csv", dtype={"O*NET-SOC Code": str})
    zones = dict(zip(jz["O*NET-SOC Code"], jz["Job Zone"].astype(int)))
    for m in majors:
        cip = m["cip"]
        assert re.fullmatch(r"\d\d\.\d{4}", cip)
        assert any(zones.get(o["soc"]) in (4, 5) for o in m["occupations"]), cip
        if m["tier"] == "generated":
            assert cip[:2] not in rules["exclude_series"] and not cip.startswith(tuple(rules["exclude_prefixes"]))
            assert not re.search(rules["exclude_title_regex"]["pattern"], m["title"]), m["title"]
            assert m["entry_target_review"]["type"] == "rule_only_not_reviewed"
    for p in PLANS:
        tier = json.loads((sidecar(p) / "plan.json").read_text())["tier"]
        assert f"Tier: **{tier}**." in p.read_text(), p.name


def test_every_plan_has_provenance():
    assert len(PLANS) >= 20
    for p in PLANS:
        t = p.read_text(); assert "**Provenance.**" in t and "CC BY 4.0" in t and "not O*NET data" in t


def test_footer_trademark_modification_and_version_statements():
    for p in PLANS:
        t = p.read_text()
        assert "O*NET\u00ae is a trademark of USDOL/ETA." in t, p.name
        assert "DreamCo has modified all or some of this information" in t, p.name
        assert "USDOL/ETA has not approved, endorsed, or tested these modifications" in t, p.name
        assert "O*NET 31.0 Database" in t and "Pinned version: O*NET 31.0" in t, p.name
        assert re.search(r"crosswalk[^.]*CC BY 4\.0", t), p.name
        assert "Essential Skills and Transferable Skills" in t, p.name


def test_sources_pinned_in_sources_md_match_raw_files():
    pins = build.load_pins()  # raises if any raw file differs from raw/SOURCES.md
    for name in build.SOURCE_FILES:
        assert sha(ROOT/"raw"/name) == pins[name][0]
        assert re.match(r"\d{4}-\d{2}-\d{2}$", pins[name][1])


@pytest.mark.parametrize("plan", PLANS, ids=[p.stem for p in PLANS])
def test_gate_files_exist_and_validate(plan):
    d = sidecar(plan)
    for f in ["provenance.json", "license_gate.json", "asset.json", "candidate.json", "plan.json"]:
        assert (d / f).is_file(), f"{d.name}/{f} missing"
    for kind, f in [("provenance", "provenance.json"), ("license_gate", "license_gate.json"), ("asset", "asset.json")]:
        doc = json.loads((d / f).read_text())
        errs = sorted(validator(kind).iter_errors(doc), key=str)
        assert not errs, f"{d.name}/{f}: {[e.message for e in errs][:5]}"


@pytest.mark.parametrize("plan", PLANS, ids=[p.stem for p in PLANS])
def test_provenance_content_and_hashes(plan):
    d = sidecar(plan)
    prov = json.loads((d / "provenance.json").read_text())
    asset = json.loads((d / "asset.json").read_text())
    cand = json.loads((d / "candidate.json").read_text())
    pins = _pins()
    assert prov["integrity_hash"] == f"sha256:{sha(plan)}" == asset["integrity_hash"]
    for f in prov["asset_files"]:
        assert sha(ROOT / f["path"]) == f["sha256"], f["path"]
    for layer in ("human_layer", "machine_layer"):
        assert sha(ROOT / asset[layer]["path"]) == asset[layer]["sha256"]
    assert prov["ownership_class"] == asset["ownership_class"] == cand["ownership_class"]
    for s in prov["sources"]:
        assert s["ownership_class"] and s["license"] == "CC BY 4.0"
        assert s["commercial_use_allowed"] is True and s["redistribution_allowed"] is True
        hashes = [(f["name"], f["sha256"]) for f in s.get("files", [])] or [("Education_CIP_to_ONET_SOC.xlsx", s["sha256"])]
        for name, h in hashes:
            assert pins[name][0] == h
        if "db_31_0" in s["url"]:
            assert s["version"] == "31.0"
    comps = {c["component"]: c for c in prov["derived_components"]}
    assert comps["four_year_outline"]["ownership_class"] == "synthetic_generated_by_dreamco"
    tier = json.loads((d / "plan.json").read_text())["tier"]
    assert comps["practice_tasks"]["ownership_class"] == ("open_license_with_conditions" if tier == "generated"
                                                          else "synthetic_generated_by_dreamco")
    # owner approval is never set by the build
    assert cand["owner_approval"] is None and cand["scorecard_score"] is None
    gate = json.loads((d / "license_gate.json").read_text())
    assert gate["sale_requirements"]["owner_approval_present"] is False
    assert gate["outcome"] != "approved_for_sale"
    assert gate["inputs"]["provenance_sha256"] == sha(d / "provenance.json")
    assert not [c["id"] for c in gate["checks"] if c["scope"] == "rights" and c["status"] == "fail"]


def test_year4_targets_are_not_manager_or_chief():
    linked = {}
    for r in csv.DictReader(open(ROOT/"data/major_to_onet.csv")):
        linked.setdefault(r["cip_code"], set()).add(r["onet_soc_code"])
    for m in json.loads((ROOT/"data/majors_selected.json").read_text()):
        ts = m["entry_targets"]
        assert 1 <= len(ts) <= 3, m["cip"]
        for t in ts:
            assert not re.search(r"Manager|Chief|Postsecondary|All Other", t["title"]), (m["cip"], t["title"])
            assert t["soc"] in linked[m["cip"]]
    for p in PLANS:
        y4 = next(l for l in p.read_text().splitlines() if l.startswith("4. Year 4"))
        assert not re.search(r"Manager|Chief", y4), (p.name, y4)


def test_practice_tasks_reference_real_tasks_of_linked_occupations():
    ts = pd.read_csv(ROOT/"raw/task_statements.csv", dtype={"O*NET-SOC Code": str})
    task_soc = dict(zip(ts["Task ID"].astype(int), ts["O*NET-SOC Code"]))
    task_text = dict(zip(ts["Task ID"].astype(int), ts["Task"]))
    linked = {}
    for r in csv.DictReader(open(ROOT/"data/major_to_onet.csv")):
        linked.setdefault(r["cip_code"], set()).add(r["onet_soc_code"])
    pt = json.loads((ROOT/"data/practice_tasks.json").read_text())["tasks"]
    per = {}
    for t in pt:
        per.setdefault(t["cip_code"], []).append(t)
        assert t["onet_task_id"] in task_soc, t["practice_id"]
        assert task_soc[t["onet_task_id"]] == t["onet_soc_code"], t["practice_id"]
        assert t["onet_soc_code"] in linked[t["cip_code"]], t["practice_id"]
        assert len(t["rubric"]) == 3 and all(c["criterion"] and len(c["description"]) > 30 and c["points"] == 2 for c in t["rubric"])
        if t["tier"] == "authored":
            assert t["label"] == "DreamCo-original practice prompt" and t["prompt"].startswith("DreamCo-original practice prompt")
            assert task_text[t["onet_task_id"]] not in t["prompt"]  # O*NET task text is referenced, not reproduced
            assert t["license"] == build.item_license("authored") and t["license"]["contains_third_party_text"] is False
            assert t["ownership_class"] == t["license"]["ownership_class"] == "synthetic_generated_by_dreamco"
        else:
            assert t["label"] == build.GENERATED_LABEL and t["prompt"].startswith(build.GENERATED_LABEL)
            assert t["onet_task_statement"] == task_text[t["onet_task_id"]].strip()  # quoted verbatim, attributed
            assert "CC BY 4.0" in t["onet_task_statement_note"] and t["authorship"] == build.GENERATED_AUTHORSHIP
            lic = t["license"]
            assert t["ownership_class"] == lic["ownership_class"] == "open_license_with_conditions"
            assert lic["license"] == "CC BY 4.0" and lic["license_url"] == build.CC_BY and lic["contains_third_party_text"] is True
            assert "USDOL/ETA" in lic["attribution"] and "has modified" in lic["modification_notice"] and lic["trademark_notice"]
    assert set(per) == set(linked)
    for cip, items in per.items():
        assert 5 <= len(items) <= 8, cip
    plans = {p.name.split("_")[0]: p.read_text() for p in PLANS}
    for t in pt:
        assert f"O*NET task {t['onet_task_id']}" in plans[t["cip_code"]]
        if t["tier"] == "authored":
            assert task_text[t["onet_task_id"]] not in plans[t["cip_code"]]
        else:
            assert ("> O*NET 31.0 task statement (quoted verbatim, USDOL/ETA, CC BY 4.0): " + t["onet_task_statement"]) in plans[t["cip_code"]]


AUTHORSHIP = "DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed"


def _tok(s):
    return re.findall(r"[a-z0-9]+", str(s).lower())


def _grams(s, n=5):
    w = _tok(s)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


@pytest.fixture(scope="module")
def onet_text_grams():
    """Every 5-word run in any O*NET 31.0 task statement, Job Zone reference text, or occupation description."""
    g = set()
    for t in pd.read_csv(ROOT/"raw/task_statements.csv")["Task"]:
        g |= _grams(t)
    jz = pd.read_csv(ROOT/"raw/job_zone_reference.csv")
    for c in ["Name", "Experience", "Education", "Job Training", "Examples"]:
        for t in jz[c]:
            g |= _grams(t)
    for t in pd.read_csv(ROOT/"raw/occupation_data.csv")["Description"]:
        g |= _grams(t)
    return g


def test_authored_practice_tasks_are_fully_original(onet_text_grams):
    """No run of 5+ words from any O*NET task statement, Job Zone text or occupation description in authored fields."""
    pt = json.loads((ROOT/"data/practice_tasks.json").read_text())["tasks"]
    authored = [t for t in pt if t.get("tier") == "authored"]
    assert authored
    for t in authored:
        fields = [t["task_intent"], t["prompt"], *t["reference_answer_outline"]]
        fields += [c["criterion"] + " " + c["description"] for c in t["rubric"]]
        for f in fields:
            hit = _grams(f) & onet_text_grams
            assert not hit, (t["practice_id"], [" ".join(h) for h in hit])


QUOTE_PREFIX = "> O*NET 31.0 task statement (quoted verbatim, USDOL/ETA, CC BY 4.0): "


def test_plan_text_has_no_onet_text_runs(onet_text_grams):
    """Whole plan files, after removing O*NET occupation titles and CIP program titles (attributed source data shown as titles), contain no
    5-word run of O*NET task, Job Zone or occupation-description text. Generated-tier plans may quote task statements
    only on attributed quote lines; those lines are removed first, and authored plans have none."""
    titles = list(pd.read_csv(ROOT/"raw/occupation_data.csv")["Title"])
    titles += [m["title"] for m in json.loads((ROOT/"data/majors_selected.json").read_text())]  # CIP titles (crosswalk data)
    title_rx = re.compile("|".join(re.escape(ti) for ti in sorted(set(titles), key=len, reverse=True)))
    for p in PLANS:
        t = p.read_text()
        tier = json.loads((sidecar(p) / "plan.json").read_text())["tier"]
        quotes = [l for l in t.splitlines() if l.startswith(QUOTE_PREFIX)]
        assert (tier == "generated") == bool(quotes), p.name
        t = "\n".join(l for l in t.splitlines() if not l.startswith(QUOTE_PREFIX))
        t = title_rx.sub(" | ", re.sub(r"study_plans/\S+", " | ", t))  # file paths carry the CIP-title slug
        hit = _grams(t) & onet_text_grams
        assert not hit, (p.name, [" ".join(h) for h in list(hit)[:5]])


def test_authored_sources_match_outputs():
    src = json.loads((ROOT/"authored/practice_tasks_authored.json").read_text())
    assert src["authorship"] == AUTHORSHIP
    by_id = {t["practice_id"]: t for t in src["tasks"]}
    pt = json.loads((ROOT/"data/practice_tasks.json").read_text())["tasks"]
    authored = [t for t in pt if t.get("tier") == "authored"]
    assert len(authored) == len(by_id) == 162
    for t in authored:
        a = by_id[t["practice_id"]]
        assert (a["onet_soc_code"], a["onet_task_id"]) == (t["onet_soc_code"], t["onet_task_id"])
        assert t["prompt"] == "DreamCo-original practice prompt. " + a["prompt"]
        assert t["rubric"] == a["rubric"] and t["reference_answer_outline"] == a["reference_answer_outline"]
        assert t["authorship"] == AUTHORSHIP and len(t["reference_answer_outline"]) >= 3
    prompts = [t["prompt"] for t in authored]
    assert len(set(prompts)) == len(prompts)  # no shared template text between tasks


def test_target_overrides_are_documented_and_applied():
    tov = json.loads((ROOT/"authored/target_overrides.json").read_text())
    majors = {m["cip"]: m for m in json.loads((ROOT/"data/majors_selected.json").read_text())}
    authored = {c for c, m in majors.items() if m.get("tier") == "authored"}
    assert authored == set(tov["overrides"]) | set(tov["reviewed_without_change"])  # every authored major reviewed
    assert not set(tov["overrides"]) & set(tov["reviewed_without_change"])
    for cip, o in tov["overrides"].items():
        assert len(o["reason"]) > 40
        m = majors[cip]
        assert [t["soc"] for t in m["entry_targets"]] == o["targets"]
        assert all(t["job_zone"] for t in m["entry_targets"])
        assert m["entry_target_review"]["type"] == "override" and m["entry_target_review"]["reason"] == o["reason"]
    cs = [t["soc"] for t in majors["11.0701"]["entry_targets"]]
    assert "15-1252.00" in cs and "15-1243.00" not in cs  # Software Developers in, Database Architects out
    cs_plan = (ROOT/"study_plans/11.0701_computer_science.md").read_text()
    y4 = next(l for l in cs_plan.splitlines() if l.startswith("4. Year 4"))
    assert "Software Developers" in y4 and "Database Architects" not in y4


def test_outline_topics_are_per_major_authored():
    topics = json.loads((ROOT/"authored/outline_topics.json").read_text())["majors"]
    generic = set(build.KNOWLEDGE_STUDY.values()) | set(build.SKILL_PRACTICE.values())
    for m in json.loads((ROOT/"data/majors_selected.json").read_text()):
        if m.get("tier") != "authored":
            continue
        plan = next(p for p in PLANS if p.name.startswith(m["cip"] + "_")).read_text()
        outline = plan.split("## 4-year outline", 1)[1].split("## Typical next steps", 1)[0]
        outline = outline.split("Knowledge areas from the top list that the outline deliberately does not cover:", 1)[0]
        for g in generic:
            assert g not in outline, (m["cip"], g)
        for kind in ("knowledge", "skills"):
            for e, phrase in topics[m["cip"]][kind].items():
                if f"{e} (" in outline:
                    assert f"{e} ({phrase})" in outline, (m["cip"], e)
    cs = topics["11.0701"]["knowledge"]
    assert "CAD" not in " ".join(cs.values())


def test_next_steps_cite_job_zone_numbers_without_quoting():
    jz = pd.read_csv(ROOT/"raw/job_zone_reference.csv")
    for p in PLANS:
        t = p.read_text()
        for c in ["Name", "Education", "Experience"]:
            for txt in jz[c]:
                assert txt not in t, (p.name, txt)
        ns = t.split("## Typical next steps", 1)[1].split("## Practice tasks", 1)[0]
        assert re.search(r"Job Zone (1-2|[345])", ns) and "O*NET describes" not in ns


def evidence_schema():
    for d in [ROOT.parents[1] / "config", pathlib.Path("/workspace/dp-merchant/config"), ROOT / "tests" / "schemas"]:
        if (d / "evidence_provenance_schema.json").is_file():
            return json.loads((d / "evidence_provenance_schema.json").read_text())


LATEST_REGRESSION_RUN = "20261002-04"
REGRESSION_BASELINE = "687b3c1"  # v3, the last release whose regression evidence the merchant reviewed


def test_regression_evidence_records_are_real_and_linked():
    """asset.json validation_evidence_ids has exactly sandbox/benchmark/holdout/regression. Regression lists every
    regression record on disk for the asset (-01..-04; evidence is append-only). Every record has the evidence-provenance
    fields, an integrity_hash equal to the sha256 of its results file, and a recomputable score. The latest run (-04)
    compares against v3 (687b3c1) and describes the files on disk now; older runs describe the release they evaluated."""
    import regression
    sch = evidence_schema()
    for p in PLANS:
        asset = json.loads((sidecar(p) / "asset.json").read_text())
        assert asset["evidence_root"] == build.EVIDENCE_ROOT
        ev = asset["validation_evidence_ids"]
        assert set(ev) == {"sandbox", "benchmark", "holdout", "regression"}
        assert ev["sandbox"] == ev["benchmark"] == ev["holdout"] == [], "no independent sandbox/benchmark/holdout runs exist"
        assert asset["machine_layer"] is not None and asset["dreamco_analysis"] is not None
        tier = json.loads((sidecar(p) / "plan.json").read_text())["tier"]
        on_disk = sorted(f"regression:{asset['asset_id']}:{r.stem}"
                         for r in (EVIDENCE_DIR / "regression" / asset["asset_id"]).glob("*.json") if not r.name.endswith(".results.json"))
        if tier == "generated":
            assert not ev["regression"] and not on_disk  # new in v4: nothing to regress against
            continue
        runs = [e.split(":")[2] for e in ev["regression"]]
        assert sorted(ev["regression"]) == on_disk and {"20261002-01", "20261002-02", "20261002-03", LATEST_REGRESSION_RUN} <= set(runs), p.name
        for eid in ev["regression"]:
            kind, aid, run = eid.split(":")
            assert kind == "regression" and aid == asset["asset_id"] and re.fullmatch(r"\d{8}-\d{2}", run)
            rec_p = EVIDENCE_DIR / kind / aid / f"{run}.json"
            rec = json.loads(rec_p.read_text())
            for f in sch["required_fields"] + ["split", "n_items", "metric", "score", "threshold", "passed"]:
                assert rec.get(f) not in (None, ""), (eid, f)
            assert rec["evidence_id"] == eid
            assert rec["source_type"] in sch["source_types"] and rec["source_type"] == "dreamco_experiment"
            assert rec["transformation"] in sch["transformation_types"] and rec["transformation"] == "original_evaluation"
            res_p = rec_p.with_name(f"{run}.results.json")
            assert rec["integrity_hash"] == "sha256:" + sha(res_p)
            res = json.loads(res_p.read_text())
            ok = sum(i["status"] in ("preserved", "changed_with_reason", "improved") for i in res["items"])
            assert rec["n_items"] == len(res["items"]) and rec["score"] == round(ok / len(res["items"]), 4)
            assert rec["passed"] is True and rec["score"] >= rec["threshold"] == 1.0
            assert all(i.get("reason") for i in res["items"] if i["status"] == "changed_with_reason")
            if run != LATEST_REGRESSION_RUN:
                continue  # an older run evaluated an older build (and -01/-02 predate deterministic results files)
            assert "run_at" not in res and "evaluated_at" not in res
            assert rec["source_reference"] == asset["integrity_hash"] == res["current"]["asset_integrity_hash"]
            assert res["baseline"]["git_ref"].startswith(REGRESSION_BASELINE), res["baseline"]["git_ref"]
            stem = sidecar(p).name
            disk = {"majors_selected.json": sha(ROOT / "data/majors_selected.json"),
                    "practice_tasks.json": sha(ROOT / "data/practice_tasks.json"),
                    f"{stem}.md": sha(p),
                    f"{stem}/license_gate.json#canonical_without_evaluated_at":
                        regression.gate_digest((sidecar(p) / "license_gate.json").read_bytes())}
            assert res["current"]["files"] == disk, (eid, res["current"]["files"], disk)


def _git_history_repo():
    """A git checkout whose history contains this pack: the pack itself if it is in a repo, else $DREAMCO_REPO_ROOT or
    the default clone. Returns (repo, pack path inside the repo) or None."""
    import subprocess
    def top(d):
        r = subprocess.run(["git", "-C", str(d), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        return pathlib.Path(r.stdout.strip()) if r.returncode == 0 else None
    t = top(ROOT)
    if t:
        return t, ROOT.resolve().relative_to(t.resolve()).as_posix()
    for d in [os.environ.get("DREAMCO_REPO_ROOT"), "/workspace/dc-ecp"]:
        if d and pathlib.Path(d).is_dir() and top(d):
            return top(d), "study_packs/career_pathways"
    return None


def test_no_committed_evidence_file_was_removed_or_changed():
    """Evidence is append-only: every evidence file that exists in any commit of the repo history is still on disk with
    the content of its most recent commit."""
    import subprocess
    found = _git_history_repo()
    if not found:
        pytest.skip("no git history available")
    repo, pack = found
    ev = f"{pack}/data/dreamco_knowledge/evidence"
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout
    commits = git("log", "--all", "--format=%H", "--", ev).split()  # newest first
    if not commits:
        pytest.skip("no committed evidence yet")
    latest = {}
    for c in commits:
        for line in git("ls-tree", "-r", c, "--", ev).splitlines():
            meta, path = line.split("\t", 1)
            latest.setdefault(path, (meta.split()[2], c))
    assert len(latest) >= 108
    for path, (blob, c) in sorted(latest.items()):
        f = ROOT / path[len(pack) + 1:]
        assert f.is_file(), f"{path} (in commit {c[:7]}) was removed"
        data = f.read_bytes()
        assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == blob, f"{path} differs from commit {c[:7]}"


def test_regression_comparator_flags_unexplained_changes():
    """The comparator is not a rubber stamp: a dropped link, an unexplained target, a changed score, a swapped task
    citation, a gate regression and O*NET text in the plan must all be caught."""
    import regression
    sel = json.loads((ROOT / "data/majors_selected.json").read_text())
    new = next(m for m in sel if m["cip"] == "40.0501")
    tasks = [t for t in json.loads((ROOT / "data/practice_tasks.json").read_text())["tasks"] if t["cip_code"] == "40.0501"]
    stem = next((ROOT / "study_plans").glob("40.0501_*.md")).stem
    gate = json.loads((ROOT / "study_plans" / stem / "license_gate.json").read_text())
    md = (ROOT / "study_plans" / f"{stem}.md").read_text()
    ts = pd.read_csv(ROOT / "raw/task_statements.csv", dtype={"O*NET-SOC Code": str})
    ctx = {"overrides": {}, "release_changes": {}, "task_index": set(zip(ts["O*NET-SOC Code"], ts["Task ID"].astype(int))),
           "grams": regression._grams(ts["Task"].iloc[0]), "titles": []}
    items, leaks = regression.compare_asset(new, new, tasks, tasks, gate, gate, md, md, ctx)
    assert all(i["status"] == "preserved" for i in items) and leaks == 0
    import copy
    cur = copy.deepcopy(new); cur["occupations"] = cur["occupations"][1:]
    cur["entry_targets"] = cur["entry_targets"][::-1] + [{"soc": "99-9999.00", "title": "x", "job_zone": 4}]
    cur["top_knowledge"][0] = [cur["top_knowledge"][0][0], cur["top_knowledge"][0][1] - 0.5]
    ctasks = copy.deepcopy(tasks); ctasks[0]["onet_task_id"] = int(ctasks[0]["onet_task_id"]) + 1
    cgate = copy.deepcopy(gate); cgate["checks"][0]["status"] = "fail"
    items, leaks = regression.compare_asset(new, cur, tasks, ctasks, gate, cgate, md + " " + ts["Task"].iloc[0], md, ctx)
    bad = {i["kind"] for i in items if i["status"] not in ("preserved", "changed_with_reason", "improved")}
    assert {"linked_occupation", "entry_target", "knowledge_value", "practice_citation", "gate_check",
            "onet_text_leakage"} <= bad and leaks > 0


EVIDENCE_DIR = ROOT / "data/dreamco_knowledge/evidence"


def test_every_evidence_record_integrity_hash_matches_its_results_file():
    """Every evidence record on disk (any kind) points at a results file whose sha256 is its integrity_hash, and its id
    resolves under evidence_root as <kind>/<asset_id>/<run>.json."""
    recs = [r for r in sorted(EVIDENCE_DIR.rglob("*.json")) if not r.name.endswith(".results.json")]
    assert recs
    for r in recs:
        rec = json.loads(r.read_text())
        kind, aid, run = rec["evidence_id"].split(":")
        assert r == EVIDENCE_DIR / kind / aid / f"{run}.json", r
        assert rec.get("evidence_root", build.EVIDENCE_ROOT) == build.EVIDENCE_ROOT  # absent in pre-v4 records
        rp = rec["results_path"]
        # v6+ records (holdout) give results_path relative to the same repository root as evidence_root; older
        # records (regression -01..-04, append-only) give it relative to the pack root.
        res = ROOT / (rp[len("study_packs/career_pathways/"):] if rp.startswith(build.EVIDENCE_ROOT + "/") else rp)
        assert res.is_file() and res == r.with_name(f"{run}.results.json")
        assert rec["integrity_hash"] == "sha256:" + sha(res), r
    results = sorted(EVIDENCE_DIR.rglob("*.results.json"))
    assert len(results) == len(recs)  # no orphan results files


def test_regression_results_are_deterministic():
    """Rerunning regression.py's hashing on unchanged inputs gives the same digest: the gate digest ignores evaluated_at."""
    import regression
    g = (next(sidecar(p) for p in PLANS) / "license_gate.json").read_bytes()
    d = json.loads(g); d["evaluated_at"] = "1999-01-01T00:00:00+00:00"
    assert regression.gate_digest(g) == regression.gate_digest(json.dumps(d).encode())


ISO_OFFSET = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$")


def _walk_keys(x, key, out):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == key:
                out.append(v)
            _walk_keys(v, key, out)
    elif isinstance(x, list):
        for v in x:
            _walk_keys(v, key, out)


def test_created_at_is_full_iso8601_with_offset():
    files = [ROOT / "data/practice_tasks.json", ROOT / "evidence/holdout_kit/items.json"]
    for p in PLANS:
        files += [sidecar(p) / "asset.json", sidecar(p) / "plan.json"]
    n = 0
    for f in files:
        vals = []
        _walk_keys(json.loads(f.read_text()), "created_at", vals)
        assert vals, f
        for v in vals:
            assert ISO_OFFSET.match(v), (f, v)
            n += 1
    assert n >= 2 * len(PLANS)


def test_license_blocks_per_item_and_per_plan():
    pt = json.loads((ROOT / "data/practice_tasks.json").read_text())
    # file level = most restrictive valid policy class among the items; per-item labels are kept
    item_classes = {t["ownership_class"] for t in pt["tasks"]}
    assert pt["ownership_class"] == build.most_restrictive(item_classes) == "open_license_with_conditions"
    assert pt["ownership_class"] in build.OWNERSHIP_RESTRICTIVENESS and item_classes <= set(build.OWNERSHIP_RESTRICTIVENESS)
    assert pt["ownership_class_rule"] and pt["note"]
    assert pt["license"]["license_url"] == build.CC_BY and "USDOL/ETA" in pt["license"]["attribution"]
    for n in build.DB_NOTICES:
        assert n in pt["license"]["required_notices"]
    for t in pt["tasks"]:
        lic = t["license"]
        third = "onet_task_statement" in t
        assert lic["contains_third_party_text"] is third and (t["tier"] == "generated") is third
        assert lic["license"] == ("CC BY 4.0" if third else build.item_license("authored")["license"])
    for p in PLANS:
        pj = json.loads((sidecar(p) / "plan.json").read_text())
        lic = pj["license"]
        assert lic == build.plan_license(pj["tier"])
        assert lic["license_url"] == build.CC_BY and "USDOL/ETA" in lic["attribution"]
        assert all(n in lic["required_notices"] for n in build.DB_NOTICES)
        assert all(t["license"] == build.item_license(pj["tier"]) for t in pj["practice_tasks"])
        t = p.read_text()  # existing notices are kept in the plan text
        assert "O*NET\u00ae is a trademark of USDOL/ETA." in t and "used under the CC BY 4.0 license" in t


def test_weighted_knowledge_and_skipped_elements_are_documented():
    for p in PLANS:
        pj = json.loads((sidecar(p) / "plan.json").read_text())
        w = pj["knowledge_weighting"]
        assert w["method"] == build.WEIGHTING_METHOD
        targets = {t["soc"] for t in pj["entry_targets"]}
        assert all(w["weights"][s] == 2 for s in targets)
        assert set(w["weights"]) <= {o["soc"] for o in pj["occupations"]}  # weight-0 occupations are omitted
        assert set(w["weights"].values()) <= {1, 2}
        for o in pj["occupations"]:
            if re.search(r"Manager|Chief|Postsecondary|All Other", o["title"]) and o["soc"] not in targets:
                assert o["soc"] not in w["weights"], (p.name, o["title"])
        t = p.read_text()
        assert "entry-weighted" in t and "unweighted mean" in t
        assert "Knowledge areas from the top list that the outline deliberately does not cover:" in t
        oe = pj["outline_elements"]
        placed = set(oe["year1_knowledge"]) | set(oe["year2_knowledge"]) | set(oe["year3_knowledge"])
        for x in oe["skipped_knowledge"]:
            assert x["element"] not in placed and len(x["reason"]) > 20
            assert f"- {x['element']} (" in t and x["reason"] in t
        assert {k for k, _ in pj["top_knowledge_entry_weighted"]} <= placed | {x["element"] for x in oe["skipped_knowledge"]}, p.name
    cs = json.loads((ROOT / "study_plans/11.0701_computer_science/plan.json").read_text())
    skipped = {x["element"] for x in cs["outline_elements"]["skipped_knowledge"]}
    placed = set(cs["outline_elements"]["year3_knowledge"]) | set(cs["outline_elements"]["year2_knowledge"])
    assert "Administration and Management" in skipped and "Design" in placed  # merchant note on v3


def test_generated_target_plausibility_and_quality_flags():
    """v5: the field-fit check drops clearly implausible generated targets (with fallback) and records the drops in
    plan.json; flags are only raised for high-confidence mismatches; the v4 lexical low_title_overlap check is retired."""
    sup = n_drop = n_flag_plans = 0
    for p in PLANS:
        pj = json.loads((sidecar(p) / "plan.json").read_text())
        qf = pj["quality_flags"]
        assert qf["flag_count"] == len(qf["flags"])
        assert all(f["flag"] != "low_title_overlap" for f in qf["flags"])
        t = p.read_text()
        tp = pj["target_plausibility"]
        if pj["tier"] != "generated":
            assert not qf["flags"] and tp is None
            continue
        assert "## Quality flags (automatic plausibility checks; generated tier)" in t
        assert tp["method"] == build.FIELD_FIT_RULE and qf["method"]["field_fit"] == build.FIELD_FIT_RULE
        final = [e["soc"] for e in pj["entry_targets"]]
        assert tp["final_targets"] == final and 1 <= len(final) <= 3
        gone = {d["soc"] for d in tp["dropped"]}
        assert not gone & set(final) and gone <= set(tp["rule_targets"])
        for d in tp["dropped"]:
            assert d["fit"] == 0 and d["base_fit"] == 0 and not d["soc"].endswith(".00") and d["reason"]
            assert d["series_fit"] < build.FIT_SERIES_KEEP
            assert max(tp["fit"].values()) >= build.FIT_DROP_MIN_BEST
            assert f"target_dropped: `{d['soc']}`" in t
            assert any(a["action"] == "target_dropped" and a["onet_soc_code"] == d["soc"] for a in qf["actions"])
        for a in tp["added"]:
            assert a["soc"] in final and a["fit"] > 0 and a["soc"] not in tp["rule_targets"]
        n_drop += len(gone)
        n_flag_plans += bool(qf["flags"])
        for f in qf["flags"]:
            assert f"- {f['flag']}" in t
            if f["flag"] == "better_field_match_available":
                assert f["onet_soc_code"] in final and f["fit"] == 0 and f["suggested_fit"] >= build.FIT_FLAG_MIN_BEST
        kept = {i for f in qf["flags"] if f["flag"] == "supervisory_task_kept" for i in f["practice_ids"]}
        for x in pj["practice_tasks"]:
            assert x["supervisory_task"] is build.is_supervisory(x["onet_task_statement"])
            if x["supervisory_task"]:
                assert x["practice_id"] in kept, x["practice_id"]
            sup += x["supervisory_task"]
    assert n_drop > 0  # the check changes target selection
    assert n_flag_plans < 200  # actionable, not a flag on most plans (v4 flagged 887 of 1,017)
    ppe = json.loads(next((ROOT / "study_plans").glob("14.4802_*/plan.json")).read_text())  # merchant example (v3 review)
    titles = {e["title"] for e in ppe["entry_targets"]}
    assert not titles & {"Robotics Engineers", "Photonics Engineers"}, titles
    assert {"Robotics Engineers", "Photonics Engineers"} <= {d["title"] for d in ppe["target_plausibility"]["dropped"]}
    gen = {m["cip"]: m for m in json.loads((ROOT / "data/majors_selected.json").read_text())}
    assert "Molecular and Cellular Biologists" in {e["title"] for e in gen["26.0803"]["entry_targets"]}  # series guard keeps it
    assert build.is_supervisory("Supervise and coordinate the work of technicians.")
    assert build.is_supervisory("Direct and coordinate activities of staff.")
    assert not build.is_supervisory("Perform analyses under supervision of a senior engineer.")


KIT = ROOT / "evidence/holdout_kit"
CS_CIP = "11.0701"
_FORBIDDEN = ("/workspace/edu-career-pathways-private", "/home/box/.ecp-holdout")
_PRIVATE_ACCESS = []


def _audit(event, args):
    if event in ("open", "os.listdir", "os.scandir", "glob.glob", "shutil.copyfile", "os.remove", "os.rename") and args:
        p = str(args[0]) if not isinstance(args[0], int) else ""
        if p.startswith(_FORBIDDEN):
            _PRIVATE_ACCESS.append((event, p))


sys.addaudithook(_audit)


@pytest.fixture(autouse=True)
def _no_private_access():
    """Every test fails if it touched the builder's private key directory or passphrase."""
    n = len(_PRIVATE_ACCESS)
    yield
    assert _PRIVATE_ACCESS[n:] == [], _PRIVATE_ACCESS[n:]


@pytest.fixture
def ktmp():
    """A temp directory that is deleted after the test (synthetic keys and passphrases never linger in /tmp)."""
    import shutil, tempfile
    d = pathlib.Path(tempfile.mkdtemp(prefix="ecp-holdout-test-"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _kit_items():
    return json.loads((KIT / "items.json").read_text())


def test_holdout_kit_v3_is_blind_shape_normalized_and_ungraded():
    items = _kit_items()
    its = items["items"]
    assert items["n_items"] == len(its) and 16 <= len(its) <= 24
    majors = [re.search(r"CIP (\d\d\.\d{4})\)$", i["major"]).group(1) for i in its]
    import score_holdout
    assert majors.count(CS_CIP) >= score_holdout.MIN_ITEMS_PER_MAJOR  # CS can produce a per-major record
    assert set(majors) <= set(build.MAJORS) and len(set(majors)) >= 8
    blob = json.dumps(items).lower()
    for word in ("weaken", "full_strength", "expected_scores", "candidate_type", "seed", "nonce", "practice_id", "11.0701-p"):
        assert word not in blob  # nothing in the grader's file reveals the key
    words = []
    for i in its:
        bullets = i["candidate_answer"].split("\n")
        assert len(bullets) == 5 and all(re.match(r"- \*\*[^*]+:\*\* \S", b) for b in bullets), i["item_id"]
        assert len(i["rubric"]) == 3 and all(c["points"] == 2 for c in i["rubric"])
        words.append(len(_tok(i["candidate_answer"])))
    assert max(words) <= 1.35 * min(words), words  # one length band; length gives nothing away
    # no key file anywhere in the kit, and the commitment is present
    assert not [f.name for f in KIT.iterdir() if "key" in f.name.lower() and f.suffix in (".json", ".enc")]
    assert not (KIT / "_key.json").exists()
    commit = dict(l.split(": ", 1) for l in (KIT / "KEY_COMMITMENT.txt").read_text().splitlines() if ": " in l)
    assert re.fullmatch(r"[0-9a-f]{64}", commit["key_sha256"])
    assert commit["items_json_sha256"] == sha(KIT / "items.json")
    assert "AES-256-GCM" in commit["key_storage"] and commit["kit"] == items["kit"]
    rows = list(csv.DictReader(open(KIT / "grading_sheet.csv")))
    assert [r["item_id"] for r in rows] == [i["item_id"] for i in its]
    assert all(not r[c] for r in rows for c in ("score_1", "score_2", "score_3", "factually_correct", "grader", "graded_at", "comments"))
    assert not (KIT / "GRADING_FINAL.txt").exists() and not (KIT / "FINALIZED.txt").exists()
    assert not (EVIDENCE_DIR / "holdout").exists()  # no holdout evidence until a human grades the kit
    readme = (KIT / "README.md").read_text()
    for s in ("Pass rule", "all 2s", "v1 kit", "KEY_COMMITMENT.txt", "False-alarm rate", "sheet_sha256", "at least 4",
              "Threat model", "baseline_score", "scored once", "Asset detection rate", "Asset false-alarm rate",
              "strictly above", "grading_commit", "committed and pushed", "passphrase is on the same shared box",
              "move the passphrase off the box", "Item order", "single `rng.shuffle`"):
        assert s in readme, s
    # the number of weakened answers is secret: no README states it
    for doc in (readme, (ROOT / "README.md").read_text(), (ROOT / "docs/DATA_DICTIONARY.md").read_text()):
        assert not re.search(r"\b[Hh]alf (of )?the (answers|items)|\b\d+ (of the \d+ )?(answers|items) are (subtly )?weakened|"
                             r"exactly (half|\d+) (are )?weakened", doc)


def test_holdout_kit_shares_no_5_word_run_with_published_content(onet_text_grams):
    """Kit prompts, answers and rubrics are new: no 5-word run appears in any published plan, practice_tasks.json,
    authored file, README or doc of the pack, the O*NET text (task statements, Job Zone text, occupation descriptions),
    or any earlier kit in git history (v1 and the public v2 draw: reusing a v2 item would let anyone compare its two
    answer versions if the shown version changed)."""
    kg = {}
    for i in _kit_items()["items"]:
        for f in [i["prompt"], i["candidate_answer"]] + [c["criterion"] + " " + c["description"] for c in i["rubric"]]:
            for g in _grams(f):
                kg.setdefault(g, i["item_id"])
    assert not set(kg) & onet_text_grams
    files = PLANS + [ROOT / "data/practice_tasks.json", ROOT / "README.md", KIT / "README.md", ROOT / "raw/SOURCES.md"]
    files += sorted((ROOT / "authored").glob("*.json")) + sorted((ROOT / "docs").glob("*.md"))
    texts = [(f.name, f.read_text()) for f in files]
    found = _git_history_repo()
    if found:
        import subprocess
        repo, pack = found
        current = (KIT / "items.json").read_bytes()
        n_old = 0
        for c in subprocess.run(["git", "-C", str(repo), "log", "--all", "--format=%H", "--", f"{pack}/evidence/holdout_kit/items.json"],
                                capture_output=True, text=True).stdout.split():
            r = subprocess.run(["git", "-C", str(repo), "show", f"{c}:{pack}/evidence/holdout_kit/items.json"], capture_output=True)
            if r.returncode or r.stdout == current:
                continue  # deleted in that commit, or it is this kit
            n_old += 1
            for name in ("items.json", "_key.json", "items.md"):
                r = subprocess.run(["git", "-C", str(repo), "show", f"{c}:{pack}/evidence/holdout_kit/{name}"], capture_output=True, text=True)
                if r.returncode == 0:
                    texts.append((f"earlier kit {c[:7]}:{name}", r.stdout))
        assert n_old >= 2  # v1 (1cda014) and v2 (def1d2d)
    hits = []
    for name, t in texts:
        w = _tok(t)
        hits += [(" ".join(w[k:k + 5]), kg[tuple(w[k:k + 5])], name) for k in range(len(w) - 4) if tuple(w[k:k + 5]) in kg]
    assert not hits, hits[:10]


# ---------- draw rule and pass rule on made-up keys (never the real key) ----------
_OTHER_CIPS = ["14.0901", "51.3801", "42.0101", "26.0101", "14.1901", "14.0801", "52.0301", "52.1401", "13.1202", "40.0501",
               "27.0501", "44.0701"]


def _fake_source(n_cs):
    return ([{"source_id": f"cs-{k}", "cip": CS_CIP} for k in range(n_cs)]
            + [{"source_id": f"other-{k}", "cip": c} for k, c in enumerate(_OTHER_CIPS)])


def _fake_key(seed, n_cs=6):
    import random, make_holdout_kit
    rng = random.Random(seed)
    src = _fake_source(n_cs)
    weak = make_holdout_kit.draw_weak(rng, src)
    items = {}
    for n, it in enumerate(src, 1):
        w = it["source_id"] in weak
        wc = rng.randint(1, 3) if w else None
        items[f"Q{n:02d}"] = {"cip": it["cip"], "asset_id": it["cip"], "candidate_type": "weakened" if w else "full_strength",
                              "weakened_criterion": wc,
                              "accepted_scores": [[0, 1] if c == wc else [1, 2] for c in (1, 2, 3)]}
    return {"items": items}


def _grades(scores):
    return {h: {"scores": s} for h, s in scores.items()}


def test_weakened_count_is_drawn_secretly_within_the_documented_ranges():
    import random, make_holdout_kit
    src = (ROOT / "make_holdout_kit.py").read_text()
    assert "n // 2" not in src and "exactly half" not in src.lower()
    for n_cs in (4, 6):
        totals, cs_counts = set(), set()
        for seed in range(3000):
            weak = make_holdout_kit.draw_weak(random.Random(seed), _fake_source(n_cs))
            n_cs_weak = sum(w.startswith("cs-") for w in weak)
            assert 6 <= len(weak) <= 10 and 1 <= n_cs_weak <= 3 and n_cs_weak < n_cs  # CS always has both types
            totals.add(len(weak)); cs_counts.add(n_cs_weak)
        assert totals == set(range(6, 11)) and cs_counts == {1, 2, 3}  # the count varies; it is not a constant
    with pytest.raises(SystemExit):
        make_holdout_kit.draw_weak(random.Random(0), _fake_source(3))  # too few CS items for a per-major record


def test_shortcut_grader_never_passes_and_perfect_grader_always_passes():
    """Shortcut grader: scores one criterion 0 and the other two 2 on EVERY item. Even in its best case (it always picks
    the true weakened criterion on weakened items) it passes the old detection+gap rule but never the rule with the
    false-alarm limit. A perfect grader always passes."""
    import random, score_holdout
    rng = random.Random(12441)
    n, old_pass, new_pass, perfect_pass, rnd_crit_pass = 2000, 0, 0, 0, 0
    for seed in range(n):
        key = _fake_key(seed, n_cs=6 if seed % 2 else 4)
        sc, sc_rnd, perfect = {}, {}, {}
        for h, k in key["items"].items():
            c = k["weakened_criterion"] - 1 if k["candidate_type"] == "weakened" else rng.randrange(3)
            sc[h] = [0 if i == c else 2 for i in range(3)]
            c2 = rng.randrange(3)
            sc_rnd[h] = [0 if i == c2 else 2 for i in range(3)]
            perfect[h] = [0 if k["weakened_criterion"] == i + 1 else 2 for i in range(3)]
        d = score_holdout.discrimination(key, _grades(sc))
        old_pass += d["detection_rate"] >= 0.8 and d["mean_gap"] >= 1.0
        new_pass += d["passed"]
        assert d["false_alarm_rate"] == 1.0
        rnd_crit_pass += score_holdout.discrimination(key, _grades(sc_rnd))["passed"]
        p = score_holdout.discrimination(key, _grades(perfect))
        perfect_pass += p["passed"]
        assert p["detection_rate"] == 1.0 and p["false_alarm_rate"] == 0 and p["mean_gap"] == 2.0
    assert old_pass == n  # the gap the merchant found: the old rule let the shortcut through
    assert new_pass == 0 and rnd_crit_pass == 0
    assert perfect_pass == n


def test_random_flagging_grader_rarely_passes():
    """A grader who cannot tell the types apart but flags a random subset of items (picking the right criterion on
    weakened ones, its best case) passes the kit rule in under 3% of draws for every subset size."""
    import random, score_holdout
    rng = random.Random(7)
    for n_flag in range(1, 19):
        wins = 0
        for seed in range(1500):
            key = _fake_key(10_000 + seed)
            ids = list(key["items"]); flagged = set(rng.sample(ids, n_flag))
            sc = {}
            for h, k in key["items"].items():
                c = k["weakened_criterion"] - 1 if k["candidate_type"] == "weakened" else rng.randrange(3)
                sc[h] = [0 if (i == c and h in flagged) else 2 for i in range(3)]
            wins += score_holdout.discrimination(key, _grades(sc))["passed"]
        assert wins / 1500 < 0.03, (n_flag, wins)


def test_baseline_scores_are_exact_expected_agreements():
    import score_holdout
    full = {"candidate_type": "full_strength", "weakened_criterion": None, "accepted_scores": [[1, 2]] * 3}
    weak = {"candidate_type": "weakened", "weakened_criterion": 2, "accepted_scores": [[1, 2], [0, 1], [1, 2]]}
    best, b = score_holdout.baselines([full, full, full, weak])
    assert b["uniform_random"] == round(2 / 3, 4)
    assert b["all_2s"] == round((3 + 3 + 3 + 2) / 12, 4)
    assert b["shortcut_one_criterion_0"] == round((2 / 3 * 3 + 1) / 4, 4)
    assert best == max(b.values())
    assert "baseline_score" in score_holdout.BASELINE_DEFINITION


# ---------- per-asset discrimination (made-up keys only) ----------
def _evaluate(key, scores):
    import score_holdout
    return score_holdout.evaluate(key, _grades(scores))


def _perfect_scores(key):
    return {h: [0 if k["weakened_criterion"] == i + 1 else 2 for i in range(3)] for h, k in key["items"].items()}


def test_cs_record_needs_discrimination_on_cs_items_themselves():
    """Merchant v3 blocker: a grader perfect on the 12 non-CS items and all 2s on CS used to get a passing CS record
    (kit-level checks pass, CS agreement >= 0.8). With per-asset detection, false-alarm and above-baseline checks it
    never does."""
    n, cs_pass, cs_pass_old_rule = 2500, 0, 0
    for seed in range(n):
        key = _fake_key(50_000 + seed, n_cs=6)
        sc = _perfect_scores(key)
        for h, k in key["items"].items():
            if k["cip"] == CS_CIP:
                sc[h] = [2, 2, 2]
        disc, assets = _evaluate(key, sc)
        cs = assets[CS_CIP]
        cs_pass += cs["passed"]
        c = cs["checks"]
        cs_pass_old_rule += c["kit_discrimination"] and c["eligible"] and c["agreement_min"] and c["no_full_strength_judged_incorrect"]
        assert cs["asset_discrimination"]["detection_rate"] == 0 and not c["asset_detection_rate"]
        assert not c["agreement_above_baseline"]  # all 2s on CS is exactly the all-2s baseline
    assert cs_pass == 0
    assert cs_pass_old_rule / n > 0.2  # the hole was real: the old rule let this grader through


def test_degenerate_graders_never_pass_any_record():
    import random
    rng = random.Random(99)

    def shortcut(k, pick_true):
        c = k["weakened_criterion"] - 1 if (pick_true and k["candidate_type"] == "weakened") else rng.randrange(3)
        return [0 if i == c else 2 for i in range(3)]

    graders = {
        "all 2s": lambda key: {h: [2, 2, 2] for h in key["items"]},
        "all 1s": lambda key: {h: [1, 1, 1] for h in key["items"]},
        "all 0s": lambda key: {h: [0, 0, 0] for h in key["items"]},
        "uniform random": lambda key: {h: [rng.randrange(3) for _ in range(3)] for h in key["items"]},
        "shortcut, best case": lambda key: {h: shortcut(k, True) for h, k in key["items"].items()},
        "shortcut, random criterion": lambda key: {h: shortcut(k, False) for h, k in key["items"].items()},
        "perfect elsewhere, shortcut on CS": lambda key: {**_perfect_scores(key), **{h: shortcut(k, True) for h, k in key["items"].items() if k["cip"] == CS_CIP}},
        "perfect elsewhere, random on CS": lambda key: {**_perfect_scores(key), **{h: [rng.randrange(3) for _ in range(3)] for h, k in key["items"].items() if k["cip"] == CS_CIP}},
        "perfect elsewhere, wrong criterion on CS": lambda key: {**_perfect_scores(key), **{h: ([0 if i == k["weakened_criterion"] % 3 else 2 for i in range(3)] if k["candidate_type"] == "weakened" else [2, 2, 2]) for h, k in key["items"].items() if k["cip"] == CS_CIP}},
    }
    # random scoring is not a fixed strategy: a lucky draw can genuinely beat the baseline, so it gets a tiny bound
    random_graders = {"uniform random", "perfect elsewhere, random on CS"}
    for name, g in graders.items():
        passes = 0
        for seed in range(2000):
            key = _fake_key(70_000 + seed, n_cs=6 if seed % 2 else 4)
            passes += sum(a["passed"] for a in _evaluate(key, g(key))[1].values())
        assert passes <= (10 if name in random_graders else 0), (name, passes)  # 0%, or <= 0.5% for random scoring


def test_perfect_grader_passes_cs_always_and_honest_grader_usually():
    """A perfect grader passes the CS record on every key. An honest grader who detects each weakened answer with
    probability 0.95 and raises a false alarm on 1% of full-strength answers passes CS most of the time."""
    import random
    rng = random.Random(2026)
    n, perfect, honest = 2000, 0, 0
    for seed in range(n):
        key = _fake_key(90_000 + seed, n_cs=6)
        disc, assets = _evaluate(key, _perfect_scores(key))
        perfect += assets[CS_CIP]["passed"]
        assert all(a["passed"] == a["eligibility"]["eligible"] for a in assets.values())
        sc = {}
        for h, k in key["items"].items():
            s = [2, 2, 2]
            if k["candidate_type"] == "weakened" and rng.random() < 0.95:
                s[k["weakened_criterion"] - 1] = rng.choice([0, 1])
            elif k["candidate_type"] == "full_strength" and rng.random() < 0.01:
                s[rng.randrange(3)] = 1
            sc[h] = s
        honest += _evaluate(key, sc)[1][CS_CIP]["passed"]
    assert perfect == n
    assert 0.78 <= honest / n <= 0.95, honest / n


def test_holdout_crypto_round_trip_and_tamper_detection(ktmp):
    import holdout_crypto
    pf = holdout_crypto.init_passphrase(ktmp / "pp" / "passphrase")
    assert oct(pf.stat().st_mode & 0o777) == "0o600" and oct(pf.parent.stat().st_mode & 0o777) == "0o700"
    pw = holdout_crypto.read_passphrase(pf)
    data = b'{"made_up": "pytest key"}\n'
    p = ktmp / "k.json.enc"
    holdout_crypto.write_encrypted(p, data, pw, "holdout_key")
    blob = p.read_bytes()
    assert b"made_up" not in blob and oct(p.stat().st_mode & 0o777) == "0o600"
    assert holdout_crypto.decrypt_bytes(blob, pw, "holdout_key") == data
    with pytest.raises(SystemExit):
        holdout_crypto.decrypt_bytes(blob, b"x" * 40, "holdout_key")  # wrong passphrase
    with pytest.raises(SystemExit):
        holdout_crypto.decrypt_bytes(blob, pw, "holdout_source")  # role is authenticated
    env = json.loads(blob); ct = bytearray(__import__("base64").b64decode(env["ciphertext"])); ct[0] ^= 1
    env["ciphertext"] = __import__("base64").b64encode(bytes(ct)).decode()
    with pytest.raises(SystemExit):
        holdout_crypto.decrypt_bytes(json.dumps(env).encode(), pw, "holdout_key")  # modified ciphertext


def test_encrypt_cli_leaves_no_plaintext_and_passphrase_lives_outside_the_repo(ktmp):
    """Temp fixtures only (never the real private directory): the encrypt step deletes the plaintext and leaves an
    authenticated envelope; the default passphrase location is outside /workspace, the repo and the private directory."""
    import subprocess, holdout_crypto, make_holdout_kit
    pp = pathlib.Path(holdout_crypto.DEFAULT_PASSPHRASE_FILE)  # string checks only; the real file is never opened
    assert not str(pp).startswith("/workspace/") and not str(pp).startswith(str(ROOT))
    assert not str(pp).startswith(str(make_holdout_kit.PRIVATE))
    priv = ktmp / "private"; priv.mkdir()
    for name in ("holdout_key.json", "holdout_source.json"):
        (priv / name).write_text('{"made_up": true}\n')
    env = dict(os.environ, DREAMCO_HOLDOUT_PASSPHRASE_FILE=str(ktmp / "secret" / "passphrase"))
    r = subprocess.run([sys.executable, str(ROOT / "holdout_crypto.py"), "init-passphrase"], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    for name, role in (("holdout_key.json", "holdout_key"), ("holdout_source.json", "holdout_source")):
        r = subprocess.run([sys.executable, str(ROOT / "holdout_crypto.py"), "encrypt", str(priv / name), role],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr
        assert not (priv / name).exists()
        e = json.loads((priv / f"{name}.enc").read_text())
        assert e["format"] == holdout_crypto.FORMAT and e["role"] == role and set(e) == {"format", "role", "kdf", "nonce", "ciphertext"}
        assert b"made_up" not in (priv / f"{name}.enc").read_bytes()


SYNTH_SPEC = [(CS_CIP, "full_strength", None), (CS_CIP, "weakened", 2), (CS_CIP, "full_strength", None), (CS_CIP, "weakened", 3),
              ("40.0501", "weakened", 1), ("52.0301", "full_strength", None), ("14.0801", "full_strength", None)]
_GIT_ID = ["-c", "user.name=pytest", "-c", "user.email=pytest@example.invalid", "-c", "commit.gpgsign=false"]


def _git(repo, *args):
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", *_GIT_ID, "-C", str(repo), *args], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _synthetic_kit(base, spec=SYNTH_SPEC):
    """A small synthetic kit + ENCRYPTED made-up key + commitment in a temp git repo with a local bare remote (never the
    real private key)."""
    import holdout_crypto
    repo = base / "repo"; kit = repo / "kit"; kit.mkdir(parents=True)
    plans = {m["cip"]: m for m in json.loads((ROOT / "data/majors_selected.json").read_text())}
    items, key_items = [], {}
    for n, (cip, kind, wc) in enumerate(spec, 1):
        qid = f"Q{n:02d}"
        ans = "\n".join(f"- **Point {k}:** synthetic test answer {n} {k}" for k in range(1, 6))
        items.append({"item_id": qid, "major": f"{plans[cip]['title']} (CIP {cip})", "prompt": f"synthetic prompt {n}",
                      "candidate_answer": ans, "rubric": [{"criterion": f"C{k}", "description": "synthetic criterion", "points": 2} for k in (1, 2, 3)]})
        key_items[qid] = {"cip": cip, "asset_id": plans[cip]["asset_id"], "candidate_type": kind, "weakened_criterion": wc,
                          "expected_scores": [0 if c == wc else 2 for c in (1, 2, 3)],
                          "accepted_scores": [[0, 1] if c == wc else [1, 2] for c in (1, 2, 3)],
                          "candidate_answer_sha256": hashlib.sha256(ans.encode()).hexdigest()}
    items_b = (json.dumps({"kit": "synthetic", "created_at": "2026-10-02T12:00:00-05:00", "n_items": len(items), "items": items}) + "\n").encode()
    (kit / "items.json").write_bytes(items_b)
    key_b = json.dumps({"kit": "synthetic", "created_at": "2026-10-02T12:00:00-05:00", "nonce": os.urandom(32).hex(), "items": key_items}).encode()
    priv = base / "private"; priv.mkdir()
    pf = holdout_crypto.init_passphrase(base / "secret" / "passphrase")
    keyp = priv / "holdout_key.json.enc"
    holdout_crypto.write_encrypted(keyp, key_b, holdout_crypto.read_passphrase(pf), "holdout_key")
    (kit / "KEY_COMMITMENT.txt").write_text(f"key_sha256: {hashlib.sha256(key_b).hexdigest()}\n"
                                           f"items_json_sha256: {hashlib.sha256(items_b).hexdigest()}\n")
    remote = base / "remote.git"
    _git(base, "init", "-q", "--bare", str(remote))
    _git(base, "init", "-q", "-b", "main", str(repo))
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "add", "kit/items.json", "kit/KEY_COMMITMENT.txt")
    _git(repo, "commit", "-q", "-m", "synthetic kit")
    _git(repo, "push", "-q", "-u", "origin", "main")
    root = base / "pack"
    (root / "data").mkdir(parents=True); (root / "study_plans").mkdir()
    import shutil
    shutil.copy(ROOT / "data/majors_selected.json", root / "data")
    for cip in {c for c, _, _ in spec}:
        src = next((ROOT / "study_plans").glob(f"{cip}_*.md"))
        (root / "study_plans" / src.stem).mkdir()
        shutil.copy(sidecar(src) / "asset.json", root / "study_plans" / src.stem)
        (root / "study_plans" / src.name).write_text("synthetic")
    return {"kit": kit, "repo": repo, "key": keyp, "key_b": key_b, "pf": pf, "root": root, "items": items,
            "key_items": key_items, "priv": priv, "base": base}


def _write_sheet(path, items, scores, grader="pytest-synthetic"):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id", "major", "criterion_1", "score_1", "criterion_2", "score_2", "criterion_3", "score_3",
                    "factually_correct", "comments", "grader", "graded_at"])
        for n, i in enumerate(items):
            s = scores[i["item_id"]]
            g = grader[n % len(grader)] if isinstance(grader, list) else grader
            w.writerow([i["item_id"], i["major"], "C1", s[0], "C2", s[1], "C3", s[2], "yes", "", g, "2026-10-02T12:00:00-05:00"])


def _run_score(*args, s, extra_env=None):
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT"}
    env.update(DREAMCO_HOLDOUT_PRIVATE_DIR=str(s["priv"]), DREAMCO_HOLDOUT_PASSPHRASE_FILE=str(s["pf"]), **(extra_env or {}))
    return subprocess.run([sys.executable, str(ROOT / "score_holdout.py"), "--kit-dir", s["kit"], "--key", s["key"],
                           "--root", s["root"], *map(str, args)], capture_output=True, text=True, env=env)


def _declare(s, grader="pytest-synthetic"):
    r = _run_score("--declare-final", "--grader", grader, s=s)
    assert r.returncode == 0, r.stderr
    return r


def _commit_grading(s, push=True, msg="grading final"):
    _git(s["repo"], "add", "kit/grading_sheet.csv", "kit/GRADING_FINAL.txt")
    _git(s["repo"], "commit", "-q", "-m", msg)
    if push:
        _git(s["repo"], "push", "-q", "origin", "main")
    return _git(s["repo"], "rev-parse", "HEAD")


def _resolve_results(root, rec):
    """results_path is relative to the same root as evidence_root (the repository root); map it into a pack root."""
    assert rec["results_path"].startswith(rec["evidence_root"] + "/") and rec["evidence_root"] == build.EVIDENCE_ROOT
    return root / rec["results_path"][len("study_packs/career_pathways/"):]


def _perfect(s):
    return {h: k["expected_scores"] for h, k in s["key_items"].items()}


def test_score_holdout_dry_run_never_opens_the_key_and_is_identical_across_sheets(ktmp):
    s = _synthetic_kit(ktmp)
    blank = _run_score("--sheet", KIT / "grading_sheet.csv", s=s)
    assert blank.returncode != 0
    import random
    rng = random.Random(3)
    sheets = [_perfect(s), {h: [2, 2, 2] for h in s["key_items"]}, {h: [0, 0, 0] for h in s["key_items"]},
              {h: [rng.randrange(3) for _ in range(3)] for h in s["key_items"]}]
    # the key and passphrase do not exist for these runs: the dry run must not need them
    nokey = dict(s, key=ktmp / "absent.enc", pf=ktmp / "absent-passphrase")
    outs = set()
    for n, sc in enumerate(sheets):
        _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], sc)
        r = _run_score(s=nokey)
        outs.add((r.returncode, r.stdout, r.stderr))
        assert r.returncode == 0 and "No scores were computed" in r.stdout
        assert not re.search(r"score=|passed=|agreement|detection|\d\.\d", r.stdout + r.stderr)
    assert len(outs) == 1  # same output and exit code whatever the scores
    assert not (s["root"] / "data/dreamco_knowledge").exists() and not (s["kit"] / "GRADING_FINAL.txt").exists()
    src = (ROOT / "score_holdout.py").read_text()
    dry = src.split("if not a.finalize:", 1)[1].split("finalize(a, kit", 1)[0]
    assert "key" not in dry and "decrypt" not in dry  # the dry-run branch has no key access


def test_finalize_requires_a_locked_sheet_and_one_matching_grader(ktmp):
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s))
    r = _run_score("--finalize", "--run-id", "20261002-91", s=s)
    assert r.returncode != 0 and "GRADING_FINAL.txt" in r.stderr  # not declared final yet
    (s["kit"] / "GRADING_FINAL.txt").write_text("FINAL: grader=pytest-synthetic; declared_at=2026-10-02T13:00:00-05:00\n")
    r = _run_score("--finalize", "--run-id", "20261002-91", s=s)
    assert r.returncode != 0 and "sheet_sha256" in r.stderr  # the old line without the sheet hash is not enough
    (s["kit"] / "GRADING_FINAL.txt").unlink()
    r = _run_score("--declare-final", "--grader", "someone-else", s=s)
    assert r.returncode != 0 and not (s["kit"] / "GRADING_FINAL.txt").exists()
    _declare(s)
    final = (s["kit"] / "GRADING_FINAL.txt").read_text()
    assert f"sheet_sha256={sha(s['kit'] / 'grading_sheet.csv')}" in final
    assert _run_score("--declare-final", "--grader", "pytest-synthetic", s=s).returncode != 0  # declared once
    # the sheet is locked: any change after the declaration is refused
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], {h: [2, 2, 2] for h in s["key_items"]})
    r = _run_score("--finalize", "--run-id", "20261002-92", s=s)
    assert r.returncode != 0 and "sheet_sha256" in r.stderr and not (s["root"] / "data/dreamco_knowledge").exists()
    # two graders on the sheet, or a grader other than the declared one, is refused
    for g in (["pytest-synthetic", "second-grader"], "someone-else"):
        _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s), grader=g)
        (s["kit"] / "GRADING_FINAL.txt").write_text("FINAL: grader=pytest-synthetic; declared_at=2026-10-02T13:00:00-05:00; "
                                                    f"sheet_sha256={sha(s['kit'] / 'grading_sheet.csv')}\n")
        r = _run_score("--finalize", "--run-id", "20261002-93", s=s)
        assert r.returncode != 0 and "exactly one grader" in r.stderr
    assert not (s["root"] / "data/dreamco_knowledge").exists()


def test_finalize_requires_grading_files_committed_and_pushed(ktmp):
    import shutil
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s))
    _declare(s)
    nokey = dict(s, key=ktmp / "absent.enc")  # git checks come first: the key is never touched when they fail
    r = _run_score("--finalize", "--run-id", "20261002-81", s=nokey)
    assert r.returncode != 0 and "not committed" in r.stderr and "decrypt" not in r.stderr
    sha_commit = _commit_grading(s, push=False)
    r = _run_score("--finalize", "--run-id", "20261002-81", s=nokey)
    assert r.returncode != 0 and "remote" in r.stderr  # committed but not pushed
    _git(s["repo"], "push", "-q", "origin", "main")
    with open(s["kit"] / "GRADING_FINAL.txt", "a") as fh:
        fh.write("# edited after the commit\n")
    r = _run_score("--finalize", "--run-id", "20261002-81", s=nokey)
    assert r.returncode != 0 and "uncommitted" in r.stderr
    _git(s["repo"], "checkout", "--", "kit/GRADING_FINAL.txt")
    outside = ktmp / "outside_sheet.csv"; shutil.copy(s["kit"] / "grading_sheet.csv", outside)
    r = _run_score("--finalize", "--sheet", outside, "--run-id", "20261002-81", s=nokey)
    assert r.returncode != 0 and "git repository" in r.stderr  # a sheet outside the repo is refused
    assert not (s["root"] / "data/dreamco_knowledge").exists()
    r = _run_score("--finalize", "--run-id", "20261002-81", s=s)
    assert r.returncode == 0, r.stderr
    recs = list((s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-81.json"))
    assert len(recs) == 4
    for p in recs:
        rec = json.loads(p.read_text())
        assert rec["grading_commit"] == sha_commit
        res = json.loads(_resolve_results(s["root"], rec).read_text())
        assert res["grading_git"]["grading_commit"] == sha_commit and res["grading_git"]["remote_branches"] == ["origin/main"]
    assert f"grading_commit: {sha_commit}" in (s["kit"] / "FINALIZED.txt").read_text()


def test_test_only_git_bypass_never_produces_passing_evidence(ktmp):
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s))
    _declare(s)  # not committed
    r = _run_score("--finalize", "--run-id", "20261002-82", s=s, extra_env={"DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT": "1"})
    assert r.returncode == 0, r.stderr
    recs = [json.loads(p.read_text()) for p in (s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-82.json")]
    assert len(recs) == 4
    for rec in recs:
        assert rec["passed"] is False and rec["grading_commit"] is None and "TEST ONLY" in rec["limitations"]
        res = json.loads(_resolve_results(s["root"], rec).read_text())
        assert "TEST ONLY" in res["grading_git"]["skipped"]


def test_finalize_verifies_the_encrypted_key_against_the_commitment(ktmp):
    import holdout_crypto
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s))
    _declare(s); _commit_grading(s)
    pw = holdout_crypto.read_passphrase(s["pf"])
    bad = ktmp / "bad_key.json.enc"
    holdout_crypto.write_encrypted(bad, s["key_b"] + b" ", pw, "holdout_key")  # a different key, validly encrypted
    r = _run_score("--finalize", "--run-id", "20261002-92", s=dict(s, key=bad))
    assert r.returncode != 0 and "KEY_COMMITMENT" in r.stderr
    wrong_pf = ktmp / "wrong" / "passphrase"; holdout_crypto.init_passphrase(wrong_pf)
    r = _run_score("--finalize", "--run-id", "20261002-92", s=dict(s, pf=wrong_pf))
    assert r.returncode != 0 and "cannot decrypt" in r.stderr
    assert not (s["root"] / "data/dreamco_knowledge").exists() and not (s["kit"] / "FINALIZED.txt").exists()


def test_all_2s_fails_and_a_key_commitment_is_finalized_only_once(ktmp):
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], {h: [2, 2, 2] for h in s["key_items"]})
    _declare(s); _commit_grading(s)
    r = _run_score("--finalize", "--run-id", "20261002-93", s=s)
    assert r.returncode == 0, r.stderr
    recs = sorted((s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-93.json"))
    assert len(recs) == 4
    for rp in recs:
        rec = json.loads(rp.read_text())
        assert rec["passed"] is False and rec["integrity_hash"] == "sha256:" + sha(_resolve_results(s["root"], rec))
        res = json.loads(_resolve_results(s["root"], rec).read_text())
        assert res["kit_discrimination"]["passed"] is False and res["kit_discrimination"]["detection_rate"] == 0
    assert "20261002-93" in (s["kit"] / "FINALIZED.txt").read_text()
    # a second finalize of the same key commitment is refused, under a new run id too, even with a new committed sheet
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s))
    (s["kit"] / "GRADING_FINAL.txt").unlink(); _declare(s); _commit_grading(s, msg="regrade")
    for run in ("20261002-94", "20261003-01", "20261002-93"):
        r = _run_score("--finalize", "--run-id", run, s=s)
        assert r.returncode != 0 and "already finalized" in r.stderr
    (s["kit"] / "FINALIZED.txt").unlink()  # the results files alone also block it
    r = _run_score("--finalize", "--run-id", "20261002-95", s=s)
    assert r.returncode != 0 and "already finalized" in r.stderr
    assert not list((s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-9[45].json"))


def test_perfect_grading_passes_only_eligible_assets_with_honest_record_fields(ktmp):
    s = _synthetic_kit(ktmp)
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], _perfect(s), grader="Irean")
    _declare(s, "Irean")
    grading_commit = _commit_grading(s)
    r = _run_score("--finalize", "--run-id", "20261002-94", s=s)
    assert r.returncode == 0, r.stderr
    sch = evidence_schema()
    recs = {json.loads(p.read_text())["evidence_id"].split(":")[1]: json.loads(p.read_text())
            for p in (s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-94.json")}
    plans = {m["cip"]: m["asset_id"] for m in json.loads((ROOT / "data/majors_selected.json").read_text())}
    assert set(recs) == {plans[c] for c, _, _ in SYNTH_SPEC}
    for aid, rec in recs.items():
        for f in sch["required_fields"] + ["split", "n_items", "metric", "score", "threshold", "passed", "baseline_score", "grading_commit"]:
            assert rec.get(f) not in (None, ""), f
        assert rec["split"] == "holdout" and rec["grader"] == "Irean" and rec["grading_commit"] == grading_commit
        res_p = _resolve_results(s["root"], rec)
        assert rec["integrity_hash"] == "sha256:" + sha(res_p)
        res = json.loads(res_p.read_text())
        assert res["split"] == "holdout" and res["graders"] == ["Irean"] and res["declared_final"]["grader"] == "Irean"
        assert res["grading_sheet_sha256"] == res["declared_final"]["sheet_sha256"] == sha(s["kit"] / "grading_sheet.csv")
        assert 0 < rec["baseline_score"] == res["baseline_score"] == max(res["baselines"].values()) <= 1
        assert rec["baseline_definition"] == res["baseline_definition"]
        assert "Irean" in rec["limitations"] and "owner" in rec["limitations"] and rec["limitations"] == res["limitations"]
        assert "single human grader who is also the owner" not in rec["limitations"]  # built from the sheet, not hard-coded
        assert res["kit_discrimination"]["passed"] is True and rec["score"] == 1.0
        elig = res["per_asset_eligibility"]
        if aid == plans[CS_CIP]:
            assert elig["eligible"] and elig["n_items"] == 4 and rec["passed"] is True and all(res["pass_checks"].values())
            ad = res["asset_discrimination"]
            assert ad["detection_rate"] == 1.0 and ad["false_alarm_rate"] == 0 and rec["score"] > rec["baseline_score"]
        else:  # single-item majors only count toward the kit-level check
            assert not elig["eligible"] and elig["n_items"] == 1 and rec["passed"] is False and elig["reason"]


def test_shortcut_sheet_fails_finalize_on_false_alarms(ktmp):
    s = _synthetic_kit(ktmp)
    sc = {h: ([0 if c == k["weakened_criterion"] else 2 for c in (1, 2, 3)] if k["candidate_type"] == "weakened" else [2, 0, 2])
          for h, k in s["key_items"].items()}
    _write_sheet(s["kit"] / "grading_sheet.csv", s["items"], sc)
    _declare(s); _commit_grading(s)
    r = _run_score("--finalize", "--run-id", "20261002-95", s=s)
    assert r.returncode == 0, r.stderr
    for p in (s["root"] / "data/dreamco_knowledge/evidence/holdout").glob("*/20261002-95.json"):
        rec = json.loads(p.read_text())
        res = json.loads(_resolve_results(s["root"], rec).read_text())
        d = res["kit_discrimination"]
        assert d["detection_rate"] == 1.0 and d["mean_gap"] >= 1.0 and d["false_alarm_rate"] == 1.0
        assert d["passed"] is False and rec["passed"] is False


def test_make_holdout_kit_cannot_regenerate_the_key_from_committed_inputs(ktmp):
    import subprocess
    before = {f.name: f.read_bytes() for f in KIT.iterdir()}
    env = dict(os.environ, DREAMCO_HOLDOUT_PRIVATE_DIR=str(ktmp),  # empty: the private source is not in the repo
               DREAMCO_HOLDOUT_PASSPHRASE_FILE=str(ktmp / "no-passphrase"))
    r = subprocess.run([sys.executable, str(ROOT / "make_holdout_kit.py"), "--redraw"], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and "private kit source not found" in (r.stdout + r.stderr)
    assert {f.name: f.read_bytes() for f in KIT.iterdir()} == before
    src = (ROOT / "make_holdout_kit.py").read_text()
    assert "secrets.randbits" in src and not re.search(r"random\.(seed|Random)\(\s*\d", src)
    assert "n_weakened" not in src.split("print(", 1)[-1]  # the drawn count is never printed
    for pat in ("holdout_source.json*", "holdout_key.json*", "write_source.py*", "passphrase"):
        assert not list(ROOT.rglob(pat)), pat


def test_tests_never_touch_the_real_private_key_or_passphrase():
    """The suite must run on any machine: no test reads the builder's private directory or passphrase. The audit
    guard (_no_private_access) records any open/listdir/scandir under them; this also checks the test source."""
    src = pathlib.Path(__file__).read_text()
    for p in _FORBIDDEN:
        assert src.count(p) == 1, p  # only in the guard's own list
    assert not _PRIVATE_ACCESS


def test_data_dictionary_covers_every_output_field():
    sys.path.insert(0, str(ROOT / "docs"))
    import _paths
    dd = json.loads((ROOT / "docs/data_dictionary.json").read_text())
    assert set(_paths.FILES) <= set(dd["files"])
    for pat in _paths.FILES:
        documented = set(dd["files"][pat]["fields"])
        found = _paths.paths(pat)
        assert found, pat
        assert not found - documented, (pat, sorted(found - documented))
        stale = {f for f in documented - found if not dd["files"][pat]["fields"][f].startswith("Optional")}
        assert not stale, (pat, sorted(stale))  # no stale entries
        assert all(len(v.strip()) >= 5 for v in dd["files"][pat]["fields"].values())
    md = (ROOT / "docs/DATA_DICTIONARY.md").read_text()
    for pat, spec in dd["files"].items():
        assert f"## `{pat}`" in md
        for f in spec["fields"]:
            assert f"`{f}`" in md, (pat, f)
