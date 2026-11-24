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
