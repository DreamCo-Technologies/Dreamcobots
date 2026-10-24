"""Synthetic fixtures only: tests do not assert model capability or training."""
from hashlib import sha256
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_buddy_teacher_coverage import AuditError, SOURCES, audit


def fixture(root: Path):
    inputs = {
        "production": {"summary": {"real_divisions": 2, "production_ready_divisions": 0},
                       "divisions": [{"name": "DreamCodeLab", "production_ready": False},
                                     {"name": "DreamData", "production_ready": False}]},
        "masterbots": {"canonical_count": 2, "divisions": [{"name": "DreamCodeLab"}, {"name": "AnotherTaxonomy"}]},
        "tasks": {"tasks": ["coding", "sql"], "runs": 0},
        "suites": {"suites": [{"id": "coding_suite"}, {"id": "sql_suite"}]},
        "models": {"models": [{"id": "docs-only", "task_types": ["coding"]}]},
        "students": {"adapters": [], "truth": {"trained_weights_exist": False}},
        "distill": {"status": "contract_draft_no_runs"},
    }
    for key, path in SOURCES.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(inputs[key]), encoding="utf-8")


class TeacherCoverageTests(unittest.TestCase):
    def test_truthful_inventory_and_declared_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            report = audit(root)
            self.assertEqual(report["summary"]["actual_divisions"], 2)
            self.assertEqual(report["summary"]["masterbot_only_names"], ["AnotherTaxonomy"])
            self.assertEqual(report["summary"]["independent_holdout_receipts_in_this_audit"], 0)
            self.assertEqual(report["summary"]["representative_fixture_suggestions"], 2)
            self.assertEqual(report["task_routes"][0]["declared_candidate_model_ids"], ["docs-only"])
            self.assertEqual(report["task_routes"][0]["independently_verified_model_ids"], [])
            self.assertTrue(all(x["independent_holdout_receipt"] is None for x in report["division_coverage"]))

    def test_duplicate_division_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"].append(data["divisions"][0])
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate name"):
                audit(root)

    def test_summary_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["real_divisions"] = 3
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "count disagrees"):
                audit(root)

    def test_alias_proposals_do_not_count_as_verified_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["models"]
            data = json.loads(p.read_text())
            data["models"] = [{"id": "code-only", "task_types": ["code"]}]
            p.write_text(json.dumps(data))
            report = audit(root)
            coding = next(row for row in report["task_routes"] if row["task"] == "coding")
            self.assertEqual(coding["declared_candidate_model_ids"], [])
            self.assertEqual(coding["suggested_alias_model_ids_unverified"], ["code-only"])
            self.assertEqual(coding["independently_verified_model_ids"], [])
            self.assertIn("coding", report["summary"]["benchmark_tasks_without_exact_catalog_type"])
            self.assertIn("code", report["summary"]["catalog_model_task_types_not_in_benchmark_registry"])

    def test_missing_dedicated_suite_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["suites"]
            p.write_text(json.dumps({"suites": [{"id": "code_generation"}]}))
            report = audit(root)
            coding = next(row for row in report["task_routes"] if row["task"] == "coding")
            sql = next(row for row in report["task_routes"] if row["task"] == "sql")
            self.assertEqual(coding["candidate_suite_ids_design_only"], ["code_generation"])
            self.assertFalse(coding["needs_dedicated_suite_design"])
            self.assertTrue(sql["needs_dedicated_suite_design"])
            self.assertIn("sql", report["summary"]["benchmark_tasks_without_candidate_suite_design"])

    def test_inconsistent_weight_claim_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["students"]
            p.write_text(json.dumps({"adapters": [], "truth": {"trained_weights_exist": True}}))
            with self.assertRaisesRegex(AuditError, "without any registered student adapter"):
                audit(root)

    def test_invalid_benchmark_run_count_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            p.write_text(json.dumps({"tasks": ["coding"], "runs": -1}))
            with self.assertRaisesRegex(AuditError, "nonnegative integer"):
                audit(root)

    def test_duplicate_benchmark_run_key_fails_closed(self):
        # JSON's default last-value-wins parser would conceal a conflicting run count.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            raw = p.read_text(encoding="utf-8")
            self.assertIn('"runs": 0', raw)
            p.write_text(raw.replace('"runs": 0', '"runs": 999, "runs": 0', 1))
            with self.assertRaisesRegex(AuditError, "duplicate JSON key"):
                audit(root)

    def test_nested_duplicate_training_truth_key_fails_closed(self):
        # Conflicting weight claims must not be erased by JSON parsing.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["students"]
            raw = p.read_text(encoding="utf-8")
            self.assertIn('"trained_weights_exist": false', raw)
            p.write_text(raw.replace(
                '"trained_weights_exist": false',
                '"trained_weights_exist": true, "trained_weights_exist": false', 1,
            ))
            with self.assertRaisesRegex(AuditError, "duplicate JSON key"):
                audit(root)

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(AuditError, "production-evidence-ledger"):
                audit(Path(tmp))


    def test_string_readiness_is_not_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"][0]["production_ready"] = "false"
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "production_ready must be a boolean"):
                audit(root)

    def test_boolean_benchmark_run_count_is_not_an_integer_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            data = json.loads(p.read_text())
            data["runs"] = True
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "nonnegative integer"):
                audit(root)

    def test_ledger_zero_weight_artifacts_rejects_distill_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["trained_weight_artifacts"] = 0
            p.write_text(json.dumps(data))
            p = root / SOURCES["distill"]
            p.write_text(json.dumps({
                "status": "research_only",
                "truth": {"trained_weights_exist": True, "distill_runs_exist": False},
            }))
            with self.assertRaisesRegex(AuditError, "reports zero artifacts"):
                audit(root)

    def test_division_subtotal_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"].update({"canonical_divisions": 2, "supplemental_divisions": 1})
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "subtotals disagree"):
                audit(root)

    def test_non_boolean_distill_claim_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["distill"]
            p.write_text(json.dumps({
                "status": "contract_draft_no_runs",
                "truth": {"distill_runs_exist": "false"},
            }))
            with self.assertRaisesRegex(AuditError, "distill_runs_exist must be a boolean"):
                audit(root)


    def test_new_unseeded_division_is_not_assumed_covered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"].append({"name": "FutureDivision", "production_ready": False})
            data["summary"]["real_divisions"] = 3
            p.write_text(json.dumps(data))
            report = audit(root)
            self.assertEqual(report["summary"]["divisions_needing_fixture_design"], 1)
            future = next(row for row in report["division_coverage"]
                          if row["division"] == "FutureDivision")
            self.assertEqual(future["status"], "representative_task_needed")
            self.assertIsNone(future["independent_holdout_receipt"])


    def test_duplicate_model_task_type_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["models"]
            data = json.loads(p.read_text())
            data["models"][0]["task_types"] = ["coding", "coding"]
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate model task_type"):
                audit(root)

    def test_boolean_masterbot_count_is_not_an_integer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["masterbots"]
            data = json.loads(p.read_text())
            data["canonical_count"] = True
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "MasterBot registry count"):
                audit(root)

    def test_boolean_readiness_count_is_not_an_integer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = False
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "production readiness count"):
                audit(root)

    def test_readiness_claim_with_failed_gate_or_blocker_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            division = data["divisions"][0]
            division["production_ready"] = True
            division["gates"] = [{"id": "runtime", "passed": False}]
            division["blockers"] = ["runtime"]
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "missing or failed gates"):
                audit(root)

    def test_readiness_claim_without_gate_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            division = data["divisions"][0]
            division["production_ready"] = True
            division["blockers"] = []
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "missing or failed gates"):
                audit(root)


    def test_casefold_equivalent_division_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"][1]["name"] = "dreamcodelab"
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate name after normalization"):
                audit(root)

    def test_nfkc_equivalent_division_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"][1]["name"] = "ＤｒｅａｍＣｏｄｅＬａｂ"
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate name after normalization"):
                audit(root)

    def test_padded_casefold_model_task_type_collision_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["models"]
            data = json.loads(p.read_text())
            data["models"][0]["task_types"] = ["coding", " CODING "]
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate model task_type"):
                audit(root)

    def test_nonfinite_json_registry_value_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            raw = p.read_text()
            self.assertIn('"runs": 0', raw)
            p.write_text(raw.replace('"runs": 0', '"runs": NaN', 1))
            with self.assertRaisesRegex(AuditError, "non-finite JSON constant NaN"):
                audit(root)

    def test_cross_registry_cosmetic_variant_not_misreported_as_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["masterbots"]
            data = json.loads(p.read_text())
            data["divisions"][0]["name"] = " dreamcodelab "
            p.write_text(json.dumps(data))
            summary = audit(root)["summary"]
            self.assertEqual(summary["masterbot_only_names"], ["AnotherTaxonomy"])
            self.assertEqual(summary["actual_only_names"], ["DreamData"])
            self.assertEqual(summary["cross_registry_identifier_variants"], [
                {"actual_division": "DreamCodeLab", "masterbot_division": " dreamcodelab "}
            ])

    def test_cross_registry_unicode_width_variant_reconciles_without_renaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["masterbots"]
            data = json.loads(p.read_text())
            data["divisions"][0]["name"] = "ＤｒｅａｍＣｏｄｅＬａｂ"
            p.write_text(json.dumps(data))
            summary = audit(root)["summary"]
            self.assertEqual(summary["masterbot_only_names"], ["AnotherTaxonomy"])
            self.assertEqual(summary["actual_only_names"], ["DreamData"])
            self.assertEqual(summary["cross_registry_identifier_variants"][0]["actual_division"], "DreamCodeLab")
            self.assertEqual(summary["cross_registry_identifier_variants"][0]["masterbot_division"],
                             "ＤｒｅａｍＣｏｄｅＬａｂ")


    def test_division_family_gaps_are_explicit_not_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            report = audit(root)
            rows = {row["division"]: row for row in report["division_coverage"]}
            self.assertTrue(rows["DreamCodeLab"]["task_family_has_exact_benchmark_label"])
            self.assertEqual(rows["DreamCodeLab"]["declared_exact_catalog_model_ids_unverified"], ["docs-only"])
            self.assertFalse(rows["DreamData"]["task_family_has_exact_benchmark_label"])
            self.assertEqual(rows["DreamData"]["declared_exact_catalog_model_ids_unverified"], [])
            self.assertIn("sql_data", report["summary"]["division_task_families_without_exact_benchmark_label"])
            self.assertEqual(report["summary"]["divisions_without_exact_benchmark_task_label"], ["DreamData"])
            self.assertEqual(report["summary"]["divisions_without_exact_declared_model_route"], ["DreamData"])
            self.assertIsNone(rows["DreamCodeLab"]["independent_holdout_receipt"])
            self.assertEqual(report["summary"]["independently_verified_routes_in_this_audit"], 0)

    def test_registry_label_and_model_declaration_still_do_not_prove_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            task_path = root / SOURCES["tasks"]
            task_data = json.loads(task_path.read_text())
            task_data["tasks"].append("sql_data")
            task_path.write_text(json.dumps(task_data))
            model_path = root / SOURCES["models"]
            model_data = json.loads(model_path.read_text())
            model_data["models"][0]["task_types"].append("sql_data")
            model_path.write_text(json.dumps(model_data))
            report = audit(root)
            row = next(r for r in report["division_coverage"] if r["division"] == "DreamData")
            self.assertTrue(row["task_family_has_exact_benchmark_label"])
            self.assertEqual(row["declared_exact_catalog_model_ids_unverified"], ["docs-only"])
            self.assertEqual(report["summary"]["divisions_without_exact_benchmark_task_label"], [])
            self.assertEqual(report["summary"]["divisions_without_exact_declared_model_route"], [])
            self.assertIsNone(row["evaluated_model_revision"])
            self.assertIsNone(row["independent_holdout_receipt"])

    def test_passing_readiness_gate_without_receipt_is_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            data["divisions"][0].update({
                "production_ready": True, "blockers": [],
                "gates": [{"id": "runtime", "passed": True}],
            })
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "missing or failed gates"):
                audit(root)

    def test_readiness_receipt_digest_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            receipt = root / "reports" / "toy-receipt.json"
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text('{"test":"synthetic"}')
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            data["divisions"][0].update({
                "production_ready": True, "blockers": [],
                "gates": [{"id": "runtime", "passed": True,
                           "evidence": "reports/toy-receipt.json",
                           "receipt_sha256": "0" * 64}],
            })
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "missing or failed gates"):
                audit(root)

    def test_readiness_receipt_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            fixture(root)
            receipt = Path(outside) / "fake-receipt.json"
            receipt.write_text('{"test":"synthetic"}')
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            data["divisions"][0].update({
                "production_ready": True, "blockers": [],
                "gates": [{"id": "runtime", "passed": True,
                           "evidence": str(receipt),
                           "receipt_sha256": sha256(receipt.read_bytes()).hexdigest()}],
            })
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "missing or failed gates"):
                audit(root)

    def test_pinned_receipt_only_supports_ledger_not_independent_model_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            receipt = root / "reports" / "toy-receipt.json"
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text('{"test":"synthetic"}')
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["production_ready_divisions"] = 1
            data["divisions"][0].update({
                "production_ready": True, "blockers": [],
                "gates": [{"id": "runtime", "passed": True,
                           "evidence": "reports/toy-receipt.json",
                           "receipt_sha256": sha256(receipt.read_bytes()).hexdigest()}],
            })
            p.write_text(json.dumps(data))
            report = audit(root)
            self.assertEqual(report["summary"]["production_ready_divisions_in_ledger"], 1)
            self.assertEqual(report["summary"]["independent_holdout_receipts_in_this_audit"], 0)
            self.assertEqual(report["summary"]["independently_verified_routes_in_this_audit"], 0)


if __name__ == "__main__":
    unittest.main()
