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
import collections, csv, hashlib, json, math, os, re, pathlib, subprocess, sys
import pandas as pd
import snowballstemmer

ROOT = pathlib.Path(__file__).resolve().parent
RAW, DATA, PLANS, AUTH = ROOT / "raw", ROOT / "data", ROOT / "study_plans", ROOT / "authored"
AUTHORED_FILES = ["practice_tasks_authored.json", "outline_topics.json", "target_overrides.json", "coverage_rules.json"]
EVIDENCE = DATA / "dreamco_knowledge" / "evidence"
# Fixed release timestamp (ISO 8601 with offset) so rebuilds are reproducible (override with DREAMCO_BUILD_TIMESTAMP).
BUILD_TIMESTAMP = os.environ.get("DREAMCO_BUILD_TIMESTAMP", "2026-10-02T18:30:00-05:00")
EVIDENCE_ROOT = "study_packs/career_pathways/data/dreamco_knowledge/evidence"
# Root of the Dreamcobots checkout that contains study_packs/career_pathways (the gate resolves evidence ids under it).
# Default: two levels above this pack, which is the repo root when the pack sits at <repo>/study_packs/career_pathways.
REPO_ROOT = pathlib.Path(os.environ.get("DREAMCO_REPO_ROOT") or pathlib.Path(__file__).resolve().parents[2]).resolve()
# Ownership classes from most to least restrictive (config/buddy-training-data-provenance-policy.json lists the classes
# but does not rank them; this order ranks by the conditions attached to use). A file mixing classes takes the most restrictive.
OWNERSHIP_RESTRICTIVENESS = ["unknown_do_not_publish", "third_party_reference_only", "licensed_for_use",
                             "open_license_with_conditions", "user_contributed_with_permission",
                             "public_domain_or_publicly_reusable", "synthetic_generated_by_dreamco",
                             "dreamco_commissioned_with_assignment", "dreamco_owned"]


def most_restrictive(classes):
    return min(set(classes), key=OWNERSHIP_RESTRICTIVENESS.index)
AUTHORSHIP = "DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed"
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

# Generic fallback guidance per O*NET knowledge element. NOT used for authored-tier majors (they use
# authored/outline_topics.json); kept only for a possible generated tier.
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
# Generic fallback practice habit per O*NET 31.0 Essential Skill (same restriction as above).
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


def load_authored():
    """Load the checked-in DreamCo-authored sources (authored/*.json)."""
    pt = json.loads((AUTH / "practice_tasks_authored.json").read_text())
    ot = json.loads((AUTH / "outline_topics.json").read_text())
    tov = json.loads((AUTH / "target_overrides.json").read_text())
    by_cip = {}
    for t in pt["tasks"]:
        by_cip.setdefault(t["practice_id"].rsplit("-P", 1)[0], []).append(t)
    return by_cip, ot["majors"], tov


def apply_target_override(cip, occs, zones, targets, basis, tov):
    """Replace rule-based targets with a documented manual override from authored/target_overrides.json."""
    o = tov["overrides"].get(cip)
    if not o:
        note = tov["reviewed_without_change"].get(cip)
        return targets, basis, ({"type": "reviewed_without_change", "note": note} if note else None)
    titles = dict(occs)
    new = []
    for soc in o["targets"]:
        if soc not in titles:
            raise SystemExit(f"target override {cip}: {soc} is not a crosswalk-linked occupation")
        if soc not in zones:
            raise SystemExit(f"target override {cip}: {soc} has no O*NET 31.0 Job Zone")
        if EXCLUDE_STRICT.search(titles[soc]):
            raise SystemExit(f"target override {cip}: {titles[soc]} is a Manager/Chief/Postsecondary/All Other title")
        new.append((soc, titles[soc]))
    rule = [s for s, _ in targets]
    basis = basis + ("; then a documented DreamCo manual override (authored/target_overrides.json) changed the rule output "
                     f"({', '.join(rule)}) to {', '.join(o['targets'])}")
    return new, basis, {"type": "override", "rule_output": rule, "targets": o["targets"], "reason": o["reason"]}


def practice_tasks(cip, occs, tasks, authored):
    """Authored-tier practice tasks: DreamCo-original scenario prompts from authored/practice_tasks_authored.json,
    each validated against O*NET 31.0 task_statements.csv (Task ID must belong to the cited, crosswalk-linked SOC)."""
    titles = dict(occs)
    ts = tasks.set_index("Task ID")
    out = []
    for a in authored.get(cip, []):
        tid, soc = int(a["onet_task_id"]), a["onet_soc_code"]
        if soc not in titles:
            raise SystemExit(f"{a['practice_id']}: {soc} is not linked to CIP {cip}")
        if tid not in ts.index or ts.loc[tid, "O*NET-SOC Code"] != soc:
            raise SystemExit(f"{a['practice_id']}: task {tid} does not belong to {soc} in O*NET 31.0")
        ttype = ts.loc[tid, "Task Type"]
        out.append({
            "practice_id": a["practice_id"],
            "cip_code": cip,
            "tier": "authored",
            "onet_soc_code": soc,
            "occupation_title": titles[soc],
            "onet_task_id": tid,
            "onet_task_type": ttype if isinstance(ttype, str) else None,
            "onet_task_url": ONLINE + soc,
            "format": a["format"],
            "task_intent": a["task_intent"],
            "task_intent_note": "DreamCo paraphrase of the cited O*NET task's purpose, in original wording; not O*NET text.",
            "label": PRACTICE_LABEL,
            "authorship": AUTHORSHIP,
            "ownership_class": "synthetic_generated_by_dreamco",
            "license": item_license("authored"),
            "prompt": f"{PRACTICE_LABEL}. {a['prompt']}",
            "rubric": a["rubric"],
            "reference_answer_outline": a["reference_answer_outline"],
        })
    if len(out) != PRACTICE_PER_MAJOR:
        raise SystemExit(f"CIP {cip}: expected {PRACTICE_PER_MAJOR} authored practice tasks, found {len(out)}")
    return out


# DreamCo-original wording per O*NET Job Zone number (cites the zone number only; O*NET Job Zone text is not quoted).
ZONE_GUIDANCE = {
    5: ("Job Zone 5 roles generally expect study beyond the bachelor's degree: a master's, a doctorate, or a professional "
        "degree such as the Pharm.D., J.D. or M.D., usually with supervised practice and a license where the field requires one."),
    4: ("For Job Zone 4 roles, DreamCo treats the bachelor's degree as the usual starting credential; in practice employers "
        "also weigh internships, co-ops, research or a project portfolio, and some roles add a license or certification."),
    3: ("Job Zone 3 roles are commonly entered with an associate degree, vocational training or relevant work history, so a "
        "bachelor's graduate should still plan on gaining hands-on experience in the field."),
    2: ("Job Zone 1-2 roles typically need a high school diploma and short on-the-job training; a degree is not the usual entry route."),
}


def zl(z):
    return "1-2" if z == 2 else str(z)


def next_steps_lines(L, occs, zones, targets, lead_line=True):
    counts = {}
    for so, _ in occs:
        counts[zones.get(so)] = counts.get(zones.get(so), 0) + 1
    dist = ", ".join(f"{counts[z]} in Job Zone {zl(z)}" for z in sorted([z for z in counts if z], reverse=True))
    if counts.get(None):
        dist += f", {counts[None]} with no Job Zone rating"
    grad = [(so, t) for so, t in occs if zones.get(so) == 5 and "All Other" not in t and (so, t) not in targets][:3]
    lead = [t for st, t in occs if re.search(r"Manager|Chief|Director|Supervisor|Treasurers", t) and (st, t) not in targets][:3]
    tz = sorted({zones[so] for so, _ in targets if so in zones}, reverse=True)
    L += ["## Typical next steps (DreamCo guidance; cites O*NET 31.0 Job Zone numbers only)", "",
          f"- Linked occupations by O*NET Job Zone: {dist}."]
    for z in tz:
        L += [f"- Entry targets in Job Zone {zl(z)}: {ZONE_GUIDANCE[z]}"]
    if grad:
        L += [f"- Graduate or professional paths (Job Zone 5): " + "; ".join(f"`{so}` {t}" for so, t in grad) + "."]
    if lead and lead_line:
        L += [f"- Leadership titles such as {'; '.join(lead)} are linked to this major but are not treated as entry targets here; "
              "they usually follow several years of experience."]


