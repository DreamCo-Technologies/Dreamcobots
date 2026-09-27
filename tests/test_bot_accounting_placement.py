import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_all_bots_categories_and_agents import audit_bot_accounting


ROOT = Path(__file__).resolve().parents[1]


class BotAccountingPlacementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "App_bots").mkdir()
        (self.root / ".github/agents").mkdir(parents=True)
        self.program = {
            "canonical_fleet": {"profiles": 1, "divisions": 1},
            "supplemental_fleet": {
                "profiles": 2, "divisions": 1, "division_profiles": {"DreamSaaS": 2},
            },
            "specialist_agents": {"review.agent.md": "DreamCodeLab"},
            "required_bot_fields": ["slug", "displayName", "category", "description", "capabilities", "status"],
            "truth_rule": "Source accounting is not proof of production ability.",
        }
        self.write_division("DreamCodeLab", [self.bot("core")])
        self.write_division("DreamSaaS", [self.bot("old-builder"), self.bot("old-pricing")], growth=True)
        (self.root / ".github/agents/review.agent.md").write_text("---\nname: Review\n---\n")

    def bot(self, slug):
        return {"slug": slug, "displayName": slug, "category": "planning", "description": "Prepare a reviewable plan.",
                "capabilities": ["Plan"], "status": "sandbox"}

    def write_division(self, division, bots, growth=False, total=None):
        payload = {"division": division, "total": len(bots) if total is None else total, "bots": bots}
        if growth:
            payload["growth"] = True
        (self.root / "App_bots" / f"{division}.json").write_text(json.dumps(payload))

    def audit(self):
        return audit_bot_accounting(self.root, self.program, {})

    def test_real_repository_keeps_both_cohorts_and_all_agents_accounted(self):
        program = json.loads((ROOT / "config/bot-accounting-placement-program.json").read_text())
        result = audit_bot_accounting(ROOT, program, {})
        self.assertEqual(result["release_blockers"], [])
        self.assertEqual((result["canonical_bot_count"], result["division_count"]), (1051, 45))
        self.assertEqual((result["supplemental_bot_count"], result["supplemental_division_count"]), (50, 10))
        self.assertEqual(result["total_profile_count"], 1101)
        self.assertEqual(result["specialist_agent_count"], 16)
        self.assertEqual(len(result["supplemental_profiles"]), 50)

    def test_growth_profiles_are_separate_but_not_ignored(self):
        result = self.audit()
        self.assertEqual(result["release_blockers"], [])
        self.assertEqual(result["canonical_bot_count"], 1)
        self.assertEqual(result["supplemental_bot_count"], 2)
        self.assertEqual(result["total_profile_count"], 3)
        self.assertEqual(result["category_counts"], {"planning": 3})
        self.assertEqual({bot["slug"] for bot in result["supplemental_profiles"]}, {"old-builder", "old-pricing"})

    def test_missing_supplemental_bot_blocks_even_when_declared_total_is_updated(self):
        self.write_division("DreamSaaS", [self.bot("old-builder")], growth=True)
        result = self.audit()
        self.assertFalse(result["accounting_complete"])
        self.assertIn("supplemental fleet count 1 != expected 2", result["release_blockers"])
        self.assertEqual(result["supplemental_division_mismatches"], [{"division": "DreamSaaS", "expected": 2, "actual": 1}])

    def test_missing_supplemental_division_blocks(self):
        (self.root / "App_bots/DreamSaaS.json").unlink()
        result = self.audit()
        self.assertIn("supplemental division count 0 != expected 1", result["release_blockers"])
        self.assertFalse(result["accounting_complete"])

    def test_duplicate_between_canonical_and_growth_is_a_blocker(self):
        self.write_division("DreamSaaS", [self.bot("core"), self.bot("old-pricing")], growth=True)
        result = self.audit()
        self.assertEqual(result["duplicate_slugs"], [{"slug": "core", "divisions": ["DreamCodeLab", "DreamSaaS"]}])
        self.assertIn("duplicate slugs: 1", result["release_blockers"])

    def test_metadata_gate_applies_to_growth_and_canonical(self):
        for division, growth in [("DreamCodeLab", False), ("DreamSaaS", True)]:
            with self.subTest(division=division):
                bot = self.bot("broken")
                bot["capabilities"] = []
                bot["category"] = "   "
                rows = [bot, self.bot("old-pricing")] if growth else [bot]
                self.write_division(division, rows, growth=growth)
                result = self.audit()
                errors = [error for error in result["metadata_errors"] if error["division"] == division]
                self.assertEqual(len(errors), 1)
                self.assertEqual(set(errors[0]["missing"]), {"capabilities", "category"})
                self.assertFalse(result["accounting_complete"])

    def test_declared_total_gate_applies_to_growth(self):
        self.write_division("DreamSaaS", [self.bot("old-builder"), self.bot("old-pricing")], growth=True, total=3)
        self.assertIn("division declared-total mismatches: 1", self.audit()["release_blockers"])

    def test_new_unowned_agent_cannot_silently_pass(self):
        (self.root / ".github/agents/new.agent.md").write_text("---\nname: New agent\n---\n")
        result = self.audit()
        self.assertEqual(result["unowned_specialist_agents"], ["new.agent.md"])
        self.assertIn("unowned specialist agents: 1", result["release_blockers"])

    def test_unknown_owner_division_does_not_count_as_owned(self):
        self.program["specialist_agents"]["review.agent.md"] = "InventedDivision"
        self.assertIn("specialist agents with unknown owner divisions: 1", self.audit()["release_blockers"])

    def test_missing_expected_agent_remains_a_blocker(self):
        (self.root / ".github/agents/review.agent.md").unlink()
        self.assertIn("missing expected specialist agents: 1", self.audit()["release_blockers"])


if __name__ == "__main__":
    unittest.main()
