from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from buddy.learning.library_knowledge_router import route_library_question

ROOT = Path(__file__).resolve().parents[1]


class BuddyLibraryKnowledgeRouterTests(unittest.TestCase):
    def test_approved_guide_is_used_before_any_external_discovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "data/buddy-library-study-guides").mkdir(parents=True)
            (root / "config/buddy-universal-library-curriculum.json").write_text(
                json.dumps({"freshness": {"recheck_official_docs_days": 30}}), encoding="utf-8"
            )
            guide = json.loads((ROOT / "data/buddy-library-study-guides/python-requests.json").read_text(encoding="utf-8"))
            guide["status"] = "approved_for_study"
            guide["evaluation"]["evidence_state"] = "guide_reviewed"
            (root / "data/buddy-library-study-guides/python-requests.json").write_text(
                json.dumps(guide), encoding="utf-8"
            )
            result = route_library_question(
                "Python HTTP requests sessions", root=root, external_discovery=False
            )
            self.assertEqual(result["route"], "internal_approved_guide")
            self.assertEqual(result["internal"]["matches"][0]["canonical_id"], "python-requests")
            self.assertFalse(result["external_discovery_performed"])
            self.assertFalse(result["external_model_call_performed"])

    def test_seed_candidate_is_not_a_guide_and_no_external_call_is_default(self):
        result = route_library_question("React", root=ROOT)
        self.assertEqual(result["route"], "internal_knowledge_gap")
        self.assertTrue(result["internal"]["seed_candidate_matches"])
        self.assertEqual(result["registry_candidates"], [])
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_model_call_performed"])

    def test_explicit_external_discovery_is_metadata_only(self):
        payload = {
            "objects": [{
                "package": {
                    "name": "react", "version": "19.0.0", "description": "UI library",
                    "links": {"npm": "https://www.npmjs.com/package/react", "repository": "https://github.com/facebook/react"},
                }
            }]
        }
        def opener(request, timeout):
            return io.BytesIO(json.dumps(payload).encode("utf-8"))
        result = route_library_question(
            "React", root=ROOT, external_discovery=True, registry_opener=opener, limit=5
        )
        self.assertTrue(result["external_discovery_performed"])
        self.assertFalse(result["external_model_call_performed"])
        self.assertTrue(result["registry_candidates"])
        for item in result["registry_candidates"]:
            for candidate in item["discovery"]["candidates"]:
                self.assertFalse(candidate["download_authorized"])
                self.assertFalse(candidate["execution_authorized"])
                self.assertEqual(candidate["training_permission"], "pending")

    def test_gap_persistence_requires_a_redacted_query_and_uses_private_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(PermissionError):
                route_library_question("React", root=ROOT, persist_gap=True, gap_root=root)
            result = route_library_question(
                "React", root=ROOT, persist_gap=True, query_is_redacted=True, gap_root=root
            )
            self.assertTrue(result["gap_recorded"])
            self.assertTrue((root / ".dreamco/library-knowledge-gaps.jsonl").exists())
            self.assertFalse((root / "data/buddy-library-knowledge-gaps.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
