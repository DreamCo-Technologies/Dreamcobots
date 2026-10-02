"""Build majors -> O*NET occupations -> study plans (+ practice tasks and per-plan gate files) from pinned raw files.

Sources (all pinned by sha256 in raw/SOURCES.md):
- O*NET 31.0 Database (USDOL/ETA, CC BY 4.0): occupation_data, knowledge, essential_skills, job_zones,
  job_zone_reference, task_statements.
- O*NET Resource Center CIP 2020 -> O*NET-SOC 2019 crosswalk (Crosswalk Files by USDOL/ETA, CC BY 4.0).

Per study plan this writes study_plans/<cip>_<slug>.md and a sidecar folder study_plans/<cip>_<slug>/ with
provenance.json + candidate.json (schemas/data_package_asset_provenance.schema.json layout) and, when the DreamCo
gate tool is available, license_gate.json produced by tools/license_provenance_gate.py.
Owner approval is never set here (it stays pending).
"""
import csv, hashlib, json, os, re, pathlib, subprocess, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent
RAW, DATA, PLANS = ROOT / "raw", ROOT / "data", ROOT / "study_plans"
ONET_VERSION = "31.0"
DB_URL = "https://www.onetcenter.org/dl_files/database/db_31_0_csv/"
CROSSWALK_URL = "https://www.onetcenter.org/crosswalks/cip/Education_CIP_to_ONET_SOC.xlsx"
CC_BY = "https://creativecommons.org/licenses/by/4.0/"
ONLINE = "https://www.onetonline.org/link/summary/"
PRACTICE_LABEL = "DreamCo-original practice prompt"

PROVENANCE = (
    "---\n**Provenance.** This study plan includes information from the O*NET 31.0 Database by the U.S. Department "
    "of Labor, Employment and Training Administration (USDOL/ETA), used under the CC BY 4.0 license "
    f"({CC_BY}). Pinned version: O*NET 31.0 (`db_31_0_csv`). Knowledge, skill, Job Zone, and task identifiers "
    "come from that release; O*NET 31.0 split the former Skills domain into Essential Skills and Transferable "
    "Skills, and the skill values here are Essential Skills (`essential_skills.csv`). Major-to-occupation links come "
    "from the O*NET Resource Center `Education_CIP_to_ONET_SOC.xlsx` crosswalk (2020 CIP to O*NET-SOC 2019); this "
    "crosswalk is also O*NET Resource Center data (Crosswalk Files by USDOL/ETA), licensed under CC BY 4.0. "
    "DreamCo has modified all or some of this information: it filtered, averaged, ranked, and reformatted O*NET values "
    "and wrote the outline, next steps, and practice prompts. USDOL/ETA has not approved, endorsed, or tested these "
    "modifications. O*NET\u00ae is a trademark of USDOL/ETA. The 4-year outline, typical next steps, and practice "
    "prompts are DreamCo-derived guidance, not O*NET data.\n")

MAJORS = ["11.0701", "14.0901", "11.0401", "51.3801", "42.0101", "26.0101", "14.1901", "14.0801", "14.1001",
          "52.0301", "52.0201", "52.0801", "52.1401", "45.0601", "45.1001", "13.1202", "40.0501", "40.0801",
          "27.0101", "27.0501", "23.0101", "09.0101", "44.0701", "43.0104", "51.2001", "50.0409", "03.0104"]

# Not treated as entry-level targets. STRICT is never relaxed; SOFT is relaxed only when no linked title survives it.
EXCLUDE_STRICT = re.compile(r"Manager|Chief|Postsecondary|All Other")
EXCLUDE_SOFT = re.compile(r"Supervisor|Director|Treasurers and Controllers")
ENTRY_ZONE_ORDER = [4, 3, 5, 2]  # Job Zone 4 = typical bachelor's level; then closest alternatives.

