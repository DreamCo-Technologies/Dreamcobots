import tempfile
import unittest
from pathlib import Path

from tools.audit_huggingface_module_review_readiness import audit


def guides():
    return {
        "schema": "dreamco.huggingface_18_ecosystem_module_guides.v1",
        "official_courses": [
            {"id": f"course-{i}", "transcript_permission": "not_granted", "training_data_authorized": False}
            for i in range(12)
        ],
        "modules": [{"module_id": f"HFEC-{i:02d}", "title": f"Module {i}"} for i in range(1, 19)],
    }


def reviews():
    return {"schema": "dreamco.huggingface_module_review_artifacts.v1", "modules": []}


class HuggingFaceModuleReviewReadinessTests(unittest.TestCase):
    def test_draft_catalog_is_not_mistaken_for_reviewed_courseware(self):
        report = audit(guides(), reviews())
        self.assertEqual(report["module_count"], 18)
        self.assertEqual(report["ready_for_study_count"], 0)
        self.assertEqual(report["status"], "human_review_and_artifact_gaps")
        self.assertFalse(report["transcript_permission_granted"])
        self.assertFalse(report["training_data_authorized"])
        self.assertFalse(report["mastery_awarded"])

    def test_module_requires_real_hashed_guide_lab_assessment_citations_and_reviews(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = {}
            for field, filename in (
                ("guide_path", "guide.md"), ("lab_path", "lab.md"), ("assessment_path", "assessment.json")
            ):
                path = root / "docs/bootcamp/huggingface/HFEC-01" / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(filename, encoding="utf-8")
                import hashlib
                files[field] = f"docs/bootcamp/huggingface/HFEC-01/{filename}"
                files[field.replace("_path", "_sha256")] = hashlib.sha256(filename.encode()).hexdigest()
            row = {
                "module_id": "HFEC-01", **files,
                "citations": [{"url": "https://huggingface.co/docs", "accessed_at": "2026-11-25", "rights_evidence_ref": "official-docs"}],
                "rights_review": "approved", "human_review": "approved",
                "reviewer": "reviewer-1", "reviewed_at": "2026-11-25T08:00:00Z",
            }
            report = audit(guides(), {"schema": "dreamco.huggingface_module_review_artifacts.v1", "modules": [row]}, root=root)
            self.assertEqual(report["ready_for_study_count"], 1)
            self.assertEqual(report["status"], "human_review_and_artifact_gaps")

    def test_tampered_guide_hash_is_not_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "docs/bootcamp/huggingface/HFEC-01/guide.md"
            path.parent.mkdir(parents=True)
            path.write_text("actual content", encoding="utf-8")
            row = {
                "module_id": "HFEC-01", "guide_path": "docs/bootcamp/huggingface/HFEC-01/guide.md",
                "guide_sha256": "0" * 64,
            }
            report = audit(guides(), {"schema": "dreamco.huggingface_module_review_artifacts.v1", "modules": [row]}, root=root)
            self.assertFalse(report["modules"][0]["artifacts"]["guide_path"])

    def test_duplicate_and_noncanonical_modules_are_rejected(self):
        manifest = reviews()
        manifest["modules"] = [{"module_id": "HFEC-01"}, {"module_id": "HFEC-01"}]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(guides(), manifest)
        manifest["modules"] = [{"module_id": "HFEC-99"}]
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            audit(guides(), manifest)

    def test_official_course_permissions_cannot_be_inferred(self):
        source = guides()
        source["official_courses"][0]["training_data_authorized"] = True
        with self.assertRaisesRegex(ValueError, "permissions"):
            audit(source, reviews())


if __name__ == "__main__":
    unittest.main()
