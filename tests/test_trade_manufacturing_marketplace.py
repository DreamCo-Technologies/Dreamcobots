import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOUT = ROOT / "config" / "china-us-tech-manufacturing-scout-program.json"
MARKET = ROOT / "config" / "us-manufacturer-rfq-marketplace-program.json"
KNOWLEDGE = ROOT / "config" / "mastery-data-pack-knowledge-layers.json"
PROGRESS = ROOT / "config" / "system-progress-gauges.json"
GENERATED = ROOT / "config" / "generated" / "trade-manufacturing-marketplace.json"


class TradeManufacturingMarketplaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_trade_manufacturing_marketplace.py")], cwd=ROOT, check=True)
        cls.scout = json.loads(SCOUT.read_text(encoding="utf-8"))
        cls.market = json.loads(MARKET.read_text(encoding="utf-8"))
        cls.knowledge = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
        cls.progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
        cls.generated = json.loads(GENERATED.read_text(encoding="utf-8"))

    def test_china_us_scout_has_broad_source_and_comparison_coverage(self):
        self.assertGreaterEqual(len(self.scout["source_classes"]), 12)
        self.assertGreaterEqual(len(self.scout["comparison_dimensions"]), 25)
        for required in {"private label","ODM customization","OEM contract manufacturing","bring manufacturing to U.S.","Shopify DTC","Amazon marketplace","U.S. manufacturer contract"}:
            self.assertIn(required, set(self.scout["opportunity_types"]))

    def test_scout_does_not_overclaim_us_gaps_or_supplier_identity(self):
        guardrails = " ".join(self.scout["guardrails"]).lower()
        self.assertIn("do not claim manufacturer identity without verification", guardrails)
        self.assertIn("do not claim u.s. absence from one failed search", guardrails)
        self.assertIn("do not bypass anti-bot controls", guardrails)

    def test_marketplace_has_full_rfq_quote_contract_and_payment_flow(self):
        self.assertGreaterEqual(len(self.market["rfq_fields"]), 15)
        self.assertGreaterEqual(len(self.market["quote_fields"]), 12)
        self.assertGreaterEqual(len(self.market["marketplace_features"]), 20)
        self.assertIn("RFQ", self.market["contract_flow"])
        self.assertIn("manufacturer verification", self.market["contract_flow"])
        self.assertIn("production", self.market["contract_flow"])
        self.assertIn("delivery", self.market["contract_flow"])
        self.assertTrue(self.market["payments"]["test_mode_default"])
        self.assertTrue(self.market["payments"]["live_payment_requires_live_revenue_gate"])
        self.assertFalse(self.market["payments"]["escrow_claim"])

    def test_data_packages_include_database_book_api_and_evaluation_knowledge(self):
        layers = self.knowledge["required_layers"]
        for required in {"database_knowledge","book_reference_knowledge","api_sdk_knowledge","library_framework_knowledge","tool_workflow_knowledge","troubleshooting_knowledge","evaluation_knowledge","provenance_rights_knowledge"}:
            self.assertIn(required, layers)

    def test_progress_gauges_require_runtime_evidence_for_100_percent(self):
        self.assertGreaterEqual(len(self.progress["gap_stages"]), 10)
        total = sum(int(row["weight"]) for row in self.progress["gap_stages"])
        self.assertEqual(total, 100)
        self.assertEqual(self.progress["gap_stages"][-1]["id"], "runtime_evidence_pass")
        self.assertIn("cannot reach 100% until runtime evidence passes", self.progress["truth_rule"].lower())

    def test_generated_marketplace_marks_sources_unconnected_until_runtime_adapter_exists(self):
        self.assertGreaterEqual(len(self.generated["scout"]["source_adapters"]), 12)
        for source in self.generated["scout"]["source_adapters"]:
            self.assertTrue(source["authorized_only"])
            self.assertEqual(source["runtime_evidence"], "missing_until_connected")
        self.assertGreaterEqual(len(self.generated["sandbox_requirements"]), 15)


if __name__ == "__main__":
    unittest.main()
