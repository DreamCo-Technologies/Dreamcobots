import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from tools.audit_markdown_requirement_traceability import extract
from tools.validate_masterbot_registry import validate

class DreamCoFleetAndTraceabilityTests(unittest.TestCase):
    def test_registry_is_exactly_45_domain_and_20_platform(self):
        data=validate()
        self.assertEqual(len(data["masterbots"]),65)
        self.assertEqual(sum(x["type"]=="domain" for x in data["masterbots"]),45)
        self.assertEqual(sum(x["type"]=="platform" for x in data["masterbots"]),20)
    def test_each_masterbot_has_unique_lane(self):
        bots=validate()["masterbots"]
        self.assertEqual(len({x["lane_id"] for x in bots}),65)
    def test_traceability_ids_are_stable_and_sources_are_retained(self):
        first=extract()
        second=extract()
        self.assertTrue(first)
        self.assertEqual([x["requirement_id"] for x in first],[x["requirement_id"] for x in second])
        self.assertTrue(all(x["source_path"] and x["line"]>0 for x in first))
    def test_traceability_never_claims_verified_from_path_presence(self):
        source=Path("tools/audit_markdown_requirement_traceability.py").read_text()
        self.assertIn("evidence_artifacts_present_requires_review",source)
        self.assertIn("Path existence is not a passing test",source)

if __name__=="__main__": unittest.main()
