"""Offline tests for frontier claim trust gate checker."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def _load_checker():
    path = Path(__file__).resolve().parents[1] / "tools" / "check_frontier_claim_trust_gates.py"
    spec = importlib.util.spec_from_file_location("check_frontier_claim_trust_gates", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class FrontierClaimTrustGatesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_checker()
        self._orig_root = self.mod.ROOT
        self._orig_disclosure = self.mod.DISCLOSURE

    def tearDown(self) -> None:
        self.mod.ROOT = self._orig_root
        self.mod.DISCLOSURE = self._orig_disclosure

    def _write_tree(self, root: Path, *, claimable: bool, soak: bool, vanity: bool) -> None:
        (root / "config" / "buddy").mkdir(parents=True)
        (root / "config" / "generated").mkdir(parents=True)
        (root / "evidence" / "frontier").mkdir(parents=True)
        (root / "reports").mkdir(parents=True)
        (root / "website").mkdir(parents=True)

        (root / "config" / "buddy-training-data-provenance-policy.json").write_text(
            json.dumps(
                {
                    "core_rule": "retain provenance",
                    "ownership_classes": ["dreamco_owned", "unknown_do_not_publish"],
                }
            ),
            encoding="utf-8",
        )
        (root / "config" / "buddy-frontier-readiness-gates.json").write_text(
            json.dumps(
                {
                    "never_claim_frontier_without_evidence": True,
                    "gates": [{"id": "G1-foundation"}],
                }
            ),
            encoding="utf-8",
        )
        (root / "config" / "buddy" / "500-model-operating-contract.json").write_text(
            json.dumps({"schema": "dreamco.buddy.500_model_contract.v1"}),
            encoding="utf-8",
        )
        disclosure = {
            "schema": "dreamco.buddy.frontier_claim_disclosure.v1",
            "required_public_disclosure_fields": [
                "evidence_suite_id",
                "evidence_status",
                "claim_scope",
                "limitations",
                "last_verified_at",
                "independent_learning_proven",
            ],
            "ship_rule": "no claims without gates",
            "vanity_claim_phrases": ["frontier-competitive", "buddy is frontier"],
            "scan_roots": ["website"],
            "scan_globs": ["*.html", "*.js", "*.json", "*.md"],
            "allowlist_requirements": {
                "readiness_gates_path": "config/buddy-frontier-readiness-gates.json",
                "require_never_claim_frontier_without_evidence": True,
                "model_contract_path": "config/buddy/500-model-operating-contract.json",
            },
            "provenance_requirements": {
                "policy_path": "config/buddy-training-data-provenance-policy.json",
                "require_core_rule_present": True,
                "block_unknown_do_not_publish_for_claims": True,
            },
            "soak_requirements": {
                "tick_path": "config/generated/sandbox-24h-tick.json",
                "report_path": "reports/SANDBOX_24H.md",
                "required_tick_status": "sandbox_tick_ok",
            },
            "claimable_assessment_path": "evidence/frontier/current-status.assessment.json",
        }
        (root / "config" / "buddy-frontier-claim-disclosure.json").write_text(
            json.dumps(disclosure), encoding="utf-8"
        )
        (root / "evidence" / "frontier" / "current-status.assessment.json").write_text(
            json.dumps(
                {
                    "claimable": claimable,
                    "status": "claimable" if claimable else "incomplete_or_unproven",
                }
            ),
            encoding="utf-8",
        )
        if soak:
            (root / "config" / "generated" / "sandbox-24h-tick.json").write_text(
                json.dumps({"status": "sandbox_tick_ok"}), encoding="utf-8"
            )
            (root / "reports" / "SANDBOX_24H.md").write_text("# ok\n", encoding="utf-8")
        site = "Buddy comparison desk.\n"
        if vanity:
            site = "Buddy is frontier-competitive today.\n"
        (root / "website" / "index.html").write_text(site, encoding="utf-8")

    def _bind(self, root: Path) -> None:
        self.mod.ROOT = root
        self.mod.DISCLOSURE = root / "config" / "buddy-frontier-claim-disclosure.json"

    def test_deploy_mode_passes_without_vanity_when_not_claimable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tree(root, claimable=False, soak=False, vanity=False)
            self._bind(root)
            result = self.mod.evaluate(require_all_gates=False)
            self.assertTrue(result["ok"])
            self.assertFalse(result["all_gates_green"])

    def test_deploy_mode_fails_on_vanity_when_gates_red(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tree(root, claimable=False, soak=False, vanity=True)
            self._bind(root)
            result = self.mod.evaluate(require_all_gates=False)
            self.assertFalse(result["ok"])
            self.assertGreater(result["vanity_hit_count"], 0)

    def test_require_all_gates_passes_when_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tree(root, claimable=True, soak=True, vanity=False)
            self._bind(root)
            result = self.mod.evaluate(require_all_gates=True)
            self.assertTrue(result["ok"])
            self.assertTrue(result["all_gates_green"])
            self.assertTrue(result["claimable"])

    def test_require_all_gates_fails_when_soak_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tree(root, claimable=True, soak=False, vanity=False)
            self._bind(root)
            result = self.mod.evaluate(require_all_gates=True)
            self.assertFalse(result["ok"])
            self.assertFalse(result["gates"]["sandbox_soak"])


if __name__ == "__main__":
    unittest.main()
