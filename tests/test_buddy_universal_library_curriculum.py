import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UniversalLibraryCurriculumTests(unittest.TestCase):
    def read_json(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_curriculum_declares_discovery_and_truth_boundaries(self):
        curriculum = self.read_json("config/buddy-universal-library-curriculum.json")
        self.assertEqual(curriculum["status"], "discovery_driven_curriculum_contract")
        self.assertTrue(curriculum["scope"]["no_finite_worldwide_completeness_claim"])
        self.assertTrue(curriculum["routing"]["internal_first"])
        self.assertTrue(curriculum["safety"]["dataset_scripts_disabled_by_default"])
        self.assertTrue(curriculum["safety"]["model_weight_training_requires_separate_explicit_approval"])

    def test_curriculum_crosswalks_existing_bootcamp_sources(self):
        curriculum = self.read_json("config/buddy-universal-library-curriculum.json")
        crosswalks = curriculum["crosswalks"]
        for key in ("onet_source", "huggingface_source", "huggingface_task_taxonomy", "division_source", "masterbot_source", "course_track_registry"):
            self.assertTrue(crosswalks[key])

    def test_course_registry_includes_universal_library_track(self):
        registry = self.read_json("config/buddy-course-track-registry.json")
        track = next(item for item in registry["tracks"] if item["id"] == "universal-software-libraries")
        self.assertEqual(track["source"], "config/buddy-universal-library-curriculum.json")
        self.assertEqual(track["guide_schema"], "config/buddy-library-study-guide.schema.json")

    def test_guide_schema_requires_evidence_and_rights(self):
        schema = self.read_json("config/buddy-library-study-guide.schema.json")
        required = set(schema["required"])
        self.assertTrue({"provenance", "api_inventory", "practice", "evaluation", "rights"}.issubset(required))
        self.assertIn("training_permission", schema["properties"]["rights"]["required"])
        self.assertIn("holdout", schema["properties"]["evaluation"]["required"])


if __name__ == "__main__":
    unittest.main()