def plan_md(cip, title, stem, occs, zones, ctx, targets, basis, tasks_for_plan, topics, review):
    zlabel = lambda z: f"Job Zone {zl(z)}" if z else "no Job Zone rating"
    L = [f"# Study plan: {title} (CIP {cip})", "",
         "Tier: **authored**. The outline course topics, entry-target review, next-steps wording, and practice tasks for this "
         f"major were written for it specifically ({AUTHORSHIP}).", "",
         "## Linked O*NET occupations (with O*NET 31.0 Job Zone)", ""]
    L += [f"- `{s}` {t} ({zlabel(zones.get(s))})" for s, t in occs]
    knowledge_lines(L, ctx["know_w"], ctx["skills_w"], ctx["know"], ctx["skills"], len(ctx["weights"]), len(occs))
    L += ["", "## Entry-level targets (DreamCo selection from O*NET 31.0 Job Zones)", ""]
    L += [f"- `{s}` {t} ({zlabel(zones.get(s))})" for s, t in targets]
    L += ["", f"Selection rule: {basis}."]
    if review and review["type"] == "override":
        L += ["", f"Manual override reason (DreamCo review): {review['reason']}"]
    elif review:
        L += ["", f"DreamCo target review (no change): {review['note']}"]
    op = ctx["outline"]
    def topic(kind, e):
        try:
            return topics[kind][e]
        except KeyError:
            raise SystemExit(f"authored/outline_topics.json has no {kind} mapping for CIP {cip} element '{e}'")
    study = lambda e: f"{e} ({topic('knowledge', e)})"
    practice = lambda e: f"{e} ({topic('skills', e)})"
    tnames = "; ".join(t for _, t in targets) or "a linked occupation"
    gened = f"General education, including {study(op['year1_knowledge'][0])}, plus" if op["year1_knowledge"] else "General education plus"
    L += ["", "## 4-year outline (DreamCo-derived guidance, not O*NET data)", "",
          f"1. Year 1, foundations. {gened} deliberate practice in the top-rated skills: "
          f"{'; '.join(practice(e) for e in op['year1_skills']) or 'core skills'}.",
          f"2. Year 2, core knowledge. Build the highest-rated knowledge areas for this major: "
          f"{'; '.join(study(e) for e in op['year2_knowledge']) or 'the major core'}.",
          f"3. Year 3, depth toward the entry targets ({tnames}): "
          f"{'; '.join(study(e) for e in op['year3_knowledge']) or 'major electives'}. Keep building "
          f"{'; '.join(practice(e) for e in op['year3_skills']) or 'applied skills'} through project work.",
          f"4. Year 4, launch. Internship or capstone aimed at {tnames}; build a portfolio from the practice tasks below "
          f"that shows {', '.join(op['year2_knowledge'][:2]) or 'major knowledge'}.",
          ""]
    skipped_lines(L, op, ctx["know_w"])
    next_steps_lines(L, occs, zones, targets)
    L += [f"- Before choosing Year 3 electives, compare the task lists of the entry targets on O*NET OnLine "
          f"({', '.join(ONLINE + so for so, _ in targets)})."]
    L += ["", "## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)", "",
          f"Authorship: {AUTHORSHIP}. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a "
          "DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET OnLine page). "
          "Scenarios marked invented are fictional; clinical, legal and financial items are practice material, not professional "
          "advice. Machine-readable copy: `data/practice_tasks.json`.", ""]
    for p in tasks_for_plan:
        L += [f"### {p['practice_id']}. `{p['onet_soc_code']}` {p['occupation_title']}, O*NET task {p['onet_task_id']} ({p['format']})", "",
              f"Work activity (DreamCo paraphrase): {p['task_intent']}", "",
              p["prompt"], "", "Rubric (0 to 2 points each):", ""]
        L += [f"- {c['criterion']}: {c['description']}" for c in p["rubric"]]
        L += ["", "Reference answer outline (what a strong answer includes):", ""]
        L += [f"- {x}" for x in p["reference_answer_outline"]]
        L += [""]
    L += [f"Machine-readable provenance and license gate: `study_plans/{stem}/provenance.json`, `study_plans/{stem}/license_gate.json`.",
          "", PROVENANCE]
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------
# Generated tier (Phase 3 coverage): majors beyond the 27 authored ones. Nothing below is individually authored.
GENERATED_AUTHORSHIP = ("DreamCo-generated by build.py from a fixed template (tier 'generated'); not individually authored, "
                        "not reviewed by a human or by an AI author")
GENERATED_LABEL = "DreamCo-generated practice exercise (template)"
GENERATED_FOOTER = ("In this generated-tier plan, each practice item quotes the cited O*NET 31.0 task statement verbatim, "
                    "with attribution (USDOL/ETA, CC BY 4.0); the quoted statements are O*NET content, not DreamCo-owned text.\n\n")


def load_coverage_rules():
    return json.loads((AUTH / "coverage_rules.json").read_text())


def select_majors(cw, valid, zones, rules):
    """Return ([(cip, tier)], coverage_rows). Authored majors first (fixed order), then generated majors by CIP code."""
    rx = re.compile(rules["exclude_title_regex"]["pattern"])
    sub = cw[cw.soc.isin(valid)]
    titles = sub.groupby("cip").cip_title.first()
    has45 = set(sub[sub.soc.map(zones).isin([4, 5])].cip)
    has_entry = set(sub[~sub.soc_title.str.strip().str.contains(EXCLUDE_STRICT)].cip)
    rows, gen = [], []
    for cip in sorted(set(cw.cip)):
        t = str(titles.get(cip, cw[cw.cip == cip].cip_title.iloc[0])).strip().rstrip(".")
        if cip in MAJORS:
            rows.append([cip, t, "authored", "included", "authored major"])
            continue
        if not re.fullmatch(r"\d\d\.\d{4}", cip):
            reason = "not a 6-digit CIP code"
        elif cip not in has45:
            reason = "no crosswalk link to an O*NET 31.0 occupation with Job Zone 4 or 5"
        elif cip[:2] in rules["exclude_series"]:
            reason = f"excluded series {cip[:2]}: " + rules["exclude_series"][cip[:2]]
        elif any(cip.startswith(p) for p in rules["exclude_prefixes"]):
            p = next(p for p in rules["exclude_prefixes"] if cip.startswith(p))
            reason = f"excluded prefix {p}: " + rules["exclude_prefixes"][p]
        elif rx.search(t):
            reason = "excluded by title rule: " + rules["exclude_title_regex"]["reason"]
        elif cip not in has_entry:
            reason = ("no possible entry target: every linked occupation is a Manager, Chief, Postsecondary-faculty or "
                      "All Other title, so a plan would have no entry-level role to aim at")
        else:
            reason = None
        if reason:
            rows.append([cip, t, "", "excluded", reason])
        else:
            rows.append([cip, t, "generated", "included", rules["include_rule"]])
            gen.append(cip)
    return [(c, "authored") for c in MAJORS] + [(c, "generated") for c in gen], rows


def generated_practice_tasks(cip, targets, eligible, sim, tasks, kim, know):
    """Six template exercises: up to 3 occupations (entry targets, then the most similar eligible linked occupations),
    Core tasks first in Task ID order, round robin, skipping supervisory/managerial task statements (is_supervisory)
    unless too few others exist. The O*NET task statement is quoted verbatim with attribution.
    Returns (tasks, dropped_supervisory_task_ids)."""
    pool = list(targets)
    for o in sorted([o for o in eligible if o not in pool], key=lambda o: -sim(o[0])):
        if len(pool) >= 3:
            break
        pool.append(o)
    recs = {}
    for s, _ in pool:
        t = tasks[tasks["O*NET-SOC Code"] == s]
        core = t[t["Task Type"] == "Core"]
        recs[s] = (core if not core.empty else t).sort_values("Task ID").to_dict("records")

    def pick(queues):
        out, used = [], set()
        while len(out) < PRACTICE_PER_MAJOR and any(queues.values()):
            for s, title in pool:
                if len(out) >= PRACTICE_PER_MAJOR or not queues[s]:
                    continue
                r = queues[s].pop(0)
                if int(r["Task ID"]) not in used:
                    used.add(int(r["Task ID"]))
                    out.append((s, title, r))
        return out
    unfiltered = pick({s: list(v) for s, v in recs.items()})
    filtered = {s: [r for r in v if not is_supervisory(r["Task"])] for s, v in recs.items()}
    if sum(len(v) for v in filtered.values()) < PRACTICE_PER_MAJOR:
        # not enough non-supervisory tasks: append supervisory ones after them (each item is flagged)
        filtered = {s: filtered[s] + [r for r in v if is_supervisory(r["Task"])] for s, v in recs.items()}
    chosen = pick(filtered)
    picked_ids = {int(r["Task ID"]) for _, _, r in chosen}
    dropped = [int(r["Task ID"]) for _, _, r in unfiltered if is_supervisory(r["Task"]) and int(r["Task ID"]) not in picked_ids]
    picked = []
    for s, title, r in chosen:
        k = [e for e, _ in top_elements(kim, [s], 2)] or [e for e, _ in know[:2]]
        k = (k + ["the field's core knowledge"] * 2)[:2]
        n = len(picked) + 1
        picked.append({
            "practice_id": f"{cip}-P{n}",
            "cip_code": cip,
            "tier": "generated",
            "onet_soc_code": s,
            "occupation_title": title,
            "onet_task_id": int(r["Task ID"]),
            "onet_task_type": r["Task Type"] if isinstance(r["Task Type"], str) else None,
            "onet_task_url": ONLINE + s,
            "onet_task_statement": str(r["Task"]).strip(),
            "onet_task_statement_note": "Quoted verbatim from O*NET 31.0 task_statements.csv (USDOL/ETA, CC BY 4.0); O*NET content, not DreamCo-owned.",
            "supervisory_task": is_supervisory(r["Task"]),
            "format": "applied exercise",
            "label": GENERATED_LABEL,
            "authorship": GENERATED_AUTHORSHIP,
            "ownership_class": "open_license_with_conditions",
            "license": item_license("generated"),
            "prompt": (f"{GENERATED_LABEL}. Assume you are in your first year in the occupation \"{title}\" and have been asked to carry out "
                       "the O*NET task quoted above for a small, realistic case that you define in two or three sentences. "
                       f"In about one page, explain what information you need first, the steps and methods you would use "
                       f"(apply {k[0]} and {k[1]}), and how you would check the result and report it."),
            "rubric": [
                {"criterion": "Task fit", "description": "The response performs the work in the quoted O*NET task statement for a concrete case with stated assumptions.", "points": 2},
                {"criterion": "Method", "description": f"The steps are specific and ordered, and they apply {k[0]} and {k[1]} correctly rather than only naming them.", "points": 2},
                {"criterion": "Check and report", "description": "The response says how the result would be verified (criteria, review or test) and how and to whom it would be reported.", "points": 2},
            ],
            "reference_answer_outline": [
                "A short, concrete case with its assumptions stated.",
                "The information or inputs needed before starting, and where they come from.",
                f"Ordered steps that use the occupation's actual methods or tools, drawing on {k[0]} and {k[1]}.",
                "A check of the result and a plan for communicating it to the right people.",
            ],
        })
    return picked, dropped


