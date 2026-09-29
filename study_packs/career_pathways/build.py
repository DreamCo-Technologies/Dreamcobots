"""Build majors -> O*NET occupations -> study plans from official raw files only.
Sources: O*NET 31.0 Database (USDOL/ETA, CC BY 4.0) and O*NET CIP 2020 -> O*NET-SOC 2019 crosswalk.
"""
import csv, json, re, pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent
RAW, DATA, PLANS = ROOT / "raw", ROOT / "data", ROOT / "study_plans"
PROVENANCE = ("---\n**Provenance.** Major-to-occupation links come from the O*NET Resource Center "
              "`Education_CIP_to_ONET_SOC.xlsx` crosswalk (2020 CIP to O*NET-SOC 2019). Knowledge and skill "
              "importance values come from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and "
              "Training Administration (USDOL/ETA), used under the CC BY 4.0 license. USDOL/ETA has not approved, "
              "endorsed, or tested these modifications. The 4-year outline is DreamCo-derived guidance, not O*NET data.\n")

MAJORS = ["11.0701", "14.0901", "11.0401", "51.3801", "42.0101", "26.0101", "14.1901", "14.0801", "14.1001",
          "52.0301", "52.0201", "52.0801", "52.1401", "45.0601", "45.1001", "13.1202", "40.0501", "40.0801",
          "27.0101", "27.0501", "23.0101", "09.0101", "44.0701", "43.0104", "51.2001", "50.0409", "03.0104"]

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

def top_elements(path, socs, n):
    df = pd.read_csv(path, dtype={"O*NET-SOC Code": str})
    df = df[(df["Scale ID"] == "IM") & (df["O*NET-SOC Code"].isin(socs))]
    if df.empty:
        return []
    g = df.groupby("Element Name")["Data Value"].mean().sort_values(ascending=False).head(n)
    return [(k, round(float(v), 2)) for k, v in g.items()]

def plan_md(cip, title, occs, know, skills):
    lines = [f"# Study plan: {title} (CIP {cip})", "",
             "## Linked O*NET occupations", ""]
    lines += [f"- `{s}` {t}" for s, t in occs]
    lines += ["", "## Most important knowledge areas (O*NET importance, 1 to 5, averaged over linked occupations)", ""]
    lines += [f"- {k} ({v})" for k, v in know] or ["- No O*NET knowledge ratings for these occupations."]
    lines += ["", "## Most important foundational skills (O*NET importance, 1 to 5)", ""]
    lines += [f"- {k} ({v})" for k, v in skills] or ["- No O*NET skill ratings for these occupations."]
    k = [x[0] for x in know]; s = [x[0] for x in skills]
    lines += ["", "## 4-year outline (DreamCo-derived guidance, not O*NET data)", "",
              f"1. Year 1, foundations. General education plus deliberate practice in {', '.join(s[:3]) or 'core skills'}.",
              f"2. Year 2, core knowledge. Introductory courses in {', '.join(k[:3]) or 'the major core'}.",
              f"3. Year 3, depth. Advanced courses in {', '.join(k[3:6]) or 'major electives'}, plus {', '.join(s[3:5]) or 'applied skills'} through projects.",
              f"4. Year 4, launch. Internship or capstone aimed at {occs[0][1] if occs else 'a target occupation'}; build a portfolio showing {', '.join(k[:2]) or 'major knowledge'}.",
              "", PROVENANCE]
    return "\n".join(lines)

def main():
    DATA.mkdir(exist_ok=True); PLANS.mkdir(exist_ok=True)
    for p in PLANS.glob("*.md"): p.unlink()
    cw = load_crosswalk()
    occ = pd.read_csv(RAW / "occupation_data.csv", dtype=str)
    valid = set(occ["O*NET-SOC Code"])
    sel, rows = [], []
    for cip in MAJORS:
        sub = cw[(cw.cip == cip) & (cw.soc.isin(valid))]
        if sub.empty:
            continue
        title = sub.cip_title.iloc[0].strip().rstrip(".")
        occs = list(dict.fromkeys(zip(sub.soc, sub.soc_title.str.strip())))
        socs = [o[0] for o in occs]
        know = top_elements(RAW / "knowledge.csv", socs, 8)
        skills = top_elements(RAW / "essential_skills.csv", socs, 6)
        for s, t in occs:
            rows.append([cip, title, s, t])
        sel.append({"cip": cip, "title": title, "occupations": [{"soc": s, "title": t} for s, t in occs],
                    "top_knowledge": know, "top_skills": skills})
        (PLANS / f"{cip}_{slug(title)}.md").write_text(plan_md(cip, title, occs, know, skills))
    with open(DATA / "major_to_onet.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cip_code", "cip_title", "onet_soc_code", "occupation_title"]); w.writerows(rows)
    (DATA / "majors_selected.json").write_text(json.dumps(sel, indent=2))
    print(f"majors={len(sel)} links={len(rows)}")

if __name__ == "__main__":
    main()
