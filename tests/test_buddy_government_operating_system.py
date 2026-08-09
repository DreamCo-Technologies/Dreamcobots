import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuddyGovernmentOperatingSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gov = json.loads((ROOT / "config" / "buddy-government-operating-system.json").read_text(encoding="utf-8"))
        cls.navigator = json.loads((ROOT / "config" / "buddy-211-government-service-navigator.json").read_text(encoding="utf-8"))
        cls.public_work = json.loads((ROOT / "config" / "government-nonprofit-contract-readiness.json").read_text(encoding="utf-8"))

    def test_government_system_has_resident_work_spending_and_opportunity_lanes(self):
        lanes = self.gov["operating_lanes"]
        for lane in {"resident_navigator", "government_work_assistant", "government_needs_watch", "public_money_watch", "government_opportunity_engine", "public_service_builder"}:
            self.assertIn(lane, lanes)
        self.assertGreaterEqual(len(lanes["resident_navigator"]), 10)
        self.assertGreaterEqual(len(lanes["government_work_assistant"]), 10)
        self.assertGreaterEqual(len(lanes["government_opportunity_engine"]), 10)

    def test_official_source_registry_covers_services_spending_contracts_and_grants(self):
        ids = {row["id"] for row in self.gov["official_us_source_registry"]}
        for source_id in {"usa_gov", "usa_spending", "sam_opportunities", "grants_gov", "agency_official_sources", "state_local_tribal_sources"}:
            self.assertIn(source_id, ids)

    def test_every_government_job_gets_benchmark_and_gap_path(self):
        rule = self.gov["government_job_coverage_rule"].lower()
        for phrase in ["every discovered government department/job family/task", "ai-assist benchmark", "human-authority boundary", "sandbox suite", "parallel gap worker", "retest path"]:
            self.assertIn(phrase, rule)
        self.assertGreaterEqual(len(self.public_work["government_job_families"]), 40)
        self.assertGreaterEqual(len(self.gov["gap_team"]), 12)

    def test_211_navigator_remains_broad_and_user_controlled(self):
        self.assertGreaterEqual(len(self.navigator["service_domains"]), 25)
        self.assertGreaterEqual(len(self.navigator["user_journey"]), 15)
        self.assertIn("user-supervised_submission_handoff", self.navigator["application_assistance_levels"])
        self.assertIn("final eligibility determination", self.navigator["never_autonomous"])

    def test_spending_and_contract_signals_are_not_outcome_claims(self):
        scoring = set(self.gov["needs_scoring"])
        for item in {"public value", "staff time saved", "backlog reduction", "procurement demand evidence", "spending evidence", "funding/opportunity evidence", "delivery feasibility"}:
            self.assertIn(item, scoring)
        truth = self.gov["truth_rule"].lower()
        self.assertIn("not a government agency", truth)
        self.assertIn("authoritative runtime evidence", truth)

    def test_consequential_government_authority_stays_human(self):
        prohibited = " ".join(self.gov["never_autonomous"]).lower()
        for phrase in ["final benefit eligibility", "contract award decision", "regulatory enforcement", "election certification", "false attestation", "unapproved bid/proposal submission"]:
            self.assertIn(phrase, prohibited)


if __name__ == "__main__":
    unittest.main()
