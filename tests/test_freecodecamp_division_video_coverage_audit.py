import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_freecodecamp_division_video_coverage import audit


def write_json(root: Path, relative: str, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture_root(root: Path):
    domains = [{"domain_id": f"domain-{i}", "owner_approval": None} for i in range(1, 56)]
    bots = [{"id": i, "name": f"MasterBot{i}"} for i in range(1, 66)]
    write_json(root, "buddy/bootcamp/sources/freecodecamp/catalog.json", {
        "schema": "dreamco.freecodecamp_catalog.v1",
        "inventory_status": "partial",
        "generated_at": "2026-11-26T00:00:00Z",
        "categories": [{"id": "python"}, {"id": "other_or_unclassified"}],
        "videos": [
            {"video_id": "video-1", "categories": ["python"]},
            {"video_id": "video-2", "categories": ["other_or_unclassified"]},
        ],
        "inventory": {
            "complete": False, "expected_entry_count": None,
            "observed_entry_count": 2, "null_entry_count": 0,
            "duplicate_video_id_count": 0,
        },
    })
    write_json(root, "config/generated/masterbot-55-domain-crosswalk.json", {
        "schema": "dreamco.masterbot_domain_crosswalk.v1",
        "domains": domains,
        "masterbots": [{"masterbot_id": i, "owner_approval": None} for i in range(1, 66)],
    })
    write_json(root, "config/freecodecamp-division-category-profiles.json", {
        "schema": "dreamco.freecodecamp_division_category_profiles.v1",
        "domain_categories": {f"domain-{i}": ["python"] for i in range(1, 56)},
    })
    write_json(root, "config/masterbot-65-registry.json", {"divisions": bots})
    write_json(root, "config/freecodecamp-division-routing-overrides.json", {"entries": []})
    write_json(root, "config/buddy-division-specialist-course-artifacts.json", {"artifacts": []})
    required_config = {
        "schema": "dreamco.division_superbot.v2",
        "identity": {"id": "domain-1"},
        "mission": "Fixture domain mission",
        "capabilities": [{"id": "cap-1"}],
        "tools": [], "connectors": [], "policies": [], "dependencies": [],
        "workflows": [], "implementationTasks": [], "benchmarks": [],
        "status": "source_mapped_needs_validation",
    }
    write_json(root, "config/divisions/domain-1.json", required_config)
    empty = root / "config/divisions/domain-2.json"
    empty.parent.mkdir(parents=True, exist_ok=True)
    empty.write_text("", encoding="utf-8")


class FreeCodeCampDivisionVideoCoverageAuditTests(unittest.TestCase):
    def test_audit_reports_missing_and_empty_division_files_without_claiming_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture_root(root)
            report = audit(root)
        counts = report["division_coverage"]["division_config_counts"]
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["catalog"]["video_rows"], 2)
        self.assertEqual(report["catalog"]["unclassified_video_count"], 1)
        self.assertEqual(counts["valid"], 1)
        self.assertEqual(counts["empty"], 1)
        self.assertEqual(counts["missing"], 53)
        self.assertEqual(report["specialist_curriculum"]["required_artifact_slots"], 960)
        self.assertEqual(report["specialist_curriculum"]["missing_artifact_slots"], 960)
        self.assertFalse(report["catalog"]["inventory_complete"])

    def test_unknown_categories_and_duplicate_video_ids_are_blockers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture_root(root)
            catalog_path = root / "buddy/bootcamp/sources/freecodecamp/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["videos"].append({"video_id": "video-1", "categories": ["made_up_category"]})
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            report = audit(root)
        self.assertEqual(report["catalog"]["duplicate_video_ids"], ["video-1"])
        self.assertEqual(report["catalog"]["invalid_video_category_count"], 1)
        self.assertIn("video_id_integrity_failure", report["blockers"])
        self.assertIn("videos_with_unknown_categories:1", report["blockers"])


if __name__ == "__main__":
    unittest.main()
