from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.generate_buddy_bot_calculators import CONFIG_OUT, TEMPLATES, WEB_OUT, build_registry, stable_json


class BuddyBotCalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build_registry()
        cls.calculators = cls.registry["calculators"]

    def test_every_bot_has_one_unique_local_calculator(self):
        summary = self.registry["summary"]
        self.assertEqual(summary["calculators"], 1051)
        self.assertEqual(summary["unique_calculator_ids"], 1051)
        self.assertEqual(summary["bots_covered"], 1051)
        self.assertEqual(summary["divisions_covered"], 45)
        self.assertEqual(summary["interactive_local_calculators"], 1051)
        self.assertEqual(len({item["bot"]["slug"] for item in self.calculators}), 1051)
        self.assertEqual(len({item["calculator_id"] for item in self.calculators}), 1051)

    def test_all_safe_templates_are_used_and_inputs_are_bounded(self):
        self.assertEqual(set(self.registry["template_counts"]), set(TEMPLATES))
        for calculator in self.calculators:
            self.assertFalse(calculator["engine"]["network_required"])
            self.assertFalse(calculator["engine"]["arbitrary_expression_evaluation"])
            self.assertEqual(calculator["engine"]["status"], "local_interactive_ready")
            keys = [item["key"] for item in calculator["inputs"]]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertTrue(all(item["min"] <= item["default"] <= item["max"] for item in calculator["inputs"]))
            self.assertTrue(all(item["step"] > 0 for item in calculator["inputs"]))
            self.assertTrue(calculator["outputs"])

    def test_real_estate_and_vehicle_profiles_receive_specialized_math(self):
        by_slug = {item["bot"]["slug"]: item for item in self.calculators}
        real_estate = [item for item in self.calculators if item["bot"]["division"] == "DreamRealEstate"]
        self.assertEqual(len(real_estate), 25)
        self.assertTrue(all(item["template_id"] == "real_estate_flip" for item in real_estate))
        self.assertEqual(by_slug["fleet-admin"]["template_id"], "car_flip")

    def test_formula_text_is_reference_only_and_outputs_are_current(self):
        self.assertTrue(all(
            item["assigned_division_formula"]["execution"] == "reference_only_not_evaluated"
            for item in self.calculators
        ))
        expected = stable_json(self.registry)
        self.assertEqual(CONFIG_OUT.read_text(encoding="utf-8"), expected)
        self.assertEqual(WEB_OUT.read_text(encoding="utf-8"), expected)
        self.assertEqual(json.loads(expected)["schema"], "dreamco.bot_calculator_registry.v1")


if __name__ == "__main__":
    unittest.main()
