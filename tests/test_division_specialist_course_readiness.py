import tempfile
import unittest
from pathlib import Path

from tools.audit_division_specialist_course_readiness import audit


def fixtures():
    registry = {"divisions": [{"id": 1, "name": "Finance"}, {"id": 2, "name": "RealEstate"}]}
    crosswalk = {
        "schema": "dreamco.masterbot_domain_crosswalk.v1",
        "domains": [
            {"domain_id": "finance", "owner_approval": None},
            {"domain_id": "real-estate", "owner_approval": None},
        ],
        "masterbots": [
            {"masterbot_id": 1, "owner_approval": None},
            {"masterbot_id": 2, "owner_approval": True},
        ],
    }
    course = {
        "schema": "dreamco.buddy_25m_cpu_llm_course.v1",
        "delivery": {"division_assignments": [{}, {}], "masterbot_assignments": [{}, {}]},
    }
    manifest = {"schema": "dreamco.buddy_division_specialist_course_artifacts.v1", "artifacts": []}
    return registry, crosswalk, course, manifest


class DivisionSpecialistCourseReadinessTests(unittest.TestCase):
    def test_shared_foundation_does_not_count_as_specialist_course(self):
        report = audit(*fixtures())
        self.assertEqual(report["division_count"], 2)
        self.assertEqual(report["masterbot_count"], 2)
        self.assertEqual(report["required_module_count"], 32)
        self.assertEqual(report["ready_module_count"], 0)
        self.assertEqual(report["status"], "specialist_curriculum_gaps")
        self.assertEqual(report["owner_pending_target_count"], 3)
        self.assertFalse(report["mastery_claim"])
        self.assertFalse(report["production_claim"])

    def test_noncanonical_targets_are_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        manifest["artifacts"] = [{"target_type": "division", "target_id": "unknown", "module_id": "domain_overview"}]
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            audit(registry, crosswalk, course, manifest)

    def test_duplicate_artifact_identity_is_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        row = {"target_type": "division", "target_id": "finance", "module_id": "domain_overview"}
        manifest["artifacts"] = [row, row]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(registry, crosswalk, course, manifest)

    def test_invalid_module_is_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        manifest["artifacts"] = [{"target_type": "division", "target_id": "finance", "module_id": "random"}]
        with self.assertRaisesRegex(ValueError, "invalid"):
            audit(registry, crosswalk, course, manifest)

    def test_complete_artifact_requires_rights_and_human_review(self):
        registry, crosswalk, course, manifest = fixtures()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            guide = root / "docs/bootcamp/specialist/finance/overview.md"
            guide.parent.mkdir(parents=True)
            guide.write_text("Finance overview", encoding="utf-8")
            manifest["artifacts"] = [{
                "target_type": "division", "target_id": "finance", "module_id": "domain_overview",
                "guide_path": "docs/bootcamp/specialist/finance/overview.md",
                "learning_objectives": ["a", "b", "c"],
                "exercises": [{"id": "x"}, {"id": "y"}],
                "assessment": {"id": "assessment"},
                "citations": [{"url": "https://example.org", "accessed_at": "2026-11-25", "rights_evidence_ref": "permission-1"}],
                "rights_review": "approved", "human_review": "approved",
            }]
            report = audit(registry, crosswalk, course, manifest, root=root)
            self.assertEqual(report["ready_module_count"], 1)
            self.assertEqual(report["status"], "specialist_curriculum_gaps")


if __name__ == "__main__":
    unittest.main()
