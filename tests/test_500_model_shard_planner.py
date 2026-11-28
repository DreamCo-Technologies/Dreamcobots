import json
import tempfile
import unittest
from pathlib import Path

from tools.plan_500_model_shards import (
    EXPECTED_MODELS, MODELS_PER_SHARD, SHARD_COUNT, build_plan, read_inventory,
)


def approved_inventory():
    return {
        "status": "VERIFIED",
        "expected_model_count": EXPECTED_MODELS,
        "models": [{
            "model_id": f"provider/model-{i:03d}",
            "provider": "ExampleProvider",
            "model_revision": f"sha256:{i:064x}",
            "adapter_id": "example-adapter-v1",
            "model_card_uri": f"https://example.org/models/{i}",
            "access_status": "AVAILABLE",
            "license_review_status": "APPROVED",
            "evaluation_authorized": True,
            "benchmark_suites": ["reasoning-v1", "tool-use-v1"],
            "review_record_id": f"review-{i:03d}",
        } for i in range(1, EXPECTED_MODELS + 1)],
    }


class FiveHundredModelShardPlannerTests(unittest.TestCase):
    def test_empty_repository_inventory_fails_closed_without_fake_models(self):
        inventory_path = Path(__file__).resolve().parents[1] / "config/verified-model-inventory.json"
        plan = build_plan(read_inventory(inventory_path))
        self.assertEqual(plan["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertEqual(plan["verified_model_records"], 0)
        self.assertEqual(plan["shard_count"], 10)
        self.assertTrue(all(shard["planned_models"] == 0 for shard in plan["shards"]))
        self.assertFalse(plan["execution_started"])
        self.assertEqual(plan["provider_calls"], 0)
        self.assertFalse(plan["paid_calls_enabled"])

    def test_exactly_500_reviewed_pinned_models_split_into_10x50(self):
        plan = build_plan(approved_inventory())
        self.assertEqual(plan["status"], "READY_FOR_SEPARATE_COMPUTE_APPROVAL")
        self.assertEqual(plan["verified_model_records"], 500)
        self.assertEqual([x["planned_models"] for x in plan["shards"]], [50] * 10)
        self.assertEqual(sum(x["planned_models"] for x in plan["shards"]), 500)
        self.assertFalse(plan["execution_started"])

    def test_499_models_never_get_padded_with_placeholder_slots(self):
        inventory = approved_inventory()
        inventory["models"].pop()
        plan = build_plan(inventory)
        self.assertEqual(plan["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertEqual(plan["verified_model_records"], 0)
        self.assertTrue(any("found 499" in item for item in plan["blockers"]))

    def test_duplicate_ids_and_unapproved_rights_block_the_whole_plan(self):
        inventory = approved_inventory()
        inventory["models"][1]["model_id"] = inventory["models"][0]["model_id"]
        inventory["models"][2]["license_review_status"] = "PENDING"
        plan = build_plan(inventory)
        self.assertEqual(plan["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertTrue(any("duplicate model_id" in item for item in plan["blockers"]))
        self.assertTrue(any("license_review_status" in item for item in plan["blockers"]))

    def test_wrong_declared_inventory_count_is_rejected(self):
        inventory = approved_inventory()
        inventory["expected_model_count"] = 499
        plan = build_plan(inventory)
        self.assertEqual(plan["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertTrue(any("expected_model_count must equal 500" in item for item in plan["blockers"]))

    def test_mutable_model_revisions_are_rejected(self):
        inventory = approved_inventory()
        inventory["models"][0]["model_revision"] = "latest"
        plan = build_plan(inventory)
        self.assertEqual(plan["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertTrue(any("immutable/pinned" in item for item in plan["blockers"]))


if __name__ == "__main__":
    unittest.main()
