#!/usr/bin/env python3
"""License/provenance gate for DreamCo data-package assets.

Input: an asset directory (provenance.json, optionally asset.json and candidate.json) or a
candidate JSON file (embedding "provenance" or pointing to "provenance_path" / "asset_path").
Output: license_gate JSON (schemas/data_package_license_gate.schema.json) with an outcome of
approved_for_sale | approved_for_private_use | reference_only | blocked and per-check results.

Truth boundary: approved_for_sale requires every rights check to pass, a complete plan 5.2
synthesis asset record (asset.json), a dataset scorecard score >= the "standard" tier minimum
(config/dataset_evaluation_scorecard.json) AND an explicit owner_approval record. Without owner approval the maximum outcome is approved_for_private_use.
Exit code: 1 when the outcome is blocked, 2 on usage/input errors, otherwise 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

GATE_CONFIG = ROOT / "config" / "license_provenance_gate.json"
OWNERSHIP_POLICY = ROOT / "config" / "buddy-training-data-provenance-policy.json"
EVIDENCE_SCHEMA = ROOT / "config" / "evidence_provenance_schema.json"
DISCOVERY_PROGRAM = ROOT / "config" / "data-discovery-bot-program.json"
SCORECARD = ROOT / "config" / "dataset_evaluation_scorecard.json"
PROVENANCE_SCHEMA = ROOT / "schemas" / "data_package_asset_provenance.schema.json"
SYNTHESIS_ASSET_SCHEMA = ROOT / "schemas" / "data_package_synthesis_asset.schema.json"
GATE_SCHEMA = ROOT / "schemas" / "data_package_license_gate.schema.json"
GATE_VERSION = "0.1.0"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
# Validation evidence ids resolve to <repo_root>/<evidence_root>/<kind>/<asset_id>/<YYYYMMDD>-<NN>.json.
DEFAULT_REPO_ROOT = ROOT
DEFAULT_EVIDENCE_ROOT = "data/dreamco_knowledge/evidence"
EVIDENCE_KINDS = ("sandbox", "benchmark", "holdout", "regression")
EVIDENCE_RESULT_FIELDS = ("split", "n_items", "metric", "score", "threshold", "passed")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_policies() -> dict:
    gate = _load(GATE_CONFIG)
    scorecard = _load(SCORECARD)
    tier = gate["sale_requirements"]["minimum_scorecard_tier"]
    minimum = next(t["minimum_score"] for t in scorecard["commercial_tiers"] if t["tier"] == tier)
    return {
        "gate": gate,
        "ownership_classes": _load(OWNERSHIP_POLICY)["ownership_classes"],
        "evidence": _load(EVIDENCE_SCHEMA),
        "hard_failures": _load(DISCOVERY_PROGRAM)["scoring"]["hard_failures"],
        "scorecard_minimum": minimum,
        "scorecard_tier": tier,
        "provenance_schema": load_schema(PROVENANCE_SCHEMA),
        "asset_schema": load_schema(SYNTHESIS_ASSET_SCHEMA),
    }


def load_subject(target: Path, provenance_override: Path | None) -> dict:
    """Return {candidate, provenance, provenance_path, asset, asset_path, candidate_path, base_dir}."""
    candidate: dict = {}
    candidate_path: Path | None = None
    provenance: dict | None = None
    provenance_path: Path | None = None
    asset_path: Path | None = None
    if target.is_dir():
        base = target
        if (target / "candidate.json").exists():
            candidate_path = target / "candidate.json"
            candidate = _load(candidate_path)
        if (target / "provenance.json").exists():
            provenance_path = target / "provenance.json"
        if (target / "asset.json").exists():
            asset_path = target / "asset.json"
    elif target.is_file():
        base = target.parent
        candidate_path = target
        candidate = _load(target)
        if isinstance(candidate.get("provenance"), dict):
            provenance = candidate["provenance"]
        elif candidate.get("provenance_path"):
            p = Path(candidate["provenance_path"])
            provenance_path = p if p.is_absolute() else (base / p)
        if candidate.get("asset_path"):
            a = Path(candidate["asset_path"])
            asset_path = a if a.is_absolute() else (base / a)
    else:
        raise FileNotFoundError(f"target not found: {target}")
    if provenance_override:
        provenance_path = provenance_override
    if provenance_path is not None:
        provenance = _load(provenance_path) if provenance_path.exists() else None
    if target.is_dir() and candidate.get("asset_path") and asset_path is None:
        asset_path = base / candidate["asset_path"]
    asset = _load(asset_path) if asset_path is not None and asset_path.exists() else None
    return {"candidate": candidate, "provenance": provenance, "provenance_path": provenance_path,
            "asset": asset, "asset_path": asset_path, "candidate_path": candidate_path, "base_dir": base}


def _check(check_id: str, status: str, reasons: list[str], cap: str | None = None, scope: str = "rights") -> dict:
    return {"id": check_id, "status": status, "scope": scope, "outcome_cap": cap if status == "fail" else None,
            "reasons": reasons}


def check_provenance(subject: dict, pol: dict) -> dict:
    prov = subject["provenance"]
    if prov is None:
        where = subject["provenance_path"] or "no provenance.json / provenance / provenance_path supplied"
        return _check("provenance_schema_conformance", "fail",
                      [f"provenance.json missing ({where}); required by config/evidence_provenance_schema.json"],
                      "reference_only")
    reasons = [f"schema: {e}" for e in validate(prov, pol["provenance_schema"])]
    for field in pol["evidence"]["required_fields"]:
        if field not in prov:
            reasons.append(f"evidence_provenance_schema required field missing: {field}")
    if prov.get("source_type") not in pol["evidence"]["source_types"]:
        reasons.append(f"source_type {prov.get('source_type')!r} not in evidence_provenance_schema.source_types")
    if prov.get("transformation") not in pol["evidence"]["transformation_types"]:
        reasons.append(f"transformation {prov.get('transformation')!r} not in evidence_provenance_schema.transformation_types")
    if reasons:
        return _check("provenance_schema_conformance", "fail", sorted(set(reasons)), "reference_only")
    return _check("provenance_schema_conformance", "pass", ["provenance.json conforms to schemas/data_package_asset_provenance.schema.json and evidence_provenance_schema required_fields"])


def _sources(subject: dict) -> list[dict]:
    prov = subject["provenance"] or {}
    return prov.get("sources") or subject["candidate"].get("sources") or []


def check_sources_pinned(subject: dict, pol: dict) -> dict:
    sources = _sources(subject)
    if not sources:
        return _check("sources_pinned", "fail", ["no sources listed; source/provenance cannot be traced (hard failure)"], "blocked")
    reasons = []
    for i, s in enumerate(sources):
        sid = s.get("source_id") or s.get("title") or f"sources[{i}]"
        if not s.get("url"):
            reasons.append(f"{sid}: missing url")
        if not s.get("version"):
            reasons.append(f"{sid}: missing version/snapshot")
        file_hashes = [f.get("sha256", "") for f in s.get("files", [])]
        pinned = bool(SHA256_RE.match(str(s.get("sha256", "")))) or (file_hashes and all(SHA256_RE.match(h) for h in file_hashes))
        if not pinned:
            reasons.append(f"{sid}: missing sha256 (or files[].sha256) integrity pin")
    if reasons:
        return _check("sources_pinned", "fail", reasons, "reference_only")
    return _check("sources_pinned", "pass", [f"{len(sources)} source(s) pinned with url + version + sha256"])


def _asset_ownership(subject: dict) -> Any:
    prov = subject["provenance"] or {}
    return prov.get("ownership_class", subject["candidate"].get("ownership_class"))


def check_ownership(subject: dict, pol: dict) -> dict:
    classes = pol["ownership_classes"]
    reasons = []
    oc = _asset_ownership(subject)
    if not oc:
        reasons.append("asset ownership_class missing (config/buddy-training-data-provenance-policy.json requires one)")
    elif oc not in classes:
        reasons.append(f"asset ownership_class {oc!r} not in policy ownership_classes")
    for i, s in enumerate(_sources(subject)):
        sid = s.get("source_id") or f"sources[{i}]"
        soc = s.get("ownership_class")
        if not soc:
            reasons.append(f"{sid}: source ownership_class missing")
        elif soc not in classes:
            reasons.append(f"{sid}: source ownership_class {soc!r} not in policy ownership_classes")
    for comp in (subject["provenance"] or {}).get("derived_components", []):
        if comp.get("ownership_class") not in classes:
            reasons.append(f"derived component {comp.get('component')!r}: invalid ownership_class")
    if reasons:
        return _check("ownership_class_valid", "fail", reasons, "reference_only")
    ref_only = pol["gate"]["reference_only_ownership_classes"]
    if oc in ref_only:
        return _check("ownership_class_valid", "fail", [f"asset ownership_class {oc!r} is reference-only / do-not-publish"], "reference_only")
    return _check("ownership_class_valid", "pass", [f"asset ownership_class {oc!r}; all sources carry valid ownership_class"])


def check_rights(subject: dict, pol: dict) -> dict:
    cand, sources = subject["candidate"], _sources(subject)
    reasons, cap = [], None
    rows = [("candidate", cand.get("commercial_use_allowed"), cand.get("redistribution_allowed"))] if (
        "commercial_use_allowed" in cand or "redistribution_allowed" in cand) else []
    rows += [(s.get("source_id") or f"sources[{i}]", s.get("commercial_use_allowed"), s.get("redistribution_allowed"))
             for i, s in enumerate(sources)]
    if not rows:
        return _check("commercial_and_redistribution_rights", "fail", ["no commercial_use_allowed / redistribution_allowed declarations"], "reference_only")
    for who, commercial, redistribution in rows:
        if redistribution is not True:
            reasons.append(f"{who}: redistribution_allowed is {redistribution!r} (must be true for a sellable package; unknown is not allowed)")
            cap = "reference_only"
        if commercial is not True:
            reasons.append(f"{who}: commercial_use_allowed is {commercial!r} (must be true for sale)")
            cap = cap or "approved_for_private_use"
    if reasons:
        return _check("commercial_and_redistribution_rights", "fail", reasons, cap)
    return _check("commercial_and_redistribution_rights", "pass", ["commercial_use_allowed and redistribution_allowed are true for the asset and every source"])


def _rule_for(source: dict, rules: list[dict]) -> dict | None:
    for rule in rules:
        m = rule["match"]
        if "url_contains" in m and m["url_contains"] in str(source.get("url", "")):
            return rule
        if "license_contains" in m and m["license_contains"] in str(source.get("license", "")):
            return rule
    return None


TEXT_SUFFIXES = {".md", ".txt", ".html", ".rst"}


def _asset_texts(subject: dict, asset_root: Path | None) -> list[tuple[str, str]]:
    prov = subject["provenance"] or {}
    base = asset_root or subject["base_dir"]
    out = []
    for f in prov.get("asset_files", []):
        p = Path(f.get("path", ""))
        p = p if p.is_absolute() else base / p
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
            out.append((f.get("path"), p.read_text(encoding="utf-8", errors="replace")))
    return out


def _missing_elements(text: str, source: dict, rule: dict, modified: bool) -> tuple[list[str], list[str]]:
    version = re.escape(str(source.get("version", "")))
    required = rule["required_elements"] + (rule["required_when_modified"] if modified else [])
    miss_req = [el["id"] for el in required if not re.search(el["pattern"].replace("{version}", version), text)]
    miss_rec = [el["id"] for el in rule["recommended_elements"] if not re.search(el["pattern"].replace("{version}", version), text)]
    return miss_req, miss_rec


def check_attribution(subject: dict, pol: dict, asset_root: Path | None = None) -> dict:
    """Attribution must be declared (provenance/candidate attribution_text) AND, for text assets,
    actually present in the shipped file, so provenance cannot claim notices the asset lacks."""
    prov = subject["provenance"] or {}
    text = prov.get("attribution_text") or subject["candidate"].get("attribution_text") or ""
    transformation = prov.get("transformation") or subject["candidate"].get("transformation") or "unknown"
    modified = transformation != "none"
    needing = [s for s in _sources(subject) if s.get("attribution_required") is not False]
    if not needing:
        return _check("attribution_present", "not_applicable", ["no source declares attribution_required"])
    if not text.strip():
        return _check("attribution_present", "fail", ["attribution required by source license but attribution_text is empty"], "approved_for_private_use")
    failures, warnings = [], []
    texts = [("attribution_text", text)] + _asset_texts(subject, asset_root)
    for s in needing:
        sid = s.get("source_id") or s.get("title")
        rule = _rule_for(s, pol["gate"]["license_rules"])
        if rule is None:
            continue
        for where, body in texts:
            miss_req, miss_rec = _missing_elements(body, s, rule, modified)
            failures += [f"{sid}: {where} missing required {el} ({rule['id']})" for el in miss_req]
            warnings += [f"{sid}: {where} missing recommended {el} ({rule['id']})" for el in miss_rec]
    if failures:
        return _check("attribution_present", "fail", failures + warnings, "approved_for_private_use")
    if warnings:
        return _check("attribution_present", "warn", warnings)
    return _check("attribution_present", "pass", ["attribution text satisfies all matched license rules"])


def check_blocked(subject: dict, pol: dict) -> dict:
    cand = subject["candidate"]
    flags = set(cand.get("flags", []))
    blocked = sorted(flags & (set(pol["hard_failures"]) | set(pol["gate"]["extra_blocked_flags"])))
    cats = {cand.get("category"), cand.get("subcategory"), *cand.get("data_types", [])} - {None}
    blocked_cats = sorted(cats & set(pol["gate"]["blocked_categories"]))
    reasons = [f"hard-failure flag: {f}" for f in blocked] + [f"blocked category: {c}" for c in blocked_cats]
    if reasons:
        return _check("no_blocked_flags_or_categories", "fail", reasons, "blocked")
    return _check("no_blocked_flags_or_categories", "pass", [f"{len(flags)} flag(s) checked against data-discovery hard_failures; none blocked"])


def check_asset_integrity(subject: dict, pol: dict, asset_root: Path | None) -> dict:
    prov = subject["provenance"]
    if not prov or not prov.get("asset_files"):
        return _check("asset_file_integrity", "not_applicable", ["no provenance asset_files to verify"])
    base = asset_root or subject["base_dir"]
    failures, unresolved, ok = [], [], 0
    for f in prov["asset_files"]:
        p = Path(f.get("path", ""))
        p = p if p.is_absolute() else base / p
        if not p.is_file():
            unresolved.append(f"{f.get('path')}: not found under {base}; hash not verified")
            continue
        got = _sha256_file(p)
        if got != f.get("sha256"):
            failures.append(f"{f.get('path')}: sha256 mismatch (recorded {f.get('sha256')}, actual {got})")
        else:
            ok += 1
    if failures:
        return _check("asset_file_integrity", "fail", failures + unresolved, "reference_only")
    if unresolved:
        return _check("asset_file_integrity", "warn", unresolved + [f"{ok} file(s) verified"])
    return _check("asset_file_integrity", "pass", [f"{ok} asset file(s) match recorded sha256"])


def check_scorecard(subject: dict, pol: dict) -> dict:
    score = subject["candidate"].get("scorecard_score")
    minimum = pol["scorecard_minimum"]
    if score is None:
        return _check("scorecard_threshold", "fail", [f"no dataset scorecard score; sale requires >= {minimum} ({pol['scorecard_tier']} tier)"], "approved_for_private_use", "sale")
    if float(score) < minimum:
        return _check("scorecard_threshold", "fail", [f"scorecard_score {score} < {minimum} ({pol['scorecard_tier']} tier)"], "approved_for_private_use", "sale")
    return _check("scorecard_threshold", "pass", [f"scorecard_score {score} >= {minimum}"], scope="sale")


def check_owner_approval(subject: dict, pol: dict) -> dict:
    req = pol["gate"]["sale_requirements"]
    appr = subject["candidate"].get("owner_approval")
    if not isinstance(appr, dict) or appr.get("approved") is not True:
        return _check("owner_approval", "fail", ["no explicit owner_approval record; truth boundary caps outcome at approved_for_private_use"], "approved_for_private_use", "sale")
    reasons = []
    if appr.get("approver") != req["owner"]:
        reasons.append(f"owner_approval.approver must be {req['owner']!r}")
    if req["owner_approval_scope"] not in appr.get("scope", []):
        reasons.append(f"owner_approval.scope must include {req['owner_approval_scope']!r}")
    if not appr.get("approved_at"):
        reasons.append("owner_approval.approved_at missing")
    if reasons:
        return _check("owner_approval", "fail", reasons, "approved_for_private_use", "sale")
    return _check("owner_approval", "pass", [f"approved by {appr['approver']} at {appr['approved_at']}"], scope="sale")


def evidence_root_error(value: Any) -> str | None:
    """None if value is a safe repo-relative POSIX directory; else the reason it is not."""
    if not isinstance(value, str) or not value:
        return "evidence_root must be a non-empty string"
    if "\\" in value:
        return f"evidence_root {value!r} contains a backslash (POSIX paths only)"
    if value.startswith("/"):
        return f"evidence_root {value!r} is absolute (must be repo-relative)"
    if ".." in value.split("/"):
        return f"evidence_root {value!r} contains a '..' segment"
    return None


def resolve_evidence_ids(asset: dict, pol: dict, repo_root: Path | None) -> tuple[int, list[str]]:
    """Resolve asset.json validation_evidence_ids; returns (number of ids that COUNT, problems).

    Only a resolved record with passed is True counts toward min_validation_evidence_ids. See
    resolve_evidence_records for the ids that resolved but did not pass."""
    counted, problems, _not_passed = resolve_evidence_records(asset, pol, repo_root)
    return counted, problems


def resolve_evidence_records(asset: dict, pol: dict, repo_root: Path | None, *, verify_holdout_remote: bool = False,
                             holdout_test_remote: str | Path | None = None,
                             holdout_log: dict | None = None) -> tuple[int, list[str], list[str]]:
    """Resolve asset.json validation_evidence_ids to evidence records on disk.

    Returns (number of ids that resolved to a conforming record with passed is True, problems,
    notes for ids that resolved to a conforming record whose passed is not True). Problems block
    sale; not-passed notes do not, but those ids do not count toward the minimum. An id resolves when it
    matches '<kind>:<asset_id>:<YYYYMMDD>-<NN>' with kind == its list key and asset_id == the asset's,
    the file <repo_root>/<evidence_root>/<kind>/<asset_id>/<YYYYMMDD>-<NN>.json exists inside the repo
    root, parses as a JSON object whose evidence_id equals the id, and carries the
    evidence_provenance_schema required_fields plus split/n_items/metric/score/threshold/passed.

    Holdout records with passed is True: without verify_holdout_remote they count, and a warning that they are
    unverified against the remote goes to holdout_log["warnings"]. With verify_holdout_remote they count only if
    verify_holdout_remote() accepts them against the canonical remote; a failure is a problem (sale scope). Under
    holdout_test_remote (tests only) a consistent record is still a problem, so it never counts and caps the outcome."""
    log = holdout_log if holdout_log is not None else {}
    log.setdefault("warnings", [])
    log.setdefault("info", [])
    log.setdefault("holdout_relied", 0)       # holdout records that resolved with passed: true
    log.setdefault("holdout_unverified", 0)   # ... of which not remotely verified in this run (absent flag or failed)
    root = Path(repo_root or DEFAULT_REPO_ROOT).resolve()
    ev_root = asset.get("evidence_root", DEFAULT_EVIDENCE_ROOT)
    err = evidence_root_error(ev_root)
    ids = asset.get("validation_evidence_ids") or {}
    if err:
        return 0, [err + "; no evidence id can resolve"], []
    asset_id = str(asset.get("asset_id", ""))
    id_re = re.compile(rf"^({'|'.join(EVIDENCE_KINDS)}):{re.escape(asset_id)}:(\d{{8}}-\d{{2}})$")
    required = list(pol["evidence"]["required_fields"]) + list(EVIDENCE_RESULT_FIELDS)
    resolved, problems, not_passed = 0, [], []
    for key in EVIDENCE_KINDS:
        for eid in ids.get(key, []):
            m = id_re.fullmatch(eid) if isinstance(eid, str) else None
            if not m:
                problems.append(f"{key}: {eid!r} is not '<kind>:{asset_id}:<YYYYMMDD>-<NN>'")
                continue
            if m.group(1) != key:
                problems.append(f"{key}: {eid!r} has kind {m.group(1)!r} but is listed under {key!r}")
                continue
            path = (root / ev_root / key / asset_id / f"{m.group(2)}.json").resolve()
            rel = f"{ev_root}/{key}/{asset_id}/{m.group(2)}.json"
            try:
                path.relative_to(root)
            except ValueError:
                problems.append(f"{key}: {eid!r} resolves outside the repo root ({rel})")
                continue
            if not path.is_file():
                problems.append(f"{key}: {eid!r} does not resolve: {rel} not found under repo root")
                continue
            try:
                record = _load(path)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                problems.append(f"{key}: {eid!r}: {rel} is not valid JSON ({exc.__class__.__name__})")
                continue
            if not isinstance(record, dict):
                problems.append(f"{key}: {eid!r}: {rel} is not a JSON object")
                continue
            if record.get("evidence_id") != eid:
                problems.append(f"{key}: {eid!r}: {rel} evidence_id is {record.get('evidence_id')!r}")
                continue
            missing = [f for f in required if f not in record]
            if missing:
                problems.append(f"{key}: {eid!r}: {rel} missing evidence fields {missing}")
                continue
            if record.get("passed") is not True:
                not_passed.append(f"{key}: {eid} resolved but passed is not true "
                                  f"(passed={record.get('passed')!r}); not counted toward the minimum")
                continue
            if key == "holdout":
                log["holdout_relied"] += 1
                if not verify_holdout_remote:
                    log["holdout_unverified"] += 1
                    log["warnings"].append(f"holdout: {eid} counted but NOT verified against the canonical remote "
                                           f"{pol['gate']['holdout_verification']['canonical_remote_url']} "
                                           "(run the gate with --verify-holdout-remote)")
                else:
                    v = verify_holdout_remote_fn(record, pol, holdout_test_remote)
                    if not v["ok"] or v["test_only"]:
                        log["holdout_unverified"] += 1
                    if not v["ok"]:
                        problems.append(f"holdout: {eid} failed remote verification, not counted: " + "; ".join(v["errors"][:4]))
                        continue
                    if v["test_only"]:
                        problems.append(f"holdout: {eid} verification consistent, but {HOLDOUT_TEST_ONLY_NOTE}")
                        continue
                    f = v["facts"]
                    log["info"].append(f"holdout: {eid} verified against the canonical remote: grading_commit "
                                       f"{f['grading_commit'][:12]} on {f['remote_branch']} (tip {f['remote_tip'][:12]}), "
                                       f"key revealed in {f['reveal_commit'][:12]}, recomputed score {f['recomputed']['score']} "
                                       f"> baseline {f['recomputed']['baseline_score']}, passed")
            resolved += 1
    return resolved, problems, not_passed


def verify_holdout_remote_fn(record: dict, pol: dict, test_remote: str | Path | None = None) -> dict:
    """Indirection so tests can stub the remote verifier; the default is verify_holdout_remote below."""
    return verify_holdout_remote(record, pol, test_remote)


# --- holdout evidence: independent verification against the canonical remote -------------------------
#
# Opt-in (--verify-holdout-remote). This is DreamCo's own implementation: it reads the published pass rule and
# re-implements it, and it never imports or executes the producer's verifier (verify_holdout.py) or scorer. Everything
# it checks comes from the canonical GitHub remote, fetched into a fresh temporary bare repository with /usr/bin/git in
# an environment built from scratch, so a git shim on PATH, GIT_* variables, proxies, HOME/XDG/system git config,
# url.*.insteadOf, replace refs or a local clone's refs cannot influence it.

HOLDOUT_NOT_VERIFIED = "holdout evidence not remotely verified; required for sale"
HOLDOUT_TEST_ONLY_NOTE = ("TEST ONLY: holdout verification ran against a local stand-in remote; the record is not counted "
                          "and the outcome is capped at approved_for_private_use")
_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_FINAL_RE = re.compile(r"^FINAL: grader=(?P<grader>[^;]+); declared_at=(?P<at>[^;\s]+); sheet_sha256=(?P<sheet>[0-9a-f]{64})\s*$",
                       re.M)


class HoldoutVerifyError(Exception):
    pass


def _trusted_git(path: str) -> str:
    """The configured git binary (default /usr/bin/git) if it is a root-owned regular executable in a root-owned
    directory that neither group nor others can write. git is never looked up on PATH."""
    import os
    import stat as _stat
    try:
        st, dst = os.stat(path), os.stat(os.path.dirname(path))
    except OSError as exc:
        raise HoldoutVerifyError(f"{path} not usable ({exc.__class__.__name__}); git is never looked up on PATH")
    if not _stat.S_ISREG(st.st_mode) or not os.access(path, os.X_OK):
        raise HoldoutVerifyError(f"{path} is not an executable regular file")
    for s, what in ((st, path), (dst, os.path.dirname(path))):
        if s.st_uid != 0 or s.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH):
            raise HoldoutVerifyError(f"{what} is not root-owned or is group/other-writable")
    return path


class _RemoteMirror:
    """A fresh temporary bare repository holding the remote's allowed branches with full contents (blobs included, so
    content searches such as the nonce pickaxe run locally). git runs as `<git> -C <dir> <safe -c overrides> ...` with an environment built from nothing."""

    def __init__(self, url: str, cfg: dict, allow_file_protocol: bool = False):
        self.url, self.cfg, self.allow_file = url, cfg, allow_file_protocol

    def __enter__(self):
        import tempfile
        self.git = _trusted_git(self.cfg.get("git_binary", "/usr/bin/git"))
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-holdout-verify-"))
        home = self.tmp / "home"
        home.mkdir()
        self.env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "XDG_CONFIG_HOME": str(home / "config"),
                    "XDG_CACHE_HOME": str(home / "cache"), "XDG_DATA_HOME": str(home / "data"),
                    "XDG_STATE_HOME": str(home / "state"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_ASKPASS": "/bin/false",
                    "SSH_ASKPASS": "/bin/false", "LC_ALL": "C"}
        self.safe = ["-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
                     "-c", f"protocol.file.allow={'always' if self.allow_file else 'never'}",
                     "-c", "protocol.ext.allow=never", "-c", "http.sslVerify=true", "-c", "http.proxy=",
                     "-c", "credential.helper=", "-c", "core.askPass=/bin/false", "-c", "core.fsmonitor=false",
                     "-c", "core.hooksPath=/dev/null", "-c", "core.commitGraph=false", "-c", "fetch.writeCommitGraph=false"]
        self.mirror = self.tmp / "mirror.git"
        self.tips: dict[str, str] = {}
        return self

    def __exit__(self, *exc):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run(self, *args: str, cwd: Path | None = None, text: bool = True):
        import subprocess
        try:
            return subprocess.run([self.git, "-C", str(cwd or self.mirror), *self.safe, *args], capture_output=True,
                                  text=text, env=self.env, stdin=subprocess.DEVNULL,
                                  timeout=float(self.cfg.get("timeout_s", 300)))
        except subprocess.TimeoutExpired:
            raise HoldoutVerifyError(f"git {args[0]} timed out")

    def ls_remote(self, branches: list[str]) -> dict[str, str]:
        refs = [f"refs/heads/{b}" for b in branches]
        r = self.run("ls-remote", "--", self.url, *refs, cwd=self.tmp)
        if r.returncode:
            raise HoldoutVerifyError(f"cannot reach the remote (git ls-remote exit {r.returncode}: {r.stderr.strip()[:200]})")
        tips = {}
        for line in r.stdout.splitlines():
            sha, _, ref = line.partition("\t")
            if ref in refs and _SHA_RE.match(sha):
                tips[ref[len("refs/heads/"):]] = sha
        return tips

    def fetch(self, tips: dict[str, str]) -> None:
        for args in (("init", "-q", "--bare", str(self.mirror)),):
            r = self.run(*args, cwd=self.tmp)
            if r.returncode:
                raise HoldoutVerifyError(f"git init failed: {r.stderr.strip()[:200]}")
        self.run("config", "remote.origin.url", self.url)
        r = self.run("fetch", "-q", "--no-tags", "origin",
                     *[f"+refs/heads/{b}:refs/heads/{b}" for b in tips])
        if r.returncode:
            raise HoldoutVerifyError(f"git fetch from the remote failed: {r.stderr.strip()[:200]}")
        for b, t in tips.items():
            got = self.run("rev-parse", "--verify", "-q", f"refs/heads/{b}^{{commit}}").stdout.strip()
            if got != t:
                raise HoldoutVerifyError(f"remote branch {b} moved during verification ({t[:12]} -> {got[:12]}); retry")
        self.tips = dict(tips)

    # --- history helpers (full local mirror; no further network access) ---
    def rev_list(self, *args: str) -> list[str]:
        r = self.run("rev-list", *args)
        if r.returncode:
            raise HoldoutVerifyError(f"git rev-list failed: {r.stderr.strip()[:200]}")
        return r.stdout.split()

    def blob_id(self, commit: str, path: str) -> str | None:
        r = self.run("rev-parse", "--verify", "-q", f"{commit}:{path}")
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None

    def parents(self, commit: str) -> list[str]:
        return self.rev_list("--parents", "-n1", commit)[1:]

    def cat_blob(self, blob: str) -> bytes | None:
        r = self.run("cat-file", "blob", blob, text=False)
        return r.stdout if r.returncode == 0 else None

    def commits_with_object(self, blob: str, tips: list[str]) -> list[str]:
        """Commits (merges diffed against each parent) that add or remove this blob under ANY path."""
        r = self.run("log", "-m", "--no-renames", "--format=%H", f"--find-object={blob}", *tips)
        if r.returncode:
            raise HoldoutVerifyError(f"git log --find-object failed: {r.stderr.strip()[:200]}")
        return sorted(set(r.stdout.split()))

    def commits_with_string(self, s: str, tips: list[str]) -> list[str]:
        """Commits (merges diffed against each parent) that change how often this literal string occurs in any file."""
        r = self.run("log", "-m", "--no-renames", "--format=%H", f"-S{s}", *tips)
        if r.returncode:
            raise HoldoutVerifyError(f"git log -S failed: {r.stderr.strip()[:200]}")
        return sorted(set(r.stdout.split()))

    def evidence_grading_commits(self, key_sha: str, kit_tag: str, ev_dir: str, fin_path: str) -> dict:
        """{grading_commit named: [where]} over every results file, record and FINALIZED.txt for this key commitment in
        any commit reachable from any allowed tip (so files deleted later still count)."""
        named: dict = {}
        cache: dict = {}

        def blob_json(b):
            if b not in cache:
                raw = self.cat_blob(b)
                try:
                    cache[b] = json.loads(raw) if raw else None
                except ValueError:
                    cache[b] = None
            return cache[b]

        for c in self.rev_list("--full-history", *self.tips.values(), "--", ev_dir, fin_path):
            entries = {}
            for line in self.run("ls-tree", "-r", c, "--", ev_dir, fin_path).stdout.splitlines():
                meta, _, path = line.partition("\t")
                parts = meta.split()
                if len(parts) == 3 and parts[1] == "blob":
                    entries[path] = parts[2]
            for path, b in entries.items():
                if path == fin_path:
                    t = (self.cat_blob(b) or b"").decode("utf-8", "replace")
                    if f"key_sha256: {key_sha}" in t:
                        m_ = re.search(r"^grading_commit: (\S+)", t, re.M)
                        named.setdefault(m_[1] if m_ else None, []).append(f"{c[:12]}:{path}")
                elif path.endswith(".results.json"):
                    d = blob_json(b)
                    if isinstance(d, dict) and d.get("key_sha256") == key_sha:
                        named.setdefault(d.get("grading_commit"), []).append(f"{c[:12]}:{path}")
                elif path.endswith(".json"):
                    d = blob_json(b)
                    if not isinstance(d, dict):
                        continue
                    rp = d.get("results_path")
                    res = blob_json(entries[rp]) if rp in entries else None
                    if (isinstance(res, dict) and res.get("key_sha256") == key_sha) or \
                            (kit_tag and str(d.get("content_version", "")).endswith(kit_tag)):
                        named.setdefault(d.get("grading_commit"), []).append(f"{c[:12]}:{path}")
        return named

    # --- signatures ---
    def check_signer(self, commit: str, signers: dict) -> tuple[bool, str]:
        """(ok, detail): the commit carries a GOOD, VALID signature from a listed signer (see _holdout_signers)."""
        raw = self.run("cat-file", "commit", commit).stdout
        sig = _commit_gpgsig(raw)
        if not sig:
            return False, "not signed"
        if "BEGIN SSH SIGNATURE" in sig:
            return self._check_ssh(commit, sig, signers)
        if "BEGIN PGP SIGNATURE" in sig:
            return self._check_gpg(commit, signers)
        return False, "unknown signature format"

    def _check_ssh(self, commit: str, sig: str, signers: dict) -> tuple[bool, str]:
        if not signers["ssh_fprs"] and not signers["ssh_allowed"]:
            return False, "SSH-signed, but no SSH signer is configured"
        keygen = _trusted_git(self.cfg.get("ssh_keygen_binary", "/usr/bin/ssh-keygen"))
        try:
            ktype, kb64, fpr = _ssh_signature_key(sig)
        except (ValueError, IndexError) as exc:
            return False, f"malformed SSH signature ({exc})"
        files = []
        if signers["ssh_allowed"]:
            ap = _repo_path(signers["ssh_allowed"])
            if not ap.is_file():
                return False, f"ssh_allowed_signers_file {signers['ssh_allowed']} not found"
            files.append(ap)
        if fpr in signers["ssh_fprs"]:
            tmpf = self.tmp / f"allowed-{commit[:12]}"
            tmpf.write_text(f'holdout-signer namespaces="git" {ktype} {kb64}\n')
            files.append(tmpf)
        if not files:
            return False, f"SSH-signed by {fpr}, not a listed signer"
        detail = ""
        for f in files:
            r = self.run("-c", "gpg.format=ssh", "-c", f"gpg.ssh.program={keygen}", "-c", f"gpg.ssh.allowedSignersFile={f}",
                         "verify-commit", "--raw", commit)
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0 and 'Good "git" signature for ' in out:  # principal matched, not just "with ... key"
                return True, fpr
            detail = out[:160]
        return False, f"SSH-signed by {fpr}, not a listed signer ({detail})"

    def _check_gpg(self, commit: str, signers: dict) -> tuple[bool, str]:
        import subprocess
        fingerprints = signers["gpg_fprs"]
        if not fingerprints:
            return False, "OpenPGP-signed, but no OpenPGP signer fingerprint is configured"
        gpg = _trusted_git(self.cfg.get("gpg_binary", "/usr/bin/gpg"))
        keys_path = signers["gpg_keys"]
        if not keys_path:
            return False, "no signer_public_keys configured"
        kp = _repo_path(keys_path)
        if not kp.is_file():
            return False, f"signer public keys file {keys_path} not found"
        gh = self.tmp / "gnupg"
        gh.mkdir(mode=0o700, exist_ok=True)
        env = dict(self.env, GNUPGHOME=str(gh))
        imp = subprocess.run([gpg, "--batch", "--quiet", "--no-autostart", "--import", str(kp)], capture_output=True,
                             text=True, env=env, stdin=subprocess.DEVNULL, timeout=60)
        if imp.returncode:
            return False, f"could not import signer keys ({imp.stderr.strip()[:120]})"
        saved, self.env = self.env, env
        try:
            r = self.run("-c", f"gpg.program={gpg}", "-c", "gpg.format=openpgp", "verify-commit", "--raw", commit)
        finally:
            self.env = saved
            subprocess.run(["/usr/bin/gpgconf", "--kill", "all"], capture_output=True, env=env, stdin=subprocess.DEVNULL,
                           timeout=60) if Path("/usr/bin/gpgconf").exists() else None
        status = r.stderr.splitlines()
        good = any(l.startswith("[GNUPG:] GOODSIG ") for l in status)
        for l in status:
            if l.startswith("[GNUPG:] VALIDSIG "):
                f = l.split()
                cands = {f[2].upper()} | ({f[11].upper()} if len(f) > 11 else set())
                hit = sorted(cands & set(fingerprints))
                if r.returncode == 0 and good and hit:
                    return True, hit[0]
                return False, f"signed by {sorted(cands)}, not a listed signer"
        return False, "no valid signature (git verify-commit exit %d)" % r.returncode

    def verify_commit_signature(self, commit: str, fingerprints: list[str], keys_path: str | None) -> tuple[bool, str]:
        """Back-compatible OpenPGP-only entry point."""
        return self.check_signer(commit, {"gpg_fprs": set(fingerprints), "gpg_keys": keys_path, "ssh_fprs": set(),
                                          "ssh_allowed": ""})

    def is_ancestor(self, a: str, b: str) -> bool:
        return bool(_SHA_RE.match(a or "")) and bool(_SHA_RE.match(b or "")) and \
            self.run("merge-base", "--is-ancestor", a, b).returncode == 0

    def show(self, commit: str, path: str) -> bytes | None:
        r = self.run("show", f"{commit}:{path}", text=False)
        return r.stdout if r.returncode == 0 else None

    def commits(self, tip: str, *paths: str, diff_filter: str | None = None) -> list[str]:
        args = ["log", "--format=%H", "--full-history", "--no-renames",
                f"--max-count={int(self.cfg.get('max_history_commits', 2000))}"]
        if diff_filter:
            args.append(f"--diff-filter={diff_filter}")
        r = self.run(*args, tip, "--", *paths)
        if r.returncode:
            raise HoldoutVerifyError(f"git log failed: {r.stderr.strip()[:200]}")
        return r.stdout.split()


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _holdout_parse_sheet(sheet: bytes, items: list[dict]) -> tuple[dict, list[str]]:
    import csv
    import io
    rubric = {i["item_id"]: [c["criterion"] for c in i["rubric"]] for i in items}
    grades, errs = {}, []
    for row in csv.DictReader(io.StringIO(sheet.decode("utf-8"), newline="")):
        hid = (row.get("item_id") or "").strip()
        if hid not in rubric or hid in grades:
            errs.append(f"unknown or duplicate item_id {hid!r}")
            continue
        if [(row.get(f"criterion_{n}") or "").strip() for n in (1, 2, 3)] != rubric[hid]:
            errs.append(f"{hid}: criteria differ from items.json")
        raw = [(row.get(f"score_{n}") or "").strip() for n in (1, 2, 3)]
        if any(v not in ("0", "1", "2") for v in raw):
            errs.append(f"{hid}: scores must be 0, 1 or 2")
            continue
        fc = (row.get("factually_correct") or "").strip().lower()
        if fc not in ("yes", "no", "unsure"):
            errs.append(f"{hid}: factually_correct must be yes, no or unsure")
        grader = " ".join((row.get("grader") or "").split())
        if not grader:
            errs.append(f"{hid}: grader empty")
        grades[hid] = {"s": [int(v) for v in raw], "fc": fc, "grader": grader}
    missing = sorted(set(rubric) - set(grades))
    if missing:
        errs.append(f"rows missing for {missing}")
    return grades, errs


def _holdout_recompute(key: dict, grades: dict, rule: dict) -> tuple[dict, dict]:
    """DreamCo's implementation of the published holdout pass rule. Returns (kit summary, {asset_id: result})."""
    def lowered(s: list[int], c: int) -> bool:  # criterion c marked down: <= 1 and below the mean of the other two
        rest = s[:c] + s[c + 1:]
        return s[c] <= 1 and 2 * s[c] < rest[0] + rest[1]

    def tally(entries):
        weak = [(h, k) for h, k in entries if k["candidate_type"] == "weakened"]
        full = [(h, k) for h, k in entries if k["candidate_type"] == "full_strength"]
        hits = sum(lowered(grades[h]["s"], k["weakened_criterion"] - 1) for h, k in weak)
        alarms = sum(lowered(grades[h]["s"], grades[h]["s"].index(min(grades[h]["s"]))) for h, _ in full)
        return weak, full, hits, alarms

    entries = sorted(key["items"].items())
    if any(k.get("candidate_type") not in ("weakened", "full_strength") for _, k in entries):
        raise HoldoutVerifyError("key has an unknown candidate_type")
    weak, full, hits, alarms = tally(entries)
    if not weak or not full:
        raise HoldoutVerifyError("key must contain both full-strength and weakened items")
    full_mean = sum(sum(grades[h]["s"]) for h, _ in full) / (3 * len(full))
    weak_mean = sum(grades[h]["s"][k["weakened_criterion"] - 1] for h, k in weak) / len(weak)
    kit = {"detection_rate": hits / len(weak), "false_alarm_rate": alarms / len(full), "mean_gap": full_mean - weak_mean}
    kit["passed"] = (kit["detection_rate"] >= rule["kit_detection_min"] and kit["false_alarm_rate"] <= rule["kit_false_alarm_max"]
                     and kit["mean_gap"] >= rule["kit_mean_gap_min"])
    per_asset: dict[str, list] = {}
    for h, k in entries:
        per_asset.setdefault(k["asset_id"], []).append((h, k))
    out = {}
    for aid, es in per_asset.items():
        n = len(es)
        inside = sum(v in band for h, k in es for v, band in zip(grades[h]["s"], k["accepted_scores"]))
        agreement = inside / (3 * n)
        # baselines: expected agreement of three graders who cannot tell the answer types apart
        uniform = sum(len({0, 1, 2} & set(band)) / 3 for _, k in es for band in k["accepted_scores"]) / (3 * n)
        all_twos = sum(2 in band for _, k in es for band in k["accepted_scores"]) / (3 * n)
        shortcut = 0.0
        for _, k in es:
            picks = [k["weakened_criterion"] - 1] if k["candidate_type"] == "weakened" else [0, 1, 2]
            for c in picks:
                shortcut += sum((0 if i == c else 2) in band for i, band in enumerate(k["accepted_scores"])) / (3 * len(picks))
        shortcut /= n
        baseline = max(uniform, all_twos, shortcut)
        w, f, a_hits, a_alarms = tally(es)
        checks = {
            "kit_discrimination": kit["passed"],
            "eligible": n >= rule["asset_min_items"] and bool(w) and bool(f),
            "asset_detection": bool(w) and a_hits / len(w) >= rule["asset_detection_min"],
            "asset_false_alarm": bool(f) and a_alarms / len(f) <= rule["asset_false_alarm_max"],
            "agreement_min": agreement >= rule["asset_agreement_min"],
            "agreement_above_baseline": agreement > baseline + 1e-12,
            "no_full_strength_judged_incorrect": not any(grades[h]["fc"] == "no" for h, _ in f),
        }
        out[aid] = {"n_items": n, "score": round(agreement, 4), "baseline_score": round(baseline, 4),
                    "checks": checks, "passed": all(checks.values())}
    return kit, out


