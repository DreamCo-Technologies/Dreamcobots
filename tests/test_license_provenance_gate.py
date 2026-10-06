import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_sellable_data_package as builder  # noqa: E402
from tools import license_provenance_gate as gate  # noqa: E402
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

CANDIDATES = ROOT / "data" / "dreamco_knowledge" / "assets" / "_candidates" / "edu_cs_11.0701"
TEMPLATE_PROVENANCE = CANDIDATES / "templates" / "provenance.json"
TEMPLATE_CANDIDATE = CANDIDATES / "templates" / "candidate.json"
TEMPLATE_ASSET = CANDIDATES / "templates" / "asset.json"
PACKAGE = ROOT / "data" / "dreamco_knowledge" / "packages" / "DP-ONET-OCC-SYN" / "0.0.1"

GOOD_FOOTER = (
    "Crosswalk Files by USDOL/ETA are licensed under CC BY 4.0 (Education_CIP_to_ONET_SOC crosswalk). "
    "This page includes information from the O*NET 31.0 Database by the U.S. Department of Labor, "
    "Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. "
    "O*NET\u00ae is a trademark of USDOL/ETA. DreamCo has modified all or some of this information. "
    "USDOL/ETA has not approved, endorsed, or tested these modifications.\n"
)


# Generic resolution fixture. A benchmark id, because holdout evidence is now remote-verified before it can support a
# sale (see the holdout tests at the end); benchmark/regression/sandbox records count exactly as before.
EVIDENCE_ID = "benchmark:edu-cs-11.0701:20261002-01"
EVIDENCE_KIND = EVIDENCE_ID.split(":")[0]


