#!/usr/bin/env python3
"""Validate (and optionally assemble) a DreamCo data-package version directory.

Manifest contract: reports/DATA_PACKAGE_PRODUCT_PLAN.md section 5.2 'Sellable package manifest'
(schemas/data_package.manifest.schema.json). Default mode is a sellable build: it REFUSES (exit 1)
unless the manifest validates, contents_digest matches, every required release artifact exists,
every included asset has a license_gate.json with outcome approved_for_sale, the package
license_gate_status (recomputed from those files) is pass or reference_only_bundle, the scorecard
meets the standard tier, and quality/benchmark reports have actually passed.
--structure-only checks schema, digest and artifact layout (exit 0 when structurally valid).
--write-digest recomputes contents_digest into manifest.json (structure checks then run).
Exit codes: 0 ok, 1 refused (not sellable), 2 invalid structure/inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.license_provenance_gate import package_gate_status  # noqa: E402
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

MANIFEST_SCHEMA = ROOT / "schemas" / "data_package.manifest.schema.json"
GATE_SCHEMA = ROOT / "schemas" / "data_package_license_gate.schema.json"
PRODUCT_STANDARD = ROOT / "config" / "dataset_product_standard.json"
SCORECARD = ROOT / "config" / "dataset_evaluation_scorecard.json"
GATE_CONFIG = ROOT / "config" / "license_provenance_gate.json"


def contents_digest(pkg: Path) -> str:
    """sha256 over sorted '<sha256>  <relpath>' lines for every file except manifest.json."""
    lines = []
    for p in sorted(pkg.rglob("*")):
        if p.is_file() and p.relative_to(pkg).as_posix() != "manifest.json":
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(pkg).as_posix()}")
    return "sha256:" + hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def _resolve_artifact(pkg: Path, ref: str) -> tuple[bool, str]:
    file_part, _, key = ref.partition("#")
    target = pkg / file_part
    if not target.exists():
        return False, f"{ref}: {file_part} not found"
    if key:
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False, f"{ref}: {file_part} is not JSON"
        if key not in data or data[key] in (None, [], ""):
            return False, f"{ref}: key {key!r} missing or empty"
    return True, ref


def check_structure(pkg: Path) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    mpath = pkg / "manifest.json"
    if not mpath.is_file():
        return None, [f"manifest.json not found in {pkg}"]
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    errors += [f"manifest schema: {e}" for e in validate(manifest, load_schema(MANIFEST_SCHEMA))]
    required = json.loads(PRODUCT_STANDARD.read_text(encoding="utf-8"))["required_release_artifacts"]
    artifacts = manifest.get("release_artifacts", {})
    for name in required:
        if name not in artifacts:
            errors.append(f"release artifact {name!r} not declared (config/dataset_product_standard.json)")
            continue
        ok, msg = _resolve_artifact(pkg, artifacts[name])
        if not ok:
            errors.append(f"release artifact {name}: {msg}")
    if not (pkg / "LICENSE").is_file():
        errors.append("LICENSE file missing")
    if manifest.get("version") and pkg.name != manifest["version"]:
        errors.append(f"directory name {pkg.name!r} != version {manifest['version']!r}")
    if manifest.get("sku_id") and pkg.parent.name != manifest["sku_id"]:
        errors.append(f"parent directory {pkg.parent.name!r} != sku_id {manifest['sku_id']!r}")
    actual = contents_digest(pkg)
    if manifest.get("contents_digest") != actual:
        errors.append(f"contents_digest {manifest.get('contents_digest')!r} != computed {actual} (run --write-digest after edits)")
    detail_ids = [a["asset_id"] for a in manifest.get("assets", [])]
    for aid in detail_ids:
        if aid not in manifest.get("included_asset_ids", []):
            errors.append(f"assets[] entry {aid!r} not in included_asset_ids")
    sellable = json.loads(GATE_CONFIG.read_text(encoding="utf-8"))["package_status_mapping"]["sellable_statuses"]
    if manifest.get("license_gate_status") not in sellable:
        if manifest.get("sales_channel") not in (None, "none"):
            errors.append(f"sales_channel set while license_gate_status is not one of {sellable}")
        if manifest.get("stripe_price_id") is not None:
            errors.append(f"stripe_price_id set while license_gate_status is not one of {sellable}")
    return manifest, errors


def check_sellable(pkg: Path, manifest: dict) -> list[str]:
    refusals: list[str] = []
    gate_schema = load_schema(GATE_SCHEMA)
    tiers = {t["tier"]: t["minimum_score"] for t in json.loads(SCORECARD.read_text(encoding="utf-8"))["commercial_tiers"]}
    sellable = json.loads(GATE_CONFIG.read_text(encoding="utf-8"))["package_status_mapping"]["sellable_statuses"]
    if manifest["license_gate_status"] not in sellable:
        refusals.append(f"license_gate_status is {manifest['license_gate_status']!r}, not one of {sellable}")
    if not manifest["included_asset_ids"]:
        refusals.append("package has no included_asset_ids")
    details = {a["asset_id"]: a for a in manifest.get("assets", [])}
    outcomes: list[str | None] = []
    for aid in manifest["included_asset_ids"]:
        asset = details.get(aid)
        if asset is None:
            refusals.append(f"asset {aid}: no assets[] entry with gate/provenance paths")
            outcomes.append(None)
            continue
        for key in ("path", "provenance_path"):
            if not (pkg / asset[key]).exists():
                refusals.append(f"asset {aid}: {key} {asset[key]} missing")
        gpath = pkg / asset["license_gate_path"]
        if not gpath.is_file():
            refusals.append(f"asset {aid}: license_gate.json missing ({asset['license_gate_path']})")
            outcomes.append(None)
            continue
        gate = json.loads(gpath.read_text(encoding="utf-8"))
        errs = validate(gate, gate_schema)
        if errs:
            refusals.append(f"asset {aid}: license_gate.json invalid: {errs[:3]}")
        outcomes.append(gate.get("outcome"))
        if gate.get("outcome") != "approved_for_sale":
            refusals.append(f"asset {aid}: gate outcome {gate.get('outcome')!r} (failed: {gate.get('failed_checks')})")
        if gate.get("outcome") != asset["license_gate_outcome"]:
            refusals.append(f"asset {aid}: manifest license_gate_outcome {asset['license_gate_outcome']!r} != gate file {gate.get('outcome')!r}")
    derived = package_gate_status(outcomes, manifest["excluded_reference_only_sources"])
    if derived != manifest["license_gate_status"]:
        refusals.append(f"license_gate_status {manifest['license_gate_status']!r} != status derived from asset gate files {derived!r}")
    score = manifest["scorecard_score"]
    if score is None or score < tiers["standard"]:
        refusals.append(f"scorecard_score {score!r} below standard tier minimum {tiers['standard']}")
    elif manifest["commercial_tier"] is None or score < tiers[manifest["commercial_tier"]]:
        refusals.append(f"commercial_tier {manifest['commercial_tier']!r} inconsistent with scorecard_score {score}")
    for report in ("quality_report", "benchmark_report"):
        rpath = pkg / manifest["release_artifacts"][report]
        status = json.loads(rpath.read_text(encoding="utf-8")).get("status") if rpath.is_file() else None
        if status != "pass":
            refusals.append(f"{report} status is {status!r}, must be 'pass'")
    if manifest["release_level"] != "sellable_verified":
        refusals.append(f"release_level is {manifest['release_level']!r}, must be sellable_verified (config/data-package-maximal-testing-program.json)")
    sample = pkg / manifest["release_artifacts"]["sample_or_preview"]
    if sample.is_dir() and not [p for p in sample.iterdir() if p.name != ".gitkeep"]:
        refusals.append("sample/ preview is empty")
    return refusals


def assemble(pkg: Path, manifest: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in pkg.rglob("*") if p.is_file())
    sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(pkg).as_posix()}" for p in files]
    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    tar_path = out_dir / f"{manifest['sku_id']}-{manifest['version']}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        for p in files:
            tar.add(p, arcname=f"{manifest['sku_id']}/{manifest['version']}/{p.relative_to(pkg).as_posix()}")
    return {"archive": str(tar_path), "sha256sums": str(out_dir / "SHA256SUMS"), "file_count": len(files)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("package_dir", help="e.g. data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1")
    ap.add_argument("--structure-only", action="store_true", help="Only validate manifest schema, digest and artifact layout")
    ap.add_argument("--write-digest", action="store_true", help="Recompute contents_digest into manifest.json, then validate structure")
    ap.add_argument("--out", help="Assemble archive + SHA256SUMS here (only when the sellable build passes)")
    args = ap.parse_args(argv)
    pkg = Path(args.package_dir).resolve()
    if args.write_digest:
        mpath = pkg / "manifest.json"
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        manifest["contents_digest"] = contents_digest(pkg)
        mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest, errors = check_structure(pkg)
    report: dict = {"package_dir": str(pkg), "sku_id": (manifest or {}).get("sku_id"),
                    "version": (manifest or {}).get("version"), "structure_errors": errors}
    if errors or manifest is None:
        report["verdict"] = "invalid"
        print(json.dumps(report, indent=2))
        return 2
    if args.structure_only or args.write_digest:
        report["verdict"] = "structurally_valid"
        print(json.dumps(report, indent=2))
        return 0
    refusals = check_sellable(pkg, manifest)
    report["refusals"] = refusals
    if refusals:
        report["verdict"] = "refused"
        print(json.dumps(report, indent=2))
        return 1
    report["verdict"] = "sellable_build_passed"
    if args.out:
        report["assembled"] = assemble(pkg, manifest, Path(args.out))
    report["truth_boundary"] = "Passing this build is release evidence, not a listing; publishing or pricing still needs the owner's explicit action."
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
