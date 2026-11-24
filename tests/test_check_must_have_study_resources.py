#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.check_must_have_study_resources import main, validate_catalogs  # noqa: E402


class MustHaveStudyTest(unittest.TestCase):
    def test_one_hundred_unique(self):
        self.assertEqual(main(), 0)

    def test_tolkien_study_track_is_scholarly_and_rights_gated(self):
        report = validate_catalogs()
        self.assertTrue(report["ok"])
        import json
        expansion = json.loads((ROOT / "config/buddy-study-resources-1101-1200-expansion.json").read_text())
        track = next(x for x in expansion["specialized_study_tracks"] if x["track_id"] == "tolkien")
        self.assertEqual(len(track["lesson_sequence"]), 8)
        self.assertFalse(track["rights_and_safety"]["primary_tolkien_texts_training_eligible"])
        self.assertFalse(track["rights_and_safety"]["model_weight_training_authorized"])
        self.assertFalse(track["rights_and_safety"]["materials_referencing_characters_stories_places_events_or_other_elements_authorized"])
        self.assertEqual(track["rights_and_safety"]["unknown_rights_status"], "BLOCKED")

    def test_database_and_dataset_track_is_ten_lessons_and_fail_closed(self):
        import json
        expansion = json.loads((ROOT / "config/buddy-study-resources-1101-1200-expansion.json").read_text())
        track = next(x for x in expansion["specialized_study_tracks"] if x["track_id"] == "database-and-dataset-engineering")
        self.assertEqual(len(track["lesson_sequence"]), 10)
        rights = track["rights_and_safety"]
        self.assertFalse(rights["live_database_writes_authorized"])
        self.assertFalse(rights["production_migrations_authorized"])
        self.assertFalse(rights["bulk_dataset_download_authorized"])
        self.assertFalse(rights["model_weight_training_authorized"])
        self.assertEqual(rights["unknown_rights_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
