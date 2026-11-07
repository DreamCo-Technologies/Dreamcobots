from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.opensource import BuddyOpenSourceLab, OpenSourceError


class DreamCoInvestigationProfileTests(unittest.TestCase):
    def setUp(self):
        self.lab = BuddyOpenSourceLab()
        self.base = {
            "owner_authorized": True,
            "written_scope": "Test documented user workflows against an isolated fixture account.",
            "customizations": ["workflow", "accessibility"],
            "differentiator": "DreamCo will serve an original learning workflow for its users.",
        }

    def test_profiles_cover_code_models_frontier_web_mobile_games_media_and_apis(self):
        policy = json.loads((ROOT / "config/dreamco-investigation-profiles.json").read_text())
        expected = {"code_repository", "open_weights_model", "frontier_model_api", "website", "mobile_app", "game", "film_or_media", "general_api"}
        self.assertEqual(set(policy["profiles"]), expected)
        self.assertTrue(policy["universal_gates"])
        self.assertTrue(policy["never_automate"])

    def test_model_plan_is_revision_pinned_bounded_and_does_not_claim_execution(self):
        plan = self.lab.investigation_plan(
            "open_weights_model", "https://huggingface.co/example/model", revision="abcdef0123456789",
            execution_requested=True, allow_network=False, max_cost_usd=5, **self.base,
        )
        self.assertEqual(plan["target"]["revision"], "abcdef0123456789")
        self.assertFalse(plan["execution_controls"]["execution_started"])
        self.assertFalse(plan["execution_controls"]["host_secrets_available"])
        self.assertIn("hidden holdout", " ".join(plan["test_plan"]))
        self.assertIn("customization", plan)

    def test_api_plan_and_authorization_and_secret_url_gates(self):
        plan = self.lab.investigation_plan("frontier_model_api", "https://api.example.test/v1", **self.base)
        self.assertIn("credential scope", " ".join(plan["evidence_to_collect"]))
        with self.assertRaisesRegex(OpenSourceError, "authorization"):
            self.lab.investigation_plan("website", "https://site.example", **{**self.base, "owner_authorized": False})
        with self.assertRaisesRegex(OpenSourceError, "credential-free"):
            self.lab.investigation_plan("website", "https://user:secret@site.example", **self.base)
        with self.assertRaisesRegex(OpenSourceError, "immutable revision"):
            self.lab.investigation_plan("code_repository", "https://github.com/example/repo", revision="main", **self.base)

    def test_customization_and_budget_gates(self):
        with self.assertRaisesRegex(OpenSourceError, "two supported"):
            self.lab.investigation_plan("game", "./my-game", **{**self.base, "customizations": ["workflow"]})
        with self.assertRaisesRegex(OpenSourceError, "budget"):
            self.lab.investigation_plan("game", "./my-game", max_cost_usd=-1, **self.base)


if __name__ == "__main__":
    unittest.main()
