import json
import tempfile
import unittest
from pathlib import Path

from tools.build_onet_task_curricula import build, read_rows
from tools.discover_open_source_bootcamp_sources import load_subjects


class BootcampDiscoveryTests(unittest.TestCase):
    def test_live_hugging_face_subjects_are_merged_with_seed_taxonomy(self):
        config = {"discovery": {"hugging_face_subjects": ["seed-topic"]}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "taxonomy.json"
            path.write_text(json.dumps({"subject_terms": ["audio", "vision-language"]}), encoding="utf-8")
            subjects, status, dynamic_count = load_subjects(config, str(path))
        self.assertEqual(subjects, ["audio", "seed-topic", "vision-language"])
        self.assertEqual(status, "live_taxonomy_plus_configured_seeds")
        self.assertEqual(dynamic_count, 2)

    def test_missing_live_taxonomy_uses_seed_fallback_with_explicit_status(self):
        config = {"discovery": {"hugging_face_subjects": ["seed-topic"]}}
        subjects, status, dynamic_count = load_subjects(config, "/path/that/does/not/exist.json")
        self.assertEqual(subjects, ["seed-topic"])
        self.assertIn("fallback", status)
        self.assertEqual(dynamic_count, 0)

    def test_reads_official_json_task_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task_statements.json"
            path.write_text(json.dumps({"Task Statements": [
                {"O*NET-SOC Code": "15-1252.00", "Occupation Title": "Software Developers",
                 "Task ID": "1.A", "Task": "Write code", "Task Type": "Core"},
                {"O*NET-SOC Code": "15-1252.00", "Occupation Title": "Software Developers",
                 "Task ID": "2.B", "Task": "Test software", "Task Type": "Supplemental"}
            ]}), encoding="utf-8")
            rows = read_rows(path)
        result = build(rows, "test-release")
        self.assertEqual(result["inventory"]["task_statements"], 2)
        self.assertEqual(result["inventory"]["occupations"], 1)
        task = result["occupations"][0]["task_playbooks"][0]
        self.assertEqual(task["learning_summary_status"], "not_yet_authored_by_buddy")
        self.assertIn("worked example", task["guide_authoring_brief"]["must_include"])


if __name__ == "__main__":
    unittest.main()