# DreamCo-derived study guidance per O*NET knowledge element (how a student can build it in college).
KNOWLEDGE_STUDY = {
    "Administration and Management": "a management or organizational-behavior course plus a role leading a student project team",
    "Administrative": "records, scheduling, and office-software practice (e.g., an information-systems or business-communication course)",
    "Biology": "the biology lecture-and-lab sequence",
    "Building and Construction": "construction materials and methods coursework with site visits",
    "Chemistry": "general and organic chemistry with labs",
    "Communications and Media": "media writing and digital media production courses",
    "Computers and Electronics": "programming, data structures, and computer-systems coursework",
    "Customer and Personal Service": "client-facing experience such as tutoring, help-desk, or service-learning roles",
    "Design": "technical drawing, CAD, or design-studio coursework",
    "Economics and Accounting": "principles of economics and financial accounting",
    "Education and Training": "an instructional-methods course or peer-tutoring / teaching-assistant work",
    "Engineering and Technology": "engineering fundamentals and applied-technology courses",
    "English Language": "advanced composition and technical or professional writing",
    "Fine Arts": "studio art, music, or theater courses",
    "Food Production": "agricultural science or food-systems coursework",
    "Foreign Language": "sustained study of a second language",
    "Geography": "physical geography and GIS coursework",
    "History and Archeology": "history and historical-methods courses",
    "Law and Government": "law, public policy, and regulation courses",
    "Mathematics": "college mathematics through calculus and statistics",
    "Mechanical": "mechanics or machine-design coursework with hands-on lab or shop work",
    "Medicine and Dentistry": "anatomy, physiology, and pharmacology coursework",
    "Personnel and Human Resources": "human resource management coursework",
    "Philosophy and Theology": "ethics and philosophy courses",
    "Physics": "calculus-based physics with labs",
    "Production and Processing": "operations, manufacturing-process, and quality-control coursework",
    "Psychology": "introductory and applied psychology courses",
    "Public Safety and Security": "safety, security, and risk-management coursework",
    "Sales and Marketing": "principles of marketing and consumer behavior",
    "Sociology and Anthropology": "sociology and cultural anthropology courses",
    "Telecommunications": "computer networking and telecommunications-systems coursework",
    "Therapy and Counseling": "counseling-methods coursework with a supervised practicum",
    "Transportation": "logistics and transportation-systems coursework",
}
# DreamCo-derived practice habit per O*NET 31.0 Essential Skill.
SKILL_PRACTICE = {
    "Reading Comprehension": "reading and summarizing technical or primary sources each week",
    "Active Listening": "paraphrasing teammates' points before responding in group work",
    "Writing": "writing memos or lab reports with a feedback-and-revision cycle",
    "Speaking": "presenting work in class or at a student conference",
    "Mathematics": "regular quantitative problem sets",
    "Science": "applying the scientific method in a lab or research project",
    "Critical Thinking": "comparing alternative solutions in case studies and stating trade-offs",
    "Active Learning": "learning one new tool or method each term and documenting it",
    "Learning Strategies": "spaced practice and teaching material back to peers",
    "Monitoring": "checking your own work against a checklist and tracking project progress",
}

# Activity type is classified only from the first verb of an O*NET task statement; task text is not reproduced.
ACTIVITY_VERBS = {
    "analyze": "analyze analyse evaluate assess review examine investigate study research identify determine calculate "
               "measure interpret compare audit diagnose estimate forecast appraise",
    "design": "develop design create build program modify install implement construct establish formulate devise "
              "write code configure",
    "document": "prepare write document compile record draft report",
    "communicate": "confer consult advise recommend communicate explain present collaborate meet interview counsel "
                   "instruct teach train educate inform discuss answer",
    "monitor": "monitor inspect test verify check observe ensure track",
    "plan": "plan direct supervise manage schedule organize arrange coordinate oversee assign allocate delegate",
}
VERB_TO_ACTIVITY = {v: a for a, vs in ACTIVITY_VERBS.items() for v in vs.split()}
PROMPTS = {
    "analyze": ("Pick a realistic small case on this theme (public data or a clearly labeled invented scenario) and write a "
                "one-page analysis: the question, the evidence used, the method, and a recommendation. Show where {k1} and "
                "{k2} knowledge shaped the reasoning.",
                "Reasoning: evidence, method, and recommendation connect, and limitations are stated."),
    "design": ("Produce a short design or build plan for a small deliverable on this theme: requirements, two alternatives "
               "considered, the choice and why, and how you would check that it works. Draw on {k1} and {k2}.",
               "Design quality: requirements are testable and the choice between alternatives is justified."),
    "document": ("Draft the work document this theme calls for (report, record, or brief) for a named audience, then add a "
                 "short note on what you would verify before it is used. Apply {k1} and {k2}.",
                 "Communication: accurate, organized, suited to the named audience, with verification needs flagged."),
    "communicate": ("Write a 5-minute briefing or role-play script for a conversation with a colleague or client on this "
                    "theme: key message, two likely questions with answers, and an agreed next step. Use {k1} and {k2}.",
                    "{s}: the message is clear, questions are anticipated, and the next step is concrete."),
    "monitor": ("Create a checklist or test plan for this theme: what to check, how often, the pass condition, and what to "
                "do when a check fails. Ground it in {k1} and {k2}.",
                "Verifiability: each check has a measurable pass condition and a defined response to failure."),
    "plan": ("Write a two-week plan for carrying out this theme on a small project: steps, roles, timeline, risks, and how "
             "progress is tracked. Apply {k1} and {k2}.",
             "Feasibility: steps, timeline, and risks are realistic and progress is trackable."),
    "perform": ("Write a step-by-step procedure for carrying out this theme in a realistic setting, noting safety, quality, or "
                "ethical considerations and how you would know it was done well. Apply {k1} and {k2}.",
                "Process quality: steps are ordered and complete and include safety, quality, or ethics checks."),
}
PRACTICE_PER_MAJOR = 6

# Raw files: name -> (source_id, url)
SOURCE_FILES = {
    "occupation_data.csv": ("onet_db_31_0", DB_URL + "occupation_data.csv"),
    "knowledge.csv": ("onet_db_31_0", DB_URL + "knowledge.csv"),
    "essential_skills.csv": ("onet_db_31_0", DB_URL + "essential_skills.csv"),
    "job_zones.csv": ("onet_db_31_0_jobzones_tasks", DB_URL + "job_zones.csv"),
    "job_zone_reference.csv": ("onet_db_31_0_jobzones_tasks", DB_URL + "job_zone_reference.csv"),
    "task_statements.csv": ("onet_db_31_0_jobzones_tasks", DB_URL + "task_statements.csv"),
    "Education_CIP_to_ONET_SOC.xlsx": ("onet_cip_soc_crosswalk", CROSSWALK_URL),
}


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load_pins():
    """Parse raw/SOURCES.md -> {file: (sha256, download_date)} and verify every raw file against its pin."""
    pins, date = {}, None
    for line in (RAW / "SOURCES.md").read_text().splitlines():
        m = re.match(r"^Downloaded (\d{4}-\d{2}-\d{2})", line)
        if m:
            date = m.group(1)
        m = re.match(r"^([0-9a-f]{64})\s+(\S+)$", line)
        if m:
            pins[m.group(2)] = (m.group(1), date)
    for name in SOURCE_FILES:
        if name not in pins:
            raise SystemExit(f"{name} not pinned in raw/SOURCES.md")
        if sha256(RAW / name) != pins[name][0]:
            raise SystemExit(f"{name}: sha256 does not match raw/SOURCES.md (run fetch_sources.py)")
    return pins


