import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "universal-human-ai-software-task-sandbox.json"
GENERATED = ROOT / "config" / "generated" / "universal-human-ai-task-sandbox.json"


class UniversalHumanAITaskSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_universal_human_ai_task_sandbox.py")], cwd=ROOT, check=True)
        cls.generated = json.loads(GENERATED.read_text(encoding="utf-8"))

    def test_has_at_least_fifty_thousand_base_categories(self):
        self.assertGreaterEqual(self.generated["category_count"], 50000)
        self.assertGreaterEqual(self.generated["task_action_count"], 100)
        self.assertGreaterEqual(self.generated["domain_count"], 60)
        self.assertGreaterEqual(self.generated["quality_dimension_count"], 20)

    def test_covers_common_chatbot_ai_and_software_requests(self):
        actions = set(self.cfg["task_actions"])
        for required in {
            "answer","explain","teach","summarize","rewrite","translate","research","compare","recommend",
            "plan","schedule","calculate","generate_image","generate_audio","generate_video","code","debug","test",
            "build_app","build_website","build_api","build_database","analyze_data","visualize_data","manage_files",
            "draft_email","manage_calendar","take_notes","convert_notes_to_code","create_document","create_spreadsheet",
            "customer_support","budget","find_resources","find_jobs","find_housing","find_suppliers","learn_skill",
            "business_plan","launch_business","security_check","privacy_check","game_build","device_control","browser_task",
            "workflow_orchestration","multi_agent_coordination","personal_assistant","benchmark","gap_analysis","self_improve"
        }:
            self.assertIn(required, actions)

    def test_covers_personal_business_technical_and_creative_domains(self):
        domains = set(self.cfg["domains"])
        for required in {
            "personal_productivity","family_parenting","housing","jobs","education","coding","software_engineering",
            "cybersecurity","data","ai_ml","open_source","robotics","gaming","music","film_video","content_creation",
            "marketing","sales","customer_service","business_startup","enterprise","finance","payments","legal",
            "government_resources","manufacturing","retail","construction","health_wellness","travel","professional_services"
        }:
            self.assertIn(required, domains)

    def test_every_generated_category_is_unique_and_not_claimed_passed(self):
        ids = [row["category_id"] for row in self.generated["categories"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["status"] == "planned_not_run" for row in self.generated["categories"]))

    def test_business_and_personal_overlays_are_present(self):
        business = set(self.cfg["special_business_client_scenarios"])
        personal = set(self.cfg["special_personal_scenarios"])
        self.assertGreaterEqual(len(business), 30)
        self.assertGreaterEqual(len(personal), 25)
        for scenario in {"billing_sandbox","customer_record","support_ticket","incident_response","business_continuity"}:
            self.assertIn(scenario, business)
        for scenario in {"daily_planning","budgeting","job_search","housing_search","fraud_alert","personal_project"}:
            self.assertIn(scenario, personal)


if __name__ == "__main__":
    unittest.main()
