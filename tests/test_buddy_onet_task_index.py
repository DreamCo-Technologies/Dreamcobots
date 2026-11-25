import json
import tempfile
import unittest
from pathlib import Path

from tools.build_onet_task_index import build_task_index
from buddy.learning.course_track_registry import _rows


class OnetTaskIndexTests(unittest.TestCase):
    def setUp(self):
        self.curriculum = {
            "source": {"current_reference_release": "31.0"},
            "source_files": [{"name": "Task Statements", "rows": 2}],
        }

    def test_build_index_preserves_release_ids_and_hash(self):
        rows = [
            {"O*NET-SOC Code": "15-1252.00", "Occupation Title": "Software Developers",
             "Task ID": "123", "Task": "Analyze user needs.", "Task Type": "Core"},
            {"O*NET-SOC Code": "15-1252.00", "Occupation Title": "Software Developers",
             "Task ID": "124", "Task": "Design software.", "Task Type": "Core"},
        ]
        raw = b"official fixture"
        result = build_task_index(
            rows, version="31.0", source_url="https://www.onetcenter.org/example.json",
            source_bytes=raw, curriculum=self.curriculum, minimum_task_count=2,
        )
        self.assertEqual(result["inventory"]["task_statement_count"], 2)
        self.assertEqual(result["inventory"]["occupation_count"], 1)
        self.assertTrue(result["inventory"]["complete"])
        self.assertEqual(result["tasks"][0]["onet_release"], "31.0")
        self.assertEqual(result["tasks"][0]["task_id"], "123")
        self.assertEqual(result["source"]["sha256"], __import__("hashlib").sha256(raw).hexdigest())
        self.assertTrue(result["task_guide_policy"]["each_task_requires_original_workflow_and_practice"])

    def test_duplicate_and_missing_ids_fail_closed(self):
        rows = [
            {"O*NET-SOC Code": "15-1252.00", "Task ID": "123", "Task": "Analyze needs."},
            {"O*NET-SOC Code": "15-1252.00", "Task ID": "123", "Task": "Duplicate."},
            {"O*NET-SOC Code": "", "Task ID": "124", "Task": "Missing occupation."},
        ]
        result = build_task_index(
            rows, version="31.0", source_url="https://www.onetcenter.org/example.json",
            source_bytes=b"fixture", curriculum=self.curriculum, minimum_task_count=1,
        )
        self.assertFalse(result["inventory"]["complete"])
        self.assertEqual(result["inventory"]["duplicate_identity_count"], 1)
        self.assertEqual(result["inventory"]["missing_identity_count"], 1)

    def test_newer_release_requires_reference_refresh_review(self):
        rows = [{"O*NET-SOC Code": "15-1252.00", "Task ID": "123", "Task": "Analyze needs."}]
        result = build_task_index(
            rows, version="32.0", source_url="https://www.onetcenter.org/example.json",
            source_bytes=b"fixture", curriculum=self.curriculum, minimum_task_count=1,
        )
        self.assertFalse(result["inventory"]["release_matches_reference"])
        self.assertEqual(result["status"], "release_review_required")

    def test_runtime_emits_task_lessons_when_index_is_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_path = root / "data/onet/onet-task-index.json"
            index_path.parent.mkdir(parents=True)
            index_path.write_text(json.dumps({
                "source": {"official_download_url": "https://www.onetcenter.org/tasks.json"},
                "inventory": {"complete": True},
                "tasks": [{
                    "occupation_code": "15-1252.00",
                    "occupation_title": "Software Developers",
                    "task_id": "123",
                    "task_statement": "Analyze user needs.",
                    "task_type": "Core",
                    "onet_release": "31.0",
                }],
            }), encoding="utf-8")
            track = {
                "parser": "onet",
                "task_index_path": "data/onet/onet-task-index.json",
                "guide": "docs/BUDDY_ONET_FULL_CONTENT_MODEL_AND_TASK_PLAYBOOKS.md",
                "rights": "onet_cc_by_4.0_attribution",
            }
            rows = _rows(track, {"subject_inventory": []}, root)
            task = next(row for row in rows if row["id"] == "onet-task-15-1252.00-123")
            self.assertIn("Analyze user needs", task["title"])
            self.assertIn("unseen assessment", task["assessment"].lower())
            self.assertEqual(task["source_url"], "https://www.onetcenter.org/tasks.json")


if __name__ == "__main__":
    unittest.main()
