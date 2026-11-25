import json
import unittest
from pathlib import Path

from tools.build_live_revenue_readiness import canonical_bots

ROOT = Path(__file__).resolve().parents[1]


class LiveRevenueReadinessCoverageTests(unittest.TestCase):
    def test_readiness_uses_every_generated_bot_profile(self):
        rows = canonical_bots()
        self.assertEqual(len(rows), 1232)
        self.assertEqual(len({slug for slug, _division in rows}), len(rows))
        self.assertTrue(all(slug and division for slug, division in rows))


    def test_revenue_lane_catalog_has_unique_core_and_expansion_lanes(self):
        data = json.loads((ROOT / "money_os/config/revenue_lanes_expanded.json").read_text(encoding="utf-8"))
        lanes = data["lanes"]
        ids = [row["id"] for row in lanes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 34)
        self.assertTrue({
            "affiliate_partnerships", "franchise_growth", "ai_model_services",
            "licensing_marketplace", "travel_booking", "unclaimed_property",
            "price_drops", "receipt_rewards", "resale_arbitrage", "revenue_intelligence",
        }.issubset(set(ids)))

    def test_expanded_opportunity_sources_remain_authorized_and_fail_closed(self):
        data = json.loads((ROOT / "money_os/data/opportunity_sources.json").read_text(encoding="utf-8"))
        self.assertTrue({
            "affiliate_offers", "professional_services", "property_opportunities",
            "software_partners", "creator_marketplaces", "digital_products",
            "equipment_supply", "travel_suppliers", "licensed_data", "auto_opportunities",
            "insurance_opportunities", "business_marketplaces", "franchise_opportunities",
            "ai_model_services", "licensing_rights", "unclaimed_money", "digital_assets",
        }.issubset(set(data["categories"])))
        self.assertTrue({
            "credential_automation", "captcha_bypass", "terms_of_service_evasion",
            "fake_claims", "fake_reviews", "unauthorized_receipt_submission",
        }.issubset(set(data["blocked_without_authorization"])))

    def test_readiness_includes_markdown_and_other_non_app_bots(self):
        rows = canonical_bots()
        divisions = {division for _slug, division in rows}
        self.assertIn("DreamAffiliate", divisions)
        self.assertIn("GrokTeammates", divisions)
        self.assertGreater(len(rows), 1051)


if __name__ == "__main__":
    unittest.main()