def _repo_path(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else ROOT / q


def _commit_gpgsig(raw_commit: str) -> str | None:
    """The armored signature in a raw commit object's gpgsig / gpgsig-sha256 header, or None."""
    sig, inside = [], False
    for line in raw_commit.split("\n"):
        if line == "":
            break
        if line.startswith("gpgsig ") or line.startswith("gpgsig-sha256 "):
            inside = True
            sig.append(line.split(" ", 1)[1])
        elif inside and line.startswith(" "):
            sig.append(line[1:])
        else:
            inside = False
    return "\n".join(sig) or None


def _ssh_signature_key(armored: str) -> tuple[str, str, str]:
    """(key type, base64 public key, 'SHA256:...' fingerprint) of the key embedded in an SSHSIG signature."""
    import base64
    import struct
    blob = base64.b64decode("".join(l for l in armored.splitlines() if l and not l.startswith("-----")))
    if blob[:6] != b"SSHSIG":
        raise ValueError("not an SSHSIG blob")
    (n,) = struct.unpack(">I", blob[10:14])
    pub = blob[14:14 + n]
    (t,) = struct.unpack(">I", pub[:4])
    fpr = "SHA256:" + base64.b64encode(hashlib.sha256(pub).digest()).decode().rstrip("=")
    return pub[4:4 + t].decode(), base64.b64encode(pub).decode(), fpr


def _holdout_signers(cfg: dict) -> dict:
    """Configured signers: OpenPGP fingerprints (40 hex, keys imported from signer_public_keys), SSH fingerprints
    (SHA256:...) and/or an SSH allowed_signers file. 'required' is true when any signer is configured."""
    gpg_fprs, ssh_fprs = set(), set()
    for f in cfg.get("required_signer_fingerprints") or []:
        f = str(f).replace(" ", "")
        if re.fullmatch(r"SHA256:[A-Za-z0-9+/]{43}", f):
            ssh_fprs.add(f)
        elif re.fullmatch(r"(0x)?[0-9A-Fa-f]{40}", f):
            gpg_fprs.add(f[-40:].upper())
        else:
            raise HoldoutVerifyError(f"required_signer_fingerprints entry {f!r} is neither an OpenPGP (40 hex) nor an "
                                     "SSH (SHA256:...) fingerprint")
    allowed = str(cfg.get("ssh_allowed_signers_file") or "")
    return {"gpg_fprs": gpg_fprs, "ssh_fprs": ssh_fprs, "ssh_allowed": allowed, "gpg_keys": cfg.get("signer_public_keys"),
            "required": bool(gpg_fprs or ssh_fprs or allowed)}


def _holdout_expected(cfg: dict, record: dict, run: str, explicit: Any = None) -> dict | None:
    """Pinned SHAs for this record: explicit argument, else cfg expected_shas[evidence_id | run_id], else
    cfg expected_shas_file (VERIFIED_SHAS.json format, or a mapping keyed by evidence_id / run_id)."""
    def pick(d):
        if not isinstance(d, dict):
            return None
        if any(k in d for k in ("grading_commit", "reveal_commit", "remote_tip_sha")):
            return d if d.get("run_id") in (None, run) else None
        return d.get(record.get("evidence_id")) or d.get(run)
    spec = explicit if explicit is not None else pick(cfg.get("expected_shas") or {})
    if spec is None and cfg.get("expected_shas_file"):
        fp = _repo_path(cfg["expected_shas_file"])
        if not fp.is_file():
            raise HoldoutVerifyError(f"expected_shas_file {cfg['expected_shas_file']} not found")
        spec = pick(json.loads(fp.read_bytes()))
    if spec is None:
        return None
    spec = spec.get("shas", spec) if isinstance(spec, dict) else spec
    out = {k: spec[k] for k in ("grading_commit", "reveal_commit", "remote_tip_sha") if isinstance(spec, dict) and spec.get(k)}
    if not out or not all(_SHA_RE.match(str(v)) for v in out.values()):
        raise HoldoutVerifyError("expected SHAs need grading_commit, reveal_commit and/or remote_tip_sha as full SHAs")
    return out


def verify_holdout_remote(record: dict, pol: dict, test_remote: str | Path | None = None, *, expect_shas: Any = None) -> dict:
    """Independently verify one holdout evidence record against the canonical remote.

    Returns {"ok", "test_only", "errors", "facts"}. ok means every check passed. test_remote (a local repository path)
    is for this gate's test suite only: the verification then reports test_only and the caller never counts it.
    expect_shas overrides the configured pins (see _holdout_expected)."""
    cfg = pol["gate"]["holdout_verification"]
    rule = cfg["pass_rule"]
    errors: list[str] = []
    facts: dict[str, Any] = {}
    out = {"ok": False, "test_only": test_remote is not None, "errors": errors, "facts": facts}

    def need(cond: Any, msg: str) -> bool:
        if not cond:
            errors.append(msg)
        return bool(cond)

    try:
        eid = record.get("evidence_id", "")
        m = re.fullmatch(r"holdout:(?P<aid>[A-Za-z0-9._-]+):(?P<run>\d{8}-\d{2})", eid if isinstance(eid, str) else "")
        gc, branch = record.get("grading_commit") or "", record.get("remote_branch")
        ev_root = record.get("evidence_root")
        ok = need(m, f"evidence_id {eid!r} is not holdout:<asset_id>:<YYYYMMDD>-<NN>")
        ok &= need(_SHA_RE.match(gc), "grading_commit missing or malformed")
        ok &= need(record.get("split") == "holdout", f"split is {record.get('split')!r}, not 'holdout'")
        ok &= need(not record.get("test_only"), "record is marked test_only")
        ok &= need(record.get("remote_url") == cfg["canonical_remote_url"], f"remote_url {record.get('remote_url')!r} is not the canonical remote")
        ok &= need(branch in cfg["allowed_branches"], f"remote_branch {branch!r} is not an allowed branch {cfg['allowed_branches']}")
        ok &= need(isinstance(ev_root, str) and evidence_root_error(ev_root) is None, f"record evidence_root {ev_root!r} invalid")
        if not ok:
            return out
        aid, run = m["aid"], m["run"]
        rec_rel = f"{ev_root}/holdout/{aid}/{run}.json"
        res_rel = f"{ev_root}/holdout/{aid}/{run}.results.json"
        if not need(record.get("results_path") == res_rel, f"results_path {record.get('results_path')!r} != {res_rel}"):
            return out
        kit = cfg["kit_dir"]
        url = str(test_remote) if test_remote is not None else cfg["fetch_url"]
        with _RemoteMirror(url, cfg, allow_file_protocol=test_remote is not None) as g:
            tips = g.ls_remote(list(cfg["allowed_branches"]))
            if not need(branch in tips, f"the remote has no branch {branch!r}"):
                return out
            g.fetch(tips)
            tip = tips[branch]
            facts.update(remote_branch=branch, remote_tip=tip, grading_commit=gc)
            if not need(g.is_ancestor(gc, tip), f"grading_commit {gc[:12]} is not on {branch} (tip {tip[:12]}) of the remote"):
                return out
            signers = _holdout_signers(cfg)
            expected = _holdout_expected(cfg, record, run, expect_shas)
            if not need(expected or not cfg.get("require_expected_shas"), "no pinned SHAs (expected_shas) for this record, "
                        "and require_expected_shas is true"):
                return out
            rts = record.get("remote_tip_sha") or ""
            need(g.is_ancestor(gc, rts) and g.is_ancestor(rts, tip), "remote_tip_sha is not between grading_commit and the branch tip")
            # the reveal: REVEALED_KEY.json must be added exactly once on the branch, strictly after grading_commit
            rk = f"{kit}/REVEALED_KEY.json"
            sheet_p, final_p, fin_p = f"{kit}/grading_sheet.csv", f"{kit}/GRADING_FINAL.txt", f"{kit}/FINALIZED.txt"
            all_tips = list(g.tips.values())
            added = g.commits(tip, rk, diff_filter="A")
            if not need(len(added) == 1, f"REVEALED_KEY.json must be added exactly once on {branch}; found {len(added)} addition(s)"):
                return out
            reveal = added[0]
            facts["reveal_commit"] = reveal
            ok = need(g.show(gc, rk) is None, "REVEALED_KEY.json already exists at grading_commit (key public before grading)")
            ok &= need(reveal != gc and g.is_ancestor(gc, reveal),
                       f"grading_commit {gc[:12]} is not an ancestor of the reveal commit {reveal[:12]} (graded after the key was public?)")
            if not ok:
                return out
            # stricter reveal-order rules (parity with the producer's verifier at dde106b, plus all-branch and any-path checks)
            key_blob = g.blob_id(reveal, rk)
            need(not g.rev_list("--full-history", gc, "--", rk),
                 "REVEALED_KEY.json exists in an ancestor of grading_commit (key public before grading)")
            nonmerge = g.rev_list("--full-history", "--no-merges", *all_tips, "--", rk)
            need(nonmerge == [reveal] and not any(g.blob_id(p_, rk) for p_ in g.parents(reveal)),
                 f"REVEALED_KEY.json must be added in exactly one commit across the allowed branches and never modified, "
                 f"removed or re-added ({len(nonmerge)} non-merge commit(s) touch it)")
            outside = [c[:12] for c in g.rev_list("--full-history", *all_tips, "--", rk)
                          if c != reveal and not (g.is_ancestor(reveal, c) and g.blob_id(c, rk) == key_blob)]
            need(not outside, f"REVEALED_KEY.json is added, changed or removed outside the reveal (commit(s) {outside[:3]}, "
                 "merges included)")
            need(g.blob_id(tip, rk) == key_blob, "REVEALED_KEY.json at the branch tip differs from the reveal commit")
            early = [c[:12] for c in g.commits_with_object(key_blob, all_tips) if c != reveal and not
                     (g.is_ancestor(gc, c) and c != gc and g.is_ancestor(reveal, c))]
            need(not early, f"the revealed key's bytes were committed outside the reveal (at {early[:3]}: before grading, "
                 "under another name, or on another branch)")
            # the key's nonce, in any encoding-preserving copy (reformatted JSON, other path, other branch), may only appear
            # in the reveal and its descendants: `git log -m --no-renames -S<nonce>` over every allowed tip
            try:
                rk_nonce = json.loads(g.show(reveal, rk) or b"null").get("nonce")
            except (ValueError, AttributeError):
                rk_nonce = None
            if need(isinstance(rk_nonce, str) and re.fullmatch(r"[0-9a-f]+", rk_nonce)
                    and len(rk_nonce) >= rule["min_nonce_hex_chars"],
                    "REVEALED_KEY.json at the reveal has no hex nonce to trace (a key without a nonce is rejected)"):
                leaked = [c[:12] for c in g.commits_with_string(rk_nonce, all_tips)
                          if c != reveal and not g.is_ancestor(reveal, c)]
                need(not leaked, f"the revealed key's nonce appears in commit(s) outside the reveal and its descendants "
                     f"(at {leaked[:3]}: a reformatted or relocated copy of the key)")
            want = (g.blob_id(gc, sheet_p), g.blob_id(gc, final_p))
            changed = [c[:12] for c in g.rev_list("--ancestry-path", f"{gc}..{reveal}")
                       if (g.blob_id(c, sheet_p), g.blob_id(c, final_p)) != want]
            need(all(want) and not changed, "the sheet or GRADING_FINAL.txt changed between grading_commit and the reveal "
                 f"(at {changed[:3]}; they must be byte-identical at every commit in between)")
            frozen = [p_ for p_ in (rec_rel, res_rel) if g.blob_id(tip, p_) != g.blob_id(reveal, p_)
                      or g.rev_list("--full-history", "--no-merges", f"{reveal}..{tip}", "--", p_)]
            need(not frozen, f"evidence changed or missing after the reveal commit: {frozen}")
            if expected:
                facts["expected_shas"] = expected
                for k, have in (("grading_commit", gc), ("reveal_commit", reveal)):
                    if k in expected:
                        need(expected[k] == have, f"{k} {have[:12]} != pinned {expected[k][:12]} (history rewritten?)")
                if "remote_tip_sha" in expected:
                    need(g.is_ancestor(expected["remote_tip_sha"], tip),
                         f"pinned remote_tip_sha {expected['remote_tip_sha'][:12]} is no longer reachable from {branch} (history rewritten)")
            if signers["required"]:
                fin_blob = want[1]
                intro = [c for c in g.rev_list("--full-history", gc, "--", final_p)
                         if fin_blob and g.blob_id(c, final_p) == fin_blob and not any(g.blob_id(p_, final_p) == fin_blob
                                                                                      for p_ in g.parents(c))]
                good, why = g.check_signer(gc, signers)
                if need(good, f"grading_commit {gc[:12]} lacks a valid signature from a required signer: {why}"):
                    facts["signed_by"] = why
                need(intro, "cannot find the commit that added GRADING_FINAL.txt")
                for c in intro:
                    if c != gc:
                        good_c, why_c = g.check_signer(c, signers)
                        need(good_c, f"the commit {c[:12]} that added GRADING_FINAL.txt lacks a valid signature from a "
                             f"required signer: {why_c}")
            sheet, final = g.show(gc, sheet_p), g.show(gc, final_p)
            items_b, commit_b = g.show(gc, f"{kit}/items.json"), g.show(gc, f"{kit}/KEY_COMMITMENT.txt")
            key_b = g.show(reveal, rk)
            rec_b, res_b = g.show(tip, rec_rel), g.show(tip, res_rel)
            files = {"grading_sheet.csv@grading_commit": sheet, "GRADING_FINAL.txt@grading_commit": final,
                     "items.json@grading_commit": items_b, "KEY_COMMITMENT.txt@grading_commit": commit_b,
                     "REVEALED_KEY.json@reveal": key_b, f"{rec_rel}@tip": rec_b, f"{res_rel}@tip": res_b}
            if not need(all(v is not None for v in files.values()),
                        "missing on the remote: " + ", ".join(k for k, v in files.items() if v is None)):
                return out
            commitment = dict(l.split(": ", 1) for l in commit_b.decode("utf-8").splitlines() if ": " in l)
            key_sha = commitment.get("key_sha256", "")
            # scored once: every results file, record and FINALIZED.txt for this key commitment, in any commit reachable
            # from any allowed branch (deleted files included), names this grading_commit
            try:
                kj = json.loads(key_b)
                kit_tag = f"{kj.get('kit')} drawn {kj.get('created_at')}"
            except ValueError:
                kit_tag = ""
            named = g.evidence_grading_commits(key_sha, kit_tag, f"{ev_root}/holdout", fin_p)
            others = sorted(str(k)[:12] for k in named if k != gc)
            need(not others, f"this key commitment was also scored from other grading commit(s) {others}; a kit is scored once "
                 f"({'; '.join(f'{str(k)[:12]} in {v[:2]}' for k, v in named.items() if k != gc)})")
        # --- content checks (no further git) ---
        need(json.loads(rec_b) == record, "the record differs from the record committed on the remote")
        need(record.get("integrity_hash") == "sha256:" + _sha256(res_b), "integrity_hash != sha256 of the committed results file")
        fm = _FINAL_RE.search(final.decode("utf-8", "replace"))
        if not need(fm, "GRADING_FINAL.txt has no FINAL line"):
            return out
        need(_sha256(sheet) == fm["sheet"], "sha256(grading_sheet.csv) at grading_commit != sheet_sha256 in GRADING_FINAL.txt")
        need(_sha256(key_b) == key_sha, "sha256(REVEALED_KEY.json) != key_sha256 in KEY_COMMITMENT.txt (bad reveal or commitment)")
        need(_sha256(items_b) == commitment.get("items_json_sha256"), "sha256(items.json) != items_json_sha256 in KEY_COMMITMENT.txt")
        key, items = json.loads(key_b), json.loads(items_b)["items"]
        nonce, seed = str(key.get("nonce", "")), str(key.get("seed", ""))
        need(re.fullmatch(r"[0-9a-f]+", nonce) and len(nonce) >= rule["min_nonce_hex_chars"] and re.fullmatch(r"[0-9a-f]+", seed),
             "REVEALED_KEY.json lacks a hex nonce of >= 256 bits and a hex seed")
        res = json.loads(res_b)
        need(res.get("key_sha256") == key_sha and res.get("grading_sheet_sha256") == _sha256(sheet)
             and res.get("items_json_sha256") == _sha256(items_b), "results file hashes differ from the committed inputs")
        need(all(res.get(f) == record.get(f) for f in ("grading_commit", "remote_url", "remote_branch", "remote_tip_sha")),
             "results and record git fields differ")
        by_id = {i["item_id"]: i for i in items}
        need(set(key.get("items", {})) == set(by_id) and all(
            _sha256(by_id[h]["candidate_answer"].encode()) == k.get("candidate_answer_sha256") for h, k in key["items"].items()),
            "revealed key and items.json disagree")
        if errors:
            return out
        grades, perrs = _holdout_parse_sheet(sheet, items)
        if not need(not perrs, "sheet invalid: " + "; ".join(perrs[:3])):
            return out
        grader = " ".join(fm["grader"].split())
        need({g_["grader"] for g_ in grades.values()} == {grader} and record.get("grader") == grader,
             "sheet graders, GRADING_FINAL grader and record grader differ")
        kit_sum, assets = _holdout_recompute(key, grades, rule)
        if not need(aid in assets, f"{aid} has no items in the revealed key"):
            return out
        a = assets[aid]
        facts["recomputed"] = {"score": a["score"], "baseline_score": a["baseline_score"], "n_items": a["n_items"],
                               "passed": a["passed"], "kit_passed": kit_sum["passed"]}
        need(record.get("score") == a["score"] == res.get("score"), f"score {record.get('score')} != recomputed {a['score']}")
        need(record.get("baseline_score") == a["baseline_score"] == res.get("baseline_score"),
             f"baseline_score {record.get('baseline_score')} != recomputed {a['baseline_score']}")
        need(record.get("n_items") == a["n_items"] == res.get("n_items"), f"n_items {record.get('n_items')} != {a['n_items']}")
        need(record.get("passed") is a["passed"] and res.get("passed") is a["passed"],
             f"passed {record.get('passed')!r} != recomputed {a['passed']}")
    except HoldoutVerifyError as exc:
        errors.append(str(exc))
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, UnicodeDecodeError) as exc:
        errors.append(f"malformed remote content: {exc.__class__.__name__}: {exc}")
    out["ok"] = not errors
    return out


