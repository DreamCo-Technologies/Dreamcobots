import json
import unittest
from pathlib import Path

class TolkienStudyTrackTests(unittest.TestCase):
    def test_tolkien_track_is_curriculum_only_and_copyright_gated(self):
        root=Path(__file__).resolve().parents[1]
        track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
        rights=track["rights_policy"]
        self.assertFalse(rights["copyrighted_tolkien_text_ingestion"])
        self.assertFalse(rights["training_on_copyrighted_tolkien_text"])
        self.assertFalse(rights["verbatim_text_reproduction"])
        self.assertEqual(rights["unknown_rights"],"BLOCK")
        self.assertGreaterEqual(len(track["curriculum"]),8)
        self.assertTrue(track["assessment"]["holdout_policy"])

    def test_tolkien_track_requires_item_level_translation_and_edition_review(self):
        root=Path(__file__).resolve().parents[1]
        track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
        self.assertTrue(any("verify edition and translation rights individually" in x["scope"] for x in track["source_families"]))
        self.assertIn("Do not ingest Tolkien novels",track["safeguards"][0])


    def test_extended_tolkien_study_path_has_twelve_units_and_pending_course_slot(self):
        root=Path(__file__).resolve().parents[1]
        track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
        self.assertEqual(len(track["extended_study_path"]),12)
        self.assertEqual(track["course_integration"]["status"],"NEEDS_USER_SUPPLIED_COURSE_REFERENCE")
        self.assertIsNone(track["course_integration"]["url"])
        self.assertFalse(track["mastery_policy"]["reading_or_catalog_discovery_is_mastery"])

    def test_tolkien_advanced_units_preserve_rights_gates_and_evidence(self):
        root=Path(__file__).resolve().parents[1]
        track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
        self.assertEqual(track["mastery_policy"]["unknown_rights"],"BLOCKED")
        self.assertFalse(track["mastery_policy"]["copyrighted_tolkien_text_model_training"])
        for unit in track["extended_study_path"]:
            self.assertTrue(unit["outcome"])
            self.assertTrue(unit["lab"])
            self.assertTrue(unit["assessment"])
            self.assertEqual(unit["rights_gate"],"secondary scholarship/metadata only unless item-level permission is verified")