def load_crosswalk():
    df = pd.read_excel(RAW / "Education_CIP_to_ONET_SOC.xlsx", header=None, dtype=str)
    hdr = df.index[df[0].astype(str).str.strip() == "2020 CIP Code"][0]
    df = df.iloc[hdr + 1:, :4]
    df.columns = ["cip", "cip_title", "soc", "soc_title"]
    df = df.dropna(subset=["cip", "soc"])
    df["cip"] = df["cip"].str.strip()
    df["soc"] = df["soc"].str.strip()
    return df


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:50]


def asset_id(cip, title):
    return "edu-" + "".join(w[0] for w in slug(title).split("_") if w) + "-" + cip


def load_im(path):
    df = pd.read_csv(path, dtype={"O*NET-SOC Code": str})
    return df[df["Scale ID"] == "IM"][["O*NET-SOC Code", "Element Name", "Data Value"]]


def top_elements(im, socs, n):
    df = im[im["O*NET-SOC Code"].isin(socs)]
    if df.empty:
        return []
    g = df.groupby("Element Name")["Data Value"].mean().sort_values(ascending=False, kind="stable").head(n)
    return [(k, round(float(v), 2)) for k, v in g.items()]


def rank_entry_targets(occs, zones, kim):
    """Pick 1-3 entry targets: eligible titles in the first Job Zone tier of ENTRY_ZONE_ORDER that has any,
    base .00 codes first, then ranked by Pearson correlation of the occupation's knowledge-importance profile to the mean profile of the
    eligible linked occupations (so leadership/faculty roles do not steer the ranking)."""
    eligible = [(s, t) for s, t in occs if not EXCLUDE_STRICT.search(t) and not EXCLUDE_SOFT.search(t)]
    rule = "excluding Manager/Chief/Postsecondary/All Other/Supervisor/Director/Treasurers and Controllers titles"
    if not any(s in zones for s, _ in eligible):
        eligible = [(s, t) for s, t in occs if not EXCLUDE_STRICT.search(t)]
        rule = ("excluding Manager/Chief/Postsecondary/All Other titles; no other linked title survives the stricter "
                "filter, so first-line supervisor and director titles were allowed")
    socs = [s for s, _ in eligible] or [s for s, _ in occs]
    major_vec = kim[kim["O*NET-SOC Code"].isin(socs)].groupby("Element Name")["Data Value"].mean()
    def sim(soc):
        v = kim[kim["O*NET-SOC Code"] == soc].set_index("Element Name")["Data Value"]
        if v.empty or major_vec.empty:
            return -1.0
        a, b = v.align(major_vec, join="inner")
        a, b = a - a.mean(), b - b.mean()  # Pearson correlation of the two profiles
        den = float((a ** 2).sum() ** 0.5 * (b ** 2).sum() ** 0.5)
        return float((a * b).sum()) / den if den else -1.0
    for zone in ENTRY_ZONE_ORDER:
        tier = [(s, t) for s, t in eligible if zones.get(s) == zone]
        if tier:
            # Base O*NET-SOC codes (.00) before detailed specialty codes, then by profile correlation; ties keep crosswalk order.
            ranked = sorted(tier, key=lambda o: (not o[0].endswith(".00"), -sim(o[0])))
            zl = "1-2" if zone == 2 else zone
            basis = (f"Job Zone {zl} linked occupations ({rule}), ranked by similarity of their O*NET knowledge-importance "
                     f"profile to the average profile of the eligible linked occupations (Pearson correlation), base O*NET-SOC .00 codes first")
            if zone != 4:
                basis += f"; no eligible Job Zone 4 occupation is linked to this major, so Job Zone {zl} was used"
            return ranked[:3], zone, basis, eligible, sim
    if eligible:
        return eligible[:1], None, "no Job Zone rating for eligible occupations; first eligible crosswalk link used", eligible, sim
    return occs[:1], None, "no linked title passes the entry-level filter; first crosswalk link used", eligible, sim


def activity_of(task_text):
    words = str(task_text).split()
    first = re.sub(r"[^a-z]", "", words[0].lower()) if words else ""
    if first in ("maintain", "keep"):  # "maintain records" is documentation; "maintain order/equipment" is not
        return "document" if re.search(r"\b(records?|logs?|files?|reports?|documentation)\b", str(task_text), re.I) else "perform"
    return VERB_TO_ACTIVITY.get(first, "perform")