@pytest.fixture(autouse=True)
def evidence_repo(tmp_path, monkeypatch):
    """Each test gets its own repo root for validation evidence ids (gate.DEFAULT_REPO_ROOT)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(gate, "DEFAULT_REPO_ROOT", repo)
    return repo


def evidence_record(eid: str) -> dict:
    return {
        "evidence_id": eid, "capability_id": "career-pathway-study-plan", "source_type": "human_evaluation",
        "source_reference": "sha256:" + "a" * 64, "retrieved_at": "2026-10-02T18:00:00-05:00",
        "content_version": "fixture", "license_or_usage_basis": "DreamCo-original evaluation output",
        "transformation": "original_evaluation", "evaluator_version": "fixture grader v1",
        "integrity_hash": "sha256:" + "b" * 64, "split": "holdout", "n_items": 12, "metric": "rubric points / max",
        "score": 0.8, "threshold": 0.7, "passed": True,
    }


def write_evidence(repo: Path, eid: str, evidence_root: str = gate.DEFAULT_EVIDENCE_ROOT, record: dict | None = None) -> Path:
    kind, asset_id, run = eid.split(":")
    path = repo / evidence_root / kind / asset_id / f"{run}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record if record is not None else evidence_record(eid)), encoding="utf-8")
    return path


def complete_layers(a):
    a["machine_layer"] = {"path": "tasks.jsonl", "format": "jsonl", "sha256": "1" * 64}
    a["dreamco_analysis"] = {"agree": ["x"], "reject": [], "improve": ["y"], "still_need_test": ["z"]}
    a["validation_evidence_ids"][EVIDENCE_KIND] = [EVIDENCE_ID]


def make_asset(tmp_path: Path, *, footer: str = GOOD_FOOTER, prov_edit=None, cand_edit=None, asset_edit=None,
               write_evidence_files: bool = True) -> Path:
    asset_dir = tmp_path / "asset"
    (asset_dir / "study_plans").mkdir(parents=True)
    body = "# Study plan: Computer Science (CIP 11.0701)\n\n---\n" + footer
    plan = asset_dir / "study_plans" / "11.0701_computer_science.md"
    plan.write_text(body, encoding="utf-8")
    digest = hashlib.sha256(plan.read_bytes()).hexdigest()
    prov = json.loads(TEMPLATE_PROVENANCE.read_text(encoding="utf-8"))
    prov["asset_files"] = [{"path": "study_plans/11.0701_computer_science.md", "sha256": digest}]
    prov["integrity_hash"] = f"sha256:{digest}"
    cand = json.loads(TEMPLATE_CANDIDATE.read_text(encoding="utf-8"))
    asset = json.loads(TEMPLATE_ASSET.read_text(encoding="utf-8"))
    asset["integrity_hash"] = f"sha256:{digest}"
    asset["human_layer"]["sha256"] = digest
    if asset_edit:
        asset_edit(asset)
    if prov_edit:
        prov_edit(prov)
    if cand_edit:
        cand_edit(cand)
    (asset_dir / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")
    (asset_dir / "candidate.json").write_text(json.dumps(cand), encoding="utf-8")
    (asset_dir / "asset.json").write_text(json.dumps(asset), encoding="utf-8")
    if write_evidence_files:  # write a conforming record for every well-formed id, under the asset's evidence_root
        for key, ids in asset["validation_evidence_ids"].items():
            for eid in ids:
                parts = eid.split(":")
                if len(parts) == 3 and parts[0] == key and parts[1] == asset["asset_id"]:
                    write_evidence(gate.DEFAULT_REPO_ROOT, eid, asset.get("evidence_root", gate.DEFAULT_EVIDENCE_ROOT))
    return asset_dir


def check(report: dict, check_id: str) -> dict:
    return next(c for c in report["checks"] if c["id"] == check_id)


def owner_ok(c):
    c["owner_approval"] = {"approved": True, "approver": "Irean Jordan", "approved_at": "2026-10-02T17:00:00-05:00", "scope": ["sale"]}


def test_good_onet_asset_without_owner_approval_is_private_use_only(tmp_path):
    report = gate.evaluate(make_asset(tmp_path))
    assert report["outcome"] == "approved_for_private_use"
    assert report["rights_ceiling"] == "approved_for_sale"
    assert set(report["failed_checks"]) == {"scorecard_threshold", "synthesis_asset_record", "owner_approval"}
    for cid in ("provenance_schema_conformance", "sources_pinned", "ownership_class_valid",
                "commercial_and_redistribution_rights", "attribution_present", "asset_file_integrity"):
        assert check(report, cid)["status"] == "pass", cid
    assert validate(report, load_schema(gate.GATE_SCHEMA)) == []


def test_sale_requires_scorecard_owner_approval_and_complete_asset(tmp_path):
    def sellable(c):
        owner_ok(c)
        c["scorecard_score"] = 80
    assert gate.evaluate(make_asset(tmp_path / "a", cand_edit=sellable, asset_edit=complete_layers))["outcome"] == "approved_for_sale"
    incomplete = gate.evaluate(make_asset(tmp_path / "a2", cand_edit=sellable))
    assert incomplete["outcome"] == "approved_for_private_use"
    assert check(incomplete, "synthesis_asset_record")["status"] == "fail"

    def low_score(c):
        owner_ok(c)
        c["scorecard_score"] = 74.9
    assert gate.evaluate(make_asset(tmp_path / "b", cand_edit=low_score))["outcome"] == "approved_for_private_use"

    def score_only(c):
        c["scorecard_score"] = 95
    assert gate.evaluate(make_asset(tmp_path / "c", cand_edit=score_only))["outcome"] == "approved_for_private_use"

    def wrong_approver(c):
        owner_ok(c)
        c["owner_approval"]["approver"] = "someone else"
        c["scorecard_score"] = 95
    report = gate.evaluate(make_asset(tmp_path / "d", cand_edit=wrong_approver, asset_edit=complete_layers))
    assert report["outcome"] == "approved_for_private_use"
    assert check(report, "owner_approval")["status"] == "fail"


def test_missing_ownership_class_fails(tmp_path):
    def drop(p):
        del p["ownership_class"]
    report = gate.evaluate(make_asset(tmp_path, prov_edit=drop, cand_edit=lambda c: c.pop("ownership_class")))
    own = check(report, "ownership_class_valid")
    assert own["status"] == "fail"
    assert any("ownership_class missing" in r for r in own["reasons"])
    assert check(report, "provenance_schema_conformance")["status"] == "fail"
    assert report["outcome"] == "reference_only"


def test_invalid_or_reference_only_ownership_class(tmp_path):
    def bogus(p):
        p["sources"][0]["ownership_class"] = "dreamco_owned_because_we_downloaded_it"
    assert check(gate.evaluate(make_asset(tmp_path / "a", prov_edit=bogus)), "ownership_class_valid")["status"] == "fail"

    def unknown(p):
        p["ownership_class"] = "unknown_do_not_publish"
    assert gate.evaluate(make_asset(tmp_path / "b", prov_edit=unknown))["outcome"] == "reference_only"


def test_redistribution_false_is_reference_only(tmp_path):
    def no_redist(p):
        p["sources"][0]["redistribution_allowed"] = False
    def sellable(c):
        owner_ok(c)
        c["scorecard_score"] = 99
    report = gate.evaluate(make_asset(tmp_path, prov_edit=no_redist, cand_edit=sellable, asset_edit=complete_layers))
    assert report["outcome"] == "reference_only"
    assert check(report, "commercial_and_redistribution_rights")["status"] == "fail"


def test_commercial_false_caps_at_private_use(tmp_path):
    def no_comm(p):
        p["sources"][1]["commercial_use_allowed"] = False
    def honest(a):
        a["commercial_redistribution_allowed"] = False
    report = gate.evaluate(make_asset(tmp_path, prov_edit=no_comm, asset_edit=honest))
    assert report["outcome"] == "approved_for_private_use"
    assert report["rights_ceiling"] == "approved_for_private_use"


def test_hard_fail_flag_is_blocked_and_exits_nonzero(tmp_path, capsys):
    def flagged(c):
        c["flags"] = ["credentials/secrets"]
    asset = make_asset(tmp_path, cand_edit=flagged)
    assert gate.evaluate(asset)["outcome"] == "blocked"
    assert gate.main([str(asset)]) == 1
    assert json.loads(capsys.readouterr().out)["outcome"] == "blocked"


def test_no_sources_is_blocked(tmp_path):
    cand = tmp_path / "candidate.json"
    cand.write_text(json.dumps({"candidate_id": "x", "ownership_class": "dreamco_owned"}), encoding="utf-8")
    assert gate.evaluate(cand)["outcome"] == "blocked"


def test_unpinned_source_fails(tmp_path):
    def unpin(p):
        p["sources"][1].pop("sha256")
    report = gate.evaluate(make_asset(tmp_path, prov_edit=unpin))
    assert check(report, "sources_pinned")["status"] == "fail"
    assert report["outcome"] == "reference_only"


def test_missing_non_endorsement_notice_fails_attribution(tmp_path):
    footer = GOOD_FOOTER.replace("USDOL/ETA has not approved, endorsed, or tested these modifications.", "")
    def strip_text(p):
        p["attribution_text"] = footer
    report = gate.evaluate(make_asset(tmp_path, footer=footer, prov_edit=strip_text))
    att = check(report, "attribution_present")
    assert att["status"] == "fail"
    assert any("non_endorsement_notice" in r for r in att["reasons"])
    assert report["outcome"] == "approved_for_private_use"


def test_asset_hash_mismatch_fails(tmp_path):
    def tamper(p):
        p["asset_files"][0]["sha256"] = "0" * 64
    report = gate.evaluate(make_asset(tmp_path, prov_edit=tamper))
    assert check(report, "asset_file_integrity")["status"] == "fail"
    assert report["outcome"] == "reference_only"


def test_cs_sample_as_is_records_known_gaps():
    report = gate.evaluate(CANDIDATES / "as_is" / "candidate.json")
    assert report["outcome"] == "reference_only"
    assert {"provenance_schema_conformance", "ownership_class_valid"} <= set(report["failed_checks"])
    assert check(report, "sources_pinned")["status"] == "pass"


def test_synthesis_asset_contradicting_provenance_is_reference_only(tmp_path):
    def overclaim(a):
        complete_layers(a)
        a["ownership_class"] = "dreamco_owned"
        a["source_refs"][0]["version"] = "30.3"
    report = gate.evaluate(make_asset(tmp_path, asset_edit=overclaim))
    rec = check(report, "synthesis_asset_record")
    assert rec["status"] == "fail" and rec["scope"] == "rights"
    assert any("ownership_class" in r for r in rec["reasons"])
    assert any("30.3" in r for r in rec["reasons"])
    assert report["outcome"] == "reference_only"


def test_synthesis_asset_redistribution_overclaim(tmp_path):
    def no_redist(p):
        p["sources"][1]["redistribution_allowed"] = False
    report = gate.evaluate(make_asset(tmp_path, prov_edit=no_redist, asset_edit=complete_layers))
    assert any("commercial_redistribution_allowed is true" in r for r in check(report, "synthesis_asset_record")["reasons"])


def test_package_status_mapping():
    f = gate.package_gate_status
    assert f([], []) == "pending"
    assert f(["approved_for_sale", None], []) == "pending"
    assert f(["approved_for_sale"], []) == "pass"
    assert f(["approved_for_sale"], [{"source_id": "book", "reason": "redistribution forbidden"}]) == "reference_only_bundle"
    for bad in ("approved_for_private_use", "reference_only", "blocked"):
        assert f(["approved_for_sale", bad], []) == "fail"


def test_templates_validate():
    prov = json.loads(TEMPLATE_PROVENANCE.read_text(encoding="utf-8"))
    assert validate(prov, load_schema(gate.PROVENANCE_SCHEMA)) == []
    asset = json.loads(TEMPLATE_ASSET.read_text(encoding="utf-8"))
    assert validate(asset, load_schema(gate.SYNTHESIS_ASSET_SCHEMA)) == []
    lg = json.loads((CANDIDATES / "templates" / "license_gate.json").read_text(encoding="utf-8"))
    assert validate(lg, load_schema(gate.GATE_SCHEMA)) == []
    assert lg["outcome"] == "approved_for_private_use"


def test_schema_enums_match_policy_configs():
    schema = load_schema(gate.PROVENANCE_SCHEMA)
    policy = json.loads(gate.OWNERSHIP_POLICY.read_text(encoding="utf-8"))
    evidence = json.loads(gate.EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    assert schema["$defs"]["ownership_class"]["enum"] == policy["ownership_classes"]
    assert schema["properties"]["source_type"]["enum"] == evidence["source_types"]
    assert schema["$defs"]["transformation_type"]["enum"] == evidence["transformation_types"]
    for field in evidence["required_fields"]:
        assert field in schema["required"]
    asset_schema = load_schema(gate.SYNTHESIS_ASSET_SCHEMA)
    perspectives = json.loads((ROOT / "buddy" / "learning" / "multi_perspective_policy.json").read_text(encoding="utf-8"))["perspectives"]
    assert asset_schema["properties"]["perspectives_used"]["items"]["enum"] == perspectives
    assert asset_schema["properties"]["ownership_class"]["enum"] == policy["ownership_classes"]
    plan = json.loads((ROOT / "reports" / "data-package-product.json").read_text(encoding="utf-8"))
    summary = plan["storage_schema_summary"]
    for field in summary["asset_required"]:
        assert field in asset_schema["required"], field
    manifest_schema = load_schema(builder.MANIFEST_SCHEMA)
    for field in summary["package_manifest_required"]:
        assert field in manifest_schema["required"] or field in manifest_schema["properties"]["release_artifacts"]["required"], field
    manifest = load_schema(builder.MANIFEST_SCHEMA)
    standard = json.loads(builder.PRODUCT_STANDARD.read_text(encoding="utf-8"))
    assert manifest["properties"]["release_artifacts"]["required"] == standard["required_release_artifacts"]


def test_manifest_schema_validates_skeleton():
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    assert validate(manifest, load_schema(builder.MANIFEST_SCHEMA)) == []
    assert manifest["license_gate_status"] == "pending"
    assert manifest["included_asset_ids"] == [] and manifest["excluded_reference_only_sources"] == []
    assert manifest["scorecard_score"] is None
    assert manifest["sales_channel"] == "none"
    assert manifest.get("stripe_price_id") is None
    assert manifest["contents_digest"] == builder.contents_digest(PACKAGE)
    gate_enum = load_schema(builder.MANIFEST_SCHEMA)["$defs"]["package_gate_status"]["enum"]
    assert gate_enum == ["pending", "pass", "fail", "reference_only_bundle"]
    assert manifest["known_limitations"]
    assert (PACKAGE / "sample" / ".gitkeep").exists()
    for stub in ("quality_report.json", "benchmark_report.json"):
        assert json.loads((PACKAGE / stub).read_text(encoding="utf-8"))["status"] == "not_run"


def test_builder_structure_ok_but_refuses_unsellable_skeleton(capsys):
    assert builder.main([str(PACKAGE), "--structure-only"]) == 0
    capsys.readouterr()
    assert builder.main([str(PACKAGE)]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["verdict"] == "refused"
    assert any("license_gate_status" in r for r in out["refusals"])


def test_builder_rejects_sale_signals_without_gate(tmp_path, capsys):
    import shutil
    pkg = tmp_path / "DP-ONET-OCC-SYN" / "0.0.1"
    shutil.copytree(PACKAGE, pkg)
    manifest = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
    manifest["sales_channel"] = "direct_stripe"
    manifest["stripe_price_id"] = "price_123"
    (pkg / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert builder.main([str(pkg)]) == 2
    assert json.loads(capsys.readouterr().out)["verdict"] == "invalid"


def test_builder_detects_contents_digest_drift(tmp_path, capsys):
    import shutil
    pkg = tmp_path / "DP-ONET-OCC-SYN" / "0.0.1"
    shutil.copytree(PACKAGE, pkg)
    assert builder.main([str(pkg), "--structure-only"]) == 0
    (pkg / "dataset_card.md").write_text("tampered\n", encoding="utf-8")
    capsys.readouterr()
    assert builder.main([str(pkg), "--structure-only"]) == 2
    assert any("contents_digest" in e for e in json.loads(capsys.readouterr().out)["structure_errors"])
    assert builder.main([str(pkg), "--write-digest"]) == 0


def test_minimal_validator_rejects_bad_manifest():
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(manifest)
    bad["license_gate_status"] = "approved_for_sale"  # gate outcome, not a package status
    bad["extra"] = 1
    del bad["known_limitations"]
    errors = validate(bad, load_schema(builder.MANIFEST_SCHEMA))
    assert len(errors) == 3


# --- evidence_root + validation evidence id resolution ------------------------------------------------

def sellable(c):
    owner_ok(c)
    c["scorecard_score"] = 80


def synthesis(report: dict) -> dict:
    return check(report, "synthesis_asset_record")


def assert_sale_scope_fail(report: dict, needle: str) -> None:
    rec = synthesis(report)
    assert rec["status"] == "fail" and rec["scope"] == "sale" and rec["outcome_cap"] == "approved_for_private_use"
    assert any(needle in r for r in rec["reasons"]), rec["reasons"]
    assert report["outcome"] == "approved_for_private_use"
    assert report["rights_ceiling"] == "approved_for_sale"  # not a rights failure


def test_evidence_root_accepted_and_ids_resolve_under_it(tmp_path, evidence_repo):
    root = "study_packs/career_pathways/data/dreamco_knowledge/evidence"
    def with_root(a):
        complete_layers(a)
        a["evidence_root"] = root
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=with_root)
    asset = json.loads((asset_dir / "asset.json").read_text(encoding="utf-8"))
    assert validate(asset, load_schema(gate.SYNTHESIS_ASSET_SCHEMA)) == []
    assert (evidence_repo / root / EVIDENCE_KIND / "edu-cs-11.0701" / "20261002-01.json").is_file()
    report = gate.evaluate(asset_dir)
    assert report["outcome"] == "approved_for_sale"
    assert any(f"1 validation evidence id(s) resolved under {root}" in r for r in synthesis(report)["reasons"])
    # the same file under the default root does not count when evidence_root points elsewhere
    def other_root(a):
        complete_layers(a)
        a["evidence_root"] = "elsewhere/evidence"
    report = gate.evaluate(make_asset(tmp_path / "b", cand_edit=sellable, asset_edit=other_root, write_evidence_files=False))
    assert_sale_scope_fail(report, "does not resolve")


def test_default_evidence_root_and_repo_root_cli(tmp_path, capsys):
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=complete_layers)
    repo = gate.DEFAULT_REPO_ROOT
    assert (repo / f"data/dreamco_knowledge/evidence/{EVIDENCE_KIND}/edu-cs-11.0701/20261002-01.json").is_file()
    n, problems = gate.resolve_evidence_ids(json.loads((asset_dir / "asset.json").read_text()), gate.load_policies(), repo)
    assert (n, problems) == (1, [])
    # --repo-root points the gate at another tree (e.g. a PR worktree)
    assert gate.main([str(asset_dir), "--repo-root", str(repo)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["outcome"] == "approved_for_sale" and out["inputs"]["repo_root"] == str(repo)
    assert gate.main([str(asset_dir), "--repo-root", str(tmp_path / "empty")]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["outcome"] == "approved_for_private_use"
    assert validate(out, load_schema(gate.GATE_SCHEMA)) == []


@pytest.mark.parametrize("bad_root", ["../evidence", "data/../../evidence", "..", "/abs/evidence", "data\\evidence", ""])
def test_bad_evidence_root_rejected(tmp_path, bad_root):
    def with_bad_root(a):
        complete_layers(a)
        a["evidence_root"] = bad_root
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=with_bad_root, write_evidence_files=False)
    asset = json.loads((asset_dir / "asset.json").read_text(encoding="utf-8"))
    assert validate(asset, load_schema(gate.SYNTHESIS_ASSET_SCHEMA)) != []
    assert_sale_scope_fail(gate.evaluate(asset_dir), "evidence_root")
    # the gate enforces the rule itself too, independent of the schema pattern
    n, problems = gate.resolve_evidence_ids(asset, gate.load_policies(), gate.DEFAULT_REPO_ROOT)
    assert n == 0 and problems and "evidence_root" in problems[0]


def test_missing_evidence_file_fails_sale(tmp_path):
    report = gate.evaluate(make_asset(tmp_path, cand_edit=sellable, asset_edit=complete_layers, write_evidence_files=False))
    assert_sale_scope_fail(report, "does not resolve")
    assert any("0 of 1 validation evidence id(s) resolved" in r for r in synthesis(report)["reasons"])


def test_kind_key_mismatch_fails(tmp_path, evidence_repo):
    eid = "benchmark:edu-cs-11.0701:20261002-01"
    write_evidence(evidence_repo, eid)
    def misfiled(a):
        complete_layers(a)
        a["validation_evidence_ids"]["holdout"] = [eid]
    report = gate.evaluate(make_asset(tmp_path, cand_edit=sellable, asset_edit=misfiled))
    assert_sale_scope_fail(report, "listed under 'holdout'")


@pytest.mark.parametrize("bad_id", ["holdout-run-001", "holdout:other-asset:20261002-01", "holdout:edu-cs-11.0701:2026-10-02",
                                    "holdout:edu-cs-11.0701:20261002-1", "validation:edu-cs-11.0701:20261002-01",
                                    "holdout:edu-cs-11.0701:20261002-01\n"])
def test_malformed_evidence_id_fails(tmp_path, bad_id):
    def malformed(a):
        complete_layers(a)
        a["validation_evidence_ids"]["holdout"] = [bad_id]
    report = gate.evaluate(make_asset(tmp_path, cand_edit=sellable, asset_edit=malformed))
    assert_sale_scope_fail(report, "is not '<kind>:edu-cs-11.0701:<YYYYMMDD>-<NN>'")


def test_one_bad_id_fails_even_with_a_resolved_one(tmp_path):
    missing = "regression:edu-cs-11.0701:20261002-09"
    def mixed(a):
        complete_layers(a)  # EVIDENCE_ID resolves (make_asset writes it)
        a["validation_evidence_ids"]["regression"] = [missing]
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=mixed)
    (gate.DEFAULT_REPO_ROOT / "data/dreamco_knowledge/evidence/regression/edu-cs-11.0701/20261002-09.json").unlink()
    report = gate.evaluate(asset_dir)
    assert_sale_scope_fail(report, missing)
    assert not any("validation evidence id(s) resolved;" in r for r in synthesis(report)["reasons"])  # 1 of 2 resolved >= min


@pytest.mark.parametrize("edit,needle", [
    (lambda r: r.update(evidence_id="holdout:edu-cs-11.0701:20261002-02"), "evidence_id is"),
    (lambda r: r.pop("passed"), "missing evidence fields ['passed']"),
    (lambda r: r.pop("integrity_hash"), "missing evidence fields ['integrity_hash']"),
])
def test_nonconforming_evidence_record_fails(tmp_path, evidence_repo, edit, needle):
    rec = evidence_record(EVIDENCE_ID)
    edit(rec)
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=complete_layers, write_evidence_files=False)
    write_evidence(evidence_repo, EVIDENCE_ID, record=rec)
    assert_sale_scope_fail(gate.evaluate(asset_dir), needle)


def test_non_json_evidence_file_fails(tmp_path, evidence_repo):
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=complete_layers, write_evidence_files=False)
    write_evidence(evidence_repo, EVIDENCE_ID).write_text("not json", encoding="utf-8")
    assert_sale_scope_fail(gate.evaluate(asset_dir), "not valid JSON")


def test_evidence_path_escaping_repo_root_via_symlink_fails(tmp_path, evidence_repo):
    outside = tmp_path / "outside"
    write_evidence(outside, EVIDENCE_ID, evidence_root="ev")
    (evidence_repo / "linked").symlink_to(outside / "ev", target_is_directory=True)
    def via_link(a):
        complete_layers(a)
        a["evidence_root"] = "linked"
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=via_link, write_evidence_files=False)
    assert_sale_scope_fail(gate.evaluate(asset_dir), "resolves outside the repo root")


@pytest.mark.parametrize("passed_value", [False, None, "true", 1])
def test_resolved_record_without_passed_true_does_not_count(tmp_path, evidence_repo, passed_value):
    rec = evidence_record(EVIDENCE_ID)
    rec["passed"] = passed_value
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=complete_layers, write_evidence_files=False)
    write_evidence(evidence_repo, EVIDENCE_ID, record=rec)
    report = gate.evaluate(asset_dir)
    assert_sale_scope_fail(report, f"{EVIDENCE_ID} resolved but passed is not true")
    assert any("0 of 1 validation evidence id(s) resolved with passed: true" in r for r in synthesis(report)["reasons"])
    asset = json.loads((asset_dir / "asset.json").read_text(encoding="utf-8"))
    n, problems = gate.resolve_evidence_ids(asset, gate.load_policies(), evidence_repo)
    assert (n, problems) == (0, [])  # it resolves and conforms; it just does not count


def test_mixed_passed_and_failed_records_meet_minimum_of_one(tmp_path, evidence_repo):
    failed = "regression:edu-cs-11.0701:20261002-02"
    def mixed(a):
        complete_layers(a)  # EVIDENCE_ID (passed: true) is written by make_asset
        a["validation_evidence_ids"]["regression"] = [failed]
    asset_dir = make_asset(tmp_path, cand_edit=sellable, asset_edit=mixed)
    rec = evidence_record(failed)
    rec["passed"] = False
    write_evidence(evidence_repo, failed, record=rec)  # overwrite make_asset's passing record with a failed one
    report = gate.evaluate(asset_dir)
    rec_check = synthesis(report)
    assert rec_check["status"] in ("pass", "warn"), rec_check  # min of 1 met by the passing record
    assert any(f"{failed} resolved but passed is not true" in r for r in rec_check["reasons"])
    assert any("1 validation evidence id(s) resolved under" in r and "passed: true" in r for r in rec_check["reasons"])
    assert report["outcome"] == "approved_for_sale"
    asset = json.loads((asset_dir / "asset.json").read_text(encoding="utf-8"))
    n, problems, not_passed = gate.resolve_evidence_records(asset, gate.load_policies(), evidence_repo)
    assert (n, problems) == (1, []) and len(not_passed) == 1 and failed in not_passed[0]


# --- holdout verification against the remote (opt-in --verify-holdout-remote) ------------------------------------
# A local bare repository stands in for the canonical GitHub remote. That is only possible through the test-only
# holdout_test_remote argument, which never lets a record count and caps the outcome, so no test here can produce a
# sale-eligible result from holdout evidence. Nothing here touches the network.

import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

HKIT = "study_packs/career_pathways/evidence/holdout_kit"
HEV = "study_packs/career_pathways/data/dreamco_knowledge/evidence"
CANON = "https://github.com/DreamCo-Technologies/Dreamcobots"
H_ASSET = "edu-cs-11.0701"
H_SPEC = [(H_ASSET, "full_strength", None), (H_ASSET, "weakened", 2), (H_ASSET, "full_strength", None),
          (H_ASSET, "weakened", 3), ("edu-x-00.0000", "weakened", 1), ("edu-x-00.0000", "full_strength", None)]


def _hgit(repo: Path, *args: str, gnupghome: Path | None = None) -> str:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(repo.parent / "fixture-home"), "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C"}
    if gnupghome is not None:
        env["GNUPGHOME"] = str(gnupghome)
    r = subprocess.run(["/usr/bin/git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "protocol.file.allow=always", "-C", str(repo), *args],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _hsheet(items: list[dict], scores: dict) -> bytes:
    rows = ["item_id,major,criterion_1,score_1,criterion_2,score_2,criterion_3,score_3,factually_correct,comments,grader,graded_at"]
    for i in items:
        s = scores[i["item_id"]]
        rows.append(f"{i['item_id']},{i['major']},C1,{s[0]},C2,{s[1]},C3,{s[2]},yes,,Irean,2026-10-03T10:00:00-05:00")
    return ("\n".join(rows) + "\n").encode()


class HoldoutRemote:
    """Synthetic kit, sheet, reveal and evidence committed in a work repo and pushed to a local bare 'remote'."""

    def __init__(self, base: Path):
        self.base, self.repo, self.remote = base, base / "work", base / "remote.git"
        self.repo.mkdir(parents=True)
        (base / "fixture-home").mkdir()
        _hgit(base, "init", "-q", "--bare", str(self.remote))
        _hgit(self.repo, "init", "-q", "-b", "main")
        self.items, self.key_items = [], {}
        for n, (aid, kind, wc) in enumerate(H_SPEC, 1):
            ans = f"synthetic answer {n}"
            qid = f"Q{n:02d}"
            self.items.append({"item_id": qid, "major": f"major {aid}", "prompt": f"prompt {n}", "candidate_answer": ans,
                               "rubric": [{"criterion": f"C{c}", "points": 2} for c in (1, 2, 3)]})
            self.key_items[qid] = {"asset_id": aid, "cip": aid, "candidate_type": kind, "weakened_criterion": wc,
                                   "accepted_scores": [[0, 1] if c == wc else [1, 2] for c in (1, 2, 3)],
                                   "expected_scores": [0 if c == wc else 2 for c in (1, 2, 3)],
                                   "candidate_answer_sha256": hashlib.sha256(ans.encode()).hexdigest()}
        self.items_b = (json.dumps({"kit": "synthetic", "items": self.items}) + "\n").encode()
        self.key_b = json.dumps({"kit": "synthetic", "created_at": "2026-10-02T12:00:00-05:00", "nonce": "ab" * 32,
                                 "seed": "cd" * 16, "items": self.key_items}).encode()
        self.commitment_b = (f"key_sha256: {hashlib.sha256(self.key_b).hexdigest()}\n"
                             f"items_json_sha256: {hashlib.sha256(self.items_b).hexdigest()}\n").encode()

    def perfect(self) -> dict:
        return {h: k["expected_scores"] for h, k in self.key_items.items()}

    def write(self, rel: str, data: bytes) -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def commit(self, msg: str, push: str | None = "main", sign: tuple | None = None) -> str:
        _hgit(self.repo, "add", "-A")
        if sign and sign[0] == "ssh":  # ("ssh", private key path) of a throwaway test key
            _hgit(self.repo, "-c", "gpg.format=ssh", "-c", "gpg.ssh.program=/usr/bin/ssh-keygen", "-c",
                  f"user.signingkey={sign[1]}", "commit", "-q", "--allow-empty", "-S", "-m", msg)
        elif sign:  # (GNUPGHOME, fingerprint) of a throwaway test key
            _hgit(self.repo, "-c", "gpg.program=/usr/bin/gpg", "-c", f"user.signingkey={sign[1]}", "commit", "-q",
                  "--allow-empty", "-S", "-m", msg, gnupghome=sign[0])
        else:
            _hgit(self.repo, "commit", "-q", "--allow-empty", "-m", msg)
        sha = _hgit(self.repo, "rev-parse", "HEAD")
        if push:
            _hgit(self.repo, "push", "-q", "--force", str(self.remote), f"HEAD:refs/heads/{push}")
        return sha

    def kit(self) -> str:
        self.write(f"{HKIT}/items.json", self.items_b)
        self.write(f"{HKIT}/KEY_COMMITMENT.txt", self.commitment_b)
        return self.commit("kit")

    def grade(self, scores: dict | None = None, tamper: bool = False, push: str | None = "main",
              sign: tuple | None = None) -> str:
        sheet = _hsheet(self.items, scores or self.perfect())
        self.write(f"{HKIT}/GRADING_FINAL.txt", (f"FINAL: grader=Irean; declared_at=2026-10-03T10:05:00-05:00; "
                                                  f"sheet_sha256={hashlib.sha256(sheet).hexdigest()}\n").encode())
        self.write(f"{HKIT}/grading_sheet.csv", sheet.replace(b",2,C3", b",1,C3", 1) if tamper else sheet)
        self.sheet_b = sheet
        return self.commit("grading final", push, sign)

    def finalize(self, gc: str, run: str = "20261003-01", key_b: bytes | None = None, edit=None,
                 push: str | None = "main") -> dict:
        """What an honest scorer would publish; computed with the gate's own rule only as a fixture convenience."""
        pol = gate.load_policies()
        rule = pol["gate"]["holdout_verification"]["pass_rule"]
        sheet = (self.repo / HKIT / "grading_sheet.csv").read_bytes()
        grades, errs = gate._holdout_parse_sheet(sheet, self.items)
        assert not errs
        _, assets = gate._holdout_recompute(json.loads(self.key_b), grades, rule)
        a = assets[H_ASSET]
        git_fields = {"grading_commit": gc, "remote_url": CANON, "remote_branch": "main", "remote_tip_sha": gc}
        results = {"asset_id": H_ASSET, "run_id": run, "key_sha256": hashlib.sha256(self.key_b).hexdigest(),
                   "items_json_sha256": hashlib.sha256(self.items_b).hexdigest(),
                   "grading_sheet_sha256": hashlib.sha256(sheet).hexdigest(), "score": a["score"],
                   "baseline_score": a["baseline_score"], "n_items": a["n_items"], "passed": a["passed"], **git_fields}
        record = evidence_record(f"holdout:{H_ASSET}:{run}")
        record.update(score=a["score"], baseline_score=a["baseline_score"], n_items=a["n_items"], passed=a["passed"],
                      threshold=0.8, grader="Irean", test_only=False, evidence_root=HEV,
                      results_path=f"{HEV}/holdout/{H_ASSET}/{run}.results.json", **git_fields)
        if edit:
            edit(record, results)
        rb = (json.dumps(results, indent=2) + "\n").encode()
        record["integrity_hash"] = "sha256:" + hashlib.sha256(rb).hexdigest()
        self.write(f"{HEV}/holdout/{H_ASSET}/{run}.results.json", rb)
        self.write(f"{HEV}/holdout/{H_ASSET}/{run}.json", (json.dumps(record, indent=2) + "\n").encode())
        self.write(f"{HKIT}/REVEALED_KEY.json", key_b if key_b is not None else self.key_b)
        self.reveal = self.commit("holdout evidence + reveal", push)
        return record