def plan_md_generated(cip, title, stem, occs, zones, ctx, targets, basis, ptasks, qf):
    zlabel = lambda z: f"Job Zone {zl(z)}" if z else "no Job Zone rating"
    L = [f"# Study plan: {title} (CIP {cip})", "",
         "Tier: **generated**. This plan was produced automatically by build.py from O*NET 31.0 data and fixed templates. "
         "Unlike the 27 authored plans, its outline topics, entry targets and practice exercises were not individually written "
         "or reviewed: the outline uses element names only, the entry targets are the unreviewed rule output, and the practice "
         "exercises are templates around quoted O*NET task statements.", ""]
    quality_lines(L, qf)
    L += ["## Linked O*NET occupations (with O*NET 31.0 Job Zone)", ""]
    L += [f"- `{s}` {t} ({zlabel(zones.get(s))})" for s, t in occs]
    knowledge_lines(L, ctx["know_w"], ctx["skills_w"], ctx["know"], ctx["skills"], len(ctx["weights"]), len(occs))
    L += ["", "## Entry-level targets (DreamCo rule output from O*NET 31.0 Job Zones; not manually reviewed)", ""]
    L += [f"- `{s}` {t} ({zlabel(zones.get(s))})" for s, t in targets]
    L += ["", f"Selection rule: {basis}. An automatic field-fit check was applied (see Quality flags); these targets have not "
          "been checked by a reviewer."]
    op = ctx["outline"]
    tnames = "; ".join(t for _, t in targets) or "a linked occupation"
    gened = "General education, including English Language, plus" if op["year1_knowledge"] else "General education plus"
    L += ["", "## 4-year outline (DreamCo-generated template, not O*NET data; element names only, no per-major course mapping)", "",
          f"1. Year 1, foundations. {gened} deliberate practice in the top-rated skills: {', '.join(op['year1_skills']) or 'core skills'}.",
          f"2. Year 2, core knowledge. Courses in the major that build the highest-rated knowledge areas: {', '.join(op['year2_knowledge']) or 'the major core'}.",
          f"3. Year 3, depth. Electives aimed at {tnames}, with further work in {', '.join(op['year3_knowledge']) or 'major electives'} "
          f"and applied practice in {', '.join(op['year3_skills']) or 'applied skills'}.",
          f"4. Year 4, launch. Internship or capstone aimed at {tnames}, with a portfolio drawn from the practice exercises below.",
          ""]
    skipped_lines(L, op, ctx["know_w"])
    next_steps_lines(L, occs, zones, targets, lead_line=False)
    L += [f"- Compare the task lists of the entry targets on O*NET OnLine ({', '.join(ONLINE + so for so, _ in targets)})."]
    L += ["", "## Practice exercises (generated template; quoted O*NET 31.0 task statements)", "",
          f"Authorship: {GENERATED_AUTHORSHIP}. Each exercise quotes one O*NET 31.0 task statement (USDOL/ETA, CC BY 4.0) and "
          "wraps it in the same DreamCo template prompt and rubric. Supervisory or managerial tasks are skipped where other "
          "tasks exist (see Quality flags). Machine-readable copy: `data/practice_tasks.json`.", ""]
    for p in ptasks:
        L += [f"### {p['practice_id']}. `{p['onet_soc_code']}` {p['occupation_title']}, O*NET task {p['onet_task_id']}", "",
              f"> O*NET 31.0 task statement (quoted verbatim, USDOL/ETA, CC BY 4.0): {p['onet_task_statement']}", "",
              p["prompt"], "", "Rubric (0 to 2 points each):", ""]
        L += [f"- {c['criterion']}: {c['description']}" for c in p["rubric"]]
        L += ["", "Reference answer outline:", ""]
        L += [f"- {x}" for x in p["reference_answer_outline"]]
        L += [""]
    L += [f"Machine-readable provenance and license gate: `study_plans/{stem}/provenance.json`, `study_plans/{stem}/license_gate.json`.",
          "", "---\n" + GENERATED_FOOTER + PROVENANCE[len("---\n"):]]
    return "\n".join(L)

# ---------------------------------------------------------------------------------------------------------------
# Entry-weighted knowledge/skill means (v4). The unweighted mean over all linked occupations is kept for comparison.
WEIGHTING_METHOD = ("entry-weighted mean of O*NET 31.0 importance (Scale IM): entry targets weight 2; other linked "
                    "occupations in Job Zone 4 or 5 (or the entry targets' Job Zone) weight 1; Manager, Chief, "
                    "Postsecondary-faculty, All Other, Supervisor, Director and Treasurers and Controllers titles, and "
                    "non-target occupations in other Job Zones, weight 0")


def entry_weights(occs, targets, zones):
    tset = {s for s, _ in targets}
    tz = {zones.get(s) for s in tset if zones.get(s)}
    w = {}
    for s, t in occs:
        if s in tset:
            w[s] = 2
        elif EXCLUDE_STRICT.search(t) or EXCLUDE_SOFT.search(t):
            continue
        elif zones.get(s) in ({4, 5} | tz):
            w[s] = 1
    return w


def weighted_top(im, weights, n):
    df = im[im["O*NET-SOC Code"].isin(weights)].copy()
    if df.empty:
        return []
    df["w"] = df["O*NET-SOC Code"].map(weights)
    df["wv"] = df["w"] * df["Data Value"]
    g = df.groupby("Element Name")[["wv", "w"]].sum()
    r = (g["wv"] / g["w"]).sort_values(ascending=False, kind="stable").head(n)
    return [(k, round(float(v), 2)) for k, v in r.items()]


# Outline element plan (v4). English Language goes to Year 1 general education; workplace/management elements get no
# course slot unless the major's CIP series is about them; at most 3 core elements in Year 2 and 3 in Year 3.
CROSS_CUTTING = {
    "Customer and Personal Service": "service and client-relations knowledge; the outline leaves it to internships, part-time work and the practice tasks rather than a course slot",
    "Administrative": "office procedures and records handling; usually learned on the job, so it gets no course slot",
    "Clerical": "office procedures and records handling; usually learned on the job, so it gets no course slot",
    "Administration and Management": "management and planning knowledge matters most after several years of experience, so the outline gives it no course slot (a management elective is optional)",
    "Personnel and Human Resources": "staffing and HR knowledge matters mainly for supervisory roles later in a career, so it gets no course slot",
    "Education and Training": "teaching and training others is built through presenting, tutoring and peer teaching in projects rather than a dedicated course",
}
CORE_BY_SERIES = {"52": {"Administration and Management", "Administrative", "Customer and Personal Service", "Personnel and Human Resources"},
                  "13": {"Education and Training"}, "44": {"Administration and Management"}}
CAPACITY_REASON = ("ranked below the knowledge areas the outline already covers (the outline gives at most six course "
                   "slots to knowledge); worth an elective if a target role needs it")


