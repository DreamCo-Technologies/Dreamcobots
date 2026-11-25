from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from buddy.learning.universal_library_registry import (
    library_coverage_report,
    record_library_knowledge_gap,
    search_internal_library_knowledge,
    validate_library_guide_document,
)
from buddy.learning.course_track_registry import load_course_lessons


class UniversalLibraryRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "config").mkdir()
        (self.root / "data/buddy-library-study-guides").mkdir(parents=True)
        (self.root / "config/buddy-universal-library-curriculum.json").write_text(json.dumps({
            "scope": {"catalog_strategy": "continuous_discovery"}
        }), encoding="utf-8")
        (self.root / "config/library_ecosystems.json").write_text(json.dumps({
            "ecosystems": [{"id": "python", "registries": ["PyPI"], "languages": ["Python"]}]
        }), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_guide(self, *, status="approved_for_study", derivative="approved", access="public"):
        guide = {
            "schema_version": "dreamco.buddy_library_study_guide.v1",
            "library": {
                "canonical_id": "python-requests",
                "name": "Requests",
                "ecosystem": "python",
                "artifact_type": "library",
                "version_reviewed": "2.32.0",
                "official_homepage": "https://requests.readthedocs.io/",
            },
            "provenance": {"sources": [{"url": "https://requests.readthedocs.io/", "source_type": "official_docs"}]},
            "learning_map": {
                "objectives": ["Use Python HTTP requests safely"],
                "concepts": [{"name": "sessions", "explanation": "Reuse connections"}],
            },
            "api_inventory": {"inventory_method": "official API reference review", "coverage": "partial", "entries": []},
            "use_cases": [{"category": "production", "scenario": "HTTP clients", "implementation_pattern": "sessions", "tradeoffs": [], "evidence": ["https://requests.readthedocs.io/"]}],
            "practice": {
                "worked_examples": [],
                "exercises": [{"difficulty": "beginner", "prompt": "Build a client", "acceptance_criteria": ["works"], "tests": ["test"]}] * 3,
                "projects": [],
                "debugging_playbook": [],
            },
            "rights": {
                "documentation_access": access,
                "derivative_summary_permission": derivative,
                "evaluation_permission": "approved",
                "training_permission": "pending",
            },
            "evaluation": {"target_benchmark": "HTTP client benchmark", "holdout": "unseen request cases", "regression": "API regression suite", "evidence_state": "guide_reviewed"},
            "status": status,
        }
        path = self.root / "data/buddy-library-study-guides/requests.json"
        path.write_text(json.dumps(guide), encoding="utf-8")

    def test_validator_rejects_missing_api_and_rights_evidence(self):
        errors = validate_library_guide_document({"schema_version": "wrong"})
        self.assertTrue(any("missing top-level fields" in error for error in errors))

    def test_internal_search_returns_approved_guide_and_never_claims_mastery(self):
        self.write_guide()
        result = search_internal_library_knowledge("Python HTTP sessions", root=self.root)
        self.assertEqual(result["source"], "dreamco_approved_library_guides")
        self.assertEqual(result["matches"][0]["canonical_id"], "python-requests")
        self.assertIsNone(result["knowledge_gap"])

    def test_internal_search_excludes_unreviewed_or_rights_blocked_guides(self):
        self.write_guide(status="draft")
        result = search_internal_library_knowledge("Python HTTP sessions", root=self.root)
        self.assertEqual(result["matches"], [])
        self.assertEqual(result["knowledge_gap"]["status"], "internal_knowledge_gap")

    def test_gated_guide_is_not_in_internal_search_without_approved_access(self):
        self.write_guide(access="gated")
        result = search_internal_library_knowledge("Python HTTP sessions", root=self.root)
        self.assertEqual(result["matches"], [])

    def test_gap_record_is_append_only_and_does_not_route_externally(self):
        record_library_knowledge_gap("Rust async runtime", root=self.root)
        record_library_knowledge_gap("Rust async runtime", root=self.root, reason="follow-up")
        lines = (self.root / "data/buddy-library-knowledge-gaps.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertFalse(json.loads(lines[0])["external_routing_performed"])

    def test_coverage_report_does_not_claim_worldwide_completeness(self):
        report = library_coverage_report(root=self.root)
        self.assertEqual(report["ecosystem_count"], 1)
        self.assertEqual(report["approved_guide_count"], 0)
        self.assertFalse(report["worldwide_completeness_claimed"])

    def test_empty_query_and_bad_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            search_internal_library_knowledge(" ", root=self.root)
        with self.assertRaises(ValueError):
            search_internal_library_knowledge("python", root=self.root, limit=0)

    def test_course_registry_exposes_library_discovery_lessons(self):
        lessons = load_course_lessons()
        rows = [row for row in lessons if row.track_id == "universal-software-libraries"]
        self.assertGreaterEqual(len(rows), 30)
        self.assertTrue(any("python" in row.lesson_id for row in rows))
        self.assertTrue(all(row.assessment for row in rows))
        self.assertTrue(all(row.rights_mode == "item_level_source_and_license_review" for row in rows))


if __name__ == "__main__":
    unittest.main()