def practice_tasks(cip, targets, eligible, sim, tasks, kim, sim_, major_know, major_skills):
    pool = list(targets)
    for o in sorted([o for o in eligible if o not in pool], key=lambda o: -sim(o[0])):
        if len(pool) >= 3:
            break
        pool.append(o)
    queues = {}
    for s, _ in pool:
        t = tasks[tasks["O*NET-SOC Code"] == s]
        core = t[t["Task Type"] == "Core"]
        queues[s] = (core if not core.empty else t).sort_values("Task ID").to_dict("records")
    picked, used_acts, used_ids = [], set(), set()
    while len(picked) < PRACTICE_PER_MAJOR and any(queues.values()):
        for s, title in pool:
            if len(picked) >= PRACTICE_PER_MAJOR or not queues[s]:
                continue
            q = queues[s]
            idx = next((i for i, r in enumerate(q) if activity_of(r["Task"]) not in used_acts), 0)
            r = q.pop(idx)
            if int(r["Task ID"]) in used_ids:
                continue
            act = activity_of(r["Task"])
            used_acts.add(act); used_ids.add(int(r["Task ID"]))
            if len(used_acts) == len(PROMPTS):
                used_acts.clear()
            k = [e for e, _ in top_elements(kim, [s], 2)] or [e for e, _ in major_know[:2]]
            k = (k + ["the major's core knowledge"] * 2)[:2]
            act_skills = {"communicate": ["Speaking", "Active Listening"], "document": ["Writing"]}.get(act)
            pool_sk = sim_[sim_["Element Name"].isin(act_skills)] if act_skills else sim_
            sk = [e for e, _ in top_elements(pool_sk, [s], 1)] or [e for e, _ in major_skills[:1]] or ["Speaking"]
            prompt, crit3 = PROMPTS[act]
            n = len(picked) + 1
            picked.append({
                "practice_id": f"{cip}-P{n}",
                "cip_code": cip,
                "onet_soc_code": s,
                "occupation_title": title,
                "onet_task_id": int(r["Task ID"]),
                "onet_task_type": r["Task Type"] if isinstance(r["Task Type"], str) else None,
                "onet_task_url": ONLINE + s,
                "activity_type": act,
                "knowledge_elements": k,
                "skill_element": sk[0],
                "label": PRACTICE_LABEL,
                "ownership_class": "synthetic_generated_by_dreamco",
                "prompt": (f"{PRACTICE_LABEL}. Theme: O*NET task {int(r['Task ID'])} for `{s}` ({title}); read the task "
                           f"statement on O*NET OnLine ({ONLINE}{s}). " + prompt.format(k1=k[0], k2=k[1], s=sk[0])),
                "rubric": [
                    {"criterion": "Task alignment", "description": f"The response addresses the work activity of O*NET task {int(r['Task ID'])} for {s} (grader checks against the O*NET task statement).", "points": 2},
                    {"criterion": "Knowledge use", "description": f"{k[0]} and {k[1]} concepts are applied accurately and specifically, not just named.", "points": 2},
                    {"criterion": crit3.split(":")[0].format(s=sk[0]), "description": crit3.split(": ", 1)[1], "points": 2},
                ],
            })
    return picked


