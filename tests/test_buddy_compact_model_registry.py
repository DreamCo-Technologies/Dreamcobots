"""Regression tests for the DreamCo compact model selection catalog."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "buddy-model-selection-registry.json"


class CompactModelRegistryTest(unittest.TestCase):
    def test_gpt_54_mini_is_listed_as_a_paid_unverified_inference_route(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertEqual(model["model_id"], "gpt-5.4-mini")
        self.assertEqual(model["provider"], "openai")
        self.assertEqual(model["availability"], "configuration_required")
        self.assertEqual(model["connection_status"], "unverified")
        self.assertTrue(model["requires_per_request_paid_approval"])
        self.assertEqual(model["benchmark_status"], "not_run")

    def test_openai_mini_weight_training_is_not_claimed(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertFalse(model["fine_tuning_supported"])
        self.assertFalse(model["weight_modification"])
        self.assertFalse(registry["weight_modification"])

    def test_model_pricing_is_recorded_without_claiming_measured_cost(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertEqual(model["price_usd_per_million_tokens"]["input"], 0.75)
        self.assertEqual(model["price_usd_per_million_tokens"]["output"], 4.5)
        self.assertIsNone(model["cost"])


if __name__ == "__main__":
    unittest.main()
