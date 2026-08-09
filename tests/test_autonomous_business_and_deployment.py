import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUSINESS = ROOT / "config" / "autonomous-bot-business-owner-program.json"
BUSINESS_OUT = ROOT / "config" / "generated" / "bot-business-owner-curriculum.json"
DEPLOY = ROOT / "config" / "any-device-prototype-to-live-program.json"


class AutonomousBusinessAndDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_bot_business_owner_curriculum.py")], cwd=ROOT, check=True)
        cls.business = json.loads(BUSINESS.read_text(encoding="utf-8"))
        cls.out = json.loads(BUSINESS_OUT.read_text(encoding="utf-8"))
        cls.deploy = json.loads(DEPLOY.read_text(encoding="utf-8"))

    def test_every_canonical_bot_gets_business_training(self):
        self.assertGreaterEqual(self.out["bot_count"], 1000)
        self.assertEqual(len(self.out["bots"]), self.out["bot_count"])
        self.assertEqual(len({b["slug"] for b in self.out["bots"]}), self.out["bot_count"])
        for bot in self.out["bots"]:
            self.assertEqual(bot["revenue_experiment"]["target_usd"], 1000)
            self.assertFalse(bot["revenue_experiment"]["guaranteed"])
            self.assertEqual(bot["business_status"], "sandbox_training_not_live_business")
            self.assertTrue(bot["personal_business_sandbox"]["required"])

    def test_business_curriculum_covers_full_company_lifecycle(self):
        curriculum = set(self.business["business_owner_curriculum"])
        for item in {"market_research","offer_design","pricing","lead_generation","sales_script","payment_checkout","fulfillment","quality_assurance","customer_support","retention","analytics","privacy","security","legal_compliance_review","business_continuity"}:
            self.assertIn(item, curriculum)
        self.assertGreaterEqual(len(self.business["marketing_channels_to_simulate"]), 15)

    def test_stripe_is_shared_and_safe_by_default(self):
        stripe = self.business["stripe_policy"]
        self.assertTrue(stripe["test_mode_default"])
        self.assertTrue(stripe["bots_use_shared_payment_abstraction"])
        self.assertFalse(stripe["bots_get_individual_secret_keys"])
        self.assertTrue(stripe["live_charges_require_explicit_authorization"])
        self.assertTrue(stripe["never_store_raw_card_data"])

    def test_any_device_program_covers_phone_browser_desktop_and_cli(self):
        surfaces = set(self.deploy["input_surfaces"])
        for required in {"mobile_browser","desktop_browser","phone_app","tablet","desktop_app","cli","api","notes_to_code"}:
            self.assertIn(required, surfaces)
        self.assertGreaterEqual(len(self.deploy["go_live_targets"]), 20)

    def test_release_quality_does_not_make_impossible_bug_free_claim(self):
        quality = self.deploy["quality_model"]
        self.assertFalse(quality["bug_free_code_guarantee"])
        self.assertIn("zero known release-blocking defects", quality["goal"])
        self.assertGreaterEqual(len(quality["required_layers"]), 12)
        self.assertTrue(self.deploy["deployment_contract"]["every_target_requires_post_deploy_health_check"])
        self.assertTrue(self.deploy["deployment_contract"]["every_target_requires_rollback_plan"])

    def test_live_consequential_actions_remain_approval_gated(self):
        gated = set(self.business["autonomy"]["approval_gated"])
        for item in {"real_ad_spend","real_messages_to_people","live_payment_charge","refund","contract_acceptance"}:
            self.assertIn(item, gated)


if __name__ == "__main__":
    unittest.main()