def plan_md(cip, title, stem, occs, zones, zref, know, skills, targets, tzone, basis, tasks_for_plan, tknow):
    zname = lambda z: zref.get(z, {}).get("Name", f"Job Zone {z}") if z else "no Job Zone rating"
    L = [f"# Study plan: {title} (CIP {cip})", "",
         "## Linked O*NET occupations (with O*NET 31.0 Job Zone)", ""]
    L += [f"- `{s}` {t} ({'Job Zone ' + ('1-2' if zones.get(s) == 2 else str(zones[s])) if s in zones else 'no Job Zone rating'})" for s, t in occs]
    L += ["", "## Most important knowledge areas (O*NET importance, 1 to 5, averaged over linked occupations)", ""]
    L += [f"- {k} ({v})" for k, v in know] or ["- No O*NET knowledge ratings for these occupations."]
    L += ["", "## Most important foundational skills (O*NET 31.0 Essential Skills importance, 1 to 5)", ""]
    L += [f"- {k} ({v})" for k, v in skills] or ["- No O*NET skill ratings for these occupations."]
    L += ["", "## Entry-level targets (DreamCo selection from O*NET 31.0 Job Zones)", ""]
    L += [f"- `{s}` {t} ({zname(zones.get(s))})" for s, t in targets]
    L += ["", f"Selection rule: {basis}."]
    k = [x[0] for x in know]; s = [x[0] for x in skills]
    year3 = [e for e in tknow if e not in k[:3]][:3] or k[3:6]
    study = lambda e: f"{e} ({KNOWLEDGE_STUDY.get(e, 'related coursework')})"
    practice = lambda e: f"{e} ({SKILL_PRACTICE.get(e, 'deliberate practice')})"
    tnames = "; ".join(t for _, t in targets) or "a linked occupation"
    L += ["", "## 4-year outline (DreamCo-derived guidance, not O*NET data)", "",
          f"1. Year 1, foundations. General education plus deliberate practice in the top-rated skills: "
          f"{'; '.join(practice(e) for e in s[:3]) or 'core skills'}.",
          f"2. Year 2, core knowledge. Build the highest-rated knowledge areas for this major: "
          f"{'; '.join(study(e) for e in k[:3]) or 'the major core'}.",
          f"3. Year 3, depth toward the entry targets. Prioritize knowledge rated highest for {tnames}: "
          f"{'; '.join(study(e) for e in year3) or 'major electives'}. Keep building "
          f"{'; '.join(practice(e) for e in s[3:5]) or 'applied skills'} through project work.",
          f"4. Year 4, launch. Internship or capstone aimed at {tnames}; build a portfolio from the practice tasks below "
          f"that shows {', '.join(k[:2]) or 'major knowledge'}.",
          ""]
    counts = {}
    for so, _ in occs:
        counts[zones.get(so)] = counts.get(zones.get(so), 0) + 1
    dist = ", ".join(f"{counts[z]} in {zname(z)}" for z in sorted([z for z in counts if z], reverse=True))
    if counts.get(None):
        dist += f", {counts[None]} with no Job Zone rating"
    grad = [(so, t) for so, t in occs if zones.get(so) == 5 and "All Other" not in t and (so, t) not in targets][:3]
    lead = [t for st, t in occs if re.search(r"Manager|Chief|Director|Supervisor|Treasurers", t) and (st, t) not in targets][:3]
    L += ["## Typical next steps (DreamCo-derived guidance using O*NET 31.0 Job Zone data)", "",
          f"- Linked occupations by Job Zone: {dist}."]
    if tzone:
        L += [f"- Entry targets are {zname(tzone)}; O*NET describes this zone's education as: "
              f"\"{zref.get(tzone, {}).get('Education', '')}\""]
    if grad:
        L += [f"- Graduate or professional paths ({zname(5)}; O*NET: \"{zref.get(5, {}).get('Education', '')}\"): "
              + "; ".join(f"`{so}` {t}" for so, t in grad) + "."]
    if lead:
        L += [f"- Leadership titles such as {'; '.join(lead)} are linked to this major but are not treated as entry targets here."]
    L += [f"- Before choosing Year 3 electives, compare the task lists of the entry targets on O*NET OnLine "
          f"({', '.join(ONLINE + so for so, _ in targets)})."]
    L += ["", "## Practice tasks (DreamCo-original practice prompts tied to O*NET 31.0 task IDs)", "",
          "Each item references an O*NET task by ID and occupation code only; read the task statement at the linked "
          "O*NET OnLine page. Prompts and rubrics are DreamCo-original. Machine-readable copy: `data/practice_tasks.json`.", ""]
    for p in tasks_for_plan:
        L += [f"### {p['practice_id']}. `{p['onet_soc_code']}` {p['occupation_title']}, O*NET task {p['onet_task_id']} ({p['activity_type']})", "",
              p["prompt"], "", "Rubric (0 to 2 points each):", ""]
        L += [f"- {c['criterion']}: {c['description']}" for c in p["rubric"]]
        L += [""]
    L += [f"Machine-readable provenance and license gate: `study_plans/{stem}/provenance.json`, `study_plans/{stem}/license_gate.json`.",
          "", PROVENANCE]
    return "\n".join(L)


