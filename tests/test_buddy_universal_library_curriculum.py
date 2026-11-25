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

    def test_ecosystem_adapter_coverage_matches_registered_providers(self):
        coverage = self.read_json("config/buddy-library-ecosystem-adapter-coverage.json")
        adapters = self.read_json("config/buddy-library-registry-adapters.json")
        ecosystems = coverage["ecosystems"]
        self.assertEqual(len(ecosystems), 38)
        self.assertEqual(coverage["ecosystem_count"], len(ecosystems))
        self.assertEqual(coverage["automated_ecosystem_count"], 10)
        self.assertEqual(coverage["manual_ecosystem_count"], 28)
        self.assertEqual(coverage["automated_ecosystem_count"] + coverage["manual_ecosystem_count"], len(ecosystems))
        provider_ids = {provider["id"] for provider in adapters["providers"]}
        for ecosystem in ecosystems:
            if ecosystem["adapter_status"].startswith("implemented_"):
                self.assertTrue(set(ecosystem["provider"].split(";")).issubset(provider_ids))
            else:
                self.assertEqual(ecosystem["adapter_status"], "manual_review_required")
        self.assertEqual(next(row for row in ecosystems if row["id"] == "java")["provider"], "maven-central")
        self.assertEqual(next(row for row in ecosystems if row["id"] == "perl")["provider"], "metacpan")

    def test_runtime_bridge_and_discovery_counts_are_consistent(self):
        curriculum = self.read_json("config/buddy-universal-library-curriculum.json")
        runtime = curriculum["runtime"]
        coverage = self.read_json("config/buddy-library-ecosystem-adapter-coverage.json")
        self.assertEqual(runtime["host_bridge"], "buddy.learning.runtime_bridge.BuddyLearningBridge.library_knowledge")
        self.assertEqual(runtime["internal_retrieval_engine"], "foundry.local_rag.LocalRagStore.tfidf")
        self.assertEqual(runtime["automated_ecosystem_metadata_discovery_count"], coverage["automated_ecosystem_count"])
        self.assertEqual(runtime["manual_ecosystem_catalog_review_count"], coverage["manual_ecosystem_count"])
        self.assertTrue(runtime["external_discovery_requires_explicit_host_opt_in"])
        self.assertTrue(runtime["gap_persistence_requires_redacted_query"])
        self.assertFalse(runtime["general_external_model_routing_on_gap"])
        self.assertEqual(runtime["study_queue_completion_default"], "queued_not_studied")
        self.assertFalse(runtime["study_queue_mastery_default"])

    def test_guide_schema_requires_evidence_and_rights(self):
        schema = self.read_json("config/buddy-library-study-guide.schema.json")
        required = set(schema["required"])
        self.assertTrue({"provenance", "api_inventory", "practice", "evaluation", "rights"}.issubset(required))
        self.assertIn("training_permission", schema["properties"]["rights"]["required"])
        self.assertIn("holdout", schema["properties"]["evaluation"]["required"])


if __name__ == "__main__":
    unittest.main()
