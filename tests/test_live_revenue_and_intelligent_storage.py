import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / "config" / "intelligent-data-storage-program.json"
REVENUE = ROOT / "config" / "live-revenue-gate.json"
READINESS = ROOT / "config" / "generated" / "live-revenue-readiness.json"


class LiveRevenueAndIntelligentStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_bot_business_owner_curriculum.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_bot_sandbox_curriculum.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_live_revenue_readiness.py")], cwd=ROOT, check=True)
        cls.storage = json.loads(STORAGE.read_text(encoding="utf-8"))
        cls.revenue = json.loads(REVENUE.read_text(encoding="utf-8"))
        cls.readiness = json.loads(READINESS.read_text(encoding="utf-8"))

    def test_storage_is_user_owned_sensitive_and_secret_aware(self):
        behaviors = " ".join(self.storage["intelligent_behaviors"]).lower()
        for phrase in ["classify before storage", "deduplicate", "provenance", "export/delete", "never store raw payment-card data"]:
            self.assertIn(phrase, behaviors)
        self.assertEqual(self.storage["storage_tiers"]["credential_secret"].split(";")[0], "secret store/environment/keychain only")

    def test_live_revenue_requires_real_evidence_and_owner_enable(self):
        gates = " ".join(self.revenue["required_gates"]).lower()
        for phrase in ["runtime evidence", "universal sandbox tests pass", "stripe test checkout succeeds", "privacy/security/permission tests pass", "owner explicitly enables live monetization"]:
            self.assertIn(phrase, gates)
        self.assertEqual(self.revenue["default_mode"], "sandbox_only")

    def test_bots_do_not_receive_direct_stripe_secrets(self):
        actions = self.revenue["live_actions"]
        self.assertIn("never direct raw-card charge", actions["charge"].lower())
        self.assertIn("approval", actions["create_live_checkout"].lower())

    def test_readiness_registry_defaults_to_no_live_checkout(self):
        self.assertGreaterEqual(self.readiness["bot_count"], 1000)
        self.assertEqual(self.readiness["live_enabled_count"], 0)
        for bot in self.readiness["bots"]:
            self.assertFalse(bot["live_checkout_allowed"])
            self.assertEqual(bot["verified_live_revenue_usd"], 0)
            self.assertFalse(bot["checks"]["owner_live_enable"])

    def test_revenue_is_never_recorded_from_forecasts(self):
        self.assertIn("verified stripe events", self.revenue["truth_rule"].lower())
        self.assertIn("never from forecasts or simulations", self.revenue["truth_rule"].lower())


if __name__ == "__main__":
    unittest.main()