def check_synthesis_asset(subject: dict, pol: dict, asset_root: Path | None, repo_root: Path | None = None,
                          verify_holdout_remote: bool = False, holdout_test_remote: str | Path | None = None) -> dict:
    """Plan 5.2 'Synthesis asset' record (asset.json). Contradictions with provenance.json are a
    rights failure (cap reference_only); an absent or incomplete record only blocks sale."""
    cid, asset, prov = "synthesis_asset_record", subject["asset"], subject["provenance"] or {}
    req = pol["gate"]["synthesis_asset_sale_requirements"]
    if asset is None:
        where = subject["asset_path"] or "no asset.json / asset_path supplied"
        return _check(cid, "fail", [f"asset.json (plan 5.2 synthesis asset) missing ({where}); required for sale"], "approved_for_private_use", "sale")
    errors = [f"schema: {e}" for e in validate(asset, pol["asset_schema"])]
    if errors:
        return _check(cid, "fail", errors, "approved_for_private_use", "sale")
    conflicts = []
    if prov:
        if asset["asset_id"] != prov.get("asset_id"):
            conflicts.append(f"asset_id {asset['asset_id']!r} != provenance asset_id {prov.get('asset_id')!r}")
        if asset["ownership_class"] != prov.get("ownership_class"):
            conflicts.append(f"ownership_class {asset['ownership_class']!r} != provenance {prov.get('ownership_class')!r}")
        if asset["integrity_hash"] != prov.get("integrity_hash"):
            conflicts.append("integrity_hash differs from provenance.json")
        by_id = {src.get("source_id"): src for src in prov.get("sources", [])}
        for ref in asset["source_refs"]:
            src = by_id.get(ref["source_id"])
            if src is None:
                conflicts.append(f"source_ref {ref['source_id']!r} not pinned in provenance.json#sources")
            elif str(src.get("version")) != ref["version"]:
                conflicts.append(f"source_ref {ref['source_id']!r} version {ref['version']!r} != pinned {src.get('version')!r}")
        missing_refs = set(by_id) - {r["source_id"] for r in asset["source_refs"]}
        if missing_refs:
            conflicts.append(f"provenance sources not listed in source_refs: {sorted(missing_refs)}")
        sources_ok = all(src.get("commercial_use_allowed") is True and src.get("redistribution_allowed") is True for src in by_id.values())
        if asset["commercial_redistribution_allowed"] is True and not sources_ok:
            conflicts.append("commercial_redistribution_allowed is true but at least one source does not allow commercial use + redistribution")
        if asset["attribution_required"] is False and any(src.get("attribution_required") for src in by_id.values()):
            conflicts.append("attribution_required is false but a source requires attribution")
        if asset["share_alike_required"] is False and any(src.get("share_alike_required") for src in by_id.values()):
            conflicts.append("share_alike_required is false but a source requires share-alike")
    base = asset_root or subject["base_dir"]
    for name in ("human_layer", "machine_layer"):
        layer = asset.get(name)
        if layer:
            lp = Path(layer["path"])
            lp = lp if lp.is_absolute() else base / lp
            if lp.is_file() and _sha256_file(lp) != layer["sha256"]:
                conflicts.append(f"{name} sha256 mismatch for {layer['path']}")
    if conflicts:
        return _check(cid, "fail", conflicts, "reference_only", "rights")
    gaps = [f"{f} is null (incomplete synthesis asset)" for f in req["non_null_fields"] if asset.get(f) is None]
    n_listed = sum(len(v) for v in asset["validation_evidence_ids"].values())
    hlog: dict = {}
    n_resolved, evidence_problems, not_passed = resolve_evidence_records(
        asset, pol, repo_root, verify_holdout_remote=verify_holdout_remote, holdout_test_remote=holdout_test_remote,
        holdout_log=hlog)
    not_passed_notes = [f"validation evidence: {n}" for n in not_passed]
    holdout_warnings = [f"validation evidence: {n}" for n in hlog["warnings"]]
    holdout_info = [f"validation evidence: {n}" for n in hlog["info"]]
    gaps += [f"validation evidence: {p}" for p in evidence_problems]
    if n_listed == 0:
        gaps.append("no sandbox/benchmark/holdout/regression validation evidence ids")
    elif n_resolved < req["min_validation_evidence_ids"]:
        gaps.append(f"{n_resolved} of {n_listed} validation evidence id(s) resolved with passed: true; "
                    f"sale requires >= {req['min_validation_evidence_ids']}")
    if asset.get("commercial_redistribution_allowed") is not True:
        gaps.append(f"commercial_redistribution_allowed is {asset.get('commercial_redistribution_allowed')!r}")
    if pol["gate"]["holdout_verification"].get("required_for_sale", True) and hlog["holdout_unverified"]:
        gaps.append(f"{HOLDOUT_NOT_VERIFIED} ({hlog['holdout_unverified']} of {hlog['holdout_relied']} holdout record(s) "
                    "with passed: true not verified against the canonical remote; run with --verify-holdout-remote)")
    if gaps:
        return _check(cid, "fail", gaps + not_passed_notes + holdout_warnings, "approved_for_private_use", "sale")
    resolved_note = (f"{n_resolved} validation evidence id(s) resolved under {asset.get('evidence_root', DEFAULT_EVIDENCE_ROOT)} "
                     "with passed: true (only these count)")
    tail = not_passed_notes + holdout_info + holdout_warnings
    if len(asset["perspectives_used"]) < req["warn_if_perspectives_below"]:
        return _check(cid, "warn", [f"only {len(asset['perspectives_used'])} perspective(s) used; multi-view synthesis expects several", resolved_note] + tail, scope="sale")
    if holdout_warnings:
        return _check(cid, "warn", holdout_warnings + ["asset.json complete and consistent with provenance.json", resolved_note]
                      + not_passed_notes + holdout_info, scope="sale")
    return _check(cid, "pass", ["asset.json complete and consistent with provenance.json", resolved_note] + tail, scope="sale")