def honest(base: Path, **grade_kw) -> tuple[HoldoutRemote, dict]:
    h = HoldoutRemote(base)
    h.kit()
    gc = h.grade(**grade_kw)
    return h, h.finalize(gc)


def hverify(h: HoldoutRemote, record: dict, remote: Path | None = None) -> dict:
    return gate.verify_holdout_remote(record, gate.load_policies(), remote or h.remote)


def holdout_asset(tmp_path: Path, record: dict, extra_ids: tuple = ()) -> Path:
    """An otherwise sale-ready asset whose validation evidence is this holdout record (plus extra_ids, which must share
    EVIDENCE_KIND and get conforming passing records)."""
    def with_holdout(a):
        complete_layers(a)
        a["evidence_root"] = HEV
        a["validation_evidence_ids"][EVIDENCE_KIND] = list(extra_ids)
        a["validation_evidence_ids"]["holdout"] = [record["evidence_id"]]
    asset_dir = make_asset(tmp_path / "asset-h", cand_edit=sellable, asset_edit=with_holdout, write_evidence_files=False)
    write_evidence(gate.DEFAULT_REPO_ROOT, record["evidence_id"], HEV, record)
    for eid in extra_ids:
        write_evidence(gate.DEFAULT_REPO_ROOT, eid, HEV)
    return asset_dir