def outline_plan(cip, know_w, skills_w, target_imp, overrides=None):
    """Which weighted top elements go where in the outline, and which are skipped (with reason)."""
    overrides = overrides or {}
    keep = CORE_BY_SERIES.get(cip[:2], set()) | set(overrides.get("core_keep", []))
    names = [e for e, _ in know_w]
    y1k = [e for e in names if e == "English Language"]
    core = [e for e in names if e != "English Language" and (e not in CROSS_CUTTING or e in keep)]
    y2 = core[:3]
    rest = sorted(core[3:], key=lambda e: -target_imp.get(e, 0.0))
    y3 = rest[:3]
    # Few core elements in the top list: add knowledge rated highest for the entry targets (outside the top list).
    extra = [e for e, _ in sorted(target_imp.items(), key=lambda kv: -kv[1])
             if e not in names and e != "English Language" and (e not in CROSS_CUTTING or e in keep) and target_imp[e] >= 2.5]
    y3_from_targets = extra[:max(0, 2 - len(y3))]
    y3 = y3 + y3_from_targets
    reasons = overrides.get("skip_reasons", {})
    skipped = [{"element": e, "reason": reasons.get(e, CROSS_CUTTING[e])} for e in names if e in CROSS_CUTTING and e not in keep]
    skipped += [{"element": e, "reason": reasons.get(e, CAPACITY_REASON)} for e in rest[3:]]
    s = [e for e, _ in skills_w]
    return {"year1_knowledge": y1k, "year1_skills": s[:3], "year2_knowledge": y2, "year3_knowledge": y3,
            "year3_knowledge_added_from_targets": y3_from_targets,
            "year3_skills": s[3:6], "skipped_knowledge": skipped,
            "rule": ("English Language is placed in Year 1 general education; workplace and management elements "
                     "(Customer and Personal Service, Administrative, Clerical, Administration and Management, Personnel and "
                     "Human Resources, Education and Training) get no course slot unless the major's CIP series is about them; "
                     "the next three elements go to Year 2 and up to three more (ordered by importance to the entry targets) "
                     "to Year 3; if fewer than two remain for Year 3, knowledge rated at least 2.5 for the entry targets fills it")}


def knowledge_lines(L, know_w, skills_w, know_all, skills_all, n_w, n_all):
    L += ["", f"## Most important knowledge areas (O*NET importance, 1 to 5, entry-weighted over {n_w} linked occupations; used for the outline)", ""]
    L += [f"- {k} ({v})" for k, v in know_w] or ["- No O*NET knowledge ratings for these occupations."]
    L += ["", f"Weighting: {WEIGHTING_METHOD}. For comparison, the unweighted mean over all {n_all} linked occupations ranks: "
          + ("; ".join(f"{k} ({v})" for k, v in know_all) or "no ratings") + "."]
    L += ["", f"## Most important foundational skills (O*NET 31.0 Essential Skills importance, 1 to 5, entry-weighted)", ""]
    L += [f"- {k} ({v})" for k, v in skills_w] or ["- No O*NET skill ratings for these occupations."]
    L += ["", "Unweighted mean over all linked occupations: " + ("; ".join(f"{k} ({v})" for k, v in skills_all) or "no ratings") + "."]


def skipped_lines(L, op, know_w):
    vals = dict(know_w)
    L += ["Knowledge areas from the top list that the outline deliberately does not cover:", ""]
    L += [f"- {x['element']} ({vals.get(x['element'])}): {x['reason']}." for x in op["skipped_knowledge"]] or \
         ["- None: every top knowledge area has a place in the outline."]
    L += [""]


# Plausibility checks for the generated tier (v4): supervisory tasks and topical overlap of targets.
SUPERVISORY = re.compile(r"\b(supervis(e|es|ing)\b|provides? supervision|direct(s|ing)? and coordinate|direct(s|ing)? "
                         r"(the )?(work|activities|staff|operations) of|manag(e|es|ing) (staff|personnel|employees|workers|teams?)\b|"
                         r"oversee(s|ing)? (the )?(work|activities|staff|personnel|workers|employees)|\bhir(e|es|ing)\b|"
                         r"subordinates|assign(s|ing)? (work|duties|tasks) to|evaluat\w+ (the )?(work|performance) of|"
                         r"train(s|ing)? and supervise)", re.I)
UNDER_SUPERVISION = re.compile(r"under (the )?(direct |general )?supervision", re.I)
SUPERVISORY_RULE = ("task statement matches a supervisory/managerial pattern (supervise, provide supervision, direct and "
                    "coordinate, direct the work/activities/staff of, manage staff/personnel/employees/workers/teams, oversee "
                    "the work/staff, hire, subordinates, assign work to, evaluate the work/performance of, train and "
                    "supervise); 'under supervision' does not count")


def is_supervisory(text):
    return bool(SUPERVISORY.search(UNDER_SUPERVISION.sub("", str(text))))


# Field-fit plausibility check for generated-tier entry targets (v5). Replaces the v4 lexical title-overlap flag, which
# flagged 1,273 targets in 756 plans and changed nothing.
_STEMMER = snowballstemmer.stemmer("english")
FIELD_STOP_WORDS = """a an and or of the for in on to with by as at from other general all studies study science sciences
technology technologies program programs related applied art arts administration management engineering engineer engineers
specialist specialists professional professionals services service system systems method methods education teacher
teachers teaching""".split()
_FIELD_STOP = {_STEMMER.stemWord(w) for w in FIELD_STOP_WORDS}
FIT_DROP_MIN_BEST = 0.02   # some same-tier linked occupation must fit at least this well before a zero-fit target is dropped
FIT_FLAG_MIN_BEST = 0.10   # a zero-fit base (.00) target is flagged only if a clearly better-fitting alternative exists
FIT_SERIES_KEEP = 0.12     # a zero-fit target is kept if it fits the program's 4-digit CIP series this well
FIELD_FIT_RULE = (
    "field fit = cosine similarity between the CIP program title's field terms and the occupation's O*NET 31.0 text "
    "(title, description and all task statements). Words are Snowball-stemmed, generic words (science, studies, "
    "technology, engineering, management, education, general, other, ...) are ignored, and terms are weighted by "
    "log term frequency times inverse document frequency over all O*NET occupations. Compound title words are also "
    "split into the O*NET vocabulary stems of 5+ letters they contain (electromechanical -> electr, mechan; "
    "telecommunications -> commun), so a compound does not count as a mismatch. CIP definitions are not in the "
    "pinned crosswalk file, so the CIP title is the field description. "
    f"A rule target is dropped as clearly implausible when (1) its fit is 0, meaning no field term of the program "
    f"title occurs anywhere in its O*NET title, description or tasks; (2) some eligible linked occupation in the same Job "
    f"Zone tier has fit >= {FIT_DROP_MIN_BEST}, so the crosswalk does offer a field match; (3) it is an O*NET "
    "detailed specialty code (not .00), whose link is typically inherited from a broad SOC code such as Engineers, All "
    "Other; (4) its base .00 occupation also has fit 0; and (5) its fit with the titles of all CIP codes in the "
    f"program's 4-digit CIP series (the field family) is below {FIT_SERIES_KEEP}, so it is not a close neighbour of the "
    "field either (e.g. a genetics program keeps Molecular and Cellular Biologists). The thresholds were set by "
    "inspecting the candidate drops of this release; they are not validated. Dropped targets are replaced from the same ranked tier "
    "with the next occupations whose fit is above 0; if none remain, the plan keeps fewer targets. "
    f"A base (.00) target with fit 0 is kept but flagged better_field_match_available when a non-target occupation "
    f"in the same tier has fit >= {FIT_FLAG_MIN_BEST}")


def field_terms(text):
    return [w for w in _STEMMER.stemWords(re.findall(r"[a-z]+", str(text).lower())) if len(w) > 2 and w not in _FIELD_STOP]


class FieldIndex:
    """TF-IDF index of O*NET occupation text (title twice, description, task statements)."""
    def __init__(self, occ, tasks):
        doc = {s: f"{t} {t} {d}" for s, t, d in zip(occ["O*NET-SOC Code"], occ["Title"], occ["Description"])}
        for s, g in tasks.groupby("O*NET-SOC Code")["Task"]:
            doc[s] = doc.get(s, "") + " " + " ".join(map(str, g))
        self.tf = {s: collections.Counter(field_terms(d)) for s, d in doc.items()}
        n = len(self.tf)
        df = collections.Counter(w for c in self.tf.values() for w in c)
        self.idf = {w: math.log(n / k) for w, k in df.items()}
        self.vocab_long = sorted(w for w in self.idf if len(w) >= 5)
        self.norm = {s: math.sqrt(sum(((1 + math.log(v)) * self.idf[w]) ** 2 for w, v in c.items())) for s, c in self.tf.items()}

    def query_terms(self, cip_title):
        """Field terms of the CIP title plus the vocabulary stems (5+ letters) contained in compound words."""
        q = set(field_terms(cip_title))
        for t in list(q):
            if len(t) >= 8:
                q |= {v for v in self.vocab_long if v != t and v in t}
        return q

    def fit(self, cip_title, soc):
        c, q = self.tf.get(soc), self.query_terms(cip_title)
        if not c or not q:
            return 0.0
        qn = math.sqrt(sum(self.idf.get(w, 0) ** 2 for w in q))
        num = sum((1 + math.log(c[w])) * self.idf[w] ** 2 for w in q if w in c)
        return round(num / ((self.norm[soc] or 1) * (qn or 1)), 4)