def provenance_record(cip, title, stem, plan_path, json_path, pins, n_occs, targets, n_tasks):
    build_sha = sha256(ROOT / "build.py")
    md_sha = sha256(plan_path)
    def files(sid):
        return [{"name": n, "url": u, "sha256": pins[n][0]} for n, (s, u) in SOURCE_FILES.items() if s == sid]
    db_notices = [
        "This page includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license.",
        "O*NET\u00ae is a trademark of USDOL/ETA.",
        "DreamCo has modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications."]
    common = {"license": "CC BY 4.0", "license_url": CC_BY, "ownership_class": "open_license_with_conditions",
              "commercial_use_allowed": True, "redistribution_allowed": True, "ai_training_allowed": True,
              "attribution_required": True, "share_alike_required": False}
    publisher = "U.S. Department of Labor, Employment and Training Administration (USDOL/ETA)"
    sources = [
        {"source_id": "onet_db_31_0", "title": "O*NET 31.0 Database (CSV): occupations, knowledge, essential skills",
         "publisher": publisher, "url": DB_URL, "version": ONET_VERSION, "files": files("onet_db_31_0"),
         "retrieved_at": pins["knowledge.csv"][1], **common, "required_notices": db_notices,
         "restrictions": ["Use 'O*NET' only as an adjective; do not imply USDOL/ETA endorsement."]},
        {"source_id": "onet_db_31_0_jobzones_tasks", "title": "O*NET 31.0 Database (CSV): job zones, job zone reference, task statements",
         "publisher": publisher, "url": DB_URL, "version": ONET_VERSION, "files": files("onet_db_31_0_jobzones_tasks"),
         "retrieved_at": pins["task_statements.csv"][1], **common, "required_notices": db_notices,
         "restrictions": ["Use 'O*NET' only as an adjective; do not imply USDOL/ETA endorsement.",
                          "Task statements are referenced by Task ID only; their text is not reproduced or relabeled as DreamCo-owned."]},
        {"source_id": "onet_cip_soc_crosswalk", "title": "CIP 2020 to O*NET-SOC 2019 crosswalk (Education_CIP_to_ONET_SOC.xlsx)",
         "publisher": publisher + "; O*NET Resource Center Crosswalk Files, based on NCES CIP 2020",
         "url": CROSSWALK_URL, "version": "CIP 2020 to O*NET-SOC 2019 (sha256-pinned; the file states no revision date)",
         "sha256": pins["Education_CIP_to_ONET_SOC.xlsx"][0], "retrieved_at": pins["Education_CIP_to_ONET_SOC.xlsx"][1],
         **common, "required_notices": ["Crosswalk Files by USDOL/ETA, licensed under CC BY 4.0."], "restrictions": []},
    ]
    o = "open_license_with_conditions"; d = "synthetic_generated_by_dreamco"
    attribution = PROVENANCE.split("**Provenance.** ", 1)[1].strip()
    return {
        "schema": "dreamco.data_package_asset_provenance.v1",
        "asset_id": asset_id(cip, title),
        "title": f"Study plan: {title} (CIP {cip})",
        "evidence_id": f"edu-career-pathways-{cip}-onet{ONET_VERSION}-{pins['task_statements.csv'][1]}",
        "capability_id": "career-pathway-study-plan",
        "source_type": "onet",
        "source_reference": DB_URL,
        "retrieved_at": pins["task_statements.csv"][1],
        "content_version": f"O*NET {ONET_VERSION} (db_31_0_csv); CIP 2020 to O*NET-SOC 2019 crosswalk",
        "license_or_usage_basis": ("CC BY 4.0 for the O*NET 31.0 Database and O*NET Crosswalk Files (USDOL/ETA), which allows "
                                   "commercial use and redistribution with attribution; the outline, next steps, and practice "
                                   "prompts are DreamCo-original synthesis (owner approval for sale pending)"),
        "transformation": "derived_metric",
        "evaluator_version": f"edu-career-pathways build.py sha256:{build_sha}",
        "integrity_hash": f"sha256:{md_sha}",
        "ownership_class": o,
        "creator": "DreamCo (Grok-Edu-Career-Pathways, build.py)",
        "owner": ("Mixed: O*NET-derived values, occupation titles, Job Zone names/descriptions, and task IDs are USDOL/ETA "
                  "content under CC BY 4.0; the outline, next-steps wording, and practice prompts/rubrics are DreamCo-original"),
        "asset_files": [{"path": f"study_plans/{stem}.md", "sha256": md_sha, "bytes": plan_path.stat().st_size},
                        {"path": f"study_plans/{stem}/plan.json", "sha256": sha256(json_path), "bytes": json_path.stat().st_size}],
        "sources": sources,
        "derived_components": [
            {"component": "linked_occupations", "ownership_class": o, "derivation_type": "structured_extraction",
             "description": f"{n_occs} O*NET-SOC codes/titles linked to CIP {cip} in the crosswalk, filtered to codes in O*NET 31.0 occupation_data.csv, with each code's O*NET 31.0 Job Zone.",
             "derived_from": ["onet_cip_soc_crosswalk", "onet_db_31_0", "onet_db_31_0_jobzones_tasks"]},
            {"component": "knowledge_and_skill_importance", "ownership_class": o, "derivation_type": "derived_metric",
             "description": "Top-8 knowledge and top-6 Essential Skills by unweighted mean O*NET 31.0 importance (Scale IM) across linked occupations.",
             "derived_from": ["onet_db_31_0"]},
            {"component": "entry_targets", "ownership_class": o, "derivation_type": "derived_metric",
             "description": f"{len(targets)} entry target(s) chosen by a DreamCo rule: Job Zone 4 first (fallback 3, 5, 1-2), excluding Manager/Chief/Postsecondary/All Other/Supervisor/Director titles, base .00 codes first, then ranked by Pearson correlation of knowledge-importance profiles.",
             "derived_from": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "linked_occupations"]},
            {"component": "four_year_outline", "ownership_class": d, "derivation_type": "synthetic_data",
             "description": "DreamCo-original synthesis: outline text keyed to this major's top knowledge/skills and entry targets; embeds O*NET element and occupation names, so O*NET attribution still applies.",
             "derived_from": ["knowledge_and_skill_importance", "entry_targets"]},
            {"component": "typical_next_steps", "ownership_class": d, "derivation_type": "synthetic_data",
             "description": "DreamCo-original synthesis summarizing linked occupations by Job Zone; quotes O*NET 31.0 Job Zone names and education descriptions with attribution.",
             "derived_from": ["linked_occupations", "onet_db_31_0_jobzones_tasks"]},
            {"component": "practice_tasks", "ownership_class": d, "derivation_type": "original_evaluation",
             "description": f"{n_tasks} DreamCo-original practice prompts with 3-criterion rubrics, each tied to an O*NET 31.0 Task ID and O*NET-SOC code of a linked occupation; O*NET task text is not reproduced (only its first verb is used to choose the prompt type).",
             "derived_from": ["onet_db_31_0_jobzones_tasks", "entry_targets"]},
        ],
        "transformation_history": [
            {"step": "fetch and verify pinned sources (sha256 vs raw/SOURCES.md)", "tool": "edu-career-pathways/fetch_sources.py",
             "tool_version": f"sha256:{sha256(ROOT / 'fetch_sources.py')}", "inputs": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "onet_cip_soc_crosswalk"]},
            {"step": "crosswalk join, importance aggregation, Job Zone entry targeting, outline, practice tasks, markdown render",
             "tool": "edu-career-pathways/build.py", "tool_version": f"sha256:{build_sha}",
             "inputs": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "onet_cip_soc_crosswalk"]},
        ],
        "attribution_text": attribution,
        "review_status": "unreviewed",
        "human_review": None,
        "notes": [
            "retrieved_at values are dates only because raw/SOURCES.md records only download dates (America/Chicago).",
            "Two O*NET 31.0 source entries exist because the job zone and task files were downloaded on a later date than the others.",
            "O*NET 31.0 split Skills into Essential Skills and Transferable Skills; this asset uses Essential Skills only.",
            "Owner approval is pending; it is never set by build.py.",
        ],
    }


