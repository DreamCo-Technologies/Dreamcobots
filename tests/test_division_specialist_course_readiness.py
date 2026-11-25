import tempfile
import unittest
from pathlib import Path

from tools.audit_division_specialist_course_readiness import audit


def fixtures():
    registry = {"divisions": [{"id": i, "name": f"MasterBot{i}"} for i in range(1, 66)]}
    crosswalk = {
        "schema": "dreamco.masterbot_domain_crosswalk.v1",
        "domains": [{"domain_id": f"domain-{i}", "owner_approval": None} for i in range(1, 56)],
        "masterbots": [
            {"masterbot_id": i, "owner_approval": True if i == 2 else None}
            for i in range(1, 66)
        ],
    }
    course = {
        "schema": "dreamco.buddy_25m_cpu_llm_course.v1",
        "delivery": {
            "division_assignments": [{} for _ in range(55)],
            "masterbot_assignments": [{} for _ in range(65)],
        },
    }
    manifest = {"schema": "dreamco.buddy_division_specialist_course_artifacts.v1", "artifacts": []}
    return registry, crosswalk, course, manifest


class DivisionSpecialistCourseReadinessTests(unittest.TestCase):
    def test_shared_foundation_does_not_count_as_specialist_course(self):
        report = audit(*fixtures())
        self.assertEqual(report["division_count"], 55)
        self.assertEqual(report["masterbot_count"], 65)
        self.assertEqual(report["target_count"], 120)
        self.assertEqual(report["required_module_count"], 960)
        self.assertEqual(report["ready_module_count"], 0)
        self.assertEqual(report["status"], "specialist_curriculum_gaps")
        self.assertEqual(report["owner_pending_target_count"], 119)
        self.assertFalse(report["mastery_claim"])
        self.assertFalse(report["production_claim"])

    def test_noncanonical_targets_are_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        manifest["artifacts"] = [{"target_type": "division", "target_id": "unknown", "module_id": "domain_overview"}]
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            audit(registry, crosswalk, course, manifest)

    def test_duplicate_artifact_identity_is_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        row = {"target_type": "division", "target_id": "domain-1", "module_id": "domain_overview"}
        manifest["artifacts"] = [row, row]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(registry, crosswalk, course, manifest)

    def test_invalid_module_is_rejected(self):
        registry, crosswalk, course, manifest = fixtures()
        manifest["artifacts"] = [{"target_type": "division", "target_id": "domain-1", "module_id": "random"}]
        with self.assertRaisesRegex(ValueError, "invalid"):
            audit(registry, crosswalk, course, manifest)

    def test_complete_artifact_requires_rights_and_human_review(self):
        registry, crosswalk, course, manifest = fixtures()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            guide = root / "docs/bootcamp/specialist/domain-1/overview.md"
            guide.parent.mkdir(parents=True)
            guide.write_text("Finance overview", encoding="utf-8")
            manifest["artifacts"] = [{
                "target_type": "division", "target_id": "domain-1", "module_id": "domain_overview",
                "guide_path": "docs/bootcamp/specialist/domain-1/overview.md",
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