def ranked_tier(eligible, zones, zone, sim):
    """The rule's ranked same-tier pool (same order rank_entry_targets uses)."""
    tier = [(s, t) for s, t in eligible if zones.get(s) == zone]
    return sorted(tier, key=lambda o: (not o[0].endswith(".00"), -sim(o[0])))


def plausibility_filter(title, targets, pool, fi, titles, series_text=""):
    """Apply FIELD_FIT_RULE to rule targets. Returns (final targets, record for plan.json)."""
    fits = {s: fi.fit(title, s) for s, _ in pool}
    for s, _ in targets:
        fits.setdefault(s, fi.fit(title, s))
    best = max(fits.values(), default=0.0)
    dropped = []
    for s, t in targets:
        if fits[s] == 0 and best >= FIT_DROP_MIN_BEST and not s.endswith(".00"):
            parent = s[:-2] + "00"
            pf = fi.fit(title, parent)
            sf = fi.fit(series_text, s) if series_text else 0.0
            if pf == 0 and sf < FIT_SERIES_KEEP:
                dropped.append({"soc": s, "title": t, "fit": fits[s], "base_soc": parent, "base_title": titles.get(parent),
                                "base_fit": pf, "series_fit": sf, "reason": "no field term of the program title in its O*NET text; base occupation does not fit either; not a close fit to the CIP series; better-fitting linked occupations exist"})
    gone = {d["soc"] for d in dropped}
    final = [x for x in targets if x[0] not in gone]
    added = []
    for s, t in pool:
        if len(final) >= len(targets):
            break
        if (s, t) in targets or s in gone or fits.get(s, 0) == 0:
            continue
        final.append((s, t)); added.append({"soc": s, "title": t, "fit": fits[s]})
    flags = []
    tset = {s for s, _ in final}
    alts = sorted([(f, s) for s, f in fits.items() if s not in tset and s not in gone and f > 0], reverse=True)
    for s, t in final:
        if fits[s] == 0 and s.endswith(".00") and alts and alts[0][0] >= FIT_FLAG_MIN_BEST:
            flags.append({"flag": "better_field_match_available", "onet_soc_code": s, "occupation_title": t, "fit": fits[s],
                          "suggested_soc": alts[0][1], "suggested_title": titles.get(alts[0][1]), "suggested_fit": alts[0][0],
                          "detail": "kept (base occupation) but no field term of the program title occurs in its O*NET text; review the suggested alternative"})
    rec = {"method": FIELD_FIT_RULE, "cip_field_terms": sorted(fi.query_terms(title)),
           "rule_targets": [s for s, _ in targets], "final_targets": [s for s, _ in final],
           "fit": {s: fits[s] for s, _ in pool} | {s: fits[s] for s, _ in targets},
           "dropped": dropped, "added": added, "flags": flags}
    return final, rec


def quality_flags(targets, zones, ptasks, dropped_tasks, basis, tp):
    """Actionable flags only; automatic changes and context go to actions and notes."""
    flags = list(tp["flags"]) if tp else []
    kept = [p["practice_id"] for p in ptasks if p.get("supervisory_task")]
    if kept:
        flags.append({"flag": "supervisory_task_kept", "count": len(kept), "practice_ids": kept,
                      "detail": "not enough non-supervisory tasks were available, so these supervisory tasks remain"})
    actions = []
    for d in (tp or {}).get("dropped", []):
        actions.append({"action": "target_dropped", "onet_soc_code": d["soc"], "occupation_title": d["title"],
                        "detail": d["reason"]})
    for a in (tp or {}).get("added", []):
        actions.append({"action": "target_added", "onet_soc_code": a["soc"], "occupation_title": a["title"],
                        "detail": f"next same-tier occupation in the rule's ranking with field fit {a['fit']}"})
    if dropped_tasks:
        actions.append({"action": "supervisory_tasks_dropped", "count": len(dropped_tasks), "onet_task_ids": dropped_tasks,
                        "detail": "supervisory/managerial tasks of the entry targets were skipped when picking practice tasks"})
    notes = []
    tz = sorted({zones.get(s) for s, _ in targets if zones.get(s)})
    if tz and 4 not in tz:
        notes.append({"note": "entry_target_not_job_zone_4", "job_zones": tz,
                      "detail": "no eligible Job Zone 4 occupation is linked, so the entry targets come from another Job Zone"})
    if "first crosswalk link used" in basis or "no Job Zone rating" in basis:
        notes.append({"note": "entry_target_fallback", "detail": basis})
    return {"method": {"field_fit": FIELD_FIT_RULE, "supervisory_tasks": SUPERVISORY_RULE},
            "flag_count": len(flags), "flags": flags, "actions": actions, "notes": notes,
            "retired_checks": ("v4 low_title_overlap (lexical title overlap) was retired in v5: it flagged 1,273 targets in 756 of "
                               "1,017 plans, mostly plausible pairs that use different words, and changed nothing")}


def quality_lines(L, qf):
    L += ["## Quality flags (automatic plausibility checks; generated tier)", ""]
    if not qf["flags"]:
        L += ["- No flags raised by the automatic checks (this does not mean the plan was reviewed)."]
    for f in qf["flags"]:
        if f["flag"] == "better_field_match_available":
            L += [f"- better_field_match_available: entry target `{f['onet_soc_code']}` {f['occupation_title']} has field fit {f['fit']} "
                  f"with the program title; `{f['suggested_soc']}` {f['suggested_title']} fits better ({f['suggested_fit']}). Review before use."]
        elif f["flag"] == "supervisory_task_kept":
            L += [f"- supervisory_task_kept: {', '.join(f['practice_ids'])} cite a supervisory task because too few other tasks exist; treat as practice for a later role."]
        else:
            L += [f"- {f['flag']}: {f['detail']}."]
    if qf["actions"]:
        L += ["", "Automatic changes made by the checks:", ""]
    for a in qf["actions"]:
        if a["action"] == "target_dropped":
            L += [f"- target_dropped: `{a['onet_soc_code']}` {a['occupation_title']} was removed from the entry targets ({a['detail']})."]
        elif a["action"] == "target_added":
            L += [f"- target_added: `{a['onet_soc_code']}` {a['occupation_title']} ({a['detail']})."]
        elif a["action"] == "supervisory_tasks_dropped":
            L += [f"- supervisory_tasks_dropped: {a['count']} supervisory or managerial task(s) of the entry targets were skipped as unsuitable for a new graduate (O*NET task IDs {', '.join(map(str, a['onet_task_ids']))})."]
    for n in qf["notes"]:
        if n["note"] == "entry_target_not_job_zone_4":
            L += ["", f"Note: the entry targets are in Job Zone {', '.join(zl(z) for z in n['job_zones'])}, not the usual bachelor's-level Job Zone 4."]
        else:
            L += ["", f"Note ({n['note']}): {n['detail']}."]
    L += ["", "Method: field fit = " + FIELD_FIT_RULE + ". Supervisory check = " + SUPERVISORY_RULE + ".", ""]

# Licensing blocks for the machine layer (v4).
DB_NOTICES = [
    "This page includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license.",
    "O*NET\u00ae is a trademark of USDOL/ETA.",
    "DreamCo has modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications."]
CROSSWALK_NOTICE = "Crosswalk Files by USDOL/ETA, licensed under CC BY 4.0."
ONET_ATTRIBUTION = ("Includes information from the O*NET 31.0 Database and O*NET Crosswalk Files by the U.S. Department of "
                    "Labor, Employment and Training Administration (USDOL/ETA), used under the CC BY 4.0 license (" + CC_BY + ").")
DREAMCO_TERMS = "not set: commercial terms for the DreamCo-original layer are pending the owner's decision"


