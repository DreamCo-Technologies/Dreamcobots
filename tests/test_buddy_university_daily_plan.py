import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.build_buddy_university_daily_plan import build_daily_plan


DIVISIONS = ["CommandCore", "DreamAIInfra", "DreamAdmin", "DreamAgents", "DreamAgriculture",
             "DreamArts", "DreamAutomation", "DreamBizLaunch", "DreamCodeLab", "DreamConstruction",
             "DreamContent", "DreamCrypto", "DreamCustIntel", "DreamCyber", "DreamData",
             "DreamDecision", "DreamEducation", "DreamEmpire", "DreamEntFinance", "DreamFinance",
             "DreamFlow", "DreamFood", "DreamGlobal", "DreamHealth", "DreamInfluence",
             "DreamLegal", "DreamLoans", "DreamMaintenance", "DreamMarket", "DreamMilitary",
             "DreamOps", "DreamPayments", "DreamPersonalCare", "DreamPlanetary", "DreamProServices",
             "DreamProduction", "DreamProtection", "DreamRealEstate", "DreamRetail", "DreamSalesPro",
             "DreamScience", "DreamSocial", "DreamTrade", "DreamTransport", "GameTitan",
             "DreamAffiliate", "DreamAgency", "DreamFoundry", "DreamFranchise", "DreamIntegrations",
             "DreamLicensing", "DreamRobotics", "DreamSaaS", "DreamStreaming", "DreamTravel"]


class BuddyUniversityDailyPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.organization = self.root / "organization.json"
        package = {
            "schema": "dreamco.buddy_learning_package.v1",
            "asset_id": "approved-guide-001",
            "division_ids": ["DreamAIInfra"],
            "source": {"url": "https://example.org/guide", "revision": "rev-1"},
            "rights": {"study_permission": True, "summary_derivative_permission": True,
                       "evaluation_permission": True, "training_permission": False, "evidence_ref": "rights-1"},
            "summary": {"executive_overview": "A verified original summary.", "detailed_explanation": "Detailed notes."},
            "study_path": {"sequence": [{"step": 1, "type": "read"}]},
            "assessment": {"knowledge_check_count": 5},
            "ownership": {"artifact_owner": "user_designated_owner"},
            "training": {"weight_training_eligible": False},
            "progress": {"status": "ready_to_assign", "mastery_status": "not_assessed"},
        }
        self.organization.write_text(json.dumps({
            "schema": "dreamco.buddy_learning_organization.v1",
            "packages": [package],
            "division_curricula": [{"division": name} for name in DIVISIONS],
        }), encoding="utf-8")
        self.university = {
            "schema": "dreamco.buddy_university_learning_map.v1",
            "instructional_model": {"teacher": {"role": "GPT-6 teacher"}, "student": {"role": "Buddy student"}},
            "university_curriculum": {"parallel_learning_policy": {"logical_parallel_division_lanes": 55, "runtime_concurrency": "fair queue"}},
            "divisions": [{"division": name, "focus_areas": ["model serving"]} for name in DIVISIONS],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_five_slots_per_division_and_only_approved_guides_are_assignable(self):
        plan = build_daily_plan(self.university, self.organization, "2026-11-24", 5)
        self.assertEqual(plan["division_count"], 55)
        self.assertEqual(plan["daily_target_slots"], 275)
        self.assertEqual(plan["ready_to_assign_slots"], 1)
        self.assertEqual(plan["awaiting_approved_summary_slots"], 274)
        self.assertEqual(plan["parallel_execution"]["logical_division_lanes"], 55)
        self.assertEqual(plan["parallel_execution"]["weight_training_jobs_started"], 0)
        ai = next(row for row in plan["divisions"] if row["division"] == "DreamAIInfra")
        self.assertEqual(ai["progress"]["assigned"], 1)
        self.assertEqual(ai["slots"][0]["completion_status"], "queued_not_studied")
        self.assertEqual(ai["slots"][0]["asset_id"], "approved-guide-001")

    def test_no_packages_means_empty_slots_not_fake_lessons(self):
        payload = json.loads(self.organization.read_text(encoding="utf-8"))
        payload["packages"] = []
        self.organization.write_text(json.dumps(payload), encoding="utf-8")
        plan = build_daily_plan(self.university, self.organization, "2026-11-24", 5)
        self.assertEqual(plan["ready_to_assign_slots"], 0)
        self.assertEqual(plan["awaiting_approved_summary_slots"], 275)

    def test_training_rights_are_not_implied_by_study_permissions(self):
        plan = build_daily_plan(self.university, self.organization, "2026-11-24", 5)
        ai = next(row for row in plan["divisions"] if row["division"] == "DreamAIInfra")
        self.assertFalse(ai["slots"][0]["weight_training_eligible"])
        self.assertTrue(plan["progress_policy"]["weight_training_requires_explicit_per_asset_permission"])

    def test_unknown_division_or_incomplete_organization_fails_closed(self):
        payload = json.loads(self.organization.read_text(encoding="utf-8"))
        payload["division_curricula"].pop()
        self.organization.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_daily_plan(self.university, self.organization, "2026-11-24", 5)


    def test_cli_bootstraps_repository_imports_outside_repository_cwd(self):
        script = Path(__file__).resolve().parents[1] / "tools/build_buddy_university_daily_plan.py"
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--university-map", result.stdout)


if __name__ == "__main__":
    unittest.main()