def candidate_record(cip, title, n_occs, n_tasks):
    return {
        "candidate_id": asset_id(cip, title),
        "asset_id": asset_id(cip, title),
        "title": f"Study plan: {title} (CIP {cip}) mapped to O*NET occupations",
        "description": (f"One markdown study plan: {n_occs} linked O*NET-SOC occupations with Job Zones, top knowledge and "
                        f"Essential Skills by mean O*NET 31.0 importance, 1-3 Job Zone-based entry targets, a DreamCo 4-year "
                        f"outline and next steps, and {n_tasks} DreamCo-original practice prompts tied to O*NET task IDs."),
        "category": "education/career-pathways",
        "data_types": ["markdown"],
        "rights_basis": "CC BY 4.0 (O*NET 31.0 Database + O*NET Crosswalk Files, USDOL/ETA); DreamCo-original outline and practice prompts",
        "ownership_class": "open_license_with_conditions",
        "commercial_use_allowed": True,
        "redistribution_allowed": True,
        "rights_declarations": {
            "onet_content": "CC BY 4.0: commercial use and redistribution allowed with attribution; notices kept in the plan footer.",
            "dreamco_original_synthesis": "4-year outline, next steps, practice prompts and rubrics (ownership_class synthetic_generated_by_dreamco); DreamCo may use and redistribute commercially, subject to owner approval for sale.",
        },
        "flags": [],
        "provenance_path": "provenance.json",
        "asset_path": "asset.json",
        "scorecard_score": None,
        "owner_approval": None,
        "owner_approval_status": "pending",
    }


def asset_record(cip, title, stem, prov, entry, n_occs, excluded):
    """Plan 5.2 synthesis asset record (schemas/data_package_synthesis_asset.schema.json)."""
    md, js = prov["asset_files"][0], prov["asset_files"][1]
    tz = sorted({t["job_zone"] for t in entry["entry_targets"] if t["job_zone"]})
    return {
        "schema": "dreamco.data_package_synthesis_asset.v1",
        "asset_id": prov["asset_id"],
        "title": prov["title"],
        "capability_ids": ["career-pathway-study-plan"],
        "perspectives_used": ["official_documentation"],
        "source_refs": [{"source_id": src["source_id"], "version": src["version"], "pinned_by": "provenance.json#sources",
                         "perspective": "official_documentation"} for src in prov["sources"]],
        "ownership_class": prov["ownership_class"],
        "commercial_redistribution_allowed": True,
        "attribution_required": True,
        "share_alike_required": False,
        "human_layer": {"path": md["path"], "format": "markdown", "sha256": md["sha256"],
                        "elements": ["linked occupations with Job Zones", "key knowledge areas", "key Essential Skills",
                                     "entry-level targets", "4-year outline", "typical next steps", "practice tasks with rubrics"]},
        "machine_layer": {"path": js["path"], "format": "json", "sha256": js["sha256"],
                          "elements": ["occupations", "top_knowledge", "top_skills", "entry_targets", "practice_tasks", "rubrics"]},
        "dreamco_analysis": {
            "agree": [f"All {n_occs} crosswalk links for CIP {cip} resolve to O*NET 31.0 occupation codes (tests check this).",
                      f"Entry targets are O*NET Job Zone {', '.join('1-2' if z == 2 else str(z) for z in tz) or 'unrated'} linked occupations: "
                      + "; ".join(t["title"] for t in entry["entry_targets"]) + "."],
            "reject": [f"Not used as entry targets (leadership, faculty, or residual titles): {'; '.join(excluded)}."] if excluded else [],
            "improve": ["Knowledge and skill importance is an unweighted mean over all linked occupations, so leadership and faculty roles still shape the top-knowledge list.",
                        "Course suggestions in the outline are generic DreamCo guidance per O*NET knowledge area, not institution-specific curricula."],
            "still_need_test": ["Practice prompts and rubrics have not been piloted with learners or scored by human graders.",
                                "No sandbox, benchmark, holdout, or regression evaluation of the plan exists yet.",
                                "DreamCo-original text has not had owner or human review."],
        },
        "validation_evidence_ids": {"sandbox": [], "benchmark": [], "holdout": [], "regression": []},
        "integrity_hash": prov["integrity_hash"],
        "created_at": __import__("datetime").date.today().isoformat(),
        "generator_version": prov["evaluator_version"],
        "notes": [
            "dreamco_analysis is generated by build.py from build facts; it is not a human review.",
            "validation_evidence_ids are empty: evidence/pytest.txt is a build-integrity test run, not sandbox, benchmark, holdout, or regression evidence.",
            "perspectives_used has one entry: O*NET and the crosswalk are both official USDOL/ETA sources (closest policy perspective: official_documentation).",
        ],
    }