def item_license(tier):
    if tier == "generated":
        return {"content_class": "mixed: quoted O*NET 31.0 task statement (third-party, CC BY 4.0) plus DreamCo template prompt, rubric and outline",
                "ownership_class": "open_license_with_conditions", "contains_third_party_text": True,
                "license": "CC BY 4.0", "license_url": CC_BY, "attribution": ONET_ATTRIBUTION,
                "modification_notice": ("DreamCo has modified all or some of this information: it added a template prompt, rubric "
                                        "and reference outline around the task statement, which is quoted unmodified. USDOL/ETA has "
                                        "not approved, endorsed, or tested these modifications."),
                "trademark_notice": "O*NET\u00ae is a trademark of USDOL/ETA.",
                "dreamco_layer": {"fields": ["prompt", "rubric", "reference_answer_outline"], "authorship": GENERATED_AUTHORSHIP,
                                  "commercial_terms": DREAMCO_TERMS}}
    return {"content_class": "DreamCo-original text that references O*NET 31.0 identifiers",
            "ownership_class": "synthetic_generated_by_dreamco", "contains_third_party_text": False,
            "license": "DreamCo-original (no third-party text); commercial terms pending owner decision",
            "commercial_terms": DREAMCO_TERMS, "authorship": AUTHORSHIP,
            "third_party_references": {"fields": ["onet_soc_code", "occupation_title", "onet_task_id", "onet_task_type", "onet_task_url"],
                                       "license": "CC BY 4.0", "license_url": CC_BY, "attribution": ONET_ATTRIBUTION,
                                       "trademark_notice": "O*NET\u00ae is a trademark of USDOL/ETA."}}


def plan_license(tier):
    gen = tier == "generated"
    comps = [{"fields": ["occupations", "top_knowledge", "top_skills", "top_knowledge_entry_weighted", "top_skills_entry_weighted",
                         "entry_targets", "knowledge_weighting"],
              "content_class": "O*NET 31.0 and crosswalk data, filtered, averaged and ranked by DreamCo",
              "ownership_class": "open_license_with_conditions", "license": "CC BY 4.0", "license_url": CC_BY}]
    if gen:
        comps.append({"fields": ["practice_tasks[].onet_task_statement"], "content_class": "O*NET 31.0 task statements quoted verbatim",
                      "ownership_class": "open_license_with_conditions", "license": "CC BY 4.0", "license_url": CC_BY})
        comps.append({"fields": ["practice_tasks[].prompt", "practice_tasks[].rubric", "practice_tasks[].reference_answer_outline",
                                 "outline_elements", "quality_flags", "entry_target_review"],
                      "content_class": "DreamCo template output (tier generated)", "ownership_class": "synthetic_generated_by_dreamco",
                      "license": "DreamCo; commercial terms pending owner decision", "authorship": GENERATED_AUTHORSHIP})
    else:
        comps.append({"fields": ["practice_tasks[].task_intent", "practice_tasks[].prompt", "practice_tasks[].rubric",
                                 "practice_tasks[].reference_answer_outline", "outline_elements", "entry_target_review"],
                      "content_class": "DreamCo-original authored text (tier authored)", "ownership_class": "synthetic_generated_by_dreamco",
                      "license": "DreamCo-original; commercial terms pending owner decision", "authorship": AUTHORSHIP})
    return {"summary": ("Mixed: O*NET-derived data and quoted O*NET task statements under CC BY 4.0, plus a DreamCo template layer"
                        if gen else "Mixed: O*NET-derived data under CC BY 4.0, plus DreamCo-original authored text"),
            "license_url": CC_BY, "attribution": ONET_ATTRIBUTION,
            "required_notices": DB_NOTICES + [CROSSWALK_NOTICE],
            "dreamco_commercial_terms": DREAMCO_TERMS, "components": comps,
            "per_item_licensing": "each practice_tasks[] item carries its own license block"}


def provenance_record(cip, title, stem, plan_path, json_path, pins, n_occs, targets, n_tasks, tier="authored"):
    gen = tier == "generated"
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
                          ("Generated tier: task statements are quoted verbatim with attribution and are not relabeled as DreamCo-owned."
                           if gen else "Task statements are referenced by Task ID only; their text is not reproduced or relabeled as DreamCo-owned.")]},
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
             "description": "Top-8 knowledge and top-6 Essential Skills by O*NET 31.0 importance (Scale IM): the unweighted mean across all linked occupations (top_knowledge/top_skills, for comparison) and the " + WEIGHTING_METHOD + " (top_*_entry_weighted, used for the outline).",
             "derived_from": ["onet_db_31_0"]},
            {"component": "entry_targets", "ownership_class": o, "derivation_type": "derived_metric",
             "description": f"{len(targets)} entry target(s) chosen by a DreamCo rule: Job Zone 4 first (fallback 3, 5, 1-2), excluding Manager/Chief/Postsecondary/All Other/Supervisor/Director titles, base .00 codes first, then ranked by Pearson correlation of knowledge-importance profiles; "
                            + ("generated tier: the rule output is used without manual review." if gen else "then reviewed for plausibility, with any manual override and its reason recorded in authored/target_overrides.json."),
             "derived_from": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "linked_occupations"] + ([] if gen else ["authored/target_overrides.json"])},
            {"component": "four_year_outline", "ownership_class": d, "derivation_type": "synthetic_data",
             "description": "Generated tier: DreamCo template that lists this major's top O*NET knowledge and Essential Skill element names by year; no per-major course mapping and no review.",
             "derived_from": ["knowledge_and_skill_importance", "entry_targets"]} if gen else
            {"component": "four_year_outline", "ownership_class": d, "derivation_type": "synthetic_data",
             "description": "DreamCo-original synthesis: per-major course-topic mappings (authored/outline_topics.json, keyed by CIP and O*NET element) for this major's top knowledge/skills and entry targets; embeds O*NET element and occupation names, so O*NET attribution still applies.",
             "derived_from": ["knowledge_and_skill_importance", "entry_targets", "authored/outline_topics.json"]},
            {"component": "typical_next_steps", "ownership_class": d, "derivation_type": "synthetic_data",
             "description": "DreamCo-original synthesis summarizing linked occupations by Job Zone; cites O*NET 31.0 Job Zone numbers only and does not quote O*NET Job Zone names or descriptions.",
             "derived_from": ["linked_occupations", "onet_db_31_0_jobzones_tasks"]},
            {"component": "practice_tasks", "ownership_class": o, "derivation_type": "synthetic_data",
             "description": f"Generated tier (mixed content, so ownership_class open_license_with_conditions; per-item license blocks in plan.json and data/practice_tasks.json): {n_tasks} DreamCo template exercises, each quoting one O*NET 31.0 task statement verbatim with attribution (USDOL/ETA, CC BY 4.0; the quote is O*NET content) and adding a fixed template prompt, 3-criterion rubric and reference outline. Authorship: " + GENERATED_AUTHORSHIP + ".",
             "derived_from": ["onet_db_31_0_jobzones_tasks", "entry_targets"]} if gen else
            {"component": "practice_tasks", "ownership_class": d, "derivation_type": "original_evaluation",
             "description": f"{n_tasks} DreamCo-original occupation-specific scenario prompts (authored/practice_tasks_authored.json), each with an original-wording paraphrase of the cited task's intent, a 3-criterion scenario-specific rubric and a reference answer outline, tied to an O*NET 31.0 Task ID and O*NET-SOC code of a linked occupation. No run of 5 or more words from O*NET task statements is reproduced (tests enforce this). Authorship: " + AUTHORSHIP + ".",
             "derived_from": ["onet_db_31_0_jobzones_tasks", "entry_targets", "authored/practice_tasks_authored.json"]},
        ],
        "transformation_history": [
            {"step": "fetch and verify pinned sources (sha256 vs raw/SOURCES.md)", "tool": "edu-career-pathways/fetch_sources.py",
             "tool_version": f"sha256:{sha256(ROOT / 'fetch_sources.py')}", "inputs": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "onet_cip_soc_crosswalk"]},
            {"step": "crosswalk join, importance aggregation, Job Zone entry targeting with documented overrides, authored outline topics and practice tasks, markdown render",
             "tool": "edu-career-pathways/build.py", "tool_version": f"sha256:{build_sha}",
             "inputs": ["onet_db_31_0", "onet_db_31_0_jobzones_tasks", "onet_cip_soc_crosswalk"]
                       + [f"authored/{n} sha256:{sha256(AUTH / n)}" for n in AUTHORED_FILES]},
        ],
        "attribution_text": attribution,
        "review_status": "unreviewed",
        "human_review": None,
        "notes": [
            "retrieved_at values are dates only because raw/SOURCES.md records only download dates (America/Chicago).",
            "Two O*NET 31.0 source entries exist because the job zone and task files were downloaded on a later date than the others.",
            "O*NET 31.0 split Skills into Essential Skills and Transferable Skills; this asset uses Essential Skills only.",
            "Owner approval is pending; it is never set by build.py.",
            ("Tier generated: outline, entry targets and practice exercises are template output of build.py with no individual authoring or review; coverage rules are in authored/coverage_rules.json."
             if gen else "DreamCo-authored content (practice tasks, outline topics, target overrides) was written by an AI agent (Grok-Edu-Career-Pathways) and has not been human-reviewed."),
        ],
    }