def test_holdout_config_names_canonical_remote_and_branches():
    cfg = gate.load_policies()["gate"]["holdout_verification"]
    assert cfg["canonical_remote_url"] == CANON and cfg["fetch_url"] == CANON + ".git"
    assert set(cfg["allowed_branches"]) == {"main", "edu-career-pathways/majors-onet-study-plans"}
    assert cfg["git_binary"] == "/usr/bin/git"


def test_holdout_matching_record_verifies_but_test_remote_never_counts(tmp_path):
    h, rec = honest(tmp_path / "h")
    assert rec["passed"] is True and rec["score"] == 1.0
    v = hverify(h, rec)
    assert v["ok"] and v["test_only"], v["errors"]
    assert v["facts"]["reveal_commit"] == h.reveal and v["facts"]["recomputed"]["passed"] is True
    report = gate.evaluate(holdout_asset(tmp_path, rec), verify_holdout_remote=True, holdout_test_remote=h.remote)
    assert_sale_scope_fail(report, "TEST ONLY")
    assert any("0 of 1 validation evidence id(s) resolved with passed: true" in r for r in synthesis(report)["reasons"])


def test_holdout_unverified_without_flag_is_capped_for_sale(tmp_path):
    """Supersedes the earlier 'unverified counts with a warning': holdout_verification.required_for_sale is true."""
    h, rec = honest(tmp_path / "h")
    report = gate.evaluate(holdout_asset(tmp_path, rec))
    assert_sale_scope_fail(report, gate.HOLDOUT_NOT_VERIFIED)
    assert any("NOT verified against the canonical remote" in r for r in synthesis(report)["reasons"])


