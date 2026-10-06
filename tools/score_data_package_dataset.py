#!/usr/bin/env python3
"""Dataset QA scorecard for a populated DreamCo data-package version (rows in sample/*.jsonl).

Checks (config/data_package_dataset_qa_scorecard.json): completeness, schema_validity, referential_integrity,
deduplication, value_ranges, freshness_version_match, provenance_coverage, synthesis_perspective. Each check has
metrics in [0, 1] with pass/warn thresholds; hard checks that fail or cannot run (no reference data) fail the
scorecard. Reference data is the pinned O*NET release: pass --onet-zip (sha256 verified against the package
provenance_manifest.json pin) or --onet-csv-dir (member sha256 compared with the asset provenance pins).

Truth boundary: the QA result is integrity evidence. It is not the dataset_evaluation_scorecard score, not
validation evidence for tools/license_provenance_gate.py, and not a sale approval.
Exit codes: 0 pass or warn, 1 fail, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

CONFIG = ROOT / "config" / "data_package_dataset_qa_scorecard.json"
SCHEMA_ID = "dreamco.data_package_dataset_qa_scorecard.v1"
REFERENCE_FILES = ("occupation_data.csv", "task_statements.csv", "knowledge.csv", "essential_skills.csv", "work_activities.csv")
WORD_RE = re.compile(r"[a-z0-9]+")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _display_path(p: Path) -> str:
    """Repo-relative path when the package is inside this repo (keeps local paths out of committed reports)."""
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def _empty(v: Any) -> bool:
    return v is None or v == "" or v == [] or v == {}


def _get(row: dict, dotted: str) -> Any:
    cur: Any = row
    for part in dotted.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def _texts(v: Any) -> list[str]:
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return [t for x in v for t in _texts(x)]
    if isinstance(v, dict):
        return [t for x in v.values() for t in _texts(x)]
    return []


def _ngrams(text: str, n: int) -> set[tuple[str, ...]]:
    w = WORD_RE.findall(text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


# ---------------------------------------------------------------- inputs

def load_rows(path: Path) -> tuple[list[dict], list[str]]:
    rows, errors = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {i}: not JSON ({exc.msg})")
            continue
        if not isinstance(obj, dict):
            errors.append(f"line {i}: not a JSON object")
            continue
        rows.append(obj)
    return rows, errors


def find_asset_provenance(pkg: Path, manifest: dict) -> Path | None:
    for a in manifest.get("assets", []):
        p = pkg / a["provenance_path"]
        if p.is_file():
            return p
    hits = sorted(pkg.glob("assets/*/provenance.json"))
    return hits[0] if hits else None


def pinned_zip_sha(pkg: Path, profile: dict) -> str | None:
    pm_path = pkg / profile["pin"]["provenance_manifest"]
    if not pm_path.is_file():
        return None
    pm = json.loads(pm_path.read_text(encoding="utf-8"))
    for src in pm.get("planned_sources", []) + pm.get("sources", []):
        for d in src.get("downloads", []):
            if d.get("name") == profile["pin"]["zip_name"]:
                return d.get("sha256")
    return None


def load_reference(profile: dict, pkg: Path, onet_zip: Path | None, onet_csv_dir: Path | None) -> tuple[dict | None, dict, list[str]]:
    """Return (tables or None, {file: sha256 of the bytes read}, notes)."""
    notes: list[str] = []
    raw: dict[str, bytes] = {}
    if onet_zip:
        want = pinned_zip_sha(pkg, profile)
        got = _sha(onet_zip.read_bytes())
        if want is None:
            notes.append(f"no {profile['pin']['zip_name']} pin in {profile['pin']['provenance_manifest']}; reference not trusted")
            return None, {}, notes
        if got != want:
            notes.append(f"{onet_zip.name} sha256 {got} != pinned {want}; reference rejected")
            return None, {}, notes
        with zipfile.ZipFile(onet_zip) as zf:
            for name in REFERENCE_FILES:
                raw[name] = zf.read(profile["pin"]["member_prefix"] + name)
        notes.append(f"reference: {onet_zip.name} sha256 matches the package pin")
    elif onet_csv_dir:
        for name in REFERENCE_FILES:
            p = onet_csv_dir / name
            if not p.is_file():
                notes.append(f"reference file missing: {p}")
                return None, {}, notes
            raw[name] = p.read_bytes()
        notes.append(f"reference: CSV directory {onet_csv_dir} (member hashes compared with provenance pins)")
    else:
        notes.append("no reference data (--onet-zip / --onet-csv-dir); reference-dependent metrics not_run")
        return None, {}, notes
    tables = {n: list(csv.DictReader(io.StringIO(b.decode("utf-8-sig")))) for n, b in raw.items()}
    return tables, {n: _sha(b) for n, b in raw.items()}, notes


# ---------------------------------------------------------------- checks

def _result(cid: str, cfg: dict, metrics: dict[str, float | None], reasons: list[str]) -> dict:
    spec = cfg["checks"][cid]
    status = "pass"
    for name, val in metrics.items():
        th = spec["metrics"][name]
        if val is None:
            status = "not_run"
            break
        if val < th["warn_min"]:
            status = "fail"
        elif val < th["pass_min"] and status == "pass":
            status = "warn"
    vals = [v for v in metrics.values() if v is not None]
    score = 0.0 if status == "not_run" or not vals else round(100 * sum(vals) / len(vals), 2)
    return {"id": cid, "status": status, "hard": spec["hard"], "weight": spec["weight"], "score": score,
            "metrics": {k: (None if v is None else round(v, 4)) for k, v in metrics.items()},
            "thresholds": spec["metrics"], "reasons": reasons[:50]}


def _ratio(ok: int, total: int) -> float:
    return ok / total if total else 0.0


def check_completeness(rows, profile, cfg, **_):
    req = profile["required_fields"]
    cells = len(rows) * len(req)
    missing = [(r.get("record_id", f"row{i}"), f) for i, r in enumerate(rows) for f in req if _empty(r.get(f))]
    return _result("completeness", cfg, {"required_field_fill_rate": _ratio(cells - len(missing), cells)},
                   [f"{rid}: {f} empty" for rid, f in missing])


def check_schema(rows, profile, cfg, parse_errors=(), **_):
    schema = load_schema(ROOT / profile["row_schema"])
    reasons, ok = list(parse_errors), 0
    for i, r in enumerate(rows):
        errs = validate(r, schema)
        ok += not errs
        reasons += [f"{r.get('record_id', f'row{i}')}: {e}" for e in errs[:5]]
    total = len(rows) + len(parse_errors)
    return _result("schema_validity", cfg, {"rows_valid": _ratio(ok, total), "rows_parse": _ratio(len(rows), total)}, reasons)


def check_referential(rows, profile, cfg, ref=None, **_):
    if ref is None:
        return _result("referential_integrity", cfg, {m: None for m in cfg["checks"]["referential_integrity"]["metrics"]},
                       ["no pinned O*NET reference data supplied"])
    titles = {r["O*NET-SOC Code"]: r["Title"] for r in ref["occupation_data.csv"]}
    names, values = {}, {}
    for field, fname in profile["element_lists"].items():
        names[fname] = {}
        for r in ref[fname]:
            names[fname][r["Element ID"]] = r["Element Name"]
            if r["Scale ID"] == "IM":
                values[(fname, r["O*NET-SOC Code"], r["Element ID"])] = round(float(r["Data Value"]), 2)
    reasons = []
    codes_ok = titles_ok = 0
    el_total = el_ok = val_ok = 0
    for r in rows:
        code = r.get("onet_soc_code")
        if code in titles:
            codes_ok += 1
            if titles[code] == r.get("onet_title"):
                titles_ok += 1
            else:
                reasons.append(f"{code}: title {r.get('onet_title')!r} != source {titles[code]!r}")
        else:
            reasons.append(f"{code}: not in pinned occupation_data.csv")
        for field, fname in profile["element_lists"].items():
            for e in r.get(field) or []:
                el_total += 1
                if names[fname].get(e.get("element_id")) == e.get("element_name"):
                    el_ok += 1
                else:
                    reasons.append(f"{code}: {field} element {e.get('element_id')!r}/{e.get('element_name')!r} not in {fname}")
                if values.get((fname, code, e.get("element_id"))) == e.get("importance"):
                    val_ok += 1
                else:
                    reasons.append(f"{code}: {field} {e.get('element_id')} importance {e.get('importance')} != source "
                                   f"{values.get((fname, code, e.get('element_id')))}")
    n = len(rows)
    return _result("referential_integrity", cfg, {"codes_resolve": _ratio(codes_ok, n), "titles_match": _ratio(titles_ok, n),
                   "elements_resolve": _ratio(el_ok, el_total), "values_match_source": _ratio(val_ok, el_total)}, reasons)


def check_dedup(rows, profile, cfg, **_):
    def uniq(vals):
        seen, dup = set(), []
        for v in vals:
            (dup.append(v) if v in seen else seen.add(v))
        return dup
    ids = uniq([r.get("record_id") for r in rows])
    keys = uniq([r.get(profile["key_field"]) for r in rows])
    payloads = uniq([json.dumps([_get(r, "dreamco_synthesis.practice_task_seed"), _get(r, "dreamco_synthesis.rubric_dimensions")],
                                sort_keys=True) for r in rows])
    n = len(rows)
    reasons = [f"duplicate record_id {d}" for d in ids] + [f"duplicate {profile['key_field']} {d}" for d in keys] + \
              [f"duplicate synthesis payload (practice seed + rubric): {d[:80]}" for d in payloads]
    return _result("deduplication", cfg, {"unique_record_ids": _ratio(n - len(ids), n), "unique_keys": _ratio(n - len(keys), n),
                   "unique_synthesis_payloads": _ratio(n - len(payloads), n)}, reasons)


def check_ranges(rows, profile, cfg, manifest=None, **_):
    reasons, in_range, consistent = [], 0, 0
    bands = profile["preparation_band_by_job_zone"]
    for r in rows:
        rid = r.get("record_id")
        bad = []
        for field in profile["element_lists"]:
            for e in r.get(field) or []:
                imp = e.get("importance")
                if not isinstance(imp, (int, float)) or not 1 <= imp <= 5:
                    bad.append(f"{field} importance {imp}")
        jz = r.get("job_zone")
        if not isinstance(jz, int) or not 1 <= jz <= 5:
            bad.append(f"job_zone {jz}")
        for k, v in (r.get("capability_lenses") or {}).items():
            if not isinstance(v, (int, float)) or not 0 <= v <= 1:
                bad.append(f"capability_lenses.{k} {v}")
        in_range += not bad
        reasons += [f"{rid}: out of range: {b}" for b in bad]
        inc = []
        for field in profile["element_lists"]:
            imps = [e.get("importance") for e in r.get(field) or []]
            if imps != sorted(imps, reverse=True):
                inc.append(f"{field} not sorted by importance")
        if bands.get(str(jz)) != r.get("preparation_band"):
            inc.append(f"preparation_band {r.get('preparation_band')} inconsistent with job_zone {jz}")
        if str(r.get("onet_soc_code", ""))[:2] != r.get("soc_major_group"):
            inc.append("soc_major_group != code prefix")
        lift = r.get("lens_lift") or {}
        if lift and r.get("dominant_lens") != max(sorted(lift), key=lambda k: lift[k]):
            inc.append("dominant_lens is not the arg-max of lens_lift")
        if not str(r.get("record_id", "")).endswith("/" + str(r.get("onet_soc_code"))):
            inc.append("record_id does not end with onet_soc_code")
        if manifest and r.get("package_version") != manifest.get("version"):
            inc.append(f"package_version {r.get('package_version')} != manifest version {manifest.get('version')}")
        consistent += not inc
        reasons += [f"{rid}: {x}" for x in inc]
    n = len(rows)
    return _result("value_ranges", cfg, {"values_in_range": _ratio(in_range, n), "internal_consistency": _ratio(consistent, n)}, reasons)


def _prov_files(prov: dict | None, source_id: str) -> tuple[dict, dict | None]:
    for s in (prov or {}).get("sources", []):
        if s.get("source_id") == source_id:
            return {f["name"]: f["sha256"] for f in s.get("files", [])}, s
    return {}, None


def check_freshness(rows, profile, cfg, prov=None, ref_hashes=None, **_):
    spec = cfg["checks"]["freshness_version_match"]
    pin = profile["pin"]
    want_version = f"O*NET {pin['version']}"
    files, src = _prov_files(prov, pin["source_id"])
    reasons = []
    if src is None:
        reasons.append(f"asset provenance has no {pin['source_id']} source")
    elif str(src.get("version")) != pin["version"]:
        reasons.append(f"provenance pins {src.get('version')}, profile expects {pin['version']}")
    v_ok = sum(r.get("source_version") == want_version for r in rows)
    reasons += [f"{r.get('record_id')}: source_version {r.get('source_version')!r} != {want_version!r}"
                for r in rows if r.get("source_version") != want_version]
    refs = [(r.get("record_id"), s) for r in rows for s in r.get("source_refs") or [] if s.get("source_id") == pin["source_id"]]
    h_ok = 0
    for rid, s in refs:
        good = files.get(s.get("file")) == s.get("file_sha256") and s.get("version") == pin["version"]
        if good and ref_hashes and s.get("file") in ref_hashes and ref_hashes[s["file"]] != s.get("file_sha256"):
            good = False
            reasons.append(f"{rid}: {s.get('file')} sha256 differs from the reference bytes read")
        if not good and files.get(s.get("file")) != s.get("file_sha256"):
            reasons.append(f"{rid}: {s.get('file')} file_sha256 not equal to provenance pin")
        h_ok += good
    if ref_hashes:
        for name, h in ref_hashes.items():
            if name in files and files[name] != h:
                reasons.append(f"provenance pin for {name} != reference bytes")
                h_ok = 0
    latest = spec["latest_known_onet_version"]
    is_latest = 1.0 if pin["version"] == latest else 0.0
    if not is_latest:
        reasons.append(f"pin {pin['version']} is not the latest known O*NET release {latest} (checked {spec['latest_known_checked_at']})")
    return _result("freshness_version_match", cfg, {"row_version_matches_pin": _ratio(v_ok, len(rows)),
                   "file_hashes_match_pin": _ratio(h_ok, len(refs)) if src else 0.0, "pin_is_latest_known_release": is_latest}, reasons)


def check_provenance(rows, profile, cfg, prov=None, **_):
    pinned = {s.get("source_id") for s in (prov or {}).get("sources", [])
              if re.fullmatch(r"[0-9a-f]{64}", str(s.get("sha256", ""))) or s.get("files")}
    reasons, covered, refs_total, refs_ok = [], 0, 0, 0
    for r in rows:
        rid = r.get("record_id")
        lic = r.get("license") or {}
        problems = []
        if sorted(lic.get("onet_derived_fields") or []) != sorted(profile["onet_derived_fields"]):
            problems.append("license.onet_derived_fields differs from profile")
        if sorted(lic.get("dreamco_fields") or []) != sorted(profile["dreamco_fields"]):
            problems.append("license.dreamco_fields differs from profile")
        onet_cov, dc_cov = set(), set()
        for s in r.get("source_refs") or []:
            if s.get("source_id") == profile["dreamco_source_id"]:
                dc_cov |= set(s.get("fields") or [])
                continue
            refs_total += 1
            if s.get("source_id") in pinned and s.get("file_sha256"):
                refs_ok += 1
                onet_cov |= set(s.get("fields") or [])
            else:
                problems.append(f"source_ref {s.get('source_id')}/{s.get('file')} not pinned in asset provenance")
        problems += [f"O*NET field {f} has no pinned source_ref" for f in profile["onet_derived_fields"] if f not in onet_cov]
        problems += [f"DreamCo field {f} has no {profile['dreamco_source_id']} source_ref" for f in profile["dreamco_fields"] if f not in dc_cov]
        covered += not problems
        reasons += [f"{rid}: {p}" for p in problems]
    return _result("provenance_coverage", cfg, {"rows_fully_covered": _ratio(covered, len(rows)),
                   "refs_pinned": _ratio(refs_ok, refs_total)}, reasons)


def check_synthesis(rows, profile, cfg, ref=None, **_):
    spec = cfg["checks"]["synthesis_perspective"]
    n_words = spec["verbatim_ngram_words"]
    reasons, layer_ok, multi = [], 0, 0
    for r in rows:
        syn = r.get("dreamco_synthesis") or {}
        an = syn.get("analysis") or {}
        good = (len(str(syn.get("practice_task_seed", ""))) >= 40 and len(syn.get("rubric_dimensions") or []) >= 3
                and (an.get("agree") or an.get("caveats")) and an.get("still_need_test"))
        layer_ok += bool(good)
        if not good:
            reasons.append(f"{r.get('record_id')}: DreamCo layer incomplete")
        multi += len(set(syn.get("evidence_perspectives") or [])) >= 2
    verbatim: float | None = None
    if ref is not None:
        corpus: dict[str, set] = {}
        for fname, col in profile["onet_text_for_overlap"].items():
            for row in ref[fname]:
                corpus.setdefault(row["O*NET-SOC Code"], set()).update(_ngrams(row[col], n_words))
        clean = 0
        for r in rows:
            text = " \n ".join(t for f in profile["dreamco_text_fields"] for t in _texts(_get(r, f)))
            hits = set()
            for chunk in text.split("\n"):
                hits |= _ngrams(chunk, n_words) & corpus.get(r.get("onet_soc_code"), set())
            clean += not hits
            if hits:
                reasons.append(f"{r.get('record_id')}: {len(hits)} verbatim {n_words}-word run(s) from O*NET text")
        verbatim = _ratio(clean, len(rows))
    else:
        reasons.append("no reference data: verbatim-overlap metric not_run")
    seeds = [_get(r, "dreamco_synthesis.practice_task_seed") for r in rows]
    share = [len((r.get("license") or {}).get("dreamco_fields") or []) /
             max(1, len((r.get("license") or {}).get("dreamco_fields") or []) + len((r.get("license") or {}).get("onet_derived_fields") or []))
             for r in rows]
    n = len(rows)
    return _result("synthesis_perspective", cfg, {"dreamco_layer_coverage": _ratio(layer_ok, n), "multi_evidence_rows": _ratio(multi, n),
                   "no_verbatim_onet_text": verbatim, "distinct_seed_ratio": _ratio(len(set(seeds)), n),
                   "dreamco_field_share": (sum(share) / n) if n else 0.0}, reasons)


CHECKS = (check_completeness, check_schema, check_referential, check_dedup, check_ranges, check_freshness,
          check_provenance, check_synthesis)


def score(pkg: Path, profile_name: str = "dp_onet_occ_syn", onet_zip: Path | None = None, onet_csv_dir: Path | None = None,
          evaluated_at: str | None = None, cfg: dict | None = None) -> dict:
    cfg = cfg or json.loads(CONFIG.read_text(encoding="utf-8"))
    profile = cfg["profiles"][profile_name]
    manifest_path = pkg / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    data = pkg / profile["data_file"]
    if not data.is_file():
        raise FileNotFoundError(f"data file not found: {data}")
    rows, parse_errors = load_rows(data)
    prov_path = find_asset_provenance(pkg, manifest)
    prov = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path else None
    ref, ref_hashes, notes = load_reference(profile, pkg, onet_zip, onet_csv_dir)
    ctx = {"ref": ref, "ref_hashes": ref_hashes, "prov": prov, "manifest": manifest, "parse_errors": parse_errors}
    checks = [fn(rows, profile, cfg, **ctx) for fn in CHECKS]
    qa_score = round(sum(c["weight"] * c["score"] for c in checks), 2)
    if any(c["hard"] and c["status"] in ("fail", "not_run") for c in checks):
        overall = "fail"
    elif all(c["status"] == "pass" for c in checks):
        overall = "pass"
    else:
        overall = "warn"
    if not rows:
        overall = "fail"
        notes.append("no rows")
    return {
        "schema": SCHEMA_ID,
        "config_version": cfg["version"],
        "profile": profile_name,
        "package_dir": _display_path(pkg),
        "sku_id": manifest.get("sku_id"),
        "version": manifest.get("version"),
        "evaluated_at": evaluated_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": {"data_file": profile["data_file"], "data_sha256": _sha(data.read_bytes()), "rows": len(rows),
                   "asset_provenance": str(prov_path.relative_to(pkg)) if prov_path else None, "reference_notes": notes},
        "overall_status": overall,
        "qa_score": qa_score,
        "checks": checks,
        "failed_checks": [c["id"] for c in checks if c["status"] in ("fail", "not_run")],
        "warned_checks": [c["id"] for c in checks if c["status"] == "warn"],
        "truth_boundary": cfg["truth_boundary"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("package_dir")
    ap.add_argument("--profile", default="dp_onet_occ_syn")
    ap.add_argument("--onet-zip", help="Pinned O*NET CSV zip (sha256 must match provenance_manifest.json)")
    ap.add_argument("--onet-csv-dir", help="Directory of extracted O*NET CSV files")
    ap.add_argument("--out", help="Also write the scorecard JSON here")
    ap.add_argument("--evaluated-at", help="Override evaluated_at (reproducible output)")
    args = ap.parse_args(argv)
    try:
        report = score(Path(args.package_dir), args.profile, Path(args.onet_zip) if args.onet_zip else None,
                       Path(args.onet_csv_dir) if args.onet_csv_dir else None, args.evaluated_at)
    except (FileNotFoundError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": f"{exc.__class__.__name__}: {exc}"}), file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if report["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
