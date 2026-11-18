"""Guards for config/buddy/resource-registry.json via the buddy:resource-connections check."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("resource_catalog", ROOT / "tools" / "generate_resource_connection_catalog.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)
REGISTRY = json.loads((ROOT / "config" / "buddy" / "resource-registry.json").read_text())


class ResourceRegistryTest(unittest.TestCase):
    def summarize(self, registry: dict) -> dict:
        original = catalog.REGISTRY
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resource-registry.json"
            path.write_text(json.dumps(registry))
            catalog.REGISTRY = path
            try:
                return catalog.registry_summary()
            finally:
                catalog.REGISTRY = original

    def mutated(self, rid: str, **changes) -> dict:
        registry = copy.deepcopy(REGISTRY)
        next(item for item in registry["resources"] if item["id"] == rid).update(changes)
        return registry

    def test_committed_registry_passes_and_ranks_fifteen(self):
        summary = catalog.registry_summary()
        self.assertEqual([item["rank"] for item in summary["ranked"]], list(range(1, 16)))
        self.assertIn("XAI_API_KEY", summary["secret_names_to_set"])
        self.assertIn("xai_outputs_for_training", summary["blocked"])

    def test_xai_router_entry_stays_contract_only_with_training_block(self):
        router = json.loads((ROOT / "config" / "buddy-model-router.json").read_text())
        xai = next(item for item in router["connectors"] if item["id"] == "xai")
        self.assertEqual(xai["implementation_status"], "contract_only")
        self.assertTrue(xai["usage_terms"]["train_on_outputs"].startswith("prohibited"))
        self.assertTrue(all(src.startswith("https://x.ai/legal/") for src in xai["usage_terms"]["sources"]))

    def test_rejects_secret_values(self):
        fake = "xai-" + "A" * 24
        with self.assertRaisesRegex(SystemExit, "secret names only"):
            self.summarize(self.mutated("xai_grok_api", blocker=fake))

    def test_rejects_unknown_status_and_promotion_flags(self):
        with self.assertRaisesRegex(SystemExit, "unknown connection_status"):
            self.summarize(self.mutated("local_rag", connection_status="live"))
        with self.assertRaisesRegex(SystemExit, "promotion flags"):
            self.summarize(self.mutated("local_rag", production_ready=True))

    def test_contract_only_connector_cannot_be_marked_connected(self):
        with self.assertRaisesRegex(SystemExit, "cannot be marked connected"):
            self.summarize(self.mutated("xai_grok_api", connection_status="connected"))

    def test_secret_names_must_match_router(self):
        with self.assertRaisesRegex(SystemExit, "router secret_references"):
            self.summarize(self.mutated("xai_grok_api", secret_names=["GROK_KEY"]))

    def test_missing_wired_path_fails(self):
        with self.assertRaisesRegex(SystemExit, "wired_into path missing"):
            self.summarize(self.mutated("local_rag", wired_into=["foundry/does_not_exist.py"]))


class CompactModelRegistryTest(unittest.TestCase):
    def test_gpt_54_mini_is_listed_as_a_paid_unverified_inference_route(self):
        registry = json.loads((ROOT / "config" / "buddy-model-selection-registry.json").read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertEqual(model["model_id"], "gpt-5.4-mini")
        self.assertEqual(model["provider"], "openai")
        self.assertEqual(model["availability"], "configuration_required")
        self.assertEqual(model["connection_status"], "unverified")
        self.assertTrue(model["requires_per_request_paid_approval"])
        self.assertEqual(model["benchmark_status"], "not_run")

    def test_openai_mini_weight_training_is_not_claimed(self):
        registry = json.loads((ROOT / "config" / "buddy-model-selection-registry.json").read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertFalse(model["fine_tuning_supported"])
        self.assertFalse(model["weight_modification"])
        self.assertFalse(registry["weight_modification"])

    def test_model_pricing_is_recorded_without_claiming_measured_cost(self):
        registry = json.loads((ROOT / "config" / "buddy-model-selection-registry.json").read_text(encoding="utf-8"))
        model = next(row for row in registry["models"] if row["id"] == "gpt-5.4-mini")
        self.assertEqual(model["price_usd_per_million_tokens"]["input"], 0.75)
        self.assertEqual(model["price_usd_per_million_tokens"]["output"], 4.5)
        self.assertIsNone(model["cost"])


if __name__ == "__main__":
    unittest.main()
