import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Buddy211AndUniversalAppBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = json.loads((ROOT / "config" / "buddy-211-government-service-navigator.json").read_text(encoding="utf-8"))
        cls.sources = json.loads((ROOT / "config" / "buddy-211-source-adapters.json").read_text(encoding="utf-8"))
        cls.digital = json.loads((ROOT / "config" / "universal-app-computer-use-expansion.json").read_text(encoding="utf-8"))

    def test_211_covers_broad_service_navigation(self):
        self.assertGreaterEqual(len(self.nav["service_domains"]), 25)
        self.assertGreaterEqual(len(self.nav["user_journey"]), 15)
        for capability in ["likely eligibility screening", "document checklist generation", "application plan generation", "form drafting", "form completeness checking"]:
            self.assertIn(capability, self.nav["capabilities"])

    def test_211_preserves_agency_and_user_authority(self):
        blocked = " ".join(self.nav["never_autonomous"]).lower()
        for phrase in ["final eligibility determination", "false attestation", "signature impersonation", "identity verification", "benefit fraud"]:
            self.assertIn(phrase, blocked)
        self.assertIn("not an agency", self.nav["truth_rule"].lower())

    def test_211_sources_separate_discovery_from_authoritative_rules(self):
        ids = {row["id"] for row in self.sources["sources"]}
        for required in {"usa_gov_services", "usa_gov_benefits", "united_way_211", "sam_contract_opportunities", "grants_gov", "usajobs"}:
            self.assertIn(required, ids)
        self.assertIn("responsible government agency", self.sources["source_selection_rule"].lower())
        self.assertIn("raw ssns", self.sources["security_rule"].lower())

    def test_digital_benchmark_expansion_is_broad(self):
        self.assertGreaterEqual(len(self.digital["domains"]), 18)
        case_count = sum(len(items) for items in self.digital["domains"].values())
        self.assertGreaterEqual(case_count, 150)
        for domain in ["government_and_civic", "business_and_entrepreneurship", "creative_and_entertainment", "accessibility_and_assistance", "devices_and_connected_life"]:
            self.assertIn(domain, self.digital["domains"])

    def test_every_digital_case_gets_parallel_gap_team(self):
        team = set(self.digital["gap_team"])
        for role in {"builder bot", "integration bot", "sandbox QA bot", "security/privacy bot", "performance bot", "business-value bot", "release reviewer"}:
            self.assertIn(role, team)
        self.assertIn("does not mean the capability is already implemented", self.digital["truth_rule"].lower())


if __name__ == "__main__":
    unittest.main()