def find_gate_tool():
    cands = [os.environ.get("DREAMCO_GATE_TOOL"), ROOT.parents[1] / "tools" / "license_provenance_gate.py",
             "/workspace/dp-merchant/tools/license_provenance_gate.py"]
    for c in cands:
        if c and pathlib.Path(c).is_file():
            return pathlib.Path(c)
    return None


def main():
    pins = load_pins()
    DATA.mkdir(exist_ok=True); PLANS.mkdir(exist_ok=True)
    for p in PLANS.glob("*.md"): p.unlink()
    cw = load_crosswalk()
    occ = pd.read_csv(RAW / "occupation_data.csv", dtype=str)
    valid = set(occ["O*NET-SOC Code"])
    kim, sim_ = load_im(RAW / "knowledge.csv"), load_im(RAW / "essential_skills.csv")
    jz = pd.read_csv(RAW / "job_zones.csv", dtype={"O*NET-SOC Code": str})
    zones = dict(zip(jz["O*NET-SOC Code"], jz["Job Zone"].astype(int)))
    zref = {int(r["Job Zone"]): r for r in pd.read_csv(RAW / "job_zone_reference.csv").to_dict("records")}
    tasks = pd.read_csv(RAW / "task_statements.csv", dtype={"O*NET-SOC Code": str})
    gate = find_gate_tool()
    sel, rows, all_tasks, built = [], [], [], []
    for cip in MAJORS:
        sub = cw[(cw.cip == cip) & (cw.soc.isin(valid))]
        if sub.empty:
            continue
        title = sub.cip_title.iloc[0].strip().rstrip(".")
        stem = f"{cip}_{slug(title)}"
        occs = list(dict.fromkeys(zip(sub.soc, sub.soc_title.str.strip())))
        socs = [o[0] for o in occs]
        know = top_elements(kim, socs, 8)
        skills = top_elements(sim_, socs, 6)
        targets, tzone, basis, eligible, sim = rank_entry_targets(occs, zones, kim)
        tknow = [e for e, _ in top_elements(kim, [s for s, _ in targets], 6)]
        ptasks = practice_tasks(cip, targets, eligible, sim, tasks, kim, sim_, know, skills)
        all_tasks += ptasks
        for s, t in occs:
            rows.append([cip, title, s, t])
        sel.append({"cip": cip, "title": title, "asset_id": asset_id(cip, title),
                    "occupations": [{"soc": s, "title": t, "job_zone": zones.get(s)} for s, t in occs],
                    "top_knowledge": know, "top_skills": skills,
                    "entry_targets": [{"soc": s, "title": t, "job_zone": zones.get(s)} for s, t in targets],
                    "entry_target_basis": basis,
                    "practice_task_ids": [p["practice_id"] for p in ptasks]})
        plan = PLANS / f"{stem}.md"
        plan.write_text(plan_md(cip, title, stem, occs, zones, zref, know, skills, targets, tzone, basis, ptasks, tknow))
        side = PLANS / stem
        side.mkdir(exist_ok=True)
        pj = side / "plan.json"
        pj.write_text(json.dumps({**sel[-1], "label": "O*NET 31.0-derived fields plus DreamCo-original practice tasks",
                                  "practice_tasks": ptasks}, indent=2) + "\n")
        prov = provenance_record(cip, title, stem, plan, pj, pins, len(occs), targets, len(ptasks))
        (side / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
        excluded = [t for s_, t in occs if (EXCLUDE_STRICT.search(t) or EXCLUDE_SOFT.search(t)) and (s_, t) not in targets]
        (side / "asset.json").write_text(json.dumps(asset_record(cip, title, stem, prov, sel[-1], len(occs), excluded), indent=2) + "\n")
        (side / "candidate.json").write_text(json.dumps(candidate_record(cip, title, len(occs), len(ptasks)), indent=2) + "\n")
        built.append(stem)
    with open(DATA / "major_to_onet.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cip_code", "cip_title", "onet_soc_code", "occupation_title"]); w.writerows(rows)
    (DATA / "majors_selected.json").write_text(json.dumps(sel, indent=2) + "\n")
    (DATA / "practice_tasks.json").write_text(json.dumps({
        "label": PRACTICE_LABEL,
        "ownership_class": "synthetic_generated_by_dreamco",
        "onet_version": ONET_VERSION,
        "note": ("Prompts and rubrics are DreamCo-original. Each item references an O*NET 31.0 Task ID and O*NET-SOC code "
                 "(task_statements.csv, CC BY 4.0, USDOL/ETA); O*NET task text is not reproduced. O*NET\u00ae is a trademark of USDOL/ETA."),
        "tasks": all_tasks}, indent=2) + "\n")
    gated = 0
    if gate:
        for stem in built:
            r = subprocess.run([sys.executable, str(gate), f"study_plans/{stem}", "--asset-root", ".",
                                "--out", f"study_plans/{stem}/license_gate.json"], cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 2:
                raise SystemExit(f"gate error for {stem}: {r.stderr}")
            gated += 1
    else:
        print("WARNING: tools/license_provenance_gate.py not found (set DREAMCO_GATE_TOOL); license_gate.json not regenerated")
    print(f"majors={len(sel)} links={len(rows)} practice_tasks={len(all_tasks)} gated={gated} gate_tool={gate}")


if __name__ == "__main__":
    main()