def candidate_record(cip, title, n_occs, n_tasks, tier="authored"):
    gen = tier == "generated"
    return {
        "candidate_id": asset_id(cip, title),
        "asset_id": asset_id(cip, title),
        "title": f"Study plan: {title} (CIP {cip}) mapped to O*NET occupations",
        "description": (f"One markdown study plan: {n_occs} linked O*NET-SOC occupations with Job Zones, top knowledge and "
                        f"Essential Skills by entry-weighted mean O*NET 31.0 importance (unweighted means also shown), 1-3 Job Zone-based entry targets, a DreamCo 4-year "
                        f"outline and next steps, and {n_tasks} "
                        + ("DreamCo template practice exercises quoting O*NET task statements (tier generated: not individually authored or reviewed)."
                           if gen else "DreamCo-original practice prompts tied to O*NET task IDs (tier authored).")),
        "category": "education/career-pathways",
        "data_types": ["markdown"],
        "rights_basis": ("CC BY 4.0 (O*NET 31.0 Database + O*NET Crosswalk Files, USDOL/ETA), including O*NET task statements quoted in "
                        "the practice exercises; DreamCo template outline, prompts and rubrics" if gen else
                        "CC BY 4.0 (O*NET 31.0 Database + O*NET Crosswalk Files, USDOL/ETA); DreamCo-original outline and practice prompts"),
        "ownership_class": "open_license_with_conditions",
        "commercial_use_allowed": True,
        "redistribution_allowed": True,
        "rights_declarations": {
            "onet_content": "CC BY 4.0: commercial use and redistribution allowed with attribution; notices kept in the plan footer.",
            "dreamco_original_synthesis": (("Generated tier: template 4-year outline, next steps, and template practice prompts/rubrics (ownership_class synthetic_generated_by_dreamco; " + GENERATED_AUTHORSHIP + "); quoted O*NET task statements remain USDOL/ETA content under CC BY 4.0.")
                                           if gen else "4-year outline topics, next steps, practice scenario prompts, rubrics and reference answer outlines (ownership_class synthetic_generated_by_dreamco; " + AUTHORSHIP + "); DreamCo may use and redistribute commercially, subject to owner approval for sale."),
        },
        "flags": [],
        "provenance_path": "provenance.json",
        "asset_path": "asset.json",
        "scorecard_score": None,
        "owner_approval": None,
        "owner_approval_status": "pending",
    }


def asset_record(cip, title, stem, prov, entry, n_occs, excluded, review, evidence_ids=None, tier="authored"):
    """Plan 5.2 synthesis asset record (schemas/data_package_synthesis_asset.schema.json)."""
    md, js = prov["asset_files"][0], prov["asset_files"][1]
    tz = sorted({t["job_zone"] for t in entry["entry_targets"] if t["job_zone"]})
    ev = evidence_ids or {"sandbox": [], "benchmark": [], "holdout": [], "regression": []}
    agree = [f"All {n_occs} crosswalk links for CIP {cip} resolve to O*NET 31.0 occupation codes (tests check this).",
             f"Entry targets are O*NET Job Zone {', '.join(zl(z) for z in tz) or 'unrated'} linked occupations: "
             + "; ".join(t["title"] for t in entry["entry_targets"]) + "."]
    if review and review["type"] == "override":
        agree.append("Entry targets were changed from the rule output by a documented manual override: " + review["reason"])
    elif review and review["type"] == "reviewed_without_change":
        agree.append("Entry targets were reviewed for plausibility and kept: " + review["note"])
    gen = tier == "generated"
    if gen:
        agree.append("Tier generated: entry targets are the unreviewed rule output; nobody checked them for plausibility.")
    still = ["Practice prompts, rubrics and reference answer outlines are AI-authored and have not been piloted with learners, scored by human graders, or human-reviewed.",
             "No sandbox, benchmark or holdout evaluation exists: this box has no independent model API key or human graders, and a self-graded run would not be independent evidence.",
             "DreamCo-original text has not had owner review."]
    if gen:
        still[0] = "Practice exercises are one fixed template around quoted O*NET task statements; they were not individually authored, reviewed, or piloted with learners."
        still.append("No regression evidence exists for generated-tier plans: they are new in this release, so there is no previous release to compare against.")
    if ev["regression"]:
        still.insert(1, "Regression evidence compares this build with the previous release (8cc1ce1) on links, targets, task citations and O*NET text leakage; it does not measure learning outcomes.")
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
                                     "entry-level targets with review notes", "4-year outline with per-major course topics",
                                     "typical next steps", "practice scenario tasks with rubrics and reference answer outlines"]
                        if not gen else
                                    ["linked occupations with Job Zones", "key knowledge areas", "key Essential Skills",
                                     "entry-level targets (rule output, not reviewed)", "4-year outline (element names only)",
                                     "typical next steps", "template practice exercises quoting O*NET task statements"]},
        "machine_layer": {"path": js["path"], "format": "json", "sha256": js["sha256"],
                          "elements": ["tier", "occupations", "top_knowledge", "top_skills", "entry_targets", "entry_target_review",
                                       "practice_tasks", "rubrics", "reference_answer_outlines"]},
        "dreamco_analysis": {
            "agree": agree,
            "reject": [f"Not used as entry targets (leadership, faculty, or residual titles): {'; '.join(excluded)}."] if excluded else [],
            "improve": ["Knowledge and skill importance used for the outline is an entry-weighted mean (targets weight 2, other Job Zone-appropriate non-leadership linked roles weight 1); the weights are a DreamCo heuristic, not an O*NET method, and the unweighted all-linked list is shown for comparison.",
                        ("Generated tier: the outline lists O*NET element names without course topics, and practice exercises share one template; authoring this major would replace both."
                         if gen else "Course topics in the outline are typical US undergraduate topics written per major, not a specific institution's curriculum.")],
            "still_need_test": still,
        },
        "validation_evidence_ids": ev,
        "integrity_hash": prov["integrity_hash"],
        "created_at": BUILD_TIMESTAMP,
        "evidence_root": EVIDENCE_ROOT,
        "generator_version": prov["evaluator_version"],
        "notes": [
            "dreamco_analysis is generated by build.py from build facts and the authored review files; it is not a human review.",
            f"tier: {tier} (see plan.json and data/majors_selected.json).",
            "validation_evidence_ids: only regression evidence (if listed) exists. sandbox and benchmark are empty on purpose; holdout stays empty until the owner grades evidence/holdout_kit; evidence/pytest.txt is a build-integrity run and is not counted.",
            ("evidence is append-only: records for earlier versions of this asset stay linked; the ones whose source_reference is this version's integrity_hash are: "
             + (", ".join(current_version_ids(prov["asset_id"], prov["integrity_hash"], ev)) or "none")),
            "perspectives_used has one entry: O*NET and the crosswalk are both official USDOL/ETA sources (closest policy perspective: official_documentation).",
        ],
    }


def current_version_ids(aid, integrity_hash, ev):
    out = []
    for kind, ids in ev.items():
        for eid in ids:
            r = json.loads((EVIDENCE / kind / aid / f"{eid.split(':')[2]}.json").read_text())
            if r.get("source_reference") == integrity_hash:
                out.append(eid)
    return out