def package_gate_status(included_outcomes: list[str | None], excluded_reference_only_sources: list) -> str:
    """Roll per-asset outcomes up to the plan 5.2 package license_gate_status
    (config/license_provenance_gate.json#package_status_mapping)."""
    if not included_outcomes or any(o in (None, "pending") for o in included_outcomes):
        return "pending"
    if any(o != "approved_for_sale" for o in included_outcomes):
        return "fail"
    return "reference_only_bundle" if excluded_reference_only_sources else "pass"


def evaluate(target: Path, provenance_override: Path | None = None, asset_root: Path | None = None,
             evaluated_at: str | None = None, repo_root: Path | None = None, verify_holdout_remote: bool = False,
             holdout_test_remote: str | Path | None = None) -> dict:
    """holdout_test_remote is for this gate's tests only (a local repository standing in for the canonical remote);
    holdout records verified against it never count and cap the outcome at approved_for_private_use."""
    pol = load_policies()
    subject = load_subject(target, provenance_override)
    checks = [
        check_provenance(subject, pol),
        check_sources_pinned(subject, pol),
        check_ownership(subject, pol),
        check_rights(subject, pol),
        check_attribution(subject, pol, asset_root),
        check_blocked(subject, pol),
        check_asset_integrity(subject, pol, asset_root),
        check_scorecard(subject, pol),
        check_synthesis_asset(subject, pol, asset_root, repo_root, verify_holdout_remote, holdout_test_remote),
        check_owner_approval(subject, pol),
    ]
    ranked = pol["gate"]["outcomes_ranked_low_to_high"]
    outcome = ranked[-1]
    for c in checks:
        if c["outcome_cap"] and ranked.index(c["outcome_cap"]) < ranked.index(outcome):
            outcome = c["outcome_cap"]
    rights_caps = [c["outcome_cap"] for c in checks if c["scope"] == "rights" and c["outcome_cap"]]
    ceiling = min(rights_caps, key=ranked.index) if rights_caps else ranked[-1]
    prov = subject["provenance"] or {}
    cand = subject["candidate"]
    inputs = {"target": str(target)}
    if repo_root is not None:
        inputs["repo_root"] = str(repo_root)
    if subject["candidate_path"]:
        inputs["candidate_path"] = str(subject["candidate_path"])
        inputs["candidate_sha256"] = _sha256_file(subject["candidate_path"])
    if subject["provenance_path"]:
        inputs["provenance_path"] = str(subject["provenance_path"])
        if Path(subject["provenance_path"]).exists():
            inputs["provenance_sha256"] = _sha256_file(Path(subject["provenance_path"]))
    if subject["asset_path"] and Path(subject["asset_path"]).exists():
        inputs["asset_record_path"] = str(subject["asset_path"])
        inputs["asset_record_sha256"] = _sha256_file(Path(subject["asset_path"]))
    return {
        "schema": "dreamco.data_package_license_gate.v1",
        "gate_version": GATE_VERSION,
        "asset_id": prov.get("asset_id") or cand.get("asset_id") or cand.get("candidate_id") or "unknown",
        "evaluated_at": evaluated_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": inputs,
        "policy_refs": pol["gate"]["policy_refs"],
        "outcome": outcome,
        "rights_ceiling": ceiling,
        "checks": checks,
        "failed_checks": [c["id"] for c in checks if c["status"] == "fail"],
        "warnings": [r for c in checks if c["status"] == "warn" for r in c["reasons"]],
        "sale_requirements": {
            "scorecard_minimum": pol["scorecard_minimum"],
            "scorecard_score": cand.get("scorecard_score"),
            "owner_approval_present": isinstance(cand.get("owner_approval"), dict) and cand["owner_approval"].get("approved") is True,
        },
        "truth_boundary": pol["gate"]["truth_boundary"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="Asset directory (provenance.json [+ candidate.json]) or candidate JSON file")
    ap.add_argument("--provenance", help="Explicit provenance.json path (overrides discovery)")
    ap.add_argument("--asset-root", help="Directory that provenance asset_files paths are relative to")
    ap.add_argument("--out", help="Also write the gate JSON to this path (e.g. <asset>/license_gate.json)")
    ap.add_argument("--evaluated-at", help="Override evaluated_at timestamp (for reproducible fixtures)")
    ap.add_argument("--repo-root", help="Repository root that asset.json evidence_root (default "
                    f"{DEFAULT_EVIDENCE_ROOT}) is relative to when resolving validation evidence ids "
                    "(default: this gate's repository)")
    ap.add_argument("--verify-holdout-remote", action="store_true",
                    help="verify each counting holdout evidence record independently against the canonical remote in "
                         "config/license_provenance_gate.json#holdout_verification (network: git ls-remote + full fetch of the allowed "
                         "branches into a temporary repository). Without it, holdout records count but are reported as unverified")
    args = ap.parse_args(argv)
    try:
        report = evaluate(Path(args.target), Path(args.provenance) if args.provenance else None,
                          Path(args.asset_root) if args.asset_root else None, args.evaluated_at,
                          Path(args.repo_root) if args.repo_root else None, args.verify_holdout_remote)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    errors = validate(report, load_schema(GATE_SCHEMA))
    if errors:
        print(json.dumps({"error": "gate output failed its own schema", "details": errors}), file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if report["outcome"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
