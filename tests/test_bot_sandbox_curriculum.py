import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
PROGRAM = ROOT / "config" / "bot-universal-sandbox-skill-gap-program.json"
GENERATED = ROOT / "config" / "generated" / "bot-sandbox-curriculum.json"
UNIVERSAL = ROOT / "config" / "generated" / "universal-human-ai-task-sandbox.json"


class BotSandboxCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(PROGRAM.read_text(encoding="utf-8"))
        cls.source_bots = []
        for path in sorted(APP_BOTS.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for bot in payload.get("bots", []):
                cls.source_bots.append((payload.get("division") or path.stem, bot))

    def test_every_source_bot_has_slug_and_capabilities(self):
        slugs = []
        for division, bot in self.source_bots:
            self.assertTrue(bot.get("slug"), f"missing slug in {division}")
            self.assertIsInstance(bot.get("capabilities"), list, bot.get("slug"))
            self.assertGreater(len(bot.get("capabilities") or []), 0, f"no declared capabilities for {bot.get('slug')}")
            slugs.append(bot["slug"])
        self.assertEqual(len(slugs), len(set(slugs)), "duplicate bot slugs detected")
        self.assertGreaterEqual(len(slugs), 1000, "canonical fleet unexpectedly shrank below 1000 bots")

    def test_program_has_deep_capability_tool_function_and_efficiency_dimensions(self):
        self.assertGreaterEqual(len(self.program["capability_test_dimensions"]), 12)
        self.assertGreaterEqual(len(self.program["tool_test_dimensions"]), 12)
        self.assertGreaterEqual(len(self.program["function_test_dimensions"]), 10)
        self.assertGreaterEqual(len(self.program["efficiency_dimensions"]), 16)
        self.assertGreaterEqual(len(self.program["skill_ladder"]), 8)
        self.assertGreaterEqual(len(self.program["gap_plan_required_fields"]), 15)

    def test_generator_output_if_present_covers_every_bot_and_capability(self):
        if not GENERATED.exists():
            self.skipTest("generated curriculum is created by tools/build_bot_sandbox_curriculum.py")
        data = json.loads(GENERATED.read_text(encoding="utf-8"))
        by_slug = {row["slug"]: row for row in data["bots"]}
        self.assertEqual(len(by_slug), len(self.source_bots))
        source_capability_count = 0
        for _, bot in self.source_bots:
            source_capability_count += len(bot.get("capabilities") or [])
            row = by_slug[bot["slug"]]
            self.assertEqual(row["declared_capability_count"], len(bot.get("capabilities") or []))
            self.assertEqual(len(row["capability_tests"]), len(bot.get("capabilities") or []))
            for test_plan in row["capability_tests"]:
                self.assertEqual(test_plan["dimensions"], self.program["capability_test_dimensions"])
            self.assertEqual(row["tool_contract"]["inventory_status"], "runtime_discovery_required")
            self.assertEqual(row["function_contract"]["inventory_status"], "runtime_discovery_required")
            self.assertEqual(row["benchmark_gap_plan"]["status"], "required")
            self.assertTrue(row["benchmark_gap_plan"]["shared_fix_first"])
            self.assertTrue(row["graduation"]["requires_runtime_evidence"])
            self.assertTrue(row["graduation"]["requires_universal_task_coverage"])
            self.assertTrue(row["graduation"]["requires_all_applicable_universal_tests_pass"])
            universal = row["universal_task_sandbox"]
            self.assertTrue(universal["all_applicable_tests_must_pass_for_graduation"])
            self.assertEqual(universal["selection_status"], "runtime_mapping_required")
        self.assertEqual(data["declared_capability_count"], source_capability_count)
        self.assertEqual(
            data["planned_capability_test_instances"],
            source_capability_count * len(self.program["capability_test_dimensions"]),
        )

    def test_universal_task_catalog_if_present_is_large_and_attached(self):
        if not UNIVERSAL.exists() or not GENERATED.exists():
            self.skipTest("universal task catalog and curriculum are generated in platform/fleet workflows")
        universal = json.loads(UNIVERSAL.read_text(encoding="utf-8"))
        data = json.loads(GENERATED.read_text(encoding="utf-8"))
        self.assertGreaterEqual(universal["category_count"], 50000)
        self.assertTrue(data["universal_task_catalog_available"])
        self.assertEqual(data["universal_task_base_category_count"], universal["category_count"])
        for row in data["bots"][:250]:
            self.assertEqual(row["universal_task_sandbox"]["base_category_count_available"], universal["category_count"])

    def test_gap_closing_cannot_be_declared_without_evidence(self):
        joined = json.dumps(self.program).lower()
        for phrase in [
            "failing benchmark evidence",
            "before/after metrics",
            "regressions become permanent fixtures",
            "do not weaken tests",
            "shared fix",
        ]:
            self.assertIn(phrase, joined)


if __name__ == "__main__":
    unittest.main()
