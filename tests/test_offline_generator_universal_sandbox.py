import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class OfflineGeneratorUniversalSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.offline = json.loads((ROOT / "config" / "offline-buddy-repository-engine.json").read_text(encoding="utf-8"))
        cls.factory = json.loads((ROOT / "config" / "dreamco-generator-factory.json").read_text(encoding="utf-8"))
        cls.sandbox = json.loads((ROOT / "config" / "universal-api-task-sandbox-program.json").read_text(encoding="utf-8"))
        cls.factory_module = load_module("dreamco_generator_factory", ROOT / "tools" / "dreamco_generator_factory.py")
        cls.sandbox_module = load_module("build_universal_api_task_sandbox", ROOT / "tools" / "build_universal_api_task_sandbox.py")

    def test_offline_core_does_not_require_github(self):
        rules = " ".join(self.offline["principles"]).lower()
        self.assertIn("github-independent", rules)
        self.assertIn("offline", rules)
        self.assertIn("same tests locally and in github actions", rules)
        self.assertGreaterEqual(len(self.offline["local_equivalents"]), 12)
        self.assertGreaterEqual(len(self.offline["required_local_commands"]), 10)

    def test_exactly_thirty_custom_generator_types_are_registered(self):
        rows = self.factory["generator_types"]
        ids = [row["id"] for row in rows]
        self.assertEqual(len(rows), 30)
        self.assertEqual(len(ids), len(set(ids)))
        categories = {row["category"] for row in rows}
        for required in {"engineering", "quality", "repair", "knowledge", "resources", "data", "ai", "training", "automation", "fleet", "operations", "research", "business", "creative", "product", "delivery"}:
            self.assertIn(required, categories)

    def test_generator_registry_covers_the_canonical_fleet(self):
        registry = self.factory_module.build_registry()
        self.assertGreaterEqual(registry["bot_count"], 1000)
        self.assertEqual(registry["generator_count"], 30)
        expected = set(registry["generator_ids"])
        for row in registry["fleet_access"]:
            self.assertEqual(set(row["allowed_generators"]), expected)

    def test_universal_sandbox_supports_many_target_types_and_dimensions(self):
        self.assertGreaterEqual(len(self.sandbox["supported_targets"]), 12)
        self.assertGreaterEqual(len(self.sandbox["shared_test_dimensions"]), 60)
        for target in ["http_api", "local_function", "cli_command", "model_call", "agent_task", "browser_task", "device_task", "user_defined_task"]:
            self.assertIn(target, self.sandbox["supported_targets"])

    def test_any_well_formed_custom_task_gets_a_large_plan(self):
        spec = {
            "target_id": "demo-user-task",
            "target_type": "user_defined_task",
            "objective": "transform an input into a verified output",
            "inputs": {"value": "string"},
            "expected_outputs": {"result": "string"},
            "side_effect_level": "none",
            "permissions": [],
            "success_metrics": ["correctness", "latency"],
        }
        plan = self.sandbox_module.build_plan(spec, self.sandbox)
        self.assertEqual(plan["target"]["target_id"], "demo-user-task")
        self.assertGreaterEqual(plan["planned_case_count"], 400)
        self.assertTrue(all(row["status"] == "planned_not_run" for row in plan["cases"]))

    def test_consequential_tasks_do_not_default_to_execution(self):
        self.assertIn("approval", self.sandbox["side_effect_levels"]["consequential"].lower())
        self.assertIn("simulate", self.sandbox["side_effect_levels"]["consequential"].lower())


if __name__ == "__main__":
    unittest.main()
