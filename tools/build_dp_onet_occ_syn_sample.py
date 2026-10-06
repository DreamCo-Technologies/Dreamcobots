#!/usr/bin/env python3
"""Build the populated DP-ONET-OCC-SYN sample from the pinned O*NET 31.0 CSV zip.

Reads db_31_0_csv.zip (sha256 verified against the package provenance_manifest.json pin before anything
is parsed), picks a small, deterministic, SOC-major-group-stratified set of data-level occupations, and
writes DreamCo synthesis rows:

  sample/occupations.jsonl      machine layer, one row per occupation (schemas/dp_onet_occ_syn.row.schema.json)
  sample/occupation_cards.md    human layer (DreamCo-authored cards + the O*NET attribution footer)
  assets/<asset_id>/{provenance.json, asset.json, candidate.json}

Rights posture (reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md):
- O*NET 31.0 Database content is CC BY 4.0 (https://www.onetcenter.org/license_db.html). Rows carry only a
  small derived subset (titles, job zone, top-5 element names + importance values, task counts). Occupation
  descriptions and task statement text are NOT copied.
- Every row lists per-field source references (file, member sha256, keys) so each O*NET-derived value can be
  traced; the DreamCo fields (lenses, confidence, practice seed, rubric, analysis) are labelled as DreamCo.
- Attribution, the modification notice and the USDOL/ETA non-endorsement statement are kept on every output.
Nothing here marks anything sellable. candidate.json keeps scorecard_score and owner_approval null.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKU = "DP-ONET-OCC-SYN"  # internal SKU id only; a buyer-facing id is decided before listing
DISPLAY_NAME = "DreamCo Occupation Synthesis Pack (built with O*NET\u00ae 31.0 data)"  # approved by Irean Jordan 2026-10-05 (option A)
SAMPLE_VERSION = "0.0.2"
GENERATOR_VERSION = "build_dp_onet_occ_syn_sample 0.1.1"
ASSET_ID = "dp-onet-occ-syn-sample-0.0.2"
SEED = "dp-onet-occ-syn-0.0.2"
PER_MAJOR_GROUP = 2
TOP_K = 5
ONET_VERSION = "31.0"
ZIP_NAME = "db_31_0_csv.zip"
ZIP_URL = "https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip"
FILE_URL = "https://www.onetcenter.org/dl_files/database/db_31_0_csv/{name}"
MEMBER_PREFIX = "db_31_0_csv/"
FILES = ("occupation_data.csv", "job_zones.csv", "knowledge.csv", "essential_skills.csv",
         "work_activities.csv", "task_statements.csv")
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

ATTRIBUTION_TEXT = (
    "This dataset includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and "
    "Training Administration (USDOL/ETA). Used under the CC BY 4.0 license (https://creativecommons.org/licenses/by/4.0/). "
    "O*NET\u00ae is a trademark of USDOL/ETA. DreamCo has modified all or some of this information. USDOL/ETA has not "
    "approved, endorsed, or tested these modifications. The O*NET\u00ae Database is sponsored by USDOL/ETA and developed by the "
    "National Center for O*NET Development (source: https://www.onetcenter.org/database.html). DreamCo's changes are "
    "listed in MODIFICATIONS.md. The O*NET\u00ae material is provided as-is under CC BY 4.0, including its disclaimer of "
    "warranties (Section 5)."
)

# DreamCo capability lenses: DreamCo's own grouping of O*NET 31.0 work-activity elements (4.A.*).
LENSES = {
    "information_and_analysis": ("4.A.1.", "4.A.2."),
    "people_and_communication": ("4.A.4.a.", "4.A.4.b."),
    "physical_and_equipment": ("4.A.3.a.", "4.A.3.b.2", "4.A.3.b.4", "4.A.3.b.5"),
    "digital_and_records": ("4.A.3.b.1", "4.A.3.b.6", "4.A.4.c."),
}
LENS_LABEL = {
    "information_and_analysis": "information and analysis",
    "people_and_communication": "people and communication",
    "physical_and_equipment": "physical work and equipment",
    "digital_and_records": "digital tools and records",
}
# 31.0 job zones: 2 = "Job Zone 1-2" (zones 1 and 2 are combined in job_zone_reference.csv), 3, 4, 5.
# DreamCo's lens for each O*NET 31.0 knowledge element (2.C.*): a second, separately rated O*NET domain used to
# cross-check the work-activity lens.
KNOWLEDGE_LENS = {
    "information_and_analysis": ("2.C.1.c", "2.C.3.b", "2.C.4.", "2.C.5.a", "2.C.7.d", "2.C.7.e", "2.C.8.b"),
    "people_and_communication": ("2.C.1.a", "2.C.1.d", "2.C.1.e", "2.C.1.f", "2.C.5.b", "2.C.6", "2.C.7.a", "2.C.7.b", "2.C.9.b"),
    "physical_and_equipment": ("2.C.2.", "2.C.3.c", "2.C.3.d", "2.C.3.e", "2.C.7.c", "2.C.8.a", "2.C.10"),
    "digital_and_records": ("2.C.1.b", "2.C.3.a", "2.C.9.a"),
}
PREP_BAND = {1: "little_to_some", 2: "little_to_some", 3: "medium", 4: "considerable", 5: "extensive"}
ONET_FIELDS = ("onet_soc_code", "onet_title", "job_zone", "top_knowledge", "top_essential_skills",
               "top_work_activities", "task_counts")
DREAMCO_FIELDS = ("preparation_band", "capability_lenses", "lens_lift", "dominant_lens", "knowledge_lens", "data_confidence",
                  "dreamco_synthesis")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pinned_zip_sha(provenance_manifest: Path) -> str:
    pm = json.loads(provenance_manifest.read_text(encoding="utf-8"))
    for src in pm.get("planned_sources", []) + pm.get("sources", []):
        for d in src.get("downloads", []):
            if d.get("name") == ZIP_NAME:
                return d["sha256"]
    raise SystemExit(f"no {ZIP_NAME} pin in {provenance_manifest}")


def load_tables(zip_path: Path, expected_sha: str) -> tuple[dict, dict]:
    """Return ({file: rows}, {file: member sha256}) after verifying the zip pin."""
    raw = zip_path.read_bytes()
    got = sha256_bytes(raw)
    if got != expected_sha:
        raise SystemExit(f"{zip_path}: sha256 {got} != pinned {expected_sha}; refusing to build")
    tables, hashes = {}, {}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for name in FILES:
            data = zf.read(MEMBER_PREFIX + name)
            hashes[name] = sha256_bytes(data)
            tables[name] = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    return tables, hashes


def _index_ratings(rows: list[dict]) -> dict:
    out: dict = defaultdict(list)
    for r in rows:
        if r["Scale ID"] == "IM":
            out[r["O*NET-SOC Code"]].append(r)
    return out


def select_occupations(tables: dict, per_group: int = PER_MAJOR_GROUP, seed: str = SEED) -> list[str]:
    """Data-level occupations (job zone + knowledge + essential skills + work activities + >=1 core task),
    stratified by SOC major group; within a group, the per_group codes with the smallest sha256(seed:code)."""
    jz = {r["O*NET-SOC Code"] for r in tables["job_zones.csv"]}
    kn = set(_index_ratings(tables["knowledge.csv"]))
    es = set(_index_ratings(tables["essential_skills.csv"]))
    wa = set(_index_ratings(tables["work_activities.csv"]))
    core = {r["O*NET-SOC Code"] for r in tables["task_statements.csv"] if r["Task Type"] == "Core"}
    groups: dict = defaultdict(list)
    for r in tables["occupation_data.csv"]:
        c = r["O*NET-SOC Code"]
        if c in jz and c in kn and c in es and c in wa and c in core:
            groups[c[:2]].append(c)
    picked = []
    for g in sorted(groups):
        ranked = sorted(groups[g], key=lambda c: sha256_bytes(f"{seed}:{c}".encode()))
        picked += sorted(ranked[:per_group])
    return sorted(picked)


def _top(ratings: list[dict], k: int = TOP_K) -> tuple[list[dict], int]:
    usable = [r for r in ratings if r.get("Recommend Suppress") != "Y"]
    suppressed = len(ratings) - len(usable)
    usable.sort(key=lambda r: (-float(r["Data Value"]), r["Element ID"]))
    return [{"element_id": r["Element ID"], "element_name": r["Element Name"], "importance": round(float(r["Data Value"]), 2)}
            for r in usable[:k]], suppressed


def _lens_scores(wa: list[dict]) -> dict:
    scores = {}
    for lens, prefixes in LENSES.items():
        vals = [float(r["Data Value"]) for r in wa if r.get("Recommend Suppress") != "Y"
                and any(r["Element ID"].startswith(p) or r["Element ID"] == p for p in prefixes)]
        scores[lens] = round((sum(vals) / len(vals) - 1) / 4, 3) if vals else 0.0
    return scores


def _ym(date: str) -> str:  # O*NET dates are MM/YYYY
    m, y = date.split("/")
    return f"{y}-{m}"


def _confidence(used: list[dict], suppressed_total: int) -> dict:
    ns = [int(r["N"]) for r in used if r.get("N", "").isdigit()]
    dates = sorted(_ym(r["Date"]) for r in used if r.get("Date"))
    sources = sorted({r["Domain Source"] for r in used if r.get("Domain Source")})
    oldest = dates[0] if dates else None
    min_n = min(ns) if ns else None
    band = "high"
    if (oldest and oldest < "2021-01") or suppressed_total > 3:
        band = "medium"
    if (oldest and oldest < "2017-01") or suppressed_total > 10:
        band = "low"
    return {"band": band, "min_n": min_n, "suppressed_ratings_excluded": suppressed_total, "rating_sources": sources,
            "oldest_rating": oldest, "newest_rating": dates[-1] if dates else None}


def _lens_of(element_id: str) -> str | None:
    for lens, prefixes in LENSES.items():
        if any(element_id.startswith(p) or element_id == p for p in prefixes):
            return lens
    return None


def _knowledge_lens(top_kn: list[dict], element_means: dict) -> str:
    """Lens with the largest summed lift (importance minus the all-occupation mean for that element) among the top
    knowledge elements, so universally high elements (e.g. English Language) do not decide the lens."""
    votes = {lens: 0.0 for lens in KNOWLEDGE_LENS}
    for e in top_kn:
        for lens, prefixes in KNOWLEDGE_LENS.items():
            if any(e["element_id"] == p or (p.endswith(".") and e["element_id"].startswith(p)) for p in prefixes):
                votes[lens] += e["importance"] - element_means.get(e["element_id"], 0.0)
    return max(sorted(votes), key=lambda k: votes[k])


def baselines(tables: dict) -> dict:
    """All-occupation means in O*NET 31.0: per knowledge element (IM) and per DreamCo lens (work activities, IM)."""
    sums: dict = defaultdict(lambda: [0.0, 0])
    for r in tables["knowledge.csv"]:
        if r["Scale ID"] == "IM" and r.get("Recommend Suppress") != "Y":
            sums[r["Element ID"]][0] += float(r["Data Value"])
            sums[r["Element ID"]][1] += 1
    element_means = {k: v[0] / v[1] for k, v in sums.items()}
    per_occ = [_lens_scores(rows) for rows in _index_ratings(tables["work_activities.csv"]).values()]
    lens_means = {lens: sum(o[lens] for o in per_occ) / len(per_occ) for lens in LENSES}
    return {"knowledge_element_means": element_means, "lens_means": lens_means}


def build_row(code: str, tables: dict, hashes: dict, base: dict | None = None) -> dict:
    base = base or baselines(tables)
    occ = next(r for r in tables["occupation_data.csv"] if r["O*NET-SOC Code"] == code)
    title = occ["Title"]
    job_zone = int(next(r["Job Zone"] for r in tables["job_zones.csv"] if r["O*NET-SOC Code"] == code))
    kn_all = _index_ratings(tables["knowledge.csv"])[code]
    es_all = _index_ratings(tables["essential_skills.csv"])[code]
    wa_all = _index_ratings(tables["work_activities.csv"])[code]
    top_kn, s1 = _top(kn_all)
    top_es, s2 = _top(es_all)
    top_wa, s3 = _top(wa_all)
    tasks = [r for r in tables["task_statements.csv"] if r["O*NET-SOC Code"] == code]
    counts = {"core": sum(r["Task Type"] == "Core" for r in tasks),
              "supplemental": sum(r["Task Type"] == "Supplemental" for r in tasks),
              "unclassified": sum(r["Task Type"] not in ("Core", "Supplemental") for r in tasks)}
    lenses = _lens_scores(wa_all)
    lift = {k: round(lenses[k] - base["lens_means"][k], 3) for k in lenses}
    dominant = max(sorted(lift), key=lambda k: lift[k])  # relative to the all-occupation lens mean
    used = [r for r in kn_all + es_all + wa_all if r.get("Recommend Suppress") != "Y"]
    conf = _confidence(used, s1 + s2 + s3)
    top_activity_lens = _lens_of(top_wa[0]["element_id"])

    agree, caveats, improve = [], [], []
    if top_activity_lens == dominant:
        agree.append(f"The highest-rated work activity ('{top_wa[0]['element_name']}') sits in the dominant DreamCo lens "
                     f"({LENS_LABEL[dominant]}), so the lens summary and the single top activity tell the same story.")
    else:
        caveats.append(f"The highest-rated work activity ('{top_wa[0]['element_name']}') is outside the dominant DreamCo lens "
                       f"({LENS_LABEL[dominant]}); treat the lens as an average, not the defining activity.")
    kn_lens = _knowledge_lens(top_kn, base["knowledge_element_means"])
    if kn_lens == dominant:
        agree.append(f"Two separately rated O*NET\u00ae domains agree: the top knowledge areas and the work activities both point to "
                     f"{LENS_LABEL[dominant]}.")
    else:
        caveats.append(f"The top knowledge areas point to {LENS_LABEL[kn_lens]} while the work activities point to "
                       f"{LENS_LABEL[dominant]}; read this as a hybrid role and test both sides in practice drills.")
    if conf["oldest_rating"] and conf["oldest_rating"] < "2021-01":
        caveats.append(f"Some ratings date from {conf['oldest_rating']}; refresh against a later O*NET\u00ae Database release before relying on them.")
    if conf["suppressed_ratings_excluded"]:
        caveats.append(f"{conf['suppressed_ratings_excluded']} rating(s) flagged 'Recommend Suppress' in the O*NET\u00ae data were left out of the rankings.")
    if conf["min_n"] is not None and conf["min_n"] < 10:
        caveats.append(f"Smallest respondent or rater count behind the ranked values is {conf['min_n']}, so small shifts in the ranking are noise.")
    if job_zone <= 2:
        improve.append("Pair with short-credential or on-the-job pathways; a four-year-degree framing would misdescribe entry.")
    elif job_zone == 5:
        improve.append("Add a graduate or licensure milestone to any pathway built from this card.")
    else:
        improve.append("Add a concrete certification or program example per region before using this card for advising.")
    if counts["supplemental"] > counts["core"]:
        improve.append("More supplemental than core tasks: practice drills should sample core tasks first.")

    seed_text = (f"Scenario drill ({LENS_LABEL[dominant]}): you are supporting work in the occupation '{title}'. "
                 f"Plan how you would handle the activity '{top_wa[0]['element_name'].lower()}' using what you know about "
                 f"{top_kn[0]['element_name'].lower()} and {top_kn[1]['element_name'].lower()}. Explain how "
                 f"{top_es[0]['element_name'].lower()} changes your approach, name one risk you would escalate, and say what "
                 f"you are unsure about.")
    rubric = [f"Uses {top_kn[0]['element_name']} concepts correctly",
              f"Uses {top_kn[1]['element_name']} concepts correctly",
              f"Shows {top_es[0]['element_name']} in the answer",
              f"Plan fits the activity '{top_wa[0]['element_name']}'",
              "Names a realistic risk and when to escalate",
              "States uncertainty instead of inventing facts"]
    perspectives = conf["rating_sources"]

    def ref(file: str, fields: list[str], keys: list[str]) -> dict:
        return {"source_id": "onet_db_31_0", "version": ONET_VERSION, "file": file, "file_sha256": hashes[file],
                "keys": keys, "fields": fields}
    source_refs = [
        ref("occupation_data.csv", ["onet_soc_code", "onet_title"], [code]),
        ref("job_zones.csv", ["job_zone"], [code]),
        ref("knowledge.csv", ["top_knowledge", "knowledge_lens"],
            [f"{code}|{e['element_id']}|IM" for e in top_kn] + ["all-occupation element means (2.C.*|IM)"]),
        ref("essential_skills.csv", ["top_essential_skills"], [f"{code}|{e['element_id']}|IM" for e in top_es]),
        ref("work_activities.csv", ["top_work_activities", "capability_lenses", "lens_lift", "dominant_lens"],
            [f"{code}|4.A.*|IM", "all-occupation lens means (4.A.*|IM)"]),
        ref("task_statements.csv", ["task_counts"], [code]),
        {"source_id": "dreamco_synthesis", "version": SAMPLE_VERSION, "file": "tools/build_dp_onet_occ_syn_sample.py",
         "generator_version": GENERATOR_VERSION, "keys": [code], "fields": list(DREAMCO_FIELDS),
         "derived_from": ["occupation_data.csv", "job_zones.csv", "knowledge.csv", "essential_skills.csv",
                          "work_activities.csv", "task_statements.csv"]},
    ]
    return {
        "record_id": f"{SKU.lower()}/{SAMPLE_VERSION}/{code}",
        "sku_id": SKU,
        "package_version": SAMPLE_VERSION,
        "source_version": f"O*NET {ONET_VERSION}",
        "onet_soc_code": code,
        "onet_title": title,
        "soc_major_group": code[:2],
        "job_zone": job_zone,
        "preparation_band": PREP_BAND[job_zone],
        "top_knowledge": top_kn,
        "top_essential_skills": top_es,
        "top_work_activities": top_wa,
        "task_counts": counts,
        "capability_lenses": lenses,
        "lens_lift": lift,
        "dominant_lens": dominant,
        "knowledge_lens": kn_lens,
        "data_confidence": conf,
        "dreamco_synthesis": {
            "practice_task_seed": seed_text,
            "rubric_dimensions": rubric,
            "analysis": {"agree": agree, "caveats": caveats, "improve": improve,
                         "still_need_test": ["Practice seed and rubric are template-generated and have not been graded "
                                             "by a person or benchmarked; no validation evidence exists yet."]},
            "evidence_perspectives": perspectives,
        },
        "source_refs": source_refs,
        "license": {
            "onet_derived_fields": list(ONET_FIELDS),
            "onet_license": "CC BY 4.0 (O*NET 31.0 Database, USDOL/ETA); recipients keep every CC BY 4.0 right in these values",
            "dreamco_fields": list(DREAMCO_FIELDS),
            "dreamco_terms": "DreamCo synthesis layer; commercial terms not set (see LICENSE). Embeds O*NET\u00ae element names, so the O*NET\u00ae attribution still applies.",
            "attribution": "See ATTRIBUTION.md (O*NET 31.0 Database, USDOL/ETA, CC BY 4.0; modified by DreamCo; not endorsed by USDOL/ETA)",
        },
    }


def render_cards(rows: list[dict]) -> str:
    out = [f"# {DISPLAY_NAME}: occupation cards, {SAMPLE_VERSION} sample ({len(rows)} occupations)", "",
           f"Internal SKU id: {SKU} (internal only; a buyer-facing id is decided before listing).", "",
           "DreamCo-authored cards built with O*NET\u00ae 31.0 data. Values in the 'O*NET\u00ae-derived' lines are a small derived "
           "subset of O*NET\u00ae data (rankings by importance); everything under 'DreamCo view' is DreamCo's own synthesis. "
           "Not for sale; not production ready.", ""]
    for r in rows:
        syn = r["dreamco_synthesis"]
        out += [f"## {r['onet_soc_code']} {r['onet_title']}", "",
                f"- O*NET\u00ae-derived: Job Zone {r['job_zone']}; top knowledge: "
                + ", ".join(f"{e['element_name']} ({e['importance']})" for e in r["top_knowledge"][:3])
                + "; top essential skills: " + ", ".join(e["element_name"] for e in r["top_essential_skills"][:3])
                + "; top work activities: " + ", ".join(e["element_name"] for e in r["top_work_activities"][:3])
                + f"; tasks: {r['task_counts']['core']} core / {r['task_counts']['supplemental']} supplemental.",
                f"- DreamCo view: preparation band `{r['preparation_band']}`, dominant lens `{r['dominant_lens']}`, "
                f"data confidence `{r['data_confidence']['band']}`.",
                f"- Practice seed: {syn['practice_task_seed']}",
                "- DreamCo analysis: " + " ".join(syn["analysis"]["agree"] + syn["analysis"]["caveats"] + syn["analysis"]["improve"]),
                ""]
    out += ["---", "", ATTRIBUTION_TEXT, ""]
    return "\n".join(out)


def provenance_record(rows_file: Path, cards_file: Path, hashes: dict, zip_sha: str, generated_at: str, rel: dict) -> dict:
    ml, hl = sha256_bytes(rows_file.read_bytes()), sha256_bytes(cards_file.read_bytes())
    integrity = sha256_bytes(f"{ml}  {rel['rows']}\n{hl}  {rel['cards']}\n".encode())
    return {
        "schema": "dreamco.data_package_asset_provenance.v1",
        "asset_id": ASSET_ID,
        "title": f"{DISPLAY_NAME}: {SAMPLE_VERSION} populated sample",
        "evidence_id": f"{ASSET_ID}-onet31.0-{generated_at[:10]}",
        "capability_id": "occupation-synthesis",
        "source_type": "onet",
        "source_reference": ZIP_URL,
        "retrieved_at": generated_at[:10],
        "content_version": f"O*NET {ONET_VERSION} (db_31_0_csv.zip sha256 {zip_sha})",
        "license_or_usage_basis": "CC BY 4.0 for O*NET 31.0 Database content (USDOL/ETA, https://www.onetcenter.org/license_db.html); DreamCo synthesis layer, commercial terms not yet set",
        "transformation": "derived_metric",
        "evaluator_version": GENERATOR_VERSION,
        "integrity_hash": f"sha256:{integrity}",
        "ownership_class": "open_license_with_conditions",
        "creator": "DreamCo (Grok-Data-Package-Merchant, tools/build_dp_onet_occ_syn_sample.py)",
        "owner": "Mixed: O*NET\u00ae-derived values and names are USDOL/ETA content under CC BY 4.0; lens scores, confidence bands, practice seeds, rubrics and analysis are DreamCo-derived",
        "asset_files": [{"path": rel["rows"], "sha256": ml, "bytes": rows_file.stat().st_size},
                        {"path": rel["cards"], "sha256": hl, "bytes": cards_file.stat().st_size}],
        "sources": [{
            "source_id": "onet_db_31_0",
            "title": "O*NET 31.0 Database (CSV)",
            "publisher": "U.S. Department of Labor, Employment and Training Administration (USDOL/ETA); developed by the National Center for O*NET Development",
            "url": ZIP_URL,
            "version": ONET_VERSION,
            "sha256": zip_sha,
            "files": [{"name": n, "url": FILE_URL.format(name=n), "sha256": hashes[n]} for n in FILES],
            "retrieved_at": generated_at[:10],
            "license": "CC BY 4.0",
            "license_url": LICENSE_URL,
            "ownership_class": "open_license_with_conditions",
            "commercial_use_allowed": True,
            "redistribution_allowed": True,
            "ai_training_allowed": True,
            "attribution_required": True,
            "share_alike_required": False,
            "required_notices": [
                "This page includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET\u00ae is a trademark of USDOL/ETA.",
                "DreamCo has modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications.",
            ],
            "restrictions": [
                "Use 'O*NET' only as an adjective followed by a generic noun (e.g. 'built with O*NET\u00ae data'), with the \u00ae symbol; never possessive or plural; never imply USDOL/ETA endorsement.",
                "Do not offer terms or technical measures that restrict a recipient's CC BY 4.0 rights in the O*NET\u00ae-derived values (CC BY 4.0 s.2(a)(5)(B)).",
                "Downloadable database files only; O*NET Web Services data (no modification, non-transferable) and Career Exploration Tools (CC BY-ND / Tools Developer License) are not sources for this asset.",
            ],
        }],
        "derived_components": [
            {"component": "onet_derived_values", "ownership_class": "open_license_with_conditions", "derivation_type": "structured_extraction",
             "description": "O*NET-SOC code and title, job zone, top-5 knowledge / essential-skill / work-activity elements by Importance (IM, ratings flagged Recommend Suppress excluded), and core/supplemental task counts. No occupation descriptions or task statement text.",
             "derived_from": ["onet_db_31_0"]},
            {"component": "dreamco_lenses_and_confidence", "ownership_class": "open_license_with_conditions", "derivation_type": "derived_metric",
             "description": "DreamCo capability-lens scores (mean IM of DreamCo-grouped 4.A.* elements, rescaled 0-1), lift over the all-occupation lens mean, dominant lens (largest lift), knowledge lens (largest lift of top knowledge elements over all-occupation element means), preparation band and data-confidence band (dates, N, suppressed count, rating sources). DreamCo method over O*NET\u00ae values.",
             "derived_from": ["onet_derived_values"]},
            {"component": "dreamco_synthesis_text", "ownership_class": "synthetic_generated_by_dreamco", "derivation_type": "synthetic_data",
             "description": "Template-generated DreamCo practice seed, rubric dimensions and agree/caveat/improve/still-need-test analysis. Embeds O*NET\u00ae titles and element names, so the O*NET\u00ae attribution still applies.",
             "derived_from": ["onet_derived_values", "dreamco_lenses_and_confidence"]},
        ],
        "transformation_history": [
            {"step": "verify db_31_0_csv.zip sha256 against provenance_manifest.json pin; read 6 CSV members in memory",
             "tool": "tools/build_dp_onet_occ_syn_sample.py", "tool_version": GENERATOR_VERSION, "at": generated_at, "inputs": ["onet_db_31_0"]},
            {"step": f"select {PER_MAJOR_GROUP} data-level occupations per SOC major group (sha256 seed '{SEED}'), derive rows, render cards",
             "tool": "tools/build_dp_onet_occ_syn_sample.py", "tool_version": GENERATOR_VERSION, "at": generated_at, "inputs": ["onet_db_31_0"]},
        ],
        "attribution_text": ATTRIBUTION_TEXT,
        "review_status": "unreviewed",
        "human_review": None,
        "notes": ["Per-row source_refs in sample/occupations.jsonl name the file, member sha256 and keys behind each O*NET\u00ae-derived field.",
                  "Run tools/score_data_package_dataset.py for the dataset QA scorecard; QA is integrity evidence, not validation evidence."],
    }


def asset_record(prov: dict, rel: dict, generated_at: str) -> dict:
    files = {f["path"]: f["sha256"] for f in prov["asset_files"]}
    return {
        "schema": "dreamco.data_package_synthesis_asset.v1",
        "asset_id": ASSET_ID,
        "title": prov["title"],
        "capability_ids": ["occupation-synthesis", "career-pathway-study-plan"],
        "perspectives_used": ["official_documentation"],
        "source_refs": [{"source_id": "onet_db_31_0", "version": ONET_VERSION, "pinned_by": "provenance.json#sources",
                         "perspective": "official_documentation"}],
        "ownership_class": prov["ownership_class"],
        "commercial_redistribution_allowed": True,
        "attribution_required": True,
        "share_alike_required": False,
        "human_layer": {"path": rel["cards"], "format": "markdown", "sha256": files[rel["cards"]],
                        "elements": ["occupation cards", "practice seeds", "DreamCo analysis", "attribution footer"]},
        "machine_layer": {"path": rel["rows"], "format": "jsonl", "sha256": files[rel["rows"]],
                          "elements": ["O*NET\u00ae-derived values", "capability lenses", "data confidence", "practice seed", "rubric", "analysis", "per-row source_refs"]},
        "dreamco_analysis": {
            "agree": ["Within the O*NET\u00ae 31.0 data, incumbent/expert-rated knowledge and activities and analyst-rated essential skills give consistent top elements for most sampled occupations (see per-row analysis.agree)."],
            "reject": [],
            "improve": ["Add a second, independent perspective (e.g. BLS wages/outlook or CIP program data) so the synthesis is multi-view rather than single-source."],
            "still_need_test": ["Practice seeds and rubrics have no human grading, benchmark, holdout or regression evidence yet."],
        },
        "validation_evidence_ids": {"sandbox": [], "benchmark": [], "holdout": [], "regression": []},
        "integrity_hash": prov["integrity_hash"],
        "created_at": generated_at,
        "generator_version": GENERATOR_VERSION,
        "notes": ["perspectives_used has one entry: every value comes from one official source (the O*NET\u00ae 31.0 Database). Rating-source mix (incumbent, occupational expert, analyst) is recorded per row as evidence_perspectives, but that is still one publisher.",
                  "validation_evidence_ids are empty on purpose: the dataset QA scorecard and pytest are integrity checks, not validation."],
    }


def candidate_record() -> dict:
    return {
        "candidate_id": ASSET_ID, "asset_id": ASSET_ID,
        "title": f"{DISPLAY_NAME}: {SAMPLE_VERSION} populated sample",
        "category": "occupational-data/synthesis", "data_types": ["jsonl", "markdown"],
        "rights_basis": "CC BY 4.0 (O*NET 31.0 Database, USDOL/ETA) + DreamCo synthesis",
        "ownership_class": "open_license_with_conditions",
        "commercial_use_allowed": True, "redistribution_allowed": True, "flags": [],
        "provenance_path": "provenance.json", "asset_path": "asset.json",
        "scorecard_score": None, "owner_approval": None,
    }


def build(zip_path: Path, pkg: Path, provenance_manifest: Path, generated_at: str) -> dict:
    tables, hashes = load_tables(zip_path, pinned_zip_sha(provenance_manifest))
    codes = select_occupations(tables)
    base = baselines(tables)
    rows = [build_row(c, tables, hashes, base) for c in codes]
    rel = {"rows": "sample/occupations.jsonl", "cards": "sample/occupation_cards.md"}
    (pkg / "sample").mkdir(parents=True, exist_ok=True)
    rows_file, cards_file = pkg / rel["rows"], pkg / rel["cards"]
    rows_file.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    cards_file.write_text(render_cards(rows), encoding="utf-8")
    adir = pkg / "assets" / ASSET_ID
    adir.mkdir(parents=True, exist_ok=True)
    prov = provenance_record(rows_file, cards_file, hashes, sha256_bytes(zip_path.read_bytes()), generated_at, rel)
    (adir / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (adir / "asset.json").write_text(json.dumps(asset_record(prov, rel, generated_at), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (adir / "candidate.json").write_text(json.dumps(candidate_record(), indent=2) + "\n", encoding="utf-8")
    return {"rows": len(rows), "codes": codes, "member_sha256": hashes, "asset_dir": str(adir)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--onet-zip", required=True, help="Local copy of db_31_0_csv.zip (verified against the pin)")
    ap.add_argument("--package-dir", default=str(ROOT / "data/dreamco_knowledge/packages" / SKU / SAMPLE_VERSION))
    ap.add_argument("--provenance-manifest", help="Pin source (default: <package-dir>/provenance_manifest.json)")
    ap.add_argument("--generated-at", required=True, help="ISO timestamp recorded in provenance (reproducible output)")
    args = ap.parse_args(argv)
    pkg = Path(args.package_dir)
    pm = Path(args.provenance_manifest) if args.provenance_manifest else pkg / "provenance_manifest.json"
    print(json.dumps(build(Path(args.onet_zip), pkg, pm, args.generated_at), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
