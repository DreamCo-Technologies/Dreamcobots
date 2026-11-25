from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "config" / "buddy-tokenizer-training-curriculum.json"
GUIDE = ROOT / "docs" / "BUDDY_TOKENIZER_TRAINING_STUDY_GUIDE.md"


class BuddyTokenizerCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CURRICULUM.read_text(encoding="utf-8"))
        cls.guide = GUIDE.read_text(encoding="utf-8")

    def test_curriculum_has_twelve_ordered_lessons(self):
        lessons = self.data["lessons"]
        self.assertEqual(len(lessons), 12)
        self.assertEqual([item["id"] for item in lessons], [f"tok-{i:02d}" for i in range(1, 13)])
        self.assertTrue(all(item.get("outcome") and item.get("lab") and item.get("assessment") for item in lessons))

    def test_references_are_link_only_and_rights_qualified(self):
        refs = self.data["course_references"]
        self.assertGreaterEqual(len(refs), 4)
        self.assertTrue(all(ref["url"].startswith("https://") and ref.get("rights") for ref in refs))

    def test_mastery_requires_evidence_not_reading(self):
        self.assertTrue(self.data["mastery"]["reading_alone_is_not_mastery"])
        self.assertTrue(self.data["mastery"]["tokenizer_training_is_not_model_weight_training"])
        self.assertIn("private holdout", self.data["mastery"]["required"])

    def test_guide_covers_core_methods_and_release_gates(self):
        for phrase in ("BPE", "WordPiece", "Unigram", "SentencePiece", "special tokens", "private holdout", "model/checkpoint"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.guide.lower())

    def test_all_course_reference_urls_are_in_the_guide(self):
        for ref in self.data["course_references"]:
            with self.subTest(url=ref["url"]):
                self.assertIn(ref["url"], self.guide)


if __name__ == "__main__":
    unittest.main()