def linked_evidence(aid, integrity_hash):
    """Evidence records under data/dreamco_knowledge/evidence/<kind>/<asset_id>/ whose id matches the file, whose
    integrity_hash matches the sha256 of the sibling .results.json, and which passed. Evidence is append-only, so records
    for earlier versions of the asset are linked too; each record's source_reference names the version it evaluated
    (tampered or failing records are not linked)."""
    ev = {"sandbox": [], "benchmark": [], "holdout": [], "regression": []}
    for kind in ev:
        d = EVIDENCE / kind / aid
        for f in sorted(d.glob("*.json")) if d.is_dir() else []:
            if f.name.endswith(".results.json"):
                continue
            r = json.loads(f.read_text())
            res = f.with_name(f.stem + ".results.json")
            res_ok = res.is_file() and r.get("integrity_hash") == "sha256:" + hashlib.sha256(res.read_bytes()).hexdigest()
            if r.get("evidence_id") == f"{kind}:{aid}:{f.stem}" and res_ok and r.get("passed") is True:
                ev[kind].append(r["evidence_id"])
    return ev


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
    tasks = pd.read_csv(RAW / "task_statements.csv", dtype={"O*NET-SOC Code": str})
    task_text = dict(zip(tasks["Task ID"].astype(int), tasks["Task"]))
    descriptions = dict(zip(occ["O*NET-SOC Code"], occ["Description"]))
    occ_titles = dict(zip(occ["O*NET-SOC Code"], occ["Title"]))
    field_index = FieldIndex(occ, tasks)
    series_titles = {}
    for c_, t_ in dict(zip(cw.cip, cw.cip_title)).items():
        series_titles.setdefault(c_[:5], set()).add(str(t_).strip())
    series_text = {k: " ".join(sorted(v)) for k, v in series_titles.items()}
    authored, topics, tov = load_authored()
    selected, coverage = select_majors(cw, valid, zones, load_coverage_rules())
    gate = find_gate_tool()
    if (REPO_ROOT / EVIDENCE_ROOT).resolve() != EVIDENCE.resolve():
        print(f"WARNING: {REPO_ROOT}/{EVIDENCE_ROOT} is not this pack's evidence directory; set DREAMCO_REPO_ROOT to the "
              "repo root that contains study_packs/career_pathways, or the gate will not resolve evidence ids")
    sel, rows, all_tasks, built = [], [], [], []
    for cip, tier in selected:
        gen = tier == "generated"
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
        dropped, tp = [], None
        if gen:
            pool = ranked_tier(eligible, zones, tzone, sim) if tzone else []
            targets, tp = plausibility_filter(title, targets, pool, field_index, occ_titles, series_text.get(cip[:5], ""))
            if tp["dropped"]:
                basis += ("; then the automatic field-fit check dropped " + ", ".join(d["soc"] for d in tp["dropped"])
                          + (" and added " + ", ".join(a["soc"] for a in tp["added"]) if tp["added"] else "")
                          + " (see target_plausibility)")
            review = {"type": "rule_only_not_reviewed",
                      "note": "Generated tier: rule output after the automatic field-fit check; not reviewed by a person."}
        else:
            targets, basis, review = apply_target_override(cip, occs, zones, targets, basis, tov)
        weights = entry_weights(occs, targets, zones)
        know_w, skills_w = weighted_top(kim, weights, 8), weighted_top(sim_, weights, 6)
        target_imp = dict(top_elements(kim, [s for s, _ in targets], 40))
        outline = outline_plan(cip, know_w, skills_w, target_imp, None if gen else topics[cip])
        ctx = {"know": know, "skills": skills, "know_w": know_w, "skills_w": skills_w, "weights": weights, "outline": outline}
        if gen:
            ptasks, dropped = generated_practice_tasks(cip, targets, eligible, sim, tasks, kim, know_w)
            qf = quality_flags(targets, zones, ptasks, dropped, basis, tp)
        else:
            ptasks = practice_tasks(cip, occs, tasks, authored)
            sup = [p["practice_id"] for p in ptasks if is_supervisory(task_text[p["onet_task_id"]])]
            qf = {"method": {"supervisory_tasks": SUPERVISORY_RULE},
                  "note": ("Authored tier: entry targets and practice tasks were chosen and reviewed per major, so the generated-tier "
                           "plausibility flags are not applied. Informational only: cited tasks whose O*NET statement is supervisory "
                           "are listed; their authored scenarios say when they are practice for a later or graduate role."),
                  "flag_count": 0, "flags": [], "informational": {"supervisory_task_cited": sup}}
        all_tasks += ptasks
        for s, t in occs:
            rows.append([cip, title, s, t])
        sel.append({"cip": cip, "title": title, "asset_id": asset_id(cip, title), "tier": tier,
                    "occupations": [{"soc": s, "title": t, "job_zone": zones.get(s)} for s, t in occs],
                    "top_knowledge": know, "top_skills": skills,
                    "top_knowledge_entry_weighted": know_w, "top_skills_entry_weighted": skills_w,
                    "knowledge_weighting": {"method": WEIGHTING_METHOD, "weights": weights,
                                            "note": "top_knowledge/top_skills are the unweighted mean over all linked occupations (kept for comparison); the outline uses the entry-weighted lists."},
                    "outline_elements": outline,
                    "quality_flags": qf,
                    "target_plausibility": tp,
                    "entry_targets": [{"soc": s, "title": t, "job_zone": zones.get(s)} for s, t in targets],
                    "entry_target_basis": basis,
                    "entry_target_review": review,
                    "practice_task_ids": [p["practice_id"] for p in ptasks]})
        plan = PLANS / f"{stem}.md"
        if gen:
            plan.write_text(plan_md_generated(cip, title, stem, occs, zones, ctx, targets, basis, ptasks, qf))
        else:
            plan.write_text(plan_md(cip, title, stem, occs, zones, ctx, targets, basis, ptasks, topics[cip], review))
        side = PLANS / stem
        side.mkdir(exist_ok=True)
        pj = side / "plan.json"
        pj.write_text(json.dumps({**sel[-1], "label": ("O*NET 31.0-derived fields plus DreamCo template practice exercises (tier generated)"
                                                       if gen else "O*NET 31.0-derived fields plus DreamCo-original practice tasks"),
                                  "authorship": GENERATED_AUTHORSHIP if gen else AUTHORSHIP, "license": plan_license(tier),
                                  "created_at": BUILD_TIMESTAMP, "practice_tasks": ptasks}, indent=2) + "\n")
        prov = provenance_record(cip, title, stem, plan, pj, pins, len(occs), targets, len(ptasks), tier)
        (side / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
        excluded = [t for s_, t in occs if (EXCLUDE_STRICT.search(t) or EXCLUDE_SOFT.search(t)) and (s_, t) not in targets]
        ev = linked_evidence(prov["asset_id"], prov["integrity_hash"])
        (side / "asset.json").write_text(json.dumps(asset_record(cip, title, stem, prov, sel[-1], len(occs), excluded, review, ev, tier), indent=2) + "\n")
        (side / "candidate.json").write_text(json.dumps(candidate_record(cip, title, len(occs), len(ptasks), tier), indent=2) + "\n")
        built.append(stem)
    with open(DATA / "major_to_onet.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cip_code", "cip_title", "onet_soc_code", "occupation_title"]); w.writerows(rows)
    (DATA / "majors_selected.json").write_text(json.dumps(sel, indent=2) + "\n")
    with open(DATA / "coverage.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cip_code", "cip_title", "tier", "status", "reason"]); w.writerows(coverage)
    (DATA / "practice_tasks.json").write_text(json.dumps({
        "label": "DreamCo career-pathway practice items, mixed licensing per item (see tasks[].license)",
        "label_note": ("Tier authored items are labeled '" + PRACTICE_LABEL + "' and are DreamCo-original text; tier generated items "
                       "are labeled '" + GENERATED_LABEL + "' and contain a quoted O*NET 31.0 task statement (third-party, CC BY 4.0)."),
        "ownership_class": most_restrictive(t["ownership_class"] for t in all_tasks),
        "ownership_class_rule": ("most restrictive class among the items (order: " + " > ".join(OWNERSHIP_RESTRICTIVENESS) +
                                 "); each item keeps its own ownership_class and license"),
        "ownership_classes": {"authored": "synthetic_generated_by_dreamco", "generated": "open_license_with_conditions"},
        "authorship": {"authored": AUTHORSHIP, "generated": GENERATED_AUTHORSHIP},
        "license": {"third_party": "CC BY 4.0", "license_url": CC_BY, "attribution": ONET_ATTRIBUTION,
                    "required_notices": DB_NOTICES + [CROSSWALK_NOTICE], "dreamco_commercial_terms": DREAMCO_TERMS},
        "created_at": BUILD_TIMESTAMP,
        "onet_version": ONET_VERSION,
        "note": ("Tier authored: scenario prompts, task-intent paraphrases, rubrics and reference answer outlines are DreamCo-original "
                 "(source: authored/practice_tasks_authored.json); each item references an O*NET 31.0 Task ID and O*NET-SOC code "
                 "(task_statements.csv, CC BY 4.0, USDOL/ETA) and no run of 5 or more words of O*NET text is reproduced. "
                 "Tier generated: one DreamCo template prompt, rubric and outline per item around the cited O*NET task statement, "
                 "quoted verbatim with attribution in onet_task_statement (O*NET content, not DreamCo-owned); "
                 f"authorship: {GENERATED_AUTHORSHIP}. O*NET\u00ae is a trademark of USDOL/ETA."),
        "tier_counts": {t: sum(1 for x in all_tasks if x["tier"] == t) for t in ("authored", "generated")},
        "tasks": all_tasks}, indent=2) + "\n")
    gated = 0
    if gate:
        for stem in built:
            r = subprocess.run([sys.executable, str(gate), f"study_plans/{stem}", "--asset-root", ".",
                                "--repo-root", os.path.relpath(REPO_ROOT, ROOT),
                                "--out", f"study_plans/{stem}/license_gate.json"], cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 2:
                raise SystemExit(f"gate error for {stem}: {r.stderr}")
            gated += 1
    else:
        print("WARNING: tools/license_provenance_gate.py not found (set DREAMCO_GATE_TOOL); license_gate.json not regenerated")
    print(f"tiers={ {t: sum(1 for m in sel if m['tier'] == t) for t in ('authored', 'generated')} } majors={len(sel)} links={len(rows)} practice_tasks={len(all_tasks)} gated={gated} gate_tool={gate}")


if __name__ == "__main__":
    main()