@pytest.mark.parametrize("variant,needle", [
    ("tampered_sheet", "sha256(grading_sheet.csv) at grading_commit != sheet_sha256"),
    ("not_on_allowed_branch", "is not on main"),
    ("bad_reveal", "bad reveal or commitment"),
    ("bad_commitment", "bad reveal or commitment"),
    ("reveal_before_grading", "already exists at grading_commit"),
    ("regraded_after_reveal", "not an ancestor of the reveal commit"),
    ("score_mismatch", "!= recomputed"),
    ("passed_mismatch", "passed True != recomputed False"),
    ("record_not_committed", "differs from the record committed on the remote"),
    ("test_only_record", "record is marked test_only"),
    ("unreachable_remote", "cannot reach the remote"),
])
def test_holdout_verification_failures_are_sale_scope_and_not_counted(tmp_path, variant, needle):
    h = HoldoutRemote(tmp_path / "h")
    remote = None
    if variant == "reveal_before_grading":
        h.write(f"{HKIT}/REVEALED_KEY.json", h.key_b)
    if variant == "bad_commitment":
        h.commitment_b = h.commitment_b.replace(b"key_sha256: ", b"key_sha256: 0", 1)
    h.kit()
    if variant == "tampered_sheet":
        rec = h.finalize(h.grade(tamper=True))
    elif variant == "not_on_allowed_branch":
        rec = h.finalize(h.grade(push="scratch-branch"), push="scratch-branch")
    elif variant == "bad_reveal":
        rec = h.finalize(h.grade(), key_b=h.key_b.replace(b'"nonce": "ab', b'"nonce": "ac', 1))
    elif variant == "regraded_after_reveal":  # honest failing grade + reveal, then a perfect sheet graded from the public key
        h.finalize(h.grade(scores={q: [2, 2, 2] for q in h.key_items}))
        (h.repo / HKIT / "GRADING_FINAL.txt").unlink()
        rec = h.finalize(h.grade(), run="20261003-02")
        assert rec["passed"] is True
    elif variant == "score_mismatch":
        rec = h.finalize(h.grade(), edit=lambda r, res: (r.update(score=0.9), res.update(score=0.9)))
    elif variant == "passed_mismatch":
        rec = h.finalize(h.grade(scores={q: [2, 2, 2] for q in h.key_items}),
                         edit=lambda r, res: (r.update(passed=True), res.update(passed=True)))
    elif variant == "record_not_committed":
        rec = dict(h.finalize(h.grade()), evaluator_version="edited after the commit")
    elif variant == "test_only_record":
        rec = h.finalize(h.grade(), edit=lambda r, res: r.update(test_only=True))
    elif variant == "unreachable_remote":
        rec = h.finalize(h.grade())
        remote = tmp_path / "no-such-remote.git"
    else:  # reveal_before_grading, bad_commitment: the defect is already in the kit commit
        rec = h.finalize(h.grade())
    v = hverify(h, rec, remote)
    assert not v["ok"] and any(needle in e for e in v["errors"]), v["errors"]
    report = gate.evaluate(holdout_asset(tmp_path, rec), verify_holdout_remote=True, holdout_test_remote=remote or h.remote)
    if rec.get("passed") is True:
        assert_sale_scope_fail(report, "failed remote verification, not counted")
    else:
        assert report["outcome"] == "approved_for_private_use" and report["rights_ceiling"] == "approved_for_sale"


def test_holdout_verifier_ignores_hostile_environment(tmp_path, monkeypatch):
    """git runs as /usr/bin/git with an environment built from scratch: a fake git first on PATH, GIT_* variables and
    proxies in the gate's own environment do not reach it."""
    h, rec = honest(tmp_path / "h")
    shim = tmp_path / "shim"
    shim.mkdir()
    (shim / "git").write_text("#!/bin/sh\necho shim >&2\nexit 1\n")
    (shim / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ.get('PATH', '')}")
    for k, val in {"GIT_DIR": str(tmp_path / "nowhere"), "GIT_EXEC_PATH": str(shim), "HTTPS_PROXY": "http://127.0.0.1:9",
                   "GIT_CONFIG_PARAMETERS": "'core.fsmonitor'='/bin/false'", "HOME": str(tmp_path / "evil-home")}.items():
        monkeypatch.setenv(k, val)
    v = hverify(h, rec)
    assert v["ok"], v["errors"]


def test_holdout_recompute_matches_published_rule_on_simple_cases():
    rule = gate.load_policies()["gate"]["holdout_verification"]["pass_rule"]
    key_items = {}
    for n, (aid, kind, wc) in enumerate(H_SPEC, 1):
        key_items[f"Q{n:02d}"] = {"asset_id": aid, "candidate_type": kind, "weakened_criterion": wc,
                                  "accepted_scores": [[0, 1] if c == wc else [1, 2] for c in (1, 2, 3)]}
    key = {"items": key_items}
    def g(scores):
        return {q: {"s": s, "fc": "yes", "grader": "Irean"} for q, s in scores.items()}
    perfect = {q: [0 if c == k["weakened_criterion"] else 2 for c in (1, 2, 3)] for q, k in key_items.items()}
    kit, a = gate._holdout_recompute(key, g(perfect), rule)
    assert kit["passed"] and a[H_ASSET]["passed"] and a[H_ASSET]["score"] == 1.0
    assert not a["edu-x-00.0000"]["passed"]  # 2 items: not eligible
    kit, a = gate._holdout_recompute(key, g({q: [2, 2, 2] for q in key_items}), rule)
    assert not kit["passed"] and not a[H_ASSET]["passed"]
    kit, a = gate._holdout_recompute(key, g({q: [0, 2, 2] for q in key_items}), rule)  # shortcut: one criterion down
    assert not a[H_ASSET]["passed"]
    # baseline for the CS items (2 full + 2 weakened): uniform 4/9; all 2s (1, 1, 2/3, 2/3) = 5/6;
    # shortcut best case (full 2/3 each, weakened 1 each) = 5/6
    assert a[H_ASSET]["baseline_score"] == round(5 / 6, 4)


