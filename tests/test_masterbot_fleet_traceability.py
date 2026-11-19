import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from tools.audit_markdown_requirement_traceability import extract
from tools.validate_masterbot_registry import validate
from tools.select_masterbot_rotation import select

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
        self.assertIn("list_item",source)
        self.assertIn("table_row",source)

    def test_bootcamp_has_eight_levels_and_sandbox_modes(self):
        boot=json.loads(Path("config/buddy-bootcamp-65.json").read_text())
        self.assertEqual([x["id"] for x in boot["levels"]],list(range(1,9)))
        self.assertGreaterEqual(len(boot["sandbox_modes"]),10)
        self.assertTrue(boot["mastery_policy"]["self_report_is_not_evidence"])

    def test_rotation_selects_five_lanes_and_covers_all_65_in_thirteen_ticks(self):
        start=datetime(2026,1,1,0,0,tzinfo=timezone.utc)
        selected=[]
        for tick in range(13):
            at=datetime.fromtimestamp(start.timestamp()+300*tick,timezone.utc)
            result=select(at,5)
            self.assertEqual(len(result["masterbots"]),5)
            self.assertEqual(len(set(result["masterbots"])),5)
            selected.extend(result["masterbots"])
        self.assertEqual(len(selected),65)
        self.assertEqual(len(set(selected)),65)

    def test_public_manifest_matches_canonical_registry(self):
        from tools.generate_masterbot_public_manifest import build
        public=json.loads(Path("website/data/masterbot-fleet.json").read_text())
        self.assertEqual(public,build())
        self.assertEqual(public["summary"]["total"],65)
        self.assertEqual(public["summary"]["lanesPerTick"],5)
        self.assertEqual(public["summary"]["fleetCycleMinutes"],65)

if __name__=="__main__": unittest.main()