def test_cli_verify_holdout_remote_flag_reaches_the_verifier(tmp_path, monkeypatch, capsys):
    h, rec = honest(tmp_path / "h")
    seen = []
    def fake(record, pol, test_remote=None):
        seen.append(record["evidence_id"])
        return {"ok": False, "test_only": False, "errors": ["stub: remote said no"], "facts": {}}
    monkeypatch.setattr(gate, "verify_holdout_remote_fn", fake)
    asset_dir = holdout_asset(tmp_path, rec)
    assert gate.main([str(asset_dir), "--verify-holdout-remote"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert seen == [rec["evidence_id"]] and out["outcome"] == "approved_for_private_use"
    assert out["rights_ceiling"] == "approved_for_sale"
    assert validate(out, load_schema(gate.GATE_SCHEMA)) == []


# --- mandatory remote verification for sale (holdout_verification.required_for_sale) ---------------------------------

BENCH_2 = f"{EVIDENCE_KIND}:{H_ASSET}:20261002-02"


def ok_stub(record, pol, test_remote=None):
    """Stands in for a successful verification against the canonical remote (the real one needs GitHub)."""
    gc = record["grading_commit"]
    return {"ok": True, "test_only": False, "errors": [], "facts": {
        "grading_commit": gc, "remote_branch": "main", "remote_tip": gc, "reveal_commit": "f" * 40,
        "recomputed": {"score": record["score"], "baseline_score": record["baseline_score"], "passed": True}}}


def no_stub(record, pol, test_remote=None):
    return {"ok": False, "test_only": False, "errors": ["stub: grading_commit not on main"], "facts": {}}


def test_holdout_required_for_sale_config_defaults():
    cfg = gate.load_policies()["gate"]["holdout_verification"]
    assert cfg["required_for_sale"] is True
    assert cfg["required_signer_fingerprints"] == []  # placeholder: no signature required until keys are listed


def test_holdout_cap_applies_even_when_other_evidence_meets_the_minimum(tmp_path):
    """A passing benchmark record alone meets min_validation_evidence_ids (1), but the asset also relies on holdout."""
    h, rec = honest(tmp_path / "h")
    report = gate.evaluate(holdout_asset(tmp_path, rec, extra_ids=(BENCH_2,)))
    assert_sale_scope_fail(report, gate.HOLDOUT_NOT_VERIFIED)
    assert any(r.startswith(gate.HOLDOUT_NOT_VERIFIED) and "1 of 1 holdout" in r for r in synthesis(report)["reasons"])


@pytest.mark.parametrize("kind", ["regression", "sandbox", "benchmark"])
def test_non_holdout_evidence_reaches_sale_without_the_flag(tmp_path, kind):
    eid = f"{kind}:{H_ASSET}:20261002-03"
    def layers(a):
        complete_layers(a)
        a["validation_evidence_ids"] = {k: [] for k in a["validation_evidence_ids"]}
        a["validation_evidence_ids"][kind] = [eid]
    report = gate.evaluate(make_asset(tmp_path, cand_edit=sellable, asset_edit=layers))
    assert report["outcome"] == "approved_for_sale", synthesis(report)["reasons"]
    assert not any(gate.HOLDOUT_NOT_VERIFIED in r for r in synthesis(report)["reasons"])


@pytest.mark.parametrize("extra", [(), (BENCH_2,)])
def test_holdout_verification_failure_caps_with_the_required_reason(tmp_path, monkeypatch, extra):
    h, rec = honest(tmp_path / "h")
    monkeypatch.setattr(gate, "verify_holdout_remote_fn", no_stub)
    report = gate.evaluate(holdout_asset(tmp_path, rec, extra_ids=extra), verify_holdout_remote=True)
    assert_sale_scope_fail(report, gate.HOLDOUT_NOT_VERIFIED)
    assert any("failed remote verification, not counted" in r for r in synthesis(report)["reasons"])


def test_remotely_verified_holdout_lifts_the_cap(tmp_path, monkeypatch):
    h, rec = honest(tmp_path / "h")
    monkeypatch.setattr(gate, "verify_holdout_remote_fn", ok_stub)
    report = gate.evaluate(holdout_asset(tmp_path, rec, extra_ids=(BENCH_2,)), verify_holdout_remote=True)
    assert report["outcome"] == "approved_for_sale", synthesis(report)["reasons"]
    assert not any(gate.HOLDOUT_NOT_VERIFIED in r for r in synthesis(report)["reasons"])


def test_passed_false_holdout_is_not_relied_on(tmp_path):
    rec = dict(evidence_record(f"holdout:{H_ASSET}:20261003-09"), passed=False)
    report = gate.evaluate(holdout_asset(tmp_path, rec, extra_ids=(BENCH_2,)))
    assert report["outcome"] == "approved_for_sale", synthesis(report)["reasons"]
    assert not any(gate.HOLDOUT_NOT_VERIFIED in r for r in synthesis(report)["reasons"])


def test_required_for_sale_false_restores_count_with_warning(tmp_path, monkeypatch):
    h, rec = honest(tmp_path / "h")
    pol = copy.deepcopy(gate.load_policies())
    pol["gate"]["holdout_verification"]["required_for_sale"] = False
    monkeypatch.setattr(gate, "load_policies", lambda: copy.deepcopy(pol))
    report = gate.evaluate(holdout_asset(tmp_path, rec))
    assert report["outcome"] == "approved_for_sale"
    assert any("NOT verified against the canonical remote" in w for w in report["warnings"])


# --- optional signer requirement on grading_commit (git verify-commit), throwaway keys only ---------------------------

@pytest.fixture
def throwaway_gpg(tmp_path):
    """Fresh GNUPGHOME (short path for the agent socket) with no-passphrase test keys; removed afterwards."""
    home = Path(tempfile.mkdtemp(prefix="gpgt-", dir="/tmp"))
    home.chmod(0o700)
    env = {"PATH": "/usr/bin:/bin", "GNUPGHOME": str(home), "LC_ALL": "C"}

    def gpg(*args):
        r = subprocess.run(["/usr/bin/gpg", "--batch", *args], capture_output=True, text=True, env=env,
                           stdin=subprocess.DEVNULL, timeout=120)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def new_key(uid):
        gpg("--pinentry-mode", "loopback", "--passphrase", "", "--quick-gen-key", uid, "ed25519", "sign", "never")
        lines = gpg("--with-colons", "--list-keys", uid).splitlines()
        return next(l.split(":")[9] for l in lines if l.startswith("fpr:"))

    def export(path, *fprs):
        path.write_text(gpg("--armor", "--export", *fprs))
        return path

    try:
        yield home, new_key, export
    finally:
        subprocess.run(["/usr/bin/gpgconf", "--kill", "all"], env=env, capture_output=True)
        shutil.rmtree(home, ignore_errors=True)


def signer_pol(fprs, keys_path):
    pol = copy.deepcopy(gate.load_policies())
    pol["gate"]["holdout_verification"].update(required_signer_fingerprints=list(fprs), signer_public_keys=str(keys_path))
    return pol


def signed_honest(base, sign):
    h = HoldoutRemote(base)
    h.kit()
    return h, h.finalize(h.grade(sign=sign))


def test_signed_grading_commit_by_listed_key_verifies(tmp_path, throwaway_gpg):
    home, new_key, export = throwaway_gpg
    fpr = new_key("Throwaway Grader <grader@example.invalid>")
    h, rec = signed_honest(tmp_path / "h", (home, fpr))
    v = gate.verify_holdout_remote(rec, signer_pol([fpr], export(tmp_path / "keys.asc", fpr)), h.remote)
    assert v["ok"] and v["test_only"], v["errors"]
    assert v["facts"]["signed_by"] == fpr


def test_unsigned_grading_commit_fails_when_signers_are_listed(tmp_path, throwaway_gpg):
    home, new_key, export = throwaway_gpg
    fpr = new_key("Throwaway Grader <grader@example.invalid>")
    h, rec = honest(tmp_path / "h")
    v = gate.verify_holdout_remote(rec, signer_pol([fpr], export(tmp_path / "keys.asc", fpr)), h.remote)
    assert not v["ok"] and any("lacks a valid signature from a required signer" in e for e in v["errors"]), v["errors"]


def test_grading_commit_signed_by_unlisted_key_fails(tmp_path, throwaway_gpg):
    home, new_key, export = throwaway_gpg
    listed = new_key("Listed Grader <listed@example.invalid>")
    other = new_key("Someone Else <other@example.invalid>")
    h, rec = signed_honest(tmp_path / "h", (home, other))
    keys = export(tmp_path / "keys.asc", listed, other)  # both keys importable; only one is listed
    v = gate.verify_holdout_remote(rec, signer_pol([listed], keys), h.remote)
    assert not v["ok"] and any("not a listed signer" in e for e in v["errors"]), v["errors"]
    # the default (empty list) does not look at signatures at all
    assert gate.verify_holdout_remote(rec, gate.load_policies(), h.remote)["ok"]


# --- reveal-order parity with the producer's verifier at dde106b (and two stricter rules) ----------------------------

PR_BRANCH = "edu-career-pathways/majors-onet-study-plans"
RK = f"{HKIT}/REVEALED_KEY.json"


def hfail(v: dict, needle: str) -> None:
    assert not v["ok"] and any(needle in e for e in v["errors"]), v["errors"]


def test_holdout_key_on_the_other_allowed_branch_before_grading_fails(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    _hgit(h.repo, "checkout", "-q", "-b", "pr")
    h.write(RK, h.key_b)
    h.commit("key published on the PR branch", push=PR_BRANCH)
    _hgit(h.repo, "checkout", "-q", "main")
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "across the allowed branches")


def test_holdout_key_bytes_committed_under_another_name_before_grading_fail(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    h.write(f"{HKIT}/KEY_STAGING.json", h.key_b)
    h.commit("staging copy of the key")
    gc = h.grade()
    _hgit(h.repo, "mv", f"{HKIT}/KEY_STAGING.json", RK)  # the reveal is a rename of the early copy
    rec = h.finalize(gc)
    hfail(hverify(h, rec), "the revealed key's bytes were committed outside the reveal")


def test_holdout_key_added_and_dropped_in_merges_before_grading_fails(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    k0 = h.kit()
    for name in ("a", "b"):
        _hgit(h.repo, "checkout", "-q", "-b", f"side-{name}", k0)
        h.write(f"{name}.txt", name.encode())
        h.commit(f"side {name}", push=None)
    _hgit(h.repo, "checkout", "-q", "main")
    _hgit(h.repo, "merge", "-q", "--no-ff", "--no-commit", "side-a")
    h.write(RK, h.key_b)
    h.commit("evil merge adds the key")
    _hgit(h.repo, "merge", "-q", "--no-ff", "--no-commit", "side-b")
    _hgit(h.repo, "rm", "-q", RK)
    h.commit("evil merge drops the key")
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "REVEALED_KEY.json exists in an ancestor of grading_commit")


def test_holdout_reveal_modified_then_restored_fails(tmp_path):
    h, rec = honest(tmp_path / "h")
    h.write(RK, h.key_b + b"\n")
    h.commit("modify key")
    h.write(RK, h.key_b)
    h.commit("restore key")
    hfail(hverify(h, rec), "never modified, removed or re-added")


@pytest.mark.parametrize("name", ["grading_sheet.csv", "GRADING_FINAL.txt"])
def test_holdout_sheet_or_final_edited_and_reverted_before_the_reveal_fails(tmp_path, name):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    gc = h.grade()
    orig = (h.repo / HKIT / name).read_bytes()
    h.write(f"{HKIT}/{name}", orig + b"\n")
    h.commit("edit after grading")
    h.write(f"{HKIT}/{name}", orig)
    h.commit("revert")
    rec = h.finalize(gc)
    hfail(hverify(h, rec), "they must be byte-identical at every commit in between")


def test_holdout_reveal_on_a_side_branch_merged_later_still_verifies(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    gc = h.grade()
    _hgit(h.repo, "checkout", "-q", "-b", "reveal-side")
    rec = h.finalize(gc, push=None)
    _hgit(h.repo, "checkout", "-q", "main")
    h.write("unrelated.txt", b"x")
    h.commit("main moves on")
    _hgit(h.repo, "merge", "-q", "--no-ff", "-m", "merge the reveal", "reveal-side")
    h.commit("after merge", push="main")
    tip = _hgit(h.repo, "rev-parse", "HEAD")
    v = hverify(h, rec)
    assert v["ok"], v["errors"]
    assert v["facts"]["reveal_commit"] != tip


@pytest.mark.parametrize("where", ["results_on_main", "results_on_other_branch", "finalized_txt"])
def test_holdout_other_grading_commit_in_deleted_history_fails(tmp_path, where):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    branch = "main"
    if where == "results_on_other_branch":
        _hgit(h.repo, "checkout", "-q", "-b", "pr")
        branch = PR_BRANCH
    g1 = h.grade(scores={q: [2, 2, 2] for q in h.key_items}, push=branch)
    key_sha = hashlib.sha256(h.key_b).hexdigest()
    if where == "finalized_txt":
        rel, data = f"{HKIT}/FINALIZED.txt", f"key_sha256: {key_sha}\ngrading_commit: {g1}\n".encode()
    else:
        rel = f"{HEV}/holdout/{H_ASSET}/20261003-07.results.json"
        data = json.dumps({"asset_id": H_ASSET, "key_sha256": key_sha, "grading_commit": g1, "passed": False}).encode()
    h.write(rel, data)
    h.commit("first scoring", push=branch)
    _hgit(h.repo, "rm", "-q", rel)
    h.commit("delete it", push=branch)
    if branch != "main":
        _hgit(h.repo, "checkout", "-q", "main")
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "also scored from other grading commit(s)")


# --- pinned SHAs (expected_shas) -------------------------------------------------------------------------------------

def test_holdout_expected_shas_match_and_mismatch(tmp_path):
    h, rec = honest(tmp_path / "h")
    gc, reveal = rec["grading_commit"], h.reveal
    pol = gate.load_policies()
    v = gate.verify_holdout_remote(rec, pol, h.remote, expect_shas={"grading_commit": gc, "reveal_commit": reveal,
                                                                     "remote_tip_sha": reveal})
    assert v["ok"] and v["facts"]["expected_shas"]["reveal_commit"] == reveal, v["errors"]
    hfail(gate.verify_holdout_remote(rec, pol, h.remote, expect_shas={"grading_commit": reveal}), "grading_commit")
    hfail(gate.verify_holdout_remote(rec, pol, h.remote, expect_shas={"reveal_commit": gc}), "!= pinned")
    hfail(gate.verify_holdout_remote(rec, pol, h.remote, expect_shas={"reveal_commit": "abc"}), "full SHAs")  # never ignored


def test_holdout_expected_shas_detect_a_force_pushed_history(tmp_path):
    h, rec = honest(tmp_path / "h")
    pin = {"grading_commit": rec["grading_commit"], "reveal_commit": h.reveal, "remote_tip_sha": h.reveal}
    _hgit(h.repo, "reset", "-q", "--hard", rec["grading_commit"])
    rec2 = h.finalize(rec["grading_commit"], edit=lambda r, res: r.update(evaluator_version="rewritten"))  # force-pushed
    pol = gate.load_policies()
    assert gate.verify_holdout_remote(rec2, pol, h.remote)["ok"]  # without a pin the rewrite is invisible
    v = gate.verify_holdout_remote(rec2, pol, h.remote, expect_shas=pin)
    hfail(v, "!= pinned")
    hfail(v, "is no longer reachable")


def test_holdout_expected_shas_from_config_file_and_required(tmp_path):
    h, rec = honest(tmp_path / "h")
    pol = copy.deepcopy(gate.load_policies())
    cfg = pol["gate"]["holdout_verification"]
    shas = tmp_path / "VERIFIED_SHAS.json"  # the producer's format, kept outside their repository
    shas.write_text(json.dumps({"run_id": "20261003-01", "grading_commit": rec["grading_commit"], "reveal_commit": h.reveal,
                                "remote_tip_sha": h.reveal}))
    cfg["expected_shas_file"] = str(shas)
    assert gate.verify_holdout_remote(rec, pol, h.remote)["ok"]
    shas.write_text(json.dumps({"run_id": "20261003-01", "grading_commit": rec["grading_commit"],
                                "reveal_commit": rec["grading_commit"]}))
    hfail(gate.verify_holdout_remote(rec, pol, h.remote), "reveal_commit")
    cfg["expected_shas_file"], cfg["require_expected_shas"] = "", True
    hfail(gate.verify_holdout_remote(rec, pol, h.remote), "no pinned SHAs")
    cfg["expected_shas"] = {rec["evidence_id"]: {"grading_commit": rec["grading_commit"], "reveal_commit": h.reveal}}
    assert gate.verify_holdout_remote(rec, pol, h.remote)["ok"]


def test_holdout_signer_and_pin_config_defaults_are_empty():
    cfg = gate.load_policies()["gate"]["holdout_verification"]
    assert cfg["required_signer_fingerprints"] == [] and cfg["ssh_allowed_signers_file"] == ""
    assert cfg["expected_shas"] == {} and cfg["expected_shas_file"] == "" and cfg["require_expected_shas"] is False
    assert gate._holdout_signers(cfg)["required"] is False


# --- SSH signers (throwaway keys in a temp dir) and the GRADING_FINAL commit -------------------------------------------

@pytest.fixture
def throwaway_ssh():
    if not Path("/usr/bin/ssh-keygen").exists():
        pytest.skip("ssh-keygen not installed")
    d = Path(tempfile.mkdtemp(prefix="sshk-", dir="/tmp"))
    d.chmod(0o700)

    def new_key(name):
        k = d / name
        subprocess.run(["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", name, "-f", str(k)], check=True,
                       capture_output=True)
        pub = (d / f"{name}.pub").read_text().split()
        fpr = subprocess.run(["/usr/bin/ssh-keygen", "-lf", str(d / f"{name}.pub")], capture_output=True, text=True,
                             check=True).stdout.split()[1]
        return k, f'{name}@example.invalid namespaces="git" {pub[0]} {pub[1]}\n', fpr

    try:
        yield d, new_key
    finally:
        shutil.rmtree(d, ignore_errors=True)


def ssh_pol(allowed: Path | None = None, fprs=()):
    pol = copy.deepcopy(gate.load_policies())
    pol["gate"]["holdout_verification"].update(ssh_allowed_signers_file=str(allowed) if allowed else "",
                                               required_signer_fingerprints=list(fprs))
    return pol


def test_ssh_signed_grading_commit_by_allowed_signer_verifies(tmp_path, throwaway_ssh):
    d, new_key = throwaway_ssh
    key, line, fpr = new_key("grader")
    (d / "allowed").write_text(line)
    h, rec = signed_honest(tmp_path / "h", ("ssh", key))
    v = gate.verify_holdout_remote(rec, ssh_pol(d / "allowed"), h.remote)
    assert v["ok"] and v["facts"]["signed_by"] == fpr, v["errors"]
    v = gate.verify_holdout_remote(rec, ssh_pol(fprs=[fpr]), h.remote)  # or listed by fingerprint only
    assert v["ok"] and v["facts"]["signed_by"] == fpr, v["errors"]


def test_ssh_unsigned_or_wrong_key_grading_commit_fails(tmp_path, throwaway_ssh):
    d, new_key = throwaway_ssh
    owner, line, owner_fpr = new_key("owner")
    other, _, other_fpr = new_key("other")
    (d / "allowed").write_text(line)
    h, rec = honest(tmp_path / "u")
    hfail(gate.verify_holdout_remote(rec, ssh_pol(d / "allowed"), h.remote), "lacks a valid signature from a required signer: not signed")
    h2, rec2 = signed_honest(tmp_path / "w", ("ssh", other))
    for pol in (ssh_pol(d / "allowed"), ssh_pol(fprs=[owner_fpr])):
        hfail(gate.verify_holdout_remote(rec2, pol, h2.remote), f"SSH-signed by {other_fpr}, not a listed signer")
    # SSH-signed while only an OpenPGP signer is configured
    gpg_only = copy.deepcopy(gate.load_policies())
    gpg_only["gate"]["holdout_verification"]["required_signer_fingerprints"] = ["0" * 40]
    hfail(gate.verify_holdout_remote(rec2, gpg_only, h2.remote), "no SSH signer is configured")


def test_signed_reveal_does_not_stand_in_for_an_unsigned_grading_commit(tmp_path, throwaway_ssh):
    d, new_key = throwaway_ssh
    key, line, _ = new_key("grader")
    (d / "allowed").write_text(line)
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    gc = h.grade()
    rec = h.finalize(gc)
    h.commit("signed follow-up", sign=("ssh", key))
    hfail(gate.verify_holdout_remote(rec, ssh_pol(d / "allowed"), h.remote), f"grading_commit {gc[:12]} lacks a valid signature")


def test_grading_final_commit_must_be_signed_too(tmp_path, throwaway_ssh):
    """A forged sheet + GRADING_FINAL in an unsigned commit, covered by a later commit the grader signed: rejected.
    Both signed: accepted."""
    d, new_key = throwaway_ssh
    key, line, fpr = new_key("grader")
    (d / "allowed").write_text(line)
    for sign_final, ok in ((None, False), (("ssh", key), True)):
        h = HoldoutRemote(tmp_path / f"h-{ok}")
        h.kit()
        fc = h.grade(sign=sign_final)
        h.write("docs.txt", b"grader edits docs")
        gc = h.commit("grader: docs", sign=("ssh", key))
        rec = h.finalize(gc)
        v = gate.verify_holdout_remote(rec, ssh_pol(d / "allowed"), h.remote)
        if ok:
            assert v["ok"] and v["facts"]["signed_by"] == fpr, v["errors"]
        else:
            hfail(v, f"the commit {fc[:12]} that added GRADING_FINAL.txt lacks a valid signature")


def test_gpg_pubkey_file_signer_covers_the_grading_final_commit(tmp_path, throwaway_gpg):
    home, new_key, export = throwaway_gpg
    fpr = new_key("Throwaway Grader <grader@example.invalid>")
    keys = export(tmp_path / "keys.asc", fpr)
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    fc = h.grade()  # unsigned sheet + GRADING_FINAL
    h.write("docs.txt", b"x")
    rec = h.finalize(h.commit("signed docs", sign=(home, fpr)))
    hfail(gate.verify_holdout_remote(rec, signer_pol([fpr], keys), h.remote), f"the commit {fc[:12]} that added GRADING_FINAL.txt")


# --- N1 (af8b2a3 recheck): the key's nonce may only appear in the reveal and its descendants ---------------------

def reformatted_key(h: HoldoutRemote) -> bytes:
    return (json.dumps(json.loads(h.key_b), indent=2) + "\n").encode()


def test_holdout_reformatted_key_copy_before_grading_is_a_sale_scope_failure(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    assert reformatted_key(h) != h.key_b
    h.write("docs/notes/key_draft.json", reformatted_key(h))
    h.commit("reformatted copy of the key under another path")
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "the revealed key's nonce appears in commit(s) outside the reveal")
    report = gate.evaluate(holdout_asset(tmp_path, rec), verify_holdout_remote=True, holdout_test_remote=h.remote)
    assert_sale_scope_fail(report, "failed remote verification, not counted")


def test_holdout_reformatted_key_copy_on_the_other_allowed_branch_fails(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    h.kit()
    _hgit(h.repo, "checkout", "-q", "-b", "pr")
    h.write("docs/key_draft.json", reformatted_key(h))
    h.commit("reformatted key on the PR branch, never merged", push=PR_BRANCH)
    _hgit(h.repo, "checkout", "-q", "main")
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "the revealed key's nonce appears in commit(s) outside the reveal")


def test_holdout_revealed_key_without_a_nonce_is_rejected(tmp_path):
    h = HoldoutRemote(tmp_path / "h")
    key = json.loads(h.key_b)
    del key["nonce"]
    h.key_b = json.dumps(key).encode()
    h.commitment_b = (f"key_sha256: {hashlib.sha256(h.key_b).hexdigest()}\n"
                      f"items_json_sha256: {hashlib.sha256(h.items_b).hexdigest()}\n").encode()
    h.kit()
    rec = h.finalize(h.grade())
    hfail(hverify(h, rec), "has no hex nonce to trace")


def test_holdout_key_copies_after_the_reveal_and_side_branch_reveal_still_verify(tmp_path):
    h, rec = honest(tmp_path / "h")
    h.write("docs/published/key_pretty.json", reformatted_key(h))
    h.commit("publish a pretty copy of the revealed key")
    v = hverify(h, rec)
    assert v["ok"], v["errors"]
    h2 = HoldoutRemote(tmp_path / "h2")
    h2.kit()
    gc = h2.grade()
    _hgit(h2.repo, "checkout", "-q", "-b", "reveal-side")
    rec2 = h2.finalize(gc, push=None)
    h2.write("docs/key_pretty.json", reformatted_key(h2))
    h2.commit("pretty copy on the reveal branch", push=None)
    _hgit(h2.repo, "checkout", "-q", "main")
    _hgit(h2.repo, "merge", "-q", "--no-ff", "-m", "merge the reveal", "reveal-side")
    h2.commit("after merge", push="main")
    v2 = hverify(h2, rec2)
    assert v2["ok"], v2["errors"]


def test_holdout_mirror_fetch_is_not_blobless():
    import inspect
    src = inspect.getsource(gate._RemoteMirror.fetch)
    assert "blob:none" not in src and "partialClone" not in src and "promisor" not in src


# Package-level notice (gate 0.1.1): the declared attribution_text must carry the CC BY 4.0 license link and,
# for O*NET, the trademark notice, even when the shipped files already carry them.
def test_gate_version_matches_config():
    config = json.loads((ROOT / "config" / "license_provenance_gate.json").read_text(encoding="utf-8"))
    assert gate.GATE_VERSION == config["version"]


def test_declared_attribution_without_license_link_fails(tmp_path):
    def strip_link(p):
        p["attribution_text"] = p["attribution_text"].replace(" (https://creativecommons.org/licenses/by/4.0/)", "")
        assert "creativecommons.org" not in p["attribution_text"]
    att = check(gate.evaluate(make_asset(tmp_path, prov_edit=strip_link)), "attribution_present")
    assert att["status"] == "fail"
    assert any("license_link" in r and "declared attribution" in r for r in att["reasons"])


def test_declared_attribution_without_trademark_notice_fails(tmp_path):
    def strip_trademark(p):
        p["attribution_text"] = p["attribution_text"].replace("O*NET\u00ae is a trademark of USDOL/ETA. ", "")
        assert "trademark" not in p["attribution_text"]
    report = gate.evaluate(make_asset(tmp_path, prov_edit=strip_trademark))
    att = check(report, "attribution_present")
    assert att["status"] == "fail"
    assert any("trademark_notice" in r and "declared attribution" in r for r in att["reasons"])
    assert report["outcome"] == "approved_for_private_use"
